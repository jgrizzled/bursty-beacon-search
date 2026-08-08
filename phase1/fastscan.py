"""Fast exact reimplementation of the M2/M3 scanner-grid scans.

Same frozen search as pipeline.scan_scanner (identical grids, likelihood,
t0 steps, scan order) restructured for speed:

- Per period T, the window function is folded once into an exact
  piecewise-linear cumulative phase-exposure function E(x) (full session
  cycles contribute a linear term; residual arcs contribute breakpoints),
  so per-(T, sigma) exposure is two np.interp calls instead of a
  sessions x t0 broadcast. Event counts use one sorted fold per T.
- M2 and M3 are evaluated densely (exact, every grid point, identical
  scan order and argmax convention).

No cell pruning is performed. A corner-style upper bound
(max sliding count, min window exposure) was prototyped and found
UNSOUND-in-practice to repair cheaply: on sparse windows the minimum
window exposure is 0 (the two-bin code maps e_in <= 0 to the pooled
floor, while real cells have tiny positive exposure and arbitrarily
large ll), and the epsilon-clamped corner is far too loose to prune
anything. A sound and effective bound needs the joint (n, e) Pareto
frontier per (T, sigma) cell; see the freeze notes before building one.

Equivalence with the reference implementation is asserted by
scripts/validate_fastscan.py before any use (frozen with the artifacts).
"""

import numpy as np

import pipeline as pl


def fold_exposure(win, T, tref):
    """Exact cumulative phase exposure: returns (xs, Es) with
    E(x) = np.interp(x, xs, Es) = measure{s in W: (s - tref) mod T < x}
    for x in [0, T]."""
    a, b = win
    d = b - a
    k = np.floor(d / T)
    K = float(np.sum(k))               # full-cycle linear slope
    p = np.mod(a - tref, T)
    r = d - k * T                      # residual arc lengths (< T)
    q = p + r
    # slope-change events from residual arcs (wrap at T)
    pts, dl = [0.0, T], [0.0, 0.0]
    for pj, qj in zip(p, q):
        if qj <= T:
            pts += [pj, qj]
            dl += [1.0, -1.0]
        else:                          # wraps: [pj, T) and [0, qj - T)
            pts += [pj, 0.0, qj - T]
            dl += [1.0, 1.0, -1.0]
    pts = np.asarray(pts)
    dl = np.asarray(dl)
    order = np.argsort(pts, kind="stable")
    xs = pts[order]
    slope = K + np.cumsum(dl[order])
    Es = np.concatenate([[0.0], np.cumsum(slope[:-1] * np.diff(xs))])
    # collapse duplicate xs (keep last cumulative value per x)
    keep = np.concatenate([xs[1:] != xs[:-1], [True]])
    return xs[keep], Es[keep]


def _interval_stats(lo, w, T, xs, Es, phi):
    """Exposure and event count of the window [lo, lo+w) on the phase
    circle, vectorized over lo (values in [0, T))."""
    hi = lo + w
    e = np.interp(np.minimum(hi, T), xs, Es) - np.interp(lo, xs, Es)
    n = (np.searchsorted(phi, np.minimum(hi, T))
         - np.searchsorted(phi, lo))
    wrap = hi > T
    if np.any(wrap):
        hw = hi[wrap] - T
        e[wrap] += np.interp(hw, xs, Es)
        n[wrap] = n[wrap] + np.searchsorted(phi, hw)
    return e, n


def _two_bin_vec(n_in, e_in, n_tot, e_tot, pooled):
    """Vectorized two-bin profile ll with rate-ordering constraint --
    formula identical to pipeline.scan_phases."""
    n_out = n_tot - n_in
    e_out = e_tot - e_in
    with np.errstate(divide="ignore", invalid="ignore"):
        ll_in = np.where(n_in > 0, n_in * np.log(
            np.where(n_in > 0, n_in, 1) / np.maximum(e_in, 1e-12)) - n_in,
            0.0)
        ll_out = np.where(n_out > 0, n_out * np.log(
            np.where(n_out > 0, n_out, 1) / np.maximum(e_out, 1e-12))
            - n_out, 0.0)
    ll = ll_in + ll_out
    lam_in = n_in / np.maximum(e_in, 1e-12)
    lam_out = n_out / np.maximum(e_out, 1e-12)
    ll = np.where(lam_in < lam_out, pooled, ll)
    ll = np.where(e_in <= 0, pooled, ll)
    return ll


def scan_scanner_fast(t, win, span, p_min, sigma_min, paired=False,
                      tau_grid=None, t0_step_frac=0.5):
    """Fast exact equivalent of pipeline.scan_scanner: same grids, same
    likelihood, same first-in-scan-order argmax. Returns (best_ll,
    best_arg, n_cells)."""
    a, b = win
    tref = float(a[0])
    e_tot = pl.live_time(win)
    n_tot = len(t)
    pooled = pl._nlogn(n_tot, e_tot)
    periods = np.concatenate(
        pl.scanner_grids(span, p_min, sigma_min) or [np.empty(0)])
    if len(periods) == 0:
        return pl.m0_ll(t, win), None, 0
    best, arg = -np.inf, None
    n_cells = 0
    for T in periods:
        xs, Es = fold_exposure(win, T, tref)
        phi = np.sort(np.mod(t - tref, T)) if n_tot else np.empty(0)
        sig = sigma_min
        while sig <= 0.5 * T:
            t0s = np.arange(0.0, T, t0_step_frac * sig)
            if not paired:
                n_cells += 1
                e_in, n_in = _interval_stats(t0s, min(sig, T), T, xs, Es,
                                             phi)
                ll = _two_bin_vec(n_in, e_in, n_tot, e_tot, pooled)
                i = int(np.argmax(ll))
                if ll[i] > best:
                    best, arg = float(ll[i]), (T, sig, None, t0s[i])
            else:
                taus = [x for x in tau_grid if x <= T / 2.0]
                if not taus:
                    break
                n_cells += len(taus)
                for tau in taus:
                    iv = pl.scanner_intervals(T, sig, tau)
                    e_in = np.zeros(len(t0s))
                    n_in = np.zeros(len(t0s))
                    for u, v in iv:
                        lo = np.mod(t0s + u, T)
                        e, n = _interval_stats(lo, v - u, T, xs, Es, phi)
                        e_in += e
                        n_in += n
                    ll = _two_bin_vec(n_in, e_in, n_tot, e_tot, pooled)
                    i = int(np.argmax(ll))
                    if ll[i] > best:
                        best, arg = float(ll[i]), (T, sig, tau, t0s[i])
            sig *= 2.0
    return best, arg, n_cells


def lambda_stat_fast(t, win, p_min, sigma_min, tau_grid, m1_kw=None):
    """Fast exact equivalent of pipeline.lambda_stat."""
    t = np.sort(np.asarray(t, float))
    span = float(win[1][-1] - win[0][0])
    ll0 = pl.m0_ll(t, win)
    ll1, arg1 = pl.m1_scan(t, win, span, p_min, **(m1_kw or {}))
    ll4 = pl.m4_fit(t, win)
    ll5 = pl.m5_fit(t, win)
    ll2, arg2, _ = scan_scanner_fast(t, win, span, p_min, sigma_min,
                                     paired=False)
    ll3, arg3, _ = scan_scanner_fast(t, win, span, p_min, sigma_min,
                                     paired=True, tau_grid=tau_grid)
    nat = max(ll0, ll1, ll4, ll5)
    lam = 2.0 * (max(ll2, ll3) - nat)
    return lam, {"ll": (ll0, ll1, ll2, ll3, ll4, ll5),
                 "m1": arg1, "m2": arg2, "m3": arg3}
