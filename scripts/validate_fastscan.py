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

    print("[6] batched kernel equivalence (scan_scanner_batch vs "
          "per-stream scan_scanner_c)")
    if sk is not None:
        for trial in range(8):
            win = rand_window(rng, rng.integers(4, 16), rng.uniform(8, 30))
            span = float(win[1][-1] - win[0][0])
            S = int(rng.integers(2, 7))
            ts = [rand_events(rng, win, int(rng.integers(0, 200)))
                  for _ in range(S)]
            if trial == 0:
                ts[0] = np.empty(0)         # empty-stream fallback parity
            p_min, s_min = span / 30.0, span / 300.0
            taus = list(np.geomspace(s_min, span / 20.0, 5))
            for paired in (False, True):
                kw = dict(paired=paired,
                          tau_grid=taus if paired else None)
                batch = sk.scan_scanner_batch(ts, win, span, p_min,
                                              s_min, **kw)
                ok = True
                detail = ""
                for s, t in enumerate(ts):
                    ll_c, arg_c, n_c = sk.scan_scanner_c(
                        t, win, span, p_min, s_min, **kw)
                    ll_b, arg_b, n_b = batch[s]
                    same_arg = (arg_c is None and arg_b is None) or (
                        arg_c is not None and arg_b is not None
                        and all((x is None and y is None)
                                or (x is not None and y is not None
                                    and x == y)
                                for x, y in zip(arg_c, arg_b)))
                    if not (ll_b == ll_c and same_arg and n_b == n_c):
                        ok = False
                        detail = (f"stream {s}: c=({ll_c:.9f},{arg_c}) "
                                  f"batch=({ll_b:.9f},{arg_b})")
                        break
                check(f"batch {'M3' if paired else 'M2'} trial {trial} "
                      f"(S={S})", ok, detail)
        # Real-window case: sepoct windows, simulated streams incl. one
        # empty and one dense.
        win = win_sepoct
        span = float(win[1][-1] - win[0][0])
        cfg = ac.TEST
        ts = [ac._sim_family(np.random.default_rng([9, k]), win,
                             ["M0", "M1", "M4", "M5"][k % 4])
              for k in range(5)] + [np.empty(0)]
        for paired in (False, True):
            kw = dict(paired=paired,
                      tau_grid=cfg["tau_grid"] if paired else None)
            batch = sk.scan_scanner_batch(ts, win, span, cfg["p_min"],
                                          cfg["sigma_min"], **kw)
            ok = True
            for s, t in enumerate(ts):
                ll_c, arg_c, n_c = sk.scan_scanner_c(
                    t, win, span, cfg["p_min"], cfg["sigma_min"], **kw)
                if not (batch[s][0] == ll_c and batch[s][1] == arg_c):
                    ok = False
                    break
            check(f"batch real-window {'M3' if paired else 'M2'} "
                  f"(S={len(ts)})", ok)

    print("[7] segmented sweep equivalence (SEG_MODE forced on/off vs "
          "per-stream scan_scanner_c)")
    if sk is not None:
        def batch_equal(ts, win, span, p_min, s_min, taus, label):
            """batch results under seg forced-on and forced-off must be
            exactly equal to per-stream scan_scanner_c (which has no
            segmented path and is validated against the reference)."""
            for paired in (False, True):
                kw = dict(paired=paired,
                          tau_grid=taus if paired else None)
                singles = [sk.scan_scanner_c(t, win, span, p_min, s_min,
                                             **kw) for t in ts]
                for mode in (1, -1, 0):
                    sk.set_seg_mode(mode)
                    batch = sk.scan_scanner_batch(ts, win, span, p_min,
                                                  s_min, **kw)
                    ok = all(b[0] == c[0] and b[1] == c[1]
                             for b, c in zip(batch, singles))
                    check(f"{label} {'M3' if paired else 'M2'} "
                          f"seg_mode={mode:+d}", ok)
            sk.set_seg_mode(0)

        # 7a: standard random configs with segmentation FORCED on (the
        # auto heuristic rarely engages at this scale, so force it).
        for trial in range(6):
            win = rand_window(rng, rng.integers(4, 16), rng.uniform(8, 30))
            span = float(win[1][-1] - win[0][0])
            S = int(rng.integers(2, 7))
            ts = [rand_events(rng, win, int(rng.integers(0, 200)))
                  for _ in range(S)]
            p_min, s_min = span / 30.0, span / 300.0
            taus = list(np.geomspace(s_min, span / 20.0, 5))
            batch_equal(ts, win, span, p_min, s_min, taus,
                        f"forced trial {trial}")

        # 7b: sparse windows (short sessions over a long span) where the
        # auto heuristic genuinely engages, small events counts.
        for trial in range(4):
            n_ses = int(rng.integers(4, 12))
            span_t = float(rng.uniform(60, 150))
            starts = np.sort(rng.uniform(0, span_t, n_ses))
            durs = rng.uniform(0.02, 0.10, n_ses)
            a, b = [], []
            end = -1.0
            for s0, d0 in zip(starts, durs):
                s0 = max(s0, end + 0.5)
                a.append(s0)
                b.append(s0 + d0)
                end = s0 + d0
            win = (np.array(a), np.array(b))
            span = float(win[1][-1] - win[0][0])
            S = int(rng.integers(2, 5))
            ts = [rand_events(rng, win, int(rng.integers(0, 40)))
                  for _ in range(S)]
            p_min, s_min = span / 12.0, span / 4000.0
            taus = list(np.geomspace(s_min, span / 20.0, 5))
            batch_equal(ts, win, span, p_min, s_min, taus,
                        f"sparse trial {trial}")

    print(f"\n{'ALL PASS' if FAIL == 0 else f'{FAIL} FAILURES'}")
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
