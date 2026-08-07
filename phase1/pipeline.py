"""H1 scanner-model timing pipeline: M0-M5 likelihoods, grids, alias sets,
the Lambda statistic, and event-stream simulation.

Implements prereg_h1.md Sections 4-6. All models are piecewise-constant
inhomogeneous point processes except M4 (Weibull renewal, per-session
stationary-forward-recurrence treatment — see M4 docstring) and M5
(session-level gamma-mixed Poisson, analytically marginalized).

Likelihood convention: unordered-collection density,
  l = sum_k log lam(t_k) - int_W lam dt,
so M5's negative-binomial marginal carries the matching n_j!/w_j^{n_j} term.

Time axis: barycentric MJD (days). Rates are per day. Window functions are
lists of (start, end) good-time intervals; overlap handling is exact
(closed-form interval-vs-periodic-window integrals, no quadrature).
"""

import numpy as np
from scipy.optimize import minimize
from scipy.special import gammaln, gammaincc, gamma as gammafn

DAY_S = 86400.0


# ---------------------------------------------------------------- windows

def live_time(win):
    a, b = win
    return float(np.sum(b - a))


def periodic_overlap(win, T, t0, intervals):
    """Exact exposure of the window set within the union of phase intervals.

    intervals: list of (u, v) with 0 <= u < v <= T, non-overlapping, in the
    phase coordinate phi = (t - t0) mod T.
    F(x) = measure of {s in [0, x): (s mod T) in [u, v)} has the closed form
    floor(x/T)*(v-u) + clip(x mod T - u, 0, v-u); overlap of [a, b) is
    F(b - t0) - F(a - t0), summed over GTIs and intervals.
    """
    a, b = win
    total = 0.0
    for u, v in intervals:
        w = v - u

        def F(x):
            n, r = np.divmod(x, T)
            return n * w + np.clip(r - u, 0.0, w)

        total += float(np.sum(F(b - t0) - F(a - t0)))
    return total


def counts_in(t, T, t0, intervals):
    phi = np.mod(t - t0, T)
    m = np.zeros(len(t), dtype=bool)
    for u, v in intervals:
        m |= (phi >= u) & (phi < v)
    return int(np.sum(m)), m


# ------------------------------------------------------------- likelihoods

def _nlogn(n, e):
    """n*log(n/e) - n with the n=0 limit (=0) handled."""
    if n == 0:
        return 0.0
    return n * np.log(n / e) - n


def m0_ll(t, win):
    return _nlogn(len(t), live_time(win))


def two_bin_ll(n_in, n_out, e_in, e_out, require_in_ge_out=True):
    """Profile log-likelihood of a two-rate piecewise-constant model.
    If the rate ordering constraint is violated at the MLE, the constrained
    optimum is the pooled single-rate fit."""
    if e_in <= 0 or e_out <= 0:
        return _nlogn(n_in + n_out, e_in + e_out)
    lin, lout = n_in / e_in, n_out / e_out
    if require_in_ge_out and lin < lout:
        return _nlogn(n_in + n_out, e_in + e_out)
    return _nlogn(n_in, e_in) + _nlogn(n_out, e_out)


def periodic_two_bin_ll(t, win, T, t0, intervals):
    e_in = periodic_overlap(win, T, t0, intervals)
    e_tot = live_time(win)
    n_in, _ = counts_in(t, T, t0, intervals)
    return two_bin_ll(n_in, len(t) - n_in, e_in, e_tot - e_in)


def scan_phases(t, win, T, intervals_fn, t0_grid, tref):
    """Vectorized profile log-likelihood over a t0 grid for a fixed period T
    and a fixed phase-interval template (returned by intervals_fn(), a list
    of (u, v) within [0, T) applied at each shifted origin tref + t0).

    Exposure: closed-form F-differences broadcast over (sessions x t0).
    Counts: circular sliding-window counts via sorted event phases.
    Returns the ll array over t0_grid.
    """
    a, b = win
    e_tot = live_time(win)
    n_tot = len(t)
    phi_t = np.sort(np.mod(t - tref, T)) if n_tot else np.empty(0)
    e_in = np.zeros(len(t0_grid))
    n_in = np.zeros(len(t0_grid))
    for u, v in intervals_fn:
        w = v - u
        # exposure: sessions x t0 broadcast of F(b) - F(a)
        for aj, bj in zip(a, b):
            xb = bj - tref - t0_grid - u
            xa = aj - tref - t0_grid - u
            nb, rb = np.divmod(xb, T)
            na, ra = np.divmod(xa, T)
            e_in += (nb - na) * w + np.clip(rb, 0, w) - np.clip(ra, 0, w)
        # counts: events with (phi - t0 - u) mod T in [0, w)
        if n_tot:
            lo = np.mod(t0_grid + u, T)
            hi = lo + w
            c = (np.searchsorted(phi_t, np.minimum(hi, T))
                 - np.searchsorted(phi_t, lo))
            wrap = np.maximum(hi - T, 0.0)
            c = c + np.searchsorted(phi_t, wrap)
            n_in += c
    n_out = n_tot - n_in
    e_out = e_tot - e_in
    with np.errstate(divide="ignore", invalid="ignore"):
        ll_in = np.where(n_in > 0, n_in * np.log(
            np.where(n_in > 0, n_in, 1) / np.maximum(e_in, 1e-12)) - n_in, 0.0)
        ll_out = np.where(n_out > 0, n_out * np.log(
            np.where(n_out > 0, n_out, 1) / np.maximum(e_out, 1e-12))
            - n_out, 0.0)
    ll = ll_in + ll_out
    # rate-ordering constraint: pooled fit where lam_in < lam_out
    lam_in = n_in / np.maximum(e_in, 1e-12)
    lam_out = n_out / np.maximum(e_out, 1e-12)
    pooled = _nlogn(n_tot, e_tot)
    ll = np.where(lam_in < lam_out, pooled, ll)
    ll = np.where(e_in <= 0, pooled, ll)
    return ll


def m1_scan(t, win, span, p_floor, n_periods=200, deltas=(0.05, 0.1, 0.2,
            0.35, 0.5, 0.65, 0.8, 0.95), n_phase=24):
    """Activity-window repeater: max ll over (P_a, delta, t0)."""
    p_max = span / 3.0
    if p_max <= p_floor:
        return m0_ll(t, win), None
    periods = np.geomspace(p_floor, p_max, n_periods)
    best, arg = -np.inf, None
    tref = float(win[0][0])
    for P in periods:
        for d in deltas:
            t0s = np.arange(0.0, P, P / n_phase)
            ll = scan_phases(t, win, P, [(0.0, d * P)], t0s, tref)
            i = int(np.argmax(ll))
            if ll[i] > best:
                best, arg = float(ll[i]), (P, d, t0s[i] / P)
    return best, arg


def scanner_intervals(T, sigma, tau=None):
    """Phase intervals of the visit set: one boxcar (M2) or a pair (M3).
    Returns non-overlapping intervals within [0, T)."""
    iv = [(0.0, min(sigma, T))]
    if tau is not None:
        u2, v2 = tau, min(tau + sigma, T)
        if u2 < iv[0][1]:               # overlapping pair: merge (superposed
            iv = [(0.0, max(v2, iv[0][1]))]  # rates -> union at profile MLE)
        else:
            iv.append((u2, v2))
    return iv


def scanner_grids(span, p_min, sigma_min, sigma_factor=2.0, f_oversample=2.0):
    """Frozen grid rule (prereg_h1 Section 5): octave-wise uniform frequency
    grid with df = sigma_min / (f_oversample * T_oct_max * span)."""
    p_max = span / 3.0
    grids = []
    t_lo = p_min
    while t_lo < p_max:
        t_hi = min(2.0 * t_lo, p_max)
        df = sigma_min / (f_oversample * t_hi * span)
        f = np.arange(1.0 / t_hi, 1.0 / t_lo, df)
        if len(f):
            grids.append(1.0 / f)
        t_lo = t_hi
    return grids


def _scan_periods(args):
    """Worker: scan one chunk of periods. Top-level for pickling."""
    (t, a, b, periods, sigma_min, paired, tau_grid, t0_step_frac,
     tref) = args
    win = (a, b)
    best, arg = -np.inf, None
    for T in periods:
        sig = sigma_min
        while sig <= 0.5 * T:
            taus = [None]
            if paired:
                taus = [x for x in tau_grid if x <= T / 2.0]
                if not taus:
                    break
            for tau in taus:
                iv = scanner_intervals(T, sig, tau)
                t0s = np.arange(0.0, T, t0_step_frac * sig)
                ll = scan_phases(t, win, T, iv, t0s, tref)
                i = int(np.argmax(ll))
                if ll[i] > best:
                    best, arg = float(ll[i]), (T, sig, tau, t0s[i])
            sig *= 2.0
    return best, arg


def scan_scanner(t, win, span, p_min, sigma_min, paired=False,
                 tau_grid=None, t0_step_frac=0.5, processes=1):
    """M2 (paired=False) / M3 (paired=True) grid scan. Returns (ll, argmax).
    t0 grid: step = t0_step_frac * sigma over [0, T).
    processes > 1 splits the period list across a process pool (used by the
    full-scale confirmatory scans; per-simulation parallelism in the
    acceptance harness keeps this at 1 there)."""
    tref = float(win[0][0])
    periods = np.concatenate(
        scanner_grids(span, p_min, sigma_min) or [np.empty(0)])
    if len(periods) == 0:
        return m0_ll(t, win), None
    chunks = np.array_split(periods, max(1, min(processes * 4,
                                                len(periods))))
    jobs = [(t, win[0], win[1], c, sigma_min, paired, tau_grid,
             t0_step_frac, tref) for c in chunks if len(c)]
    if processes > 1:
        from concurrent.futures import ProcessPoolExecutor
        with ProcessPoolExecutor(max_workers=processes) as ex:
            results = list(ex.map(_scan_periods, jobs))
    else:
        results = [_scan_periods(j) for j in jobs]
    best, arg = -np.inf, None
    for ll, a in results:
        if ll > best:
            best, arg = ll, a
    return best, arg


def m4_ll(t, win, k, r):
    """Weibull renewal (shape k, rate r), per-session treatment with
    stationary forward recurrence at each session start (pre-freeze spec
    refinement of the Oppermann, Yu & Pen 2018 approach: sessions are
    treated as independent draws from the stationary renewal process;
    hidden-event correlation across the gaps between sessions is dropped).
    lamt = r * Gamma(1 + 1/k); S(d) = exp(-(d*lamt)^k);
    f(d) = (k/d) * (d*lamt)^k * S(d);
    forward-recurrence density f_fr(d) = r * S(d);
    S_fr(d) = (r/(k*lamt)) * Gamma_upper(1/k, (d*lamt)^k).
    """
    lamt = r * gammafn(1.0 + 1.0 / k)

    def logS(d):
        return -np.power(d * lamt, k)

    def logf(d):
        return np.log(k / d) + k * np.log(d * lamt) + logS(d)

    def S_fr(d):
        return (r / (k * lamt)) * gammaincc(1.0 / k, np.power(d * lamt, k)) \
            * gammafn(1.0 / k)

    a, b = win
    ll = 0.0
    for aj, bj in zip(a, b):
        tj = t[(t >= aj) & (t < bj)]
        if len(tj) == 0:
            ll += np.log(max(S_fr(bj - aj), 1e-300))
            continue
        tj = np.sort(tj)
        ll += np.log(r) + logS(max(tj[0] - aj, 1e-9))          # fwd recurrence
        if len(tj) > 1:
            d = np.maximum(np.diff(tj), 1e-9)
            ll += float(np.sum(logf(d)))
        ll += logS(max(bj - tj[-1], 1e-9))       # quiet to session end
    return ll


def m4_fit(t, win):
    n = len(t)
    if n < 2:
        return m0_ll(t, win)
    r0 = n / live_time(win)
    best = -np.inf
    for k0 in (0.3, 0.7, 1.0):
        for rm in (0.5, 1.0, 2.0):
            res = minimize(
                lambda p: -m4_ll(t, win, np.clip(p[0], 0.05, 5.0),
                                 max(p[1], 1e-8)),
                x0=[k0, r0 * rm], method="Nelder-Mead",
                options={"maxiter": 300, "fatol": 1e-6})
            best = max(best, -res.fun)
    return best


def m5_ll(t, win, alpha, beta):
    a, b = win
    ll = 0.0
    for aj, bj in zip(a, b):
        w = bj - aj
        nj = int(np.sum((t >= aj) & (t < bj)))
        mu = alpha * beta * w
        p = beta * w / (1.0 + beta * w)
        ll += (gammaln(nj + alpha) - gammaln(alpha) - gammaln(nj + 1)
               + alpha * np.log(1 - p) + nj * np.log(max(p, 1e-300)))
        ll += gammaln(nj + 1) - nj * np.log(w)   # collection-density terms
    return ll


def m5_fit(t, win):
    n = len(t)
    rate = n / live_time(win)
    best = -np.inf
    for a0 in (0.3, 1.0, 3.0):
        res = minimize(
            lambda p: -m5_ll(t, win, max(p[0], 1e-4), max(p[1], 1e-10)),
            x0=[a0, rate / a0], method="Nelder-Mead",
            options={"maxiter": 400, "fatol": 1e-6})
        best = max(best, -res.fun)
    return best


# --------------------------------------------------------------- statistic

def lambda_stat(t, win, p_min, sigma_min, tau_grid, m1_kw=None, processes=1):
    """The frozen primary statistic (prereg_h1 Section 6.1) for one
    source-campaign. Returns (Lambda, details)."""
    t = np.sort(np.asarray(t, float))
    span = float(win[1][-1] - win[0][0])
    ll0 = m0_ll(t, win)
    ll1, arg1 = m1_scan(t, win, span, p_min, **(m1_kw or {}))
    ll4 = m4_fit(t, win)
    ll5 = m5_fit(t, win)
    ll2, arg2 = scan_scanner(t, win, span, p_min, sigma_min, paired=False,
                             processes=processes)
    ll3, arg3 = scan_scanner(t, win, span, p_min, sigma_min, paired=True,
                             tau_grid=tau_grid, processes=processes)
    nat = max(ll0, ll1, ll4, ll5)
    lam = 2.0 * (max(ll2, ll3) - nat)
    return lam, {"ll": (ll0, ll1, ll2, ll3, ll4, ll5),
                 "m1": arg1, "m2": arg2, "m3": arg3}


# ------------------------------------------------------------- alias sets

F_SIDEREAL = 1.0 / 0.99726957   # per day
F_SOLAR = 1.0

def alias_frequencies():
    out = []
    for fd in (F_SIDEREAL, F_SOLAR):
        for n in (1, 2):
            for p in (1, 2, 3):
                for q in (1, 2, 3):
                    out.append(n * (p / q) * fd)
    return np.unique(np.round(out, 9))


def spectral_window(win, f):
    """|W~(f)|^2 normalized to 1 at f=0."""
    a, b = win
    num = np.zeros(len(f), dtype=complex)
    for aj, bj in zip(a, b):
        w = 2j * np.pi * f
        num += (np.exp(w * bj) - np.exp(w * aj)) / np.where(f == 0, 1, w)
    tot = live_time(win)
    return np.abs(num / tot) ** 2


def alias_flag(f_candidate, win, span, window_peak_thresh=0.2):
    """Frozen alias rule (prereg_h1 Section 5.4): within 2/span of any
    day-rational frequency, or of a spectral-window peak above threshold."""
    tol = 2.0 / span
    for fa in alias_frequencies():
        if abs(f_candidate - fa) < tol:
            return True
    fgrid = np.arange(tol, max(3.0, f_candidate * 1.5), tol / 4.0)
    p = spectral_window(win, fgrid)
    peaks = fgrid[p > window_peak_thresh]
    return bool(np.any(np.abs(peaks - f_candidate) < tol))


# ------------------------------------------------------------- simulation

def sim_m0(rng, win, lam):
    a, b = win
    out = []
    for aj, bj in zip(a, b):
        n = rng.poisson(lam * (bj - aj))
        out.append(rng.uniform(aj, bj, n))
    return np.sort(np.concatenate(out))


def sim_periodic(rng, win, T, t0, intervals, lam_in, lam_out):
    """M1/M2/M3 simulation: two-rate piecewise process."""
    a, b = win
    out = []
    for aj, bj in zip(a, b):
        n = rng.poisson(max(lam_in, lam_out) * (bj - aj))
        cand = rng.uniform(aj, bj, n)
        _, m = counts_in(cand, T, t0, intervals)
        rate = np.where(m, lam_in, lam_out)
        keep = rng.uniform(0, max(lam_in, lam_out), n) < rate
        out.append(cand[keep])
    return np.sort(np.concatenate(out))


def sim_m4(rng, win, k, r, pad=50.0):
    lamt = r * gammafn(1.0 + 1.0 / k)
    t0, t1 = win[0][0] - pad, win[1][-1]
    t, cur = [], t0
    while cur < t1:
        cur += rng.weibull(k) / lamt
        t.append(cur)
    t = np.asarray(t)
    m = np.zeros(len(t), dtype=bool)
    for aj, bj in zip(*win):
        m |= (t >= aj) & (t < bj)
    return t[m]


def sim_m5(rng, win, alpha, beta):
    a, b = win
    out = []
    for aj, bj in zip(a, b):
        lam_j = rng.gamma(alpha, beta)
        n = rng.poisson(lam_j * (bj - aj))
        out.append(rng.uniform(aj, bj, n))
    return np.sort(np.concatenate(out))
