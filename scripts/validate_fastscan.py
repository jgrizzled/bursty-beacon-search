#!/usr/bin/env python3
"""Equivalence validation for phase1/fastscan.py against the reference
implementation (pipeline.scan_scanner / lambda_stat).

Checks, on randomized windows and event streams plus the real sepoct
window at smoke scale:

1. exposure/count primitives: fold_exposure + _interval_stats reproduce
   periodic_overlap / counts_in exactly (1e-9 abs) on random templates;
2. M2: identical (ll, argmax) to scan_scanner(paired=False);
3. M3: identical (ll, argmax) to scan_scanner(paired=True);
4. lambda_stat_fast reproduces lambda_stat's Lambda on simulated streams.

Exits nonzero on any mismatch. Run before any use of the fast path; the
output is recorded with the acceptance artifacts.
"""

import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "phase1"))
import acceptance as ac  # noqa: E402
import fastscan as fs  # noqa: E402
import pipeline as pl  # noqa: E402

FAIL = 0


def check(name, ok, detail=""):
    global FAIL
    print(f"  {'PASS' if ok else 'FAIL'}  {name} {detail}")
    if not ok:
        FAIL += 1


def rand_window(rng, n_sessions, span):
    starts = np.sort(rng.uniform(0, span, n_sessions))
    durs = rng.uniform(0.01, 0.35, n_sessions)
    a, b = [], []
    end = -1.0
    for s, d in zip(starts, durs):
        s = max(s, end + 1e-3)
        a.append(s)
        b.append(s + d)
        end = s + d
    return np.array(a), np.array(b)


def rand_events(rng, win, n):
    """Events uniform over the LIVE time (inside sessions), matching the
    physical invariant of prereg 4.1 ("events outside W impossible by
    construction"). Streams scattered into exposure gaps can reach
    degenerate zero-exposure/nonzero-count grid cells whose value under
    the reference implementation is a floating-point accident (session-sum
    residue vs. exact zero decides between a clamped log explosion and the
    pooled floor); such inputs are outside the frozen model and outside
    this validation's scope."""
    a, b = win
    w = b - a
    j = rng.choice(len(a), size=n, p=w / w.sum())
    return np.sort(rng.uniform(a[j], b[j]))



def args_equiv(ll_ref, arg_ref, arg_new, t, win, tref):
    """Argmax tuples match, or the new tuple is a degenerate tie: the
    reference likelihood at the new tuple equals the reference maximum
    (fp-level differences between implementations may reorder exact
    ties among degenerate cells; the maximum itself must agree)."""
    if arg_ref is None and arg_new is None:
        return True
    if arg_ref is None or arg_new is None:
        return False
    if all(x is None and y is None or
           (x is not None and y is not None and abs(x - y) < 1e-9)
           for x, y in zip(arg_ref, arg_new)):
        return True
    T, sig, tau, t0 = arg_new
    iv = pl.scanner_intervals(T, sig, tau)
    val = pl.scan_phases(t, win, T, iv, np.array([t0]), tref)[0]
    return abs(val - ll_ref) < 1e-6


def main():
    rng = np.random.default_rng(20260807)

    print("[1] primitive equivalence (exposure + counts)")
    for trial in range(60):
        win = rand_window(rng, rng.integers(3, 25), rng.uniform(5, 60))
        span = float(win[1][-1] - win[0][0])
        t = rand_events(rng, win, int(rng.integers(0, 400)))
        T = float(rng.uniform(0.05, span / 3))
        tref = float(win[0][0])
        sig = float(rng.uniform(0.001, 0.5 * T))
        tau = float(rng.uniform(0.001, 0.5 * T)) if trial % 2 else None
        iv = pl.scanner_intervals(T, sig, tau)
        t0s = np.arange(0.0, T, 0.5 * sig)[:200]
        xs, Es = fs.fold_exposure(win, T, tref)
        e_fast = np.zeros(len(t0s))
        n_fast = np.zeros(len(t0s))
        phi = np.sort(np.mod(t - tref, T))
        for u, v in iv:
            e, n = fs._interval_stats(np.mod(t0s + u, T), v - u, T, xs, Es,
                                      phi)
            e_fast += e
            n_fast += n
        e_ref = np.array([pl.periodic_overlap(win, T, tref + t0, iv)
                          for t0 in t0s])
        n_ref = np.array([pl.counts_in(t, T, tref + t0, iv)[0]
                          for t0 in t0s])
        if not (np.allclose(e_fast, e_ref, atol=1e-9)
                and np.array_equal(n_fast, n_ref)):
            check(f"trial {trial}", False,
                  f"max|de|={np.max(np.abs(e_fast - e_ref)):.2e} "
                  f"dn={np.max(np.abs(n_fast - n_ref))}")
            break
    else:
        check("60 random (window, T, sigma, tau) templates", True)

    print("[2] M2 scan equivalence (random configs)")
    for trial in range(12):
        win = rand_window(rng, rng.integers(4, 20), rng.uniform(8, 40))
        span = float(win[1][-1] - win[0][0])
        t = rand_events(rng, win, int(rng.integers(5, 250)))
        p_min, s_min = span / 40.0, span / 400.0
        ll_ref, arg_ref = pl.scan_scanner(t, win, span, p_min, s_min,
                                          paired=False)
        ll_f, arg_f, _ = fs.scan_scanner_fast(t, win, span, p_min,
                                              s_min, paired=False)
        ok = abs(ll_ref - ll_f) < 1e-7 and args_equiv(
            ll_ref, arg_ref, arg_f, t, win, float(win[0][0]))
        check(f"M2 trial {trial}", ok,
              f"ref={ll_ref:.6f} fast={ll_f:.6f}")

    print("[3] M3 scan equivalence")
    for trial in range(8):
        win = rand_window(rng, rng.integers(4, 16), rng.uniform(8, 30))
        span = float(win[1][-1] - win[0][0])
        t = rand_events(rng, win, int(rng.integers(5, 200)))
        p_min, s_min = span / 30.0, span / 300.0
        taus = list(np.geomspace(s_min, span / 20.0, 5))
        ll_ref, arg_ref = pl.scan_scanner(t, win, span, p_min, s_min,
                                          paired=True, tau_grid=taus)
        ll_f, arg_f, nc = fs.scan_scanner_fast(
            t, win, span, p_min, s_min, paired=True, tau_grid=taus)
        ok = abs(ll_ref - ll_f) < 1e-7 and args_equiv(
            ll_ref, arg_ref, arg_f, t, win, float(win[0][0]))
        check(f"M3 trial {trial}", ok,
              f"ref={ll_ref:.6f} fast={ll_f:.6f} cells={nc}")

    print("[4] Lambda equivalence on real sepoct window (smoke config)")
    win_sepoct = win = ac.load_sepoct_windows()
    cfg = ac.TEST
    smoke_lams = {}
    for i, fam in enumerate(["M0", "M1", "M4", "M5"]):
        r = np.random.default_rng([7, i])
        t = ac._sim_family(r, win, fam)
        t0c = time.time()
        lam_ref, det_ref = pl.lambda_stat(t, win, cfg["p_min"],
                                          cfg["sigma_min"],
                                          cfg["tau_grid"],
                                          m1_kw=cfg["m1_kw"])
        t_ref = time.time() - t0c
        t0c = time.time()
        lam_f, det_f = fs.lambda_stat_fast(t, win, cfg["p_min"],
                                           cfg["sigma_min"],
                                           cfg["tau_grid"],
                                           m1_kw=cfg["m1_kw"])
        t_f = time.time() - t0c
        smoke_lams[fam] = lam_f
        check(f"Lambda {fam}", abs(lam_ref - lam_f) < 1e-6,
              f"ref={lam_ref:.6f} fast={lam_f:.6f} "
              f"({t_ref:.2f}s -> {t_f:.2f}s)")

    print("[5] C kernel equivalence (scankernel vs reference and fastscan)")
    try:
        import scankernel as sk
    except Exception as e:
        check("C kernel import/build", False, str(e))
        sk = None
    if sk is not None:
        for trial in range(10):
            win = rand_window(rng, rng.integers(4, 16), rng.uniform(8, 30))
            span = float(win[1][-1] - win[0][0])
            t = rand_events(rng, win, int(rng.integers(5, 200)))
            p_min, s_min = span / 30.0, span / 300.0
            taus = list(np.geomspace(s_min, span / 20.0, 5))
            for paired in (False, True):
                kw = dict(paired=paired,
                          tau_grid=taus if paired else None)
                ll_ref, arg_ref = pl.scan_scanner(t, win, span, p_min,
                                                  s_min, **kw)
                ll_c, arg_c, _ = sk.scan_scanner_c(t, win, span, p_min,
                                                   s_min, **kw)
                ok = abs(ll_ref - ll_c) < 1e-7 and args_equiv(
                    ll_ref, arg_ref, arg_c, t, win, float(win[0][0]))
                check(f"C {'M3' if paired else 'M2'} trial {trial}", ok,
                      f"ref={ll_ref:.6f} c={ll_c:.6f}")
        for i, fam in enumerate(["M0", "M1", "M4", "M5"]):
            r = np.random.default_rng([7, i])
            t = ac._sim_family(r, win_sepoct, fam)
            t0c = time.time()
            lam_c, _ = sk.lambda_stat_c(t, win_sepoct, cfg["p_min"],
                                        cfg["sigma_min"], cfg["tau_grid"],
                                        m1_kw=cfg["m1_kw"])
            t_c = time.time() - t0c
            lam_f = smoke_lams[fam]
            check(f"C Lambda {fam}", abs(lam_f - lam_c) < 1e-6,
                  f"fast={lam_f:.6f} c={lam_c:.6f} ({t_c:.2f}s)")

    print(f"\n{'ALL PASS' if FAIL == 0 else f'{FAIL} FAILURES'}")
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
