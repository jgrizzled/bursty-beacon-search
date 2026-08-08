"""ctypes wrapper for the exact C scan kernel (_scankernel.c).

Provides scan_scanner_c / lambda_stat_c, drop-in equivalents of
fastscan.scan_scanner_fast / lambda_stat_fast (same frozen search, same
argmax semantics; validated by scripts/validate_fastscan.py --kernel).

Build once with scripts/build_scankernel.sh (cc -O2 -shared). The .c
source SHA-256 is recorded in acceptance artifacts; the dylib is a build
product and is gitignored.
"""

import ctypes
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
        lib.scan_period.restype = ctypes.c_int
        lib.scan_period.argtypes = [
            d, ctypes.c_int, d, d, ctypes.c_int, ctypes.c_double,
            ctypes.c_int, ctypes.c_double, ctypes.c_double,
            ctypes.c_double, d, ctypes.c_int, ctypes.c_double,
            ctypes.c_int, d, d, d, d]
        _LIB = lib
    return _LIB


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
