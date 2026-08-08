#!/usr/bin/env python3
"""Compute and commit the frozen per-source alias sets and search grids
(prereg_h1.md Sections 5.1-5.4) from the six verified window functions in
phase1/windows/.

Per prereg Section 5.4 the alias set must be computed and committed BEFORE
the first scan of real data. For each confirmatory source-campaign pair this
script derives, from the extracted session log only (no burst times are
read):

  - the frozen period bounds P_min = max(1 h, 2 sigma_v,min) and
    P_max = T_span/3, and the octave-wise frequency grid of Section 5.3,
    taken verbatim from pipeline.scanner_grids (the same code the scan
    uses);
  - the normalized spectral window |W~(f)|^2 evaluated on exactly that
    grid;
  - the frozen alias set: (i) the day-rational frequencies n*(p/q)*f_d,
    n in {1,2}, p,q in {1,2,3}, for both sidereal and solar f_d, and
    (ii) window-function peaks: contiguous grid runs with |W~(f)|^2 > 0.2
    (every grid frequency satisfies f > 2/T_span by construction, since
    f_min = 3/T_span);
  - per-octave alias-flagged fractions (rule tolerance 2/T_span), so the
    alias-blanket property of short-baseline campaigns is recorded
    explicitly.

Multi-station campaigns (AstroFlash): the likelihood sums station exposures
(shared source parameters, per-station windows), so the alias-relevant
spectral window is that of the summed exposure Sum_s W_s(t) -- computed here
by concatenating all stations' GTIs (overlapping station time is
multiplicity-weighted, exactly as in the likelihood's exposure integral).

Windows are used on their published topocentric axis (as extracted); the
barycentric correction shifts window edges by <= ~5 min and grid
frequencies by O(1e-8) relative -- negligible against the 2/T_span alias
tolerance (>= 3e-3 per day).

Outputs: phase1/grids/<campaign>_grid_alias.json (one committed artifact
per source-campaign pair, with input/script SHA-256) and
phase1/grids/SUMMARY.json.
"""

import csv
import hashlib
import json
import sys
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "phase1"))
import pipeline as pl  # noqa: E402

WIN = ROOT / "phase1" / "windows"
OUT = ROOT / "phase1" / "grids"

SIGMA_MIN_D = 60.0 / pl.DAY_S
P_MIN_D = 1.0 / 24.0          # max(1 h, 2*sigma_v,min, P_floor); P_floor
                              # << 1 h for all six sources (prereg 2.2)
PEAK_THRESH = 0.2
CHUNK = 1 << 18


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


# ------------------------------------------------------- window loaders

def _load_csv(name):
    with open(WIN / name, newline="") as f:
        return list(csv.DictReader(f))


def win_nancay():
    r = _load_csv("nancay20220912A_sessions.csv")
    a = [float(x["mjd_start_topo"]) for x in r]
    b = [float(x["mjd_end_topo"]) for x in r]
    return a, b, {}


def win_astroflash():
    r = _load_csv("astroflash20220912A_sessions.csv")
    a = [float(x["mjd_start"]) for x in r]
    b = [float(x["mjd_end"]) for x in r]
    stations = sorted({x["Telescope"] for x in r})
    return a, b, {"stations": stations,
                  "note": "summed multi-station exposure (see docstring)"}


def win_fast20240114A():
    r = _load_csv("fast20240114A_zhou111_sessions.csv")
    a = [float(x["mjd_start_topo_inffreq"]) for x in r]
    b = [float(x["mjd_end_topo_inffreq"]) for x in r]
    return a, b, {}


def win_fast20201124A():
    r = _load_csv("fast20201124A_sepoct_sessions.csv")
    a = [float(x["mjd_start_topo"]) for x in r]
    b = [float(x["mjd_start_topo"]) + float(x["duration_s"]) / pl.DAY_S
         for x in r]
    return a, b, {}


def win_tmrt():
    rows = _load_csv("tmrt20240114A_sessions.csv")
    a, b = [], []
    for x in rows:
        dt = datetime(int(x["Obs.Y"]), int(x["Obs.M"]), int(x["Obs.D"]),
                      int(x["Obs.h"]), int(x["Obs.m"]), int(x["Obs.s"]))
        mjd = (dt - datetime(1858, 11, 17)).total_seconds() / pl.DAY_S
        a.append(mjd)
        b.append(mjd + float(x["Duration"]) / pl.DAY_S)
    return a, b, {}


def win_effelsberg20200120E():
    r = _load_csv("effelsberg20200120E_sessions.csv")
    a = [float(x["mjd_start_topo"]) for x in r]
    b = [float(x["mjd_end_topo"]) for x in r]
    return a, b, {}


CAMPAIGNS = [
    ("nancay20220912A", "nancay20220912A_sessions.csv", win_nancay),
    ("astroflash20220912A", "astroflash20220912A_sessions.csv",
     win_astroflash),
    ("fast20240114A", "fast20240114A_zhou111_sessions.csv",
     win_fast20240114A),
    ("fast20201124A_sepoct", "fast20201124A_sepoct_sessions.csv",
     win_fast20201124A),
    ("tmrt20240114A", "tmrt20240114A_sessions.csv", win_tmrt),
    ("effelsberg20200120E", "effelsberg20200120E_sessions.csv",
     win_effelsberg20200120E),
]


# ------------------------------------------------------------ computation

def _power_chunk(args):
    a, b, f = args
    return pl.spectral_window((a, b), f)


def peak_runs(f, power, df):
    """Contiguous grid runs with power > PEAK_THRESH, as intervals."""
    mask = power > PEAK_THRESH
    if not np.any(mask):
        return []
    idx = np.flatnonzero(mask)
    splits = np.flatnonzero(np.diff(idx) > 1)
    runs = np.split(idx, splits + 1)
    out = []
    for run in runs:
        seg = power[run]
        j = run[int(np.argmax(seg))]
        out.append({"f_lo_per_d": float(f[run[0]]),
                    "f_hi_per_d": float(f[run[-1]]),
                    "n_grid_points": int(len(run)),
                    "max_power": float(np.max(seg)),
                    "f_at_max_per_d": float(f[j])})
    return out


def process(name, fname, loader, pool):
    a, b, meta = loader()
    order = np.argsort(a)
    a = np.array(a)[order]
    b = np.array(b)[order]
    assert np.all(b > a), f"{name}: non-positive session duration"
    win = (a, b)
    span = float(b[-1] - a[0])
    live = pl.live_time(win)
    grids, octaves = pl.scanner_grids(span, P_MIN_D, SIGMA_MIN_D,
                                      detail=True)
    fa = pl.alias_frequencies()
    tol = 2.0 / span

    oct_out, all_peaks = [], []
    n_total = n_flagged = 0
    for o in octaves:
        f = o["f"]
        chunks = [f[i:i + CHUNK] for i in range(0, len(f), CHUNK)]
        power = np.concatenate(list(pool.map(
            _power_chunk, [(a, b, c) for c in chunks])))
        rat = np.zeros(len(f), dtype=bool)
        for x in fa:
            rat |= np.abs(f - x) < tol
        peaks = peak_runs(f, power, o["df_per_d"])
        pk = power > PEAK_THRESH
        # flagged = within tol of a day-rational or inside/near a peak run
        near_pk = pk.copy()
        k = int(np.ceil(tol / o["df_per_d"]))
        if peaks and k > 0:
            idx = np.flatnonzero(pk)
            lo = np.maximum(idx - k, 0)
            hi = np.minimum(idx + k, len(f) - 1)
            for l, h in zip(lo, hi):
                near_pk[l:h + 1] = True
        flagged = rat | near_pk
        oct_out.append({
            "t_lo_d": o["t_lo_d"], "t_hi_d": o["t_hi_d"],
            "df_per_d": o["df_per_d"], "n_f": int(len(f)),
            "f_lo_per_d": float(f[0]), "f_hi_per_d": float(f[-1]),
            "n_peak_points": int(np.sum(pk)),
            "alias_flagged_frac": float(np.mean(flagged))})
        all_peaks.extend(peaks)
        n_total += len(f)
        n_flagged += int(np.sum(flagged))

    art = {
        "campaign": name,
        "computed_utc": datetime.now(timezone.utc).isoformat(
            timespec="seconds"),
        "prereg": "prereg_h1.md Sections 5.1-5.4 (pre-tag frozen artifact)",
        "window_file": f"phase1/windows/{fname}",
        "window_sha256": sha256(WIN / fname),
        "script_sha256": sha256(__file__),
        "n_sessions": int(len(a)),
        "mjd_first": float(a[0]), "mjd_last": float(b[-1]),
        "span_days": span, "live_days": live,
        "params": {
            "p_min_d": P_MIN_D, "p_max_d": span / 3.0,
            "sigma_min_d": SIGMA_MIN_D, "sigma_factor": 2.0,
            "f_oversample": 2.0, "t0_step_frac": 0.5,
            "tau_grid_d": pl.frozen_tau_grid(),
            "peak_power_threshold": PEAK_THRESH,
            "alias_tolerance_per_d": tol,
            "p_floor_note": ("P_floor << 1 h for all six sources "
                             "(interferometric/FAST localization, prereg "
                             "2.2); grid floor 1 h governs"),
            "time_axis": "topocentric as extracted (see script docstring)",
        },
        "meta": meta,
        "grid": {"n_octaves": len(oct_out), "n_f_total": int(n_total),
                 "octaves": oct_out},
        "alias_set": {
            "day_rational_per_d": [float(x) for x in fa],
            "window_peaks": all_peaks,
            "n_peak_intervals": len(all_peaks),
            "alias_flagged_frac_total": float(n_flagged / n_total),
        },
    }
    out_path = OUT / f"{name}_grid_alias.json"
    with open(out_path, "w") as fjson:
        json.dump(art, fjson, indent=1)
    return art


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    summary = {}
    with ProcessPoolExecutor() as pool:
        for name, fname, loader in CAMPAIGNS:
            art = process(name, fname, loader, pool)
            g, al = art["grid"], art["alias_set"]
            summary[name] = {
                "n_sessions": art["n_sessions"],
                "span_days": round(art["span_days"], 3),
                "live_days": round(art["live_days"], 3),
                "p_max_d": round(art["params"]["p_max_d"], 4),
                "alias_tolerance_per_d": round(
                    art["params"]["alias_tolerance_per_d"], 6),
                "n_f_total": g["n_f_total"],
                "n_peak_intervals": al["n_peak_intervals"],
                "alias_flagged_frac": round(
                    al["alias_flagged_frac_total"], 4),
                "artifact": f"phase1/grids/{name}_grid_alias.json",
                "artifact_sha256": sha256(
                    OUT / f"{name}_grid_alias.json"),
            }
            s = summary[name]
            print(f"{name}: {s['n_sessions']} sessions, span "
                  f"{s['span_days']} d, grid {s['n_f_total']:,} f-points, "
                  f"{s['n_peak_intervals']} peak intervals, flagged frac "
                  f"{s['alias_flagged_frac']}")
    with open(OUT / "SUMMARY.json", "w") as f:
        json.dump({"computed_utc": datetime.now(timezone.utc).isoformat(
            timespec="seconds"), "campaigns": summary}, f, indent=1)
    print("SUMMARY.json written")


if __name__ == "__main__":
    main()
