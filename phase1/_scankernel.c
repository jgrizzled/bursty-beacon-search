/* Exact cache-optimized C kernel for the M2/M3 scanner-grid scans.
 *
 * Same frozen search as pipeline.scan_scanner / fastscan.scan_scanner_fast:
 * identical grids (sigma doubling, tau filtering, t0 = i*h), identical
 * two-bin profile likelihood (1e-12 clamps, rate-ordering and e<=0 pooled
 * replacement), identical first-in-scan-order argmax under strict '>'.
 *
 * Speed comes from two exact techniques, not approximation:
 *  1. Sequential sweeps: the t0 grid is increasing, so event counts and
 *     piecewise-linear exposure lookups advance forward pointers
 *     (amortized O(1) per t0) over arrays extended to [0, 2T) so no
 *     wraparound arithmetic is needed.
 *  2. A threshold table e_star[n]: the coded two-bin ll at fixed n_in is
 *     monotone non-increasing in e_in (decreasing in the valid region,
 *     then equal to the pooled floor), so a t0 can only strictly exceed
 *     the running best B when e_in < e_star[n_in], where e_star is the
 *     unique boundary found by bisection. The table depends only on
 *     (n_tot, e_tot, B) and is rebuilt only when B improves. Log calls
 *     therefore happen only at competitive grid points; the reported
 *     maxima are exact.
 *  3. Shared first-interval cache for M3: at fixed (T, sigma), every
 *     non-overlapping tau uses the same [t0, t0+sigma) first interval.
 *     Its count and exposure are swept once over t0 and reused while the
 *     original tau/t0 scan order and likelihood arithmetic are preserved.
 *
 * Caller (scankernel.py) passes, per period T: sorted event phases and
 * the cumulative phase-exposure polyline of fastscan.fold_exposure, both
 * extended to [0, 2T).
 */

#include <float.h>
#include <math.h>
#include <stdlib.h>

typedef struct {
    const double *phi2;   /* sorted event phases, extended: phi and phi+T */
    int n2;               /* = 2 * n_events */
    const double *xs2;    /* exposure polyline nodes, extended to 2T */
    const double *es2;
    int m2;               /* number of polyline nodes */
} FoldTables;

typedef struct {
    int lo_ev, hi_ev;     /* event pointers: # phi2 < lo, # phi2 < hi */
    int lo_sg, hi_sg;     /* polyline segment pointers */
} Walkers;

static void walkers_init(Walkers *w) {
    w->lo_ev = w->hi_ev = 0;
    w->lo_sg = w->hi_sg = 0;
}

static inline int adv_ev(const FoldTables *ft, int p, double x) {
    while (p < ft->n2 && ft->phi2[p] < x) p++;
    return p;
}

static inline int adv_sg(const FoldTables *ft, int p, double x) {
    /* segment index k with xs2[k] <= x (largest such k < m2-1) */
    while (p < ft->m2 - 2 && ft->xs2[p + 1] <= x) p++;
    return p;
}

static inline double ev_at(const FoldTables *ft, int k, double x) {
    /* np.interp-parity piecewise-linear evaluation on segment k */
    double x0 = ft->xs2[k], x1 = ft->xs2[k + 1];
    double y0 = ft->es2[k], y1 = ft->es2[k + 1];
    if (x1 == x0) return y0;
    return y0 + (y1 - y0) / (x1 - x0) * (x - x0);
}

/* coded two-bin profile ll, formula-identical to fastscan._two_bin_vec */
static double two_bin(double n_in, double e_in, int n_tot, double e_tot,
                      double pooled) {
    double n_out = (double)n_tot - n_in;
    double e_out = e_tot - e_in;
    double ei = e_in > 1e-12 ? e_in : 1e-12;
    double eo = e_out > 1e-12 ? e_out : 1e-12;
    double ll_in = n_in > 0 ? n_in * log(n_in / ei) - n_in : 0.0;
    double ll_out = n_out > 0 ? n_out * log(n_out / eo) - n_out : 0.0;
    double ll = ll_in + ll_out;
    double lam_in = n_in / ei;
    double lam_out = n_out / eo;
    if (lam_in < lam_out) ll = pooled;
    if (e_in <= 0.0) ll = pooled;
    return ll;
}

/* rebuild e_star for threshold B: largest e with two_bin(n, e) > B, found
 * by bisection on the monotone non-increasing coded ll; 0 if even e->0+
 * cannot beat B; e_tot if even e_tot beats B. */
static void build_table(double *e_star, int n_tot, double e_tot,
                        double pooled, double B) {
    for (int n = 0; n <= n_tot; n++) {
        double nn = (double)n;
        if (two_bin(nn, 1e-13, n_tot, e_tot, pooled) <= B) {
            e_star[n] = 0.0;          /* can never beat B */
            continue;
        }
        if (two_bin(nn, e_tot, n_tot, e_tot, pooled) > B) {
            e_star[n] = e_tot * 2.0;  /* always passes */
            continue;
        }
        double lo = 1e-13, hi = e_tot;
        for (int it = 0; it < 60; it++) {
            double mid = 0.5 * (lo + hi);
            if (two_bin(nn, mid, n_tot, e_tot, pooled) > B) lo = mid;
            else hi = mid;
        }
        e_star[n] = hi;               /* e_in < hi may beat B (padded) */
    }
}

/* ------------------------------------------------------------------ *
 * Batched variant: scan_period_multi evaluates S event streams that
 * share one window function (prereg 6.2 simulations: same campaign,
 * different simulated streams). The exposure-side work -- polyline
 * walks, ev_at interpolation, the cell geometry -- is stream-independent
 * and computed ONCE per cell; only event counting, pruning, and the
 * two-bin evaluation run per stream. Per-stream results (best, argmax,
 * e_star pruning state) are bit-identical to S independent scan_period
 * calls: the cell order is unchanged and each stream's accept/reject
 * decisions depend only on its own state.
 * ------------------------------------------------------------------ */

typedef struct { int lo, hi; } EvPtr;   /* per-stream event pointers */

static inline int adv_ptr(const double *phi2, int n2, int p, double x) {
    while (p < n2 && phi2[p] < x) p++;
    return p;
}

/* ------------------------------------------------------------------ *
 * Segmented exact sweep (batched kernel only).
 *
 * Between breakpoints -- an interval edge crossing an exposure-polyline
 * node or any stream's event phase -- every stream's event count is
 * constant in t0 and the exact in-window exposure is affine in t0. A
 * whole run of t0 grid points is skipped ONLY when every stream
 * provably fails the same "e_in >= e_star[n]" prune test the dense walk
 * applies at each point: the run's minimum endpoint exposure minus a
 * rigorous rounding guard already meets the threshold, so each skipped
 * cell is one the dense walk would 'continue' past without touching any
 * state. Runs that might compete are walked with the dense-path
 * arithmetic verbatim. Outputs (best, argmax, pruning state) are
 * therefore bit-identical to the dense paths -- this is a traversal
 * shortcut, not a change of evaluation.
 *
 * Guard: computed e_in at any grid point differs from the affine model
 * through the run's endpoints by at most a few ulps of the exposure
 * scale (<= ~24 eps E_max interpolation/summation rounding per
 * evaluation, plus <= ~24 eps T S_max from position rounding times the
 * polyline slope). 64 eps (E_max + T S_max) covers both with an
 * order-of-magnitude margin; cells within the guard of their threshold
 * simply fall back to the dense walk.
 *
 * SEG_MODE: 0 auto (density heuristic), 1 force on, -1 force off --
 * a pure performance knob; every setting yields identical results
 * (exercised by scripts/validate_fastscan.py section [7]).
 * ------------------------------------------------------------------ */

static int SEG_MODE = 0;

void scankernel_set_seg_mode(int m) { SEG_MODE = m; }

/* smallest i in (i_lo, n_t0) whose edge position pos(i) = (double)i*h + u
 * (+ w if is_hi) satisfies pos > x (strict) or pos >= x; n_t0 if none.
 * pos(i) is nondecreasing in i (rounding is monotone), so the predicate
 * is monotone and the guess +/- walk is exact. */
static long find_cross(long i_lo, long n_t0, double x, int strict,
                       double h, double u, double w, int is_hi) {
    double base = x - u - (is_hi ? w : 0.0);
    double gd = base / h;
    long g;
    if (gd <= (double)(i_lo + 1)) g = i_lo + 1;
    else if (gd >= (double)n_t0) g = n_t0;
    else g = (long)gd;
    if (g < i_lo + 1) g = i_lo + 1;
    if (g > n_t0) g = n_t0;
    while (g < n_t0) {
        double p = (double)g * h + u;
        if (is_hi) p += w;
        if (strict ? (p > x) : (p >= x)) break;
        g++;
    }
    while (g > i_lo + 1) {
        double p = (double)(g - 1) * h + u;
        if (is_hi) p += w;
        if (strict ? (p > x) : (p >= x)) g--;
        else break;
    }
    return g;
}

/* One (sigma, tau) sweep over t0 in segmented form. Geometry: n_iv
 * intervals [t0+u[j], t0+u[j]+w[j]), the same cells as the dense paths.
 * ev is caller storage for 2*S EvPtr (per interval x stream). */
static void seg_sweep_multi(const FoldTables *ex, const double *phi2_all,
                            const long long *phi2_off, int S, double h,
                            long n_t0, const double *u, const double *w,
                            int n_iv, double sig, double tau,
                            const int *n_tot, double e_tot,
                            const double *pooled, double *best,
                            double *out_arg, double *e_star_all,
                            long long estar_stride, double *table_B,
                            int *improved_out, EvPtr *ev, double guard) {
    int n_edge = 2 * n_iv;
    int sg[4] = {0, 0, 0, 0};       /* edge 2j = lo_j, 2j+1 = hi_j */
    for (int j = 0; j < n_iv; j++)
        for (int s = 0; s < S; s++)
            ev[(size_t)j * S + s].lo = ev[(size_t)j * S + s].hi = 0;
    long i = 0;
    while (i < n_t0) {
        double t0 = (double)i * h;
        double lo_j[2], hi_j[2];
        for (int j = 0; j < n_iv; j++) {
            lo_j[j] = t0 + u[j];
            hi_j[j] = lo_j[j] + w[j];
            sg[2 * j] = adv_sg(ex, sg[2 * j], lo_j[j]);
            sg[2 * j + 1] = adv_sg(ex, sg[2 * j + 1], hi_j[j]);
        }
        for (int s = 0; s < S; s++) {
            const double *ph = phi2_all + phi2_off[s];
            int n2 = (int)(phi2_off[s + 1] - phi2_off[s]);
            for (int j = 0; j < n_iv; j++) {
                EvPtr *P = &ev[(size_t)j * S + s];
                P->lo = adv_ptr(ph, n2, P->lo, lo_j[j]);
                P->hi = adv_ptr(ph, n2, P->hi, hi_j[j]);
            }
        }
        /* run end: first i' > i where any edge's node segment or any
         * stream's count changes */
        long i_end = n_t0;
        for (int e = 0; e < n_edge; e++) {
            int j = e >> 1, is_hi = e & 1;
            if (sg[e] < ex->m2 - 2) {           /* node: pos >= xs2[k+1] */
                long c = find_cross(i, n_t0, ex->xs2[sg[e] + 1], 0, h,
                                    u[j], w[j], is_hi);
                if (c < i_end) i_end = c;
            }
            double ev_x = HUGE_VAL;             /* event: pos > phi */
            for (int s = 0; s < S; s++) {
                const double *ph = phi2_all + phi2_off[s];
                int n2 = (int)(phi2_off[s + 1] - phi2_off[s]);
                const EvPtr *P = &ev[(size_t)j * S + s];
                int p = is_hi ? P->hi : P->lo;
                if (p < n2 && ph[p] < ev_x) ev_x = ph[p];
            }
            if (ev_x < HUGE_VAL) {
                long c = find_cross(i, n_t0, ev_x, 1, h, u[j], w[j],
                                    is_hi);
                if (c < i_end) i_end = c;
            }
        }
        if (i_end <= i) i_end = i + 1;          /* defensive */
        /* endpoint exposures, dense-path accumulation order. If every
         * edge sits in a zero-slope polyline segment, ev_at returns the
         * node value exactly, so e_in is bitwise CONSTANT over the run:
         * no rounding guard is needed (this covers the dominant case,
         * exposure gaps, where e_in == 0 == e_star[0]). */
        int flat = 1;
        for (int e = 0; e < n_edge; e++)
            if (ex->es2[sg[e] + 1] != ex->es2[sg[e]]) { flat = 0; break; }
        double e_a = 0.0;
        for (int j = 0; j < n_iv; j++)
            e_a += ev_at(ex, sg[2 * j + 1], hi_j[j])
                 - ev_at(ex, sg[2 * j], lo_j[j]);
        double e_min = e_a;
        if (!flat && i_end - 1 > i) {
            double t0b = (double)(i_end - 1) * h;
            double e_b = 0.0;
            for (int j = 0; j < n_iv; j++) {
                double lob = t0b + u[j];
                double hib = lob + w[j];
                e_b += ev_at(ex, sg[2 * j + 1], hib)
                     - ev_at(ex, sg[2 * j], lob);
            }
            if (e_b < e_min) e_min = e_b;
        }
        double g_eff = flat ? 0.0 : guard;
        /* certificate: every stream pruned at every point of the run? */
        int all_pruned = 1;
        for (int s = 0; s < S; s++) {
            double n_in = 0.0;
            for (int j = 0; j < n_iv; j++)
                n_in += (double)(ev[(size_t)j * S + s].hi
                                 - ev[(size_t)j * S + s].lo);
            int ni = (int)(n_in + 0.5);
            if (!(e_min - g_eff
                  >= e_star_all[(size_t)s * estar_stride + ni])) {
                all_pruned = 0;
                break;
            }
        }
        if (all_pruned) {
            i = i_end;
            continue;
        }
        /* competitive run: dense walk, verbatim uncached-path body */
        for (; i < i_end; i++) {
            double t0w = (double)i * h;
            double e_in = 0.0;
            double lo_w[2], hi_w[2];
            for (int j = 0; j < n_iv; j++) {
                lo_w[j] = t0w + u[j];
                hi_w[j] = lo_w[j] + w[j];
                sg[2 * j] = adv_sg(ex, sg[2 * j], lo_w[j]);
                sg[2 * j + 1] = adv_sg(ex, sg[2 * j + 1], hi_w[j]);
                e_in += ev_at(ex, sg[2 * j + 1], hi_w[j])
                      - ev_at(ex, sg[2 * j], lo_w[j]);
            }
            for (int s = 0; s < S; s++) {
                const double *ph = phi2_all + phi2_off[s];
                int n2 = (int)(phi2_off[s + 1] - phi2_off[s]);
                double n_in = 0.0;
                for (int j = 0; j < n_iv; j++) {
                    EvPtr *P = &ev[(size_t)j * S + s];
                    P->lo = adv_ptr(ph, n2, P->lo, lo_w[j]);
                    P->hi = adv_ptr(ph, n2, P->hi, hi_w[j]);
                    n_in += (double)(P->hi - P->lo);
                }
                int ni = (int)(n_in + 0.5);
                const double *es = e_star_all + (size_t)s * estar_stride;
                if (e_in >= es[ni]) continue;
                double ll = two_bin(n_in, e_in, n_tot[s], e_tot,
                                    pooled[s]);
                if (ll > best[s]) {
                    best[s] = ll;
                    out_arg[s * 4 + 0] = sig;
                    out_arg[s * 4 + 1] = tau;
                    out_arg[s * 4 + 2] = t0w;
                    out_arg[s * 4 + 3] = ll;
                    improved_out[s] = 1;
                    build_table(e_star_all + (size_t)s * estar_stride,
                                n_tot[s], e_tot, pooled[s], best[s]);
                    table_B[s] = best[s];
                }
            }
        }
    }
}

/* Batched scan of one period T over S streams.
 * phi2_all/phi2_off: stream s's extended phases are
 *   phi2_all[phi2_off[s] .. phi2_off[s+1]).
 * n_tot/pooled/best/table_B: per-stream arrays [S]; out_arg: [S][4];
 * e_star_all: [S][estar_stride]; improved_out: [S] set to 1 when that
 * stream's best improved during this call. Returns count of improved
 * streams. */
int scan_period_multi(const double *phi2_all, const long long *phi2_off,
                      int S, const double *xs2, const double *es2, int m2,
                      double T, const int *n_tot, double e_tot,
                      const double *pooled, double sigma_min,
                      const double *tau_grid, int n_tau_grid,
                      double t0_frac, int mode, double *best,
                      double *out_arg, double *e_star_all,
                      long long estar_stride, double *table_B,
                      int *improved_out) {
    FoldTables ex = {NULL, 0, xs2, es2, m2};   /* exposure side only */
    int n_improved = 0;
    /* segmented-sweep guard and density inputs (see seg_sweep_multi) */
    double slope_max = 0.0;
    for (int k = 0; k < m2 - 1; k++) {
        double dx = xs2[k + 1] - xs2[k];
        if (dx > 0.0) {
            double sl = (es2[k + 1] - es2[k]) / dx;
            if (sl > slope_max) slope_max = sl;
        }
    }
    double seg_guard = 64.0 * DBL_EPSILON
                       * (es2[m2 - 1] + T * slope_max);
    double total_n2 = (double)phi2_off[S];
    for (int s = 0; s < S; s++) {
        improved_out[s] = 0;
        if (table_B[s] < best[s]) {
            build_table(e_star_all + (size_t)s * estar_stride, n_tot[s],
                        e_tot, pooled[s], best[s]);
            table_B[s] = best[s];
        }
    }

    /* Per-period caches: shared exposure of the first interval, and the
     * per-stream first-interval counts (the M3 tau-cache of the single-
     * stream kernel, extended per stream). Allocation failure falls back
     * to the uncached path. */
    long cache_len = 0;
    double *base_e = NULL;      /* [cache_len] shared */
    double *base_n = NULL;      /* [S][cache_len] */
    if (mode == 1 && sigma_min > 0.0 && t0_frac > 0.0) {
        cache_len = (long)ceil(T / (t0_frac * sigma_min));
        if (cache_len > 0) {
            base_e = malloc((size_t)cache_len * sizeof(*base_e));
            base_n = malloc((size_t)S * (size_t)cache_len
                            * sizeof(*base_n));
            if (!base_e || !base_n) {
                free(base_e); free(base_n);
                base_e = base_n = NULL;
            }
        }
    }
    EvPtr *ev = malloc((size_t)S * 2 * sizeof(*ev));   /* 2 intervals max */
    EvPtr *ev2 = malloc((size_t)S * sizeof(*ev2));
    if (!ev || !ev2) {                    /* cannot scan without pointers */
        free(base_e); free(base_n); free(ev); free(ev2);
        return -1;
    }

    for (double sig = sigma_min; sig <= 0.5 * T; sig *= 2.0) {
        double h = t0_frac * sig;
        long n_t0 = (long)ceil(T / h);
        int n_tau = 0;
        double taus_local[64];
        if (mode == 1) {
            for (int i = 0; i < n_tau_grid && n_tau < 64; i++)
                if (tau_grid[i] <= 0.5 * T) taus_local[n_tau++] = tau_grid[i];
            if (n_tau == 0) break;
        } else {
            n_tau = 1;
            taus_local[0] = -1.0;
        }

        double s1 = sig < T ? sig : T;

        /* Segmented sweep when the t0 grid is much denser than the
         * breakpoint set (sparse-campaign octaves). Pure performance
         * choice: results are bit-identical on every path. */
        int use_seg = SEG_MODE > 0
            || (SEG_MODE == 0
                && (double)n_t0 >= 8.0 * ((double)m2 + total_n2));
        if (use_seg) {
            for (int it = 0; it < n_tau; it++) {
                double tau = taus_local[it];
                double u[2], w[2];
                int n_iv;
                if (mode == 0) {
                    n_iv = 1; u[0] = 0.0; w[0] = s1;
                } else if (tau < s1) {
                    double v2 = tau + sig < T ? tau + sig : T;
                    double top = v2 > s1 ? v2 : s1;
                    n_iv = 1; u[0] = 0.0; w[0] = top;
                } else {
                    n_iv = 2;
                    u[0] = 0.0; w[0] = s1;
                    u[1] = tau;
                    w[1] = (tau + sig < T ? tau + sig : T) - tau;
                }
                seg_sweep_multi(&ex, phi2_all, phi2_off, S, h, n_t0,
                                u, w, n_iv, sig, tau, n_tot, e_tot,
                                pooled, best, out_arg, e_star_all,
                                estar_stride, table_B, improved_out,
                                ev, seg_guard);
            }
            continue;
        }

        int use_cache = 0;
        if (base_e && n_t0 <= cache_len) {
            for (int it = 0; it < n_tau; it++)
                if (taus_local[it] >= s1) { use_cache = 1; break; }
        }

        if (use_cache) {
            Walkers exw; walkers_init(&exw);
            for (int s = 0; s < S; s++) { ev[s].lo = ev[s].hi = 0; }
            for (long i = 0; i < n_t0; i++) {
                double lo = (double)i * h;
                double hi = lo + s1;
                exw.lo_sg = adv_sg(&ex, exw.lo_sg, lo);
                exw.hi_sg = adv_sg(&ex, exw.hi_sg, hi);
                base_e[i] = ev_at(&ex, exw.hi_sg, hi)
                          - ev_at(&ex, exw.lo_sg, lo);
                for (int s = 0; s < S; s++) {
                    const double *ph = phi2_all + phi2_off[s];
                    int n2 = (int)(phi2_off[s + 1] - phi2_off[s]);
                    ev[s].lo = adv_ptr(ph, n2, ev[s].lo, lo);
                    ev[s].hi = adv_ptr(ph, n2, ev[s].hi, hi);
                    base_n[(size_t)s * cache_len + i] =
                        (double)(ev[s].hi - ev[s].lo);
                }
            }
        }

        for (int it = 0; it < n_tau; it++) {
            double tau = taus_local[it];

            if (use_cache && tau >= s1) {
                double u2 = tau;
                double w2 = (tau + sig < T ? tau + sig : T) - tau;
                Walkers exw; walkers_init(&exw);
                for (int s = 0; s < S; s++) { ev2[s].lo = ev2[s].hi = 0; }
                for (long i = 0; i < n_t0; i++) {
                    double t0 = (double)i * h;
                    double lo = t0 + u2;
                    double hi = lo + w2;
                    exw.lo_sg = adv_sg(&ex, exw.lo_sg, lo);
                    exw.hi_sg = adv_sg(&ex, exw.hi_sg, hi);
                    /* associativity parity with scan_period: base + (X-Y) */
                    double e_in = base_e[i];
                    e_in += ev_at(&ex, exw.hi_sg, hi)
                          - ev_at(&ex, exw.lo_sg, lo);
                    for (int s = 0; s < S; s++) {
                        const double *ph = phi2_all + phi2_off[s];
                        int n2 = (int)(phi2_off[s + 1] - phi2_off[s]);
                        ev2[s].lo = adv_ptr(ph, n2, ev2[s].lo, lo);
                        ev2[s].hi = adv_ptr(ph, n2, ev2[s].hi, hi);
                        double n_in = base_n[(size_t)s * cache_len + i]
                            + (double)(ev2[s].hi - ev2[s].lo);
                        int ni = (int)(n_in + 0.5);
                        const double *es = e_star_all
                            + (size_t)s * estar_stride;
                        if (e_in >= es[ni]) continue;
                        double ll = two_bin(n_in, e_in, n_tot[s], e_tot,
                                            pooled[s]);
                        if (ll > best[s]) {
                            best[s] = ll;
                            out_arg[s * 4 + 0] = sig;
                            out_arg[s * 4 + 1] = tau;
                            out_arg[s * 4 + 2] = t0;
                            out_arg[s * 4 + 3] = ll;
                            improved_out[s] = 1;
                            build_table(e_star_all
                                        + (size_t)s * estar_stride,
                                        n_tot[s], e_tot, pooled[s],
                                        best[s]);
                            table_B[s] = best[s];
                        }
                    }
                }
                continue;
            }

            /* Uncached path: M2, overlapping M3, or malloc fallback. */
            double u[2], w[2];
            int n_iv;
            if (mode == 0) {
                n_iv = 1; u[0] = 0.0; w[0] = s1;
            } else if (tau < s1) {
                double v2 = tau + sig < T ? tau + sig : T;
                double top = v2 > s1 ? v2 : s1;
                n_iv = 1; u[0] = 0.0; w[0] = top;
            } else {
                n_iv = 2;
                u[0] = 0.0; w[0] = s1;
                u[1] = tau;
                w[1] = (tau + sig < T ? tau + sig : T) - tau;
            }
            Walkers exw[2];
            for (int j = 0; j < n_iv; j++) walkers_init(&exw[j]);
            for (int s = 0; s < S; s++)
                for (int j = 0; j < n_iv; j++)
                    ev[(size_t)j * S + s].lo = ev[(size_t)j * S + s].hi = 0;
            for (long i = 0; i < n_t0; i++) {
                double t0 = (double)i * h;
                double e_in = 0.0;
                double lo_j[2], hi_j[2];
                for (int j = 0; j < n_iv; j++) {
                    lo_j[j] = t0 + u[j];
                    hi_j[j] = lo_j[j] + w[j];
                    exw[j].lo_sg = adv_sg(&ex, exw[j].lo_sg, lo_j[j]);
                    exw[j].hi_sg = adv_sg(&ex, exw[j].hi_sg, hi_j[j]);
                    e_in += ev_at(&ex, exw[j].hi_sg, hi_j[j])
                          - ev_at(&ex, exw[j].lo_sg, lo_j[j]);
                }
                for (int s = 0; s < S; s++) {
                    const double *ph = phi2_all + phi2_off[s];
                    int n2 = (int)(phi2_off[s + 1] - phi2_off[s]);
                    double n_in = 0.0;
                    for (int j = 0; j < n_iv; j++) {
                        EvPtr *P = &ev[(size_t)j * S + s];
                        P->lo = adv_ptr(ph, n2, P->lo, lo_j[j]);
                        P->hi = adv_ptr(ph, n2, P->hi, hi_j[j]);
                        n_in += (double)(P->hi - P->lo);
                    }
                    int ni = (int)(n_in + 0.5);
                    const double *es = e_star_all + (size_t)s * estar_stride;
                    if (e_in >= es[ni]) continue;
                    double ll = two_bin(n_in, e_in, n_tot[s], e_tot,
                                        pooled[s]);
                    if (ll > best[s]) {
                        best[s] = ll;
                        out_arg[s * 4 + 0] = sig;
                        out_arg[s * 4 + 1] = tau;
                        out_arg[s * 4 + 2] = t0;
                        out_arg[s * 4 + 3] = ll;
                        improved_out[s] = 1;
                        build_table(e_star_all + (size_t)s * estar_stride,
                                    n_tot[s], e_tot, pooled[s], best[s]);
                        table_B[s] = best[s];
                    }
                }
            }
        }
    }
    free(base_e); free(base_n); free(ev); free(ev2);
    for (int s = 0; s < S; s++) n_improved += improved_out[s];
    return n_improved;
}

/* Scan all (sigma, tau, t0) cells of one period T.
 * mode: 0 = single window (M2), 1 = paired (M3).
 * Returns 1 if best improved; updates *best and out_arg[4] =
 * {sigma, tau (-1 if none), t0, ll}. e_star/table_B are caller-owned
 * persistent state (table_B must start below any possible ll). */
int scan_period(const double *phi2, int n2, const double *xs2,
                const double *es2, int m2, double T, int n_tot,
                double e_tot, double pooled, double sigma_min,
                const double *tau_grid, int n_tau_grid, double t0_frac,
                int mode, double *best, double *out_arg, double *e_star,
                double *table_B) {
    FoldTables ft = {phi2, n2, xs2, es2, m2};
    int improved = 0;

    /* One allocation per period, reused across all sigma values. Counts are
     * stored as doubles to reproduce the baseline accumulation exactly.
     * Allocation failure is harmless: the code falls back to the original
     * two-interval path. */
    long cache_len = 0;
    double *base_cache = NULL;
    if (mode == 1 && sigma_min > 0.0 && t0_frac > 0.0) {
        cache_len = (long)ceil(T / (t0_frac * sigma_min));
        if (cache_len > 0)
            base_cache = malloc(2 * (size_t)cache_len
                                * sizeof(*base_cache));
    }
    double *base_n = base_cache;
    double *base_e = base_cache ? base_cache + cache_len : NULL;

    if (*table_B < *best) {           /* sync table with incoming best */
        build_table(e_star, n_tot, e_tot, pooled, *best);
        *table_B = *best;
    }
    for (double sig = sigma_min; sig <= 0.5 * T; sig *= 2.0) {
        double h = t0_frac * sig;
        long n_t0 = (long)ceil(T / h);   /* np.arange length parity */
        int n_tau = 0;
        double taus_local[64];
        if (mode == 1) {
            for (int i = 0; i < n_tau_grid && n_tau < 64; i++)
                if (tau_grid[i] <= 0.5 * T) taus_local[n_tau++] = tau_grid[i];
            if (n_tau == 0) break;    /* reference: break sigma loop */
        } else {
            n_tau = 1;
            taus_local[0] = -1.0;
        }

        double s1 = sig < T ? sig : T;
        int use_cache = 0;
        if (base_cache && n_t0 <= cache_len) {
            for (int it = 0; it < n_tau; it++) {
                if (taus_local[it] >= s1) {
                    use_cache = 1;
                    break;
                }
            }
        }

        if (use_cache) {
            Walkers first;
            walkers_init(&first);
            for (long i = 0; i < n_t0; i++) {
                double lo = (double)i * h;
                double hi = lo + s1;
                first.lo_ev = adv_ev(&ft, first.lo_ev, lo);
                first.hi_ev = adv_ev(&ft, first.hi_ev, hi);
                base_n[i] = (double)(first.hi_ev - first.lo_ev);
                first.lo_sg = adv_sg(&ft, first.lo_sg, lo);
                first.hi_sg = adv_sg(&ft, first.hi_sg, hi);
                base_e[i] = ev_at(&ft, first.hi_sg, hi)
                          - ev_at(&ft, first.lo_sg, lo);
            }
        }

        for (int it = 0; it < n_tau; it++) {
            double tau = taus_local[it];

            if (use_cache && tau >= s1) {
                /* Non-overlapping M3 pair: reuse interval one and walk only
                 * the tau-shifted second interval. */
                double u2 = tau;
                double w2 = (tau + sig < T ? tau + sig : T) - tau;
                Walkers second;
                walkers_init(&second);
                for (long i = 0; i < n_t0; i++) {
                    double t0 = (double)i * h;
                    double lo = t0 + u2;
                    double hi = lo + w2;
                    double n_in = base_n[i];
                    double e_in = base_e[i];
                    second.lo_ev = adv_ev(&ft, second.lo_ev, lo);
                    second.hi_ev = adv_ev(&ft, second.hi_ev, hi);
                    n_in += (double)(second.hi_ev - second.lo_ev);
                    second.lo_sg = adv_sg(&ft, second.lo_sg, lo);
                    second.hi_sg = adv_sg(&ft, second.hi_sg, hi);
                    e_in += ev_at(&ft, second.hi_sg, hi)
                          - ev_at(&ft, second.lo_sg, lo);
                    int ni = (int)(n_in + 0.5);
                    if (e_in >= e_star[ni]) continue;
                    double ll = two_bin(n_in, e_in, n_tot, e_tot, pooled);
                    if (ll > *best) {
                        *best = ll;
                        out_arg[0] = sig;
                        out_arg[1] = tau;
                        out_arg[2] = t0;
                        out_arg[3] = ll;
                        improved = 1;
                        build_table(e_star, n_tot, e_tot, pooled, *best);
                        *table_B = *best;
                    }
                }
                continue;
            }

            /* Original path: M2, overlapping M3, or malloc fallback. */
            double u[2], w[2];
            int n_iv;
            if (mode == 0) {
                n_iv = 1; u[0] = 0.0; w[0] = s1;
            } else if (tau < s1) {    /* overlapping pair: merged */
                double v2 = tau + sig < T ? tau + sig : T;
                double top = v2 > s1 ? v2 : s1;
                n_iv = 1; u[0] = 0.0; w[0] = top;
            } else {
                n_iv = 2;
                u[0] = 0.0; w[0] = s1;
                u[1] = tau;
                w[1] = (tau + sig < T ? tau + sig : T) - tau;
            }
            Walkers wk[4];
            for (int i = 0; i < n_iv; i++) walkers_init(&wk[i]);
            for (long i = 0; i < n_t0; i++) {
                double t0 = (double)i * h;
                double n_in = 0.0, e_in = 0.0;
                for (int j = 0; j < n_iv; j++) {
                    double lo = t0 + u[j], hi = lo + w[j];
                    Walkers *W = &wk[j];
                    W->lo_ev = adv_ev(&ft, W->lo_ev, lo);
                    W->hi_ev = adv_ev(&ft, W->hi_ev, hi);
                    n_in += (double)(W->hi_ev - W->lo_ev);
                    W->lo_sg = adv_sg(&ft, W->lo_sg, lo);
                    W->hi_sg = adv_sg(&ft, W->hi_sg, hi);
                    e_in += ev_at(&ft, W->hi_sg, hi)
                          - ev_at(&ft, W->lo_sg, lo);
                }
                int ni = (int)(n_in + 0.5);
                if (e_in >= e_star[ni]) continue;    /* cannot beat B */
                double ll = two_bin(n_in, e_in, n_tot, e_tot, pooled);
                if (ll > *best) {
                    *best = ll;
                    out_arg[0] = sig;
                    out_arg[1] = tau;
                    out_arg[2] = t0;
                    out_arg[3] = ll;
                    improved = 1;
                    build_table(e_star, n_tot, e_tot, pooled, *best);
                    *table_B = *best;
                }
            }
        }
    }
    free(base_cache);
    return improved;
}
