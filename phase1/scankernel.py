"""ctypes wrapper for the exact cache-optimized C scan kernel.

Provides scan_scanner_c / lambda_stat_c, drop-in equivalents of
fastscan.scan_scanner_fast / lambda_stat_fast (same frozen search, same
argmax semantics; validated by scripts/validate_fastscan.py). The C kernel
reuses M3's common first interval across non-overlapping tau values without
changing scan order or likelihood arithmetic.

Build once with scripts/build_scankernel.sh (cc -O2 -shared). The .c
source SHA-256 is recorded in acceptance artifacts; the dylib is a build
product and is gitignored.
"""

import ctypes
import os
import sys
from pathlib import Path

import numpy as np

import pipeline as pl
from fastscan import fold_exposure

_HERE = Path(__file__).resolve().parent
_SUFFIX = ".dylib" if sys.platform == "darwin" else ".so"
_LIB = None


def _lib():
    global _LIB
    if _LIB is None:
        path = _HERE / f"_scankernel{_SUFFIX}"
        if not path.exists():
            raise RuntimeError(
                "scan kernel not built: run scripts/build_scankernel.sh")
        lib = ctypes.CDLL(str(path))
        d = ctypes.POINTER(ctypes.c_double)
        i = ctypes.POINTER(ctypes.c_int)
        ll = ctypes.POINTER(ctypes.c_longlong)
        lib.scan_period.restype = ctypes.c_int
        lib.scan_period.argtypes = [
            d, ctypes.c_int, d, d, ctypes.c_int, ctypes.c_double,
            ctypes.c_int, ctypes.c_double, ctypes.c_double,
            ctypes.c_double, d, ctypes.c_int, ctypes.c_double,
            ctypes.c_int, d, d, d, d]
        lib.scan_period_multi.restype = ctypes.c_int
        lib.scan_period_multi.argtypes = [
            d, ll, ctypes.c_int, d, d, ctypes.c_int, ctypes.c_double,
            i, ctypes.c_double, d, ctypes.c_double, d, ctypes.c_int,
            ctypes.c_double, ctypes.c_int, d, d, d, ctypes.c_longlong,
            d, i]
        lib.scankernel_set_seg_mode.restype = None
        lib.scankernel_set_seg_mode.argtypes = [ctypes.c_int]
        lib.scankernel_set_seg_mode(
            int(os.environ.get("BBS_SEG_MODE", "0")))
        _LIB = lib
    return _LIB


def set_seg_mode(mode):
    """Segmented-sweep knob for the batched kernel: 0 auto (default),
    1 force on, -1 force off. Pure performance choice -- every setting
    is validated bit-identical (validate_fastscan.py section [7])."""
    _lib().scankernel_set_seg_mode(int(mode))


def _cptr(a):
    return a.ctypes.data_as(ctypes.POINTER(ctypes.c_double))


def scan_scanner_c(t, win, span, p_min, sigma_min, paired=False,
                   tau_grid=None, t0_step_frac=0.5):
    """C equivalent of fastscan.scan_scanner_fast; returns
    (best_ll, best_arg, n_periods)."""
    lib = _lib()
    a, b = win
    tref = float(a[0])
    e_tot = pl.live_time(win)
    n_tot = len(t)
    pooled = pl._nlogn(n_tot, e_tot)
    periods = np.concatenate(
        pl.scanner_grids(span, p_min, sigma_min) or [np.empty(0)])
    if len(periods) == 0 or n_tot == 0:
        from fastscan import scan_scanner_fast
        return scan_scanner_fast(t, win, span, p_min, sigma_min,
                                 paired=paired, tau_grid=tau_grid,
                                 t0_step_frac=t0_step_frac)
    taus = np.ascontiguousarray(tau_grid if paired else [0.0], dtype=float)
    best = ctypes.c_double(-np.inf)
    table_b = ctypes.c_double(-np.inf)
    out = np.zeros(4)
    e_star = np.full(n_tot + 2, np.inf)   # permissive until first build
    arg = None
    t = np.asarray(t, float)
    for T in periods:
        T = float(T)
        phi = np.sort(np.mod(t - tref, T))
        phi2 = np.ascontiguousarray(np.concatenate([phi, phi + T]))
        xs, Es = fold_exposure(win, T, tref)
        xs2 = np.ascontiguousarray(np.concatenate([xs, xs[1:] + T]))
        es2 = np.ascontiguousarray(np.concatenate([Es, Es[1:] + Es[-1]]))
        improved = lib.scan_period(
            _cptr(phi2), len(phi2), _cptr(xs2), _cptr(es2), len(xs2),
            T, n_tot, e_tot, pooled, sigma_min, _cptr(taus), len(taus),
            t0_step_frac, 1 if paired else 0, ctypes.byref(best),
            _cptr(out), _cptr(e_star), ctypes.byref(table_b))
        if improved:
            tau = None if out[1] < 0 else float(out[1])
            arg = (T, float(out[0]), tau, float(out[2]))
    return float(best.value), arg, len(periods)


def scan_scanner_batch(ts, win, span, p_min, sigma_min, paired=False,
                       tau_grid=None, t0_step_frac=0.5):
    """Batched exact scan over S event streams sharing one window function
    (the Section 6.2 simulation workload: same campaign windows, different
    simulated streams). Returns a list of (best_ll, best_arg, n_periods),
    one per stream, bit-identical to scan_scanner_c on each stream: the
    kernel shares only the stream-independent exposure work, and each
    stream keeps its own pruning state and first-in-scan-order argmax
    (validated by scripts/validate_fastscan.py section [6]).

    Streams with zero events take the same per-stream fallback path as
    scan_scanner_c, preserving exact output parity."""
    lib = _lib()
    a, b = win
    tref = float(a[0])
    e_tot = pl.live_time(win)
    periods = np.concatenate(
        pl.scanner_grids(span, p_min, sigma_min) or [np.empty(0)])
    ts = [np.asarray(t, float) for t in ts]
    S_all = len(ts)
    results = [None] * S_all
    live = [s for s in range(S_all) if len(ts[s]) > 0]
    if len(periods) == 0 or not live:
        return [scan_scanner_c(t, win, span, p_min, sigma_min,
                               paired=paired, tau_grid=tau_grid,
                               t0_step_frac=t0_step_frac) for t in ts]
    for s in range(S_all):
        if len(ts[s]) == 0:            # scan_scanner_c's n_tot==0 fallback
            results[s] = scan_scanner_c(
                ts[s], win, span, p_min, sigma_min, paired=paired,
                tau_grid=tau_grid, t0_step_frac=t0_step_frac)

    S = len(live)
    n_tot = np.array([len(ts[s]) for s in live], dtype=np.int32)
    pooled = np.array([pl._nlogn(int(n), e_tot) for n in n_tot])
    taus = np.ascontiguousarray(tau_grid if paired else [0.0], dtype=float)
    best = np.full(S, -np.inf)
    table_b = np.full(S, -np.inf)
    out = np.zeros((S, 4))
    improved = np.zeros(S, dtype=np.int32)
    estar_stride = int(n_tot.max()) + 2
    e_star = np.full((S, estar_stride), np.inf)
    args = [None] * S
    ipt = ctypes.POINTER(ctypes.c_int)
    for T in periods:
        T = float(T)
        xs, Es = fold_exposure(win, T, tref)
        xs2 = np.ascontiguousarray(np.concatenate([xs, xs[1:] + T]))
        es2 = np.ascontiguousarray(np.concatenate([Es, Es[1:] + Es[-1]]))
        phi2s = []
        for s in live:
            phi = np.sort(np.mod(ts[s] - tref, T))
            phi2s.append(np.concatenate([phi, phi + T]))
        off = np.zeros(S + 1, dtype=np.int64)
        np.cumsum([len(p) for p in phi2s], out=off[1:])
        flat = np.ascontiguousarray(np.concatenate(phi2s))
        rc = lib.scan_period_multi(
            _cptr(flat), off.ctypes.data_as(
                ctypes.POINTER(ctypes.c_longlong)), S,
            _cptr(xs2), _cptr(es2), len(xs2), T,
            n_tot.ctypes.data_as(ipt), e_tot, _cptr(pooled),
            sigma_min, _cptr(taus), len(taus), t0_step_frac,
            1 if paired else 0, _cptr(best), _cptr(out.reshape(-1)),
            _cptr(e_star.reshape(-1)), estar_stride, _cptr(table_b),
            improved.ctypes.data_as(ipt))
        if rc < 0:
            raise MemoryError("scan_period_multi allocation failure")
        for k in range(S):
            if improved[k]:
                tau = None if out[k, 1] < 0 else float(out[k, 1])
                args[k] = (T, float(out[k, 0]), tau, float(out[k, 2]))
    for k, s in enumerate(live):
        results[s] = (float(best[k]), args[k], len(periods))
    return results


def events_in_windows(t, win, tol=1e-9):
    """Prereg 4.1 invariant: every event lies inside a good-time interval.
    Implementations may differ (fp-accidentally, via the e_in <= 0 branch)
    only at grid cells where events sit in zero-exposure phase regions --
    configurations the frozen model excludes. Asserted before every
    production Lambda evaluation."""
    a, b = win
    t = np.asarray(t, float)
    i = np.clip(np.searchsorted(a, t, side="right") - 1, 0, len(a) - 1)
    return bool(np.all((t >= a[i] - tol) & (t <= b[i] + tol)))


def lambda_stat_c(t, win, p_min, sigma_min, tau_grid, m1_kw=None):
    """C equivalent of pipeline.lambda_stat (exact Lambda and argmaxes)."""
    t = np.sort(np.asarray(t, float))
    assert events_in_windows(t, win), \
        "events outside W(t): input violates prereg 4.1"
    span = float(win[1][-1] - win[0][0])
    ll0 = pl.m0_ll(t, win)
    ll1, arg1 = pl.m1_scan(t, win, span, p_min, **(m1_kw or {}))
    ll4 = pl.m4_fit(t, win)
    ll5 = pl.m5_fit(t, win)
    ll2, arg2, _ = scan_scanner_c(t, win, span, p_min, sigma_min,
                                  paired=False)
    ll3, arg3, _ = scan_scanner_c(t, win, span, p_min, sigma_min,
                                  paired=True, tau_grid=tau_grid)
    nat = max(ll0, ll1, ll4, ll5)
    lam = 2.0 * (max(ll2, ll3) - nat)
    return lam, {"ll": (ll0, ll1, ll2, ll3, ll4, ll5),
                 "m1": arg1, "m2": arg2, "m3": arg3}
