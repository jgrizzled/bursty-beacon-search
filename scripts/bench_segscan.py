#!/usr/bin/env python3
"""Real-workload equivalence + benchmark for the segmented batched scan.

For each calibration campaign: draw the actual production M4 simulation
streams (calibration.draw_stream, the frozen seeded generator), pick
period slices from several octaves of the frozen grid, and run
scan_scanner_batch under seg_mode=-1 (the pre-optimization code paths,
byte-identical to the previously committed kernel logic) and seg_mode=0
(production auto). Results must match EXACTLY (float equality of ll and
argmax per stream, M2 and M3); wall times give the per-octave speedup.

Usage: bench_segscan.py [--streams 4] [--per-octave 8] [--campaigns a,b]
"""

import argparse
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "phase1"))
import calibration as cal  # noqa: E402
import pipeline as pl      # noqa: E402
import scankernel as sk    # noqa: E402


def run_modes(ts, win, span, periods, paired):
    orig = pl.scanner_grids
    out = {}
    try:
        pl.scanner_grids = (lambda *a, _p=periods, **k: [_p])
        for mode in (-1, 0):
            sk.set_seg_mode(mode)
            t0 = time.time()
            res = sk.scan_scanner_batch(
                ts, win, span, cal.FULL["p_min"], cal.FULL["sigma_min"],
                paired=paired,
                tau_grid=cal.FULL["tau_grid"] if paired else None)
            out[mode] = (time.time() - t0, res)
    finally:
        pl.scanner_grids = orig
        sk.set_seg_mode(0)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--streams", type=int, default=4)
    ap.add_argument("--per-octave", type=int, default=8)
    ap.add_argument("--campaigns", default=None)
    args = ap.parse_args()
    campaigns = (args.campaigns.split(",") if args.campaigns
                 else list(cal.CAMPAIGNS))

    _, data = cal.load_inputs()
    n_fail = 0
    tot = {-1: 0.0, 0: 0.0}
    for camp in campaigns:
        _t, win = data[camp]
        span = float(win[1][-1] - win[0][0])
        ts = [cal.cached_stream("M4", camp, s) for s in range(args.streams)]
        layout = cal.octave_layout(span)
        picks = sorted({0, len(layout) // 2, 2 * len(layout) // 3,
                        len(layout) - 1})
        for oi in picks:
            o = layout[oi]
            P = 1.0 / o["f"]
            step = max(1, len(P) // args.per_octave)
            periods = np.ascontiguousarray(P[::step][:args.per_octave])
            for model, paired in (("M2", False), ("M3", True)):
                r = run_modes(ts, win, span, periods, paired)
                (t_off, res_off), (t_on, res_on) = r[-1], r[0]
                same = all(a[0] == b[0] and a[1] == b[1]
                           for a, b in zip(res_off, res_on))
                tot[-1] += t_off
                tot[0] += t_on
                if not same:
                    n_fail += 1
                print(f"{'PASS' if same else 'FAIL'}  {camp:26s} oct={oi:2d} "
                      f"t_hi={o['t_hi_d']:7.2f}d {model} "
                      f"n_p={len(periods):2d}  off={t_off:7.2f}s "
                      f"on={t_on:7.2f}s  x{t_off / max(t_on, 1e-9):5.2f}",
                      flush=True)
    print(f"\ntotals: off={tot[-1]:.1f}s on={tot[0]:.1f}s "
          f"x{tot[-1] / max(tot[0], 1e-9):.2f}  "
          f"{'ALL PASS' if n_fail == 0 else f'{n_fail} FAILURES'}")
    return 1 if n_fail else 0


if __name__ == "__main__":
    sys.exit(main())
