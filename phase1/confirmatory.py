"""Confirmatory H1 scan runner (phase1/CONFIRMATORY_PLAN.md; post-tag,
prereg-h1-v1.0 = 277fc8b).

Per source-campaign pair: frozen event construction (prereg 2.1),
barycentred windows (prereg 2.2 via bary.py, DE440), per-octave M2/M3
scans with the validated exact C kernel (identical Lambda to
pipeline.lambda_stat; per-octave decomposition for the ranked peak list),
natural-model fits M0/M1/M4/M5, the frozen Lambda statistic (prereg 6.1),
and alias flagging of every peak (prereg 5.4; live rule cross-checked
against the committed pre-scan artifacts in phase1/grids/).

NO false-alarm probabilities are produced here: FAP calibration is the
Section 6.2 cluster job. To support it, the scan path is a pure function
of (event times, windows) -- scan_campaign() -- so simulated streams can
drive the identical per-campaign search unchanged.

Checkpointing: every (campaign, octave, model) scan result and each
campaign's natural-model block append to confirmatory_checkpoint.jsonl;
completed entries are skipped on restart (sound: entries are
deterministic functions of the frozen inputs). The assembled output is
phase1/confirmatory_results.json, rewritten after every campaign.

Gate: refuses to scan unless phase1/validation_output_confirmatory.txt
ends in ALL PASS (kernel equivalence, scripts/validate_fastscan.py --
required after any rebuild of _scankernel.c or compiler change).

Run:  uv run python phase1/confirmatory.py [--campaigns a,b,...]
                                           [--dry-run]
"""

import argparse
import csv
import hashlib
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pipeline as pl        # noqa: E402
import scankernel as sk      # noqa: E402
import bary                  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
WIN = ROOT / "phase1" / "windows"
RAW = ROOT / "data" / "raw"
GRIDS = ROOT / "phase1" / "grids"
CKPT = ROOT / "phase1" / "confirmatory_checkpoint.jsonl"
OUT = ROOT / "phase1" / "confirmatory_results.json"
VALIDATION = ROOT / "phase1" / "validation_output_confirmatory.txt"
PIN = ROOT / "phase0" / "environment_pin.json"

MERGE_S = 0.1                      # prereg 2.1: < 100 ms merges
FULL = dict(p_min=1.0 / 24.0, sigma_min=60.0 / pl.DAY_S,
            tau_grid=pl.frozen_tau_grid(),
            m1_kw=dict(n_periods=200, n_phase=24))

# Frozen sky positions (CONFIRMATORY_PLAN rule 2). Coarse (<~ arcmin)
# positions suffice: window-edge conversion error < 0.2 s << sigma_v,min
# = 60 s. FRB 20200120E uses the exact VLBI position frozen in
# environment_pin.json (loaded at runtime).
POSITIONS_SEX = {
    "20220912A": ("23:09:04.9", "+48:42:25.4"),
    "20240114A": ("21:27:39.8", "+04:19:45.6"),
    "20201124A": ("05:08:03.5", "+26:03:38.4"),
}

AF_SITE = {"stk": "stockert", "wb": "westerbork_rt1",
           "tr": "torun", "o8": "onsala85"}


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def sex_to_deg(ra_s, dec_s):
    h, m, s = [float(x) for x in ra_s.split(":")]
    ra = 15.0 * (h + m / 60.0 + s / 3600.0)
    sign = -1.0 if dec_s.strip().startswith("-") else 1.0
    d, m2, s2 = [abs(float(x)) for x in dec_s.lstrip("+-").split(":")]
    return ra, sign * (d + m2 / 60.0 + s2 / 3600.0)


def load_pin():
    with open(PIN) as f:
        return json.load(f)


def assert_reference_conversion(pin):
    """Frozen regression anchor (environment_pin.json / manifest Section 6):
    must hold to 1e-8 d before any window is converted."""
    rc = pin["reference_conversion"]
    loc = bary.get_location(rc["site"])
    got = float(bary.topo_utc_to_bjd_tdb(rc["mjd_utc_topo"], loc,
                                         rc["ra_deg"], rc["dec_deg"]))
    err_d = abs(got - rc["bjd_tdb_inf_freq"])
    assert err_d < 1e-8, (
        f"reference conversion regression: got {got!r}, pinned "
        f"{rc['bjd_tdb_inf_freq']!r} (|err| = {err_d:.3e} d)")
    return {"site": rc["site"], "mjd_utc_topo": rc["mjd_utc_topo"],
            "expected_bjd_tdb": rc["bjd_tdb_inf_freq"],
            "computed_bjd_tdb": got, "abs_err_d": err_d, "pass": True}


# ---------------------------------------------------- event construction

def merge_events(toa, weight, ids):
    """Prereg 2.1 trigger-event rule: transitively merge rows whose peak
    times are < 100 ms apart; event time = peak time of the brightest
    component (weight = S/N, or the documented brightness proxy).
    weight=None asserts that no merging is required (campaigns whose
    frozen tables carry no brightness column and are documented
    merge-free). Returns (event times, n merged away, per-event id)."""
    toa = np.asarray(toa, float)
    order = np.argsort(toa, kind="stable")
    toa = toa[order]
    ids = [ids[i] for i in order]
    w = None if weight is None else np.asarray(weight, float)[order]
    gap = np.diff(toa) * pl.DAY_S
    new_group = np.concatenate([[True], gap >= MERGE_S])
    gid = np.cumsum(new_group) - 1
    n_groups = int(gid[-1]) + 1 if len(toa) else 0
    if w is None:
        assert n_groups == len(toa), (
            "merge required but no brightness column in the frozen table")
        return toa, 0, ids
    out = np.empty(n_groups)
    out_ids = []
    for g in range(n_groups):
        idx = np.flatnonzero(gid == g)
        j = idx[int(np.argmax(w[idx]))]
        out[g] = toa[j]
        out_ids.append(ids[j])
    return out, int(len(toa) - n_groups), out_ids


def _read_csv(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def events_nancay():
    """TOA-frame correction (2026-08-09, on first data contact): the
    CONFIRMATORY_PLAN table annotated this column bary TDB inf-freq, but
    the TOAs are empirically TOPOCENTRIC -- 639/640 events lie inside the
    topocentric session log (whose starts equal the candidate-file
    filterbank tstart values), while the barycentric reading places
    84/640 outside the converted windows. The prereg 2.2 frozen path for
    topocentric inputs applies: convert topo UTC -> BJD_TDB via bary.py
    (same site/position as the windows). Reference-frequency ambiguity
    (<= ~1 s at DM ~223) and 1e-5 d printed precision (~0.86 s) are both
    << sigma_v,min = 60 s."""
    rows = _read_csv(RAW / "nancay_20220912A" /
                     "Supplementary Material (online).csv")
    toa = [float(r["Time of arrival (MJD)"]) for r in rows]
    sn = [float(r["S/N"]) for r in rows]
    ids = [r["Burst ID"] for r in rows]
    return toa, sn, ids, {
        "table_rows": len(rows), "weight_col": "S/N",
        "toa_frame": "topo_utc",
        "toa_frame_note": ("Supplementary TOAs empirically topocentric "
                           "(see events_nancay docstring); converted via "
                           "prereg 2.2 frozen path; plan annotation "
                           "corrected 2026-08-09")}


def events_astroflash():
    """Prereg 2.1 / manifest 1.2c: dedup by published base burst ID FIRST
    (146 rows -> 130 unique; keep the highest-peak_sn station row), never
    by time window; then the 100 ms rule (no pairs remain within it --
    inter-station offsets are 0.1-0.55 s by construction)."""
    rows = _read_csv(RAW / "astroflash_20220912A" /
                     "FRB20220912A_table_paper.csv")
    best = {}
    for r in rows:
        bid = r["id"].rsplit("-", 1)[0]
        if bid not in best or float(r["peak_sn"]) > float(
                best[bid]["peak_sn"]):
            best[bid] = r
    toa = [float(r["toa"]) for r in best.values()]
    sn = [float(r["peak_sn"]) for r in best.values()]
    ids = list(best.keys())
    return toa, sn, ids, {
        "table_rows": len(rows), "n_unique_base_id": len(best),
        "weight_col": "peak_sn",
        "dedup": "published base burst ID, highest-S/N station row"}


def events_fast20240114A():
    rows = _read_csv(RAW / "fast_20240114A" / "FRB20240114A_SuppTab2.csv")
    toa = [float(r["MJD(bary@inf freq.)"]) for r in rows]
    flux = [float(r["Flux(mJy)"]) for r in rows]
    ids = [r["BurstID"] for r in rows]
    return toa, flux, ids, {
        "table_rows": len(rows), "weight_col": "Flux(mJy)",
        "weight_note": ("no S/N column in the frozen table; peak flux is "
                        "the brightness proxy for the brightest-component "
                        "rule")}


def events_fast20201124A():
    rows = _read_csv(WIN / "fast20201124A_sepoct_bursts.csv")
    toa = [float(r["toa_mjd_bary_inffreq"]) for r in rows]
    sn = [float(r["snr"]) for r in rows]
    ids = [f"{r['session_date']}-{r['burst_no']}" for r in rows]
    return toa, sn, ids, {
        "table_rows": len(rows), "weight_col": "snr",
        "note": ("625 rows = 624 numbered bursts; burst No. 108's two "
                 "component rows fall under the merge rule")}


def events_tmrt():
    """ApJ MRT fixed-width (manifest 1.5 / CONFIRMATORY_PLAN): bytes 1-4
    Name, 6-20 Epoch (bary MJD inf-freq), 28-32 final S/N."""
    toa, sn, ids = [], [], []
    with open(RAW / "tmrt_20240114A" / "apjadfecet3_mrt.txt") as f:
        for line in f:
            if line[:1] == "B" and line[1:4].strip().isdigit():
                ids.append(line[0:4].strip())
                toa.append(float(line[5:20]))
                sn.append(float(line[27:32]))
    return toa, sn, ids, {"table_rows": len(toa),
                          "weight_col": "S/N (final, bytes 28-32)"}


def events_effelsberg():
    rows = _read_csv(WIN / "effelsberg20200120E_bursts.csv")
    toa = [float(r["toa_mjd_bary_tdb_inffreq"]) for r in rows]
    ids = [r["burst_id"] for r in rows]
    return toa, None, ids, {
        "table_rows": len(rows), "weight_col": None,
        "note": ("frozen composed list (manifest 1.7a): cross-table dedup "
                 "already applied; minimum pairwise gap 0.39 s > 100 ms, "
                 "so no merge arises and no brightness column is needed")}


# ---------------------------------------------------- window construction

def _bary_windows(site_edges, ra_deg, dec_deg):
    """site_edges: list of (site, a_topo, b_topo) arrays. Converts each
    station's session edges topocentric UTC -> BJD_TDB and returns the
    concatenated GTIs sorted by start (summed exposure; overlapping
    station time is multiplicity-weighted, exactly as in the committed
    alias artifacts and the likelihood's exposure integral)."""
    A, B = [], []
    for site, a, b in site_edges:
        loc = bary.get_location(site)
        A.append(bary.topo_utc_to_bjd_tdb(np.asarray(a, float), loc,
                                          ra_deg, dec_deg))
        B.append(bary.topo_utc_to_bjd_tdb(np.asarray(b, float), loc,
                                          ra_deg, dec_deg))
    a = np.concatenate(A)
    b = np.concatenate(B)
    order = np.argsort(a, kind="stable")
    a, b = a[order], b[order]
    assert np.all(b > a), "non-positive session duration after conversion"
    return a, b


def win_nancay():
    r = _read_csv(WIN / "nancay20220912A_sessions.csv")
    a = [float(x["mjd_start_topo"]) for x in r]
    b = [float(x["mjd_end_topo"]) for x in r]
    return [("nancay", a, b)], "nancay20220912A_sessions.csv"


def win_astroflash():
    r = _read_csv(WIN / "astroflash20220912A_sessions.csv")
    groups = {}
    for x in r:
        site = AF_SITE[x["Telescope"]]
        groups.setdefault(site, ([], []))
        groups[site][0].append(float(x["mjd_start"]))
        groups[site][1].append(float(x["mjd_end"]))
    return ([(site, a, b) for site, (a, b) in sorted(groups.items())],
            "astroflash20220912A_sessions.csv")


def win_fast20240114A():
    r = _read_csv(WIN / "fast20240114A_zhou111_sessions.csv")
    a = [float(x["mjd_start_topo_inffreq"]) for x in r]
    b = [float(x["mjd_end_topo_inffreq"]) for x in r]
    return [("FAST", a, b)], "fast20240114A_zhou111_sessions.csv"


def win_fast20201124A():
    r = _read_csv(WIN / "fast20201124A_sepoct_sessions.csv")
    a = [float(x["mjd_start_topo"]) for x in r]
    b = [float(x["mjd_start_topo"]) + float(x["duration_s"]) / pl.DAY_S
         for x in r]
    return [("FAST", a, b)], "fast20201124A_sepoct_sessions.csv"


def win_tmrt():
    rows = _read_csv(WIN / "tmrt20240114A_sessions.csv")
    a, b = [], []
    for x in rows:
        dt = datetime(int(x["Obs.Y"]), int(x["Obs.M"]), int(x["Obs.D"]),
                      int(x["Obs.h"]), int(x["Obs.m"]), int(x["Obs.s"]))
        mjd = (dt - datetime(1858, 11, 17)).total_seconds() / pl.DAY_S
        a.append(mjd)
        b.append(mjd + float(x["Duration"]) / pl.DAY_S)
    return [("tianma65", a, b)], "tmrt20240114A_sessions.csv"


def win_effelsberg():
    r = _read_csv(WIN / "effelsberg20200120E_sessions.csv")
    a = [float(x["mjd_start_topo"]) for x in r]
    b = [float(x["mjd_end_topo"]) for x in r]
    return [("effelsberg", a, b)], "effelsberg20200120E_sessions.csv"


# ---------------------------------------------------------- containment

# Edge tolerance for the prereg 4.1 containment check. Two documented
# session-edge convention mismatches exist between the frozen (published,
# unmodifiable) burst tables and session logs:
#   1. before session start: burst TOAs are barycentric at INFINITE
#      frequency, so a burst detected in-band right after recording start
#      precedes the converted session edge by up to the intra-band
#      dispersion sweep (~2.2 s at DM 527.7 / 1.0 GHz for FAST 20240114A;
#      ~1.7 s at DM 413 for 20201124A) plus published rounding;
#   2. after session end: the FAST 20240114A release's published stop
#      times end before its own last burst TOAs in ~33 sessions, by up to
#      23.6 s (Zhou 111-row and Zhang 57-row logs agree to ~1 s with each
#      other, so this is a property of the release -- nominal scheduled
#      stops vs actual recording -- not an extraction or frame error).
# Events within EDGE_TOL_S of a session are accepted at their published
# times and reported (harmless at sigma_v >= 60 s visit scales, same
# class as the documented AstroFlash 0.1-0.55 s station offsets; the
# two-bin likelihood handles the boundary deterministically via the
# pooled floor, and the Section 6.2 calibration drives simulations
# through the identical windows and procedure). Events farther out are
# excluded by the prereg S2 "within verified windows" criterion, subject
# to the max(3, 1%) systematic-error guard below.
EDGE_TOL_S = 30.0


def containment(t, win, tol_s=EDGE_TOL_S):
    """Overlap-aware prereg 4.1 check (the AstroFlash multi-station GTIs
    can overlap, so the sorted-searchsorted shortcut is insufficient
    there). Returns (all_inside, stats dict, violators beyond tol)."""
    a, b = win
    t = np.asarray(t, float)
    tol_d = tol_s / pl.DAY_S
    strict = np.zeros(len(t), dtype=bool)
    near = np.zeros(len(t), dtype=bool)
    margin = np.full(len(t), -np.inf)   # signed: >0 strictly inside
    for aj, bj in zip(a, b):
        m = (t >= aj) & (t <= bj)
        strict |= m
        near |= (t >= aj - tol_d) & (t <= bj + tol_d)
        edge = np.minimum(t - aj, bj - t) * pl.DAY_S
        margin = np.maximum(margin, edge)
    bad = [float(x) for x in t[~near]]
    stats = {
        "n_strictly_inside": int(np.sum(strict)),
        "n_edge_marginal": int(np.sum(near & ~strict)),
        "edge_tolerance_s": tol_s,
        "max_excursion_s": (float(-np.min(margin[near & ~strict]))
                            if np.any(near & ~strict) else 0.0),
        "min_inside_margin_s": (float(np.min(margin[strict]))
                                if np.any(strict) else None),
        "note": ("edge-marginal events: infinite-frequency TOA precedes "
                 "the as-published session edge by up to the intra-band "
                 "dispersion sweep (see EDGE_TOL_S comment); frozen "
                 "inputs kept unmodified"),
    }
    return bool(np.all(near)), stats, bad


# ------------------------------------------------------------- scanning
#
# Execution model: the frozen search decomposes into independent units --
# one "natural" unit per campaign (M0/M1/M4/M5 fits) and one unit per
# (octave, model, period-chunk), where each octave's period list is
# partitioned IN SCAN ORDER into deterministic chunks of <= CHUNK_PERIODS.
# Unit results are bit-identical regardless of execution order (each is a
# self-contained kernel scan over its own periods), and per-octave
# (ll, arg) is recombined chunk-by-chunk in order with a strict ">" --
# exactly the sequential scan's first-in-scan-order argmax semantics. So
# running units on a worker pool changes wall-clock only, never results.
# The parent process is the sole checkpoint writer (CkptPool pattern).
# Legacy whole-octave checkpoint entries (from the sequential runner) are
# honored as complete octaves.
#
# For the Section 6.2 cluster: the pure per-stream path (no chunking, no
# checkpoints) is scankernel.lambda_stat_c(t, win, ...FULL config) -- one
# call per simulated stream through the same frozen search.

CHUNK_PERIODS = 100_000

_WCACHE = {}


def _worker_inputs(name):
    if name not in _WCACHE:
        t, win, _meta = build_campaign_inputs(name, load_pin())
        _WCACHE[name] = (np.sort(np.asarray(t, float)), win)
    return _WCACHE[name]


def _octave_layout(span, cfg):
    _, octaves = pl.scanner_grids(span, cfg["p_min"], cfg["sigma_min"],
                                  detail=True)
    layout = []
    for o in octaves:
        n_chunks = int(np.ceil(len(o["f"]) / CHUNK_PERIODS))
        layout.append((o, n_chunks))
    return layout


def run_unit(args):
    """Worker: one checkpoint unit. args = (campaign, kind, idx,
    model_str) mirroring the checkpoint key. Deterministic pure function
    of the frozen inputs."""
    name, kind, idx, model_str = args
    t, win = _worker_inputs(name)
    span = float(win[1][-1] - win[0][0])
    cfg = FULL
    t0c = time.time()
    if kind == "natural":
        ll0 = pl.m0_ll(t, win)
        ll1, arg1 = pl.m1_scan(t, win, span, cfg["p_min"], **cfg["m1_kw"])
        ll4 = pl.m4_fit(t, win)
        ll5 = pl.m5_fit(t, win)
        return args, {"ll_m0": float(ll0), "ll_m1": float(ll1),
                      "m1_arg": list(arg1) if arg1 else None,
                      "ll_m4": float(ll4), "ll_m5": float(ll5),
                      "walltime_s": round(time.time() - t0c, 1)}
    model, part = model_str.split("/")            # e.g. "M3/4of18"
    c, n_chunks = (int(x) for x in part.split("of"))
    o, n_chunks_ck = _octave_layout(span, cfg)[idx]
    assert n_chunks == n_chunks_ck, "chunk layout drift"
    sub = np.array_split(1.0 / o["f"], n_chunks)[c]
    orig = pl.scanner_grids
    try:
        pl.scanner_grids = (lambda *a_, _p=sub, **k_: [_p])
        ll, arg, n_p = sk.scan_scanner_c(
            t, win, span, cfg["p_min"], cfg["sigma_min"],
            paired=(model == "M3"),
            tau_grid=cfg["tau_grid"] if model == "M3" else None)
    finally:
        pl.scanner_grids = orig
    return args, {"ll": float(ll), "arg": list(arg) if arg else None,
                  "n_periods": int(n_p),
                  "walltime_s": round(time.time() - t0c, 1)}


def pending_units(name, span, cfg, done):
    units = []
    if ("natural", -1, "M0M1M4M5") not in done:
        units.append((name, "natural", -1, "M0M1M4M5", 0.0))
    for i, (o, n_chunks) in enumerate(_octave_layout(span, cfg)):
        for model in ("M2", "M3"):
            if ("octave", i, model) in done:      # legacy sequential entry
                continue
            for c in range(n_chunks):
                key = ("chunk", i, f"{model}/{c}of{n_chunks}")
                if key in done:
                    continue
                est = (len(o["f"]) / n_chunks) * o["t_hi_d"] \
                    * (5.0 if model == "M3" else 1.0)
                units.append((name, "chunk", i, key[2], est))
    return units


def _octave_result(done, i, model, n_chunks):
    """Combine chunk entries (or return a legacy whole-octave entry) --
    strict ">" in chunk order preserves the sequential argmax."""
    if ("octave", i, model) in done:
        return done[("octave", i, model)]
    best, arg, n_p, wall = -np.inf, None, 0, 0.0
    for c in range(n_chunks):
        v = done[("chunk", i, f"{model}/{c}of{n_chunks}")]
        n_p += v["n_periods"]
        wall += v["walltime_s"]
        if v["ll"] > best:
            best, arg = v["ll"], v["arg"]
    return {"ll": best, "arg": arg, "n_periods": n_p,
            "walltime_s": round(wall, 1)}


def assemble_campaign(t, win, cfg, done):
    """Assemble the frozen per-campaign statistics from completed units
    (without alias flags, added by the caller)."""
    span = float(win[1][-1] - win[0][0])
    nat = done[("natural", -1, "M0M1M4M5")]
    layout = _octave_layout(span, cfg)
    oct_results = []
    for i, (o, n_chunks) in enumerate(layout):
        for model in ("M2", "M3"):
            oct_results.append((i, model, o,
                                _octave_result(done, i, model, n_chunks)))
    ll2 = max(v["ll"] for i, m, o, v in oct_results if m == "M2")
    ll3 = max(v["ll"] for i, m, o, v in oct_results if m == "M3")
    nat_max = max(nat["ll_m0"], nat["ll_m1"], nat["ll_m4"], nat["ll_m5"])
    lam = 2.0 * (max(ll2, ll3) - nat_max)
    peaks = []
    for i, model, o, v in oct_results:
        if v["arg"] is None:
            continue
        T, sig, tau, t0 = v["arg"]
        peaks.append({
            "octave": i, "model": model,
            "t_lo_d": o["t_lo_d"], "t_hi_d": o["t_hi_d"],
            "T_d": T, "f_per_d": 1.0 / T, "sigma_v_d": sig,
            "tau_c_d": tau, "t0_d": t0, "ll": v["ll"],
            "delta_ll_vs_natural_x2": 2.0 * (v["ll"] - nat_max),
        })
    peaks.sort(key=lambda p: -p["ll"])
    return {"span_days": span, "live_days": pl.live_time(win),
            "natural": nat,
            "ll": {"M0": nat["ll_m0"], "M1": nat["ll_m1"], "M2": ll2,
                   "M3": ll3, "M4": nat["ll_m4"], "M5": nat["ll_m5"]},
            "lambda": lam, "n_octaves": len(layout),
            "walltime_scan_s": round(sum(
                v["walltime_s"] for _, _, _, v in oct_results), 1),
            "peaks_ranked": peaks}


# ---------------------------------------------------------- alias flags

def load_alias_artifact(campaign):
    with open(GRIDS / f"{campaign}_grid_alias.json") as f:
        return json.load(f)


def flag_peaks(peaks, win, span, artifact):
    """Live prereg 5.4 rule on the (barycentric) scan windows, plus the
    cross-check against the committed pre-scan artifact (computed on the
    topocentric axis; frequency shift O(1e-8) relative, negligible vs the
    2/T_span tolerance)."""
    art_tol = artifact["params"]["alias_tolerance_per_d"]
    day_rat = np.asarray(artifact["alias_set"]["day_rational_per_d"])
    intervals = [(p["f_lo_per_d"], p["f_hi_per_d"])
                 for p in artifact["alias_set"]["window_peaks"]]
    for p in peaks:
        f = p["f_per_d"]
        p["alias_flag"] = bool(pl.alias_flag(f, win, span))
        in_rat = bool(np.any(np.abs(day_rat - f) < art_tol))
        in_peak = any(lo - art_tol <= f <= hi + art_tol
                      for lo, hi in intervals)
        p["alias_flag_artifact"] = in_rat or in_peak
        p["alias_src"] = ("day_rational" if in_rat else
                          "window_peak" if in_peak else None)
    return peaks


# ------------------------------------------------------------ campaigns

CAMPAIGNS = {
    # name: (events_fn, windows_fn, source key for position)
    "fast20201124A_sepoct": (events_fast20201124A, win_fast20201124A,
                             "20201124A"),
    "nancay20220912A": (events_nancay, win_nancay, "20220912A"),
    "astroflash20220912A": (events_astroflash, win_astroflash,
                            "20220912A"),
    "tmrt20240114A": (events_tmrt, win_tmrt, "20240114A"),
    "effelsberg20200120E": (events_effelsberg, win_effelsberg,
                            "20200120E"),
    "fast20240114A": (events_fast20240114A, win_fast20240114A,
                      "20240114A"),
}


def build_campaign_inputs(name, pin):
    ev_fn, win_fn, poskey = CAMPAIGNS[name]
    if poskey == "20200120E":
        rc = pin["reference_conversion"]
        ra, dec = rc["ra_deg"], rc["dec_deg"]
        pos_note = "exact VLBI position frozen in environment_pin.json"
    else:
        ra, dec = sex_to_deg(*POSITIONS_SEX[poskey])
        pos_note = ("coarse (<~ arcmin) published position; window-edge "
                    "conversion error < 0.2 s << sigma_v,min = 60 s")
    toa, weight, ids, ev_meta = ev_fn()
    site_edges, win_file = win_fn()
    if ev_meta.get("toa_frame") == "topo_utc":
        sites = {s for s, _, _ in site_edges}
        assert len(sites) == 1, "topo TOA conversion needs a single site"
        loc = bary.get_location(next(iter(sites)))
        toa = bary.topo_utc_to_bjd_tdb(np.asarray(toa, float), loc,
                                       ra, dec)
    t, n_merged, ev_ids = merge_events(toa, weight, ids)
    a, b = _bary_windows(site_edges, ra, dec)
    ok, cont, bad = containment(t, (a, b))
    if not ok:
        # Prereg S2 defines the confirmatory event set as events "within
        # verified windows". An event farther than EDGE_TOL_S from every
        # verified session is outside that set by the frozen criterion
        # (published burst table vs published session log inconsistency;
        # keeping it would also bias Lambda: phase-folded models count it
        # while the per-session M4/M5 likelihoods skip it). Excluded and
        # reported. Guard: more than max(3, 1%) excluded aborts -- that
        # scale indicates a systematic frame/axis error (e.g. the
        # topocentric Nancay TOA reading placed 84/640 outside), not
        # isolated table/log glitches (observed: Nancay B602 at 205 s,
        # AstroFlash B39/B67 at ~5000 s, single-station rows uncovered by
        # either published log).
        limit = max(3, int(0.01 * len(t)))
        if len(bad) > limit:
            raise RuntimeError(
                f"{name}: {len(bad)} events outside converted windows by "
                f"> {EDGE_TOL_S} s (guard limit {limit}) -- systematic "
                f"frame/axis error suspected: {bad[:5]}")
        bad_set = set(bad)
        dropped = [{"id": i, "toa_mjd_bary": float(x)}
                   for x, i in zip(t, ev_ids) if float(x) in bad_set]
        keep = np.array([float(x) not in bad_set for x in t])
        t, ev_ids = t[keep], [i for i, k in zip(ev_ids, keep) if k]
        ev_meta["excluded_outside_windows"] = {
            "n": len(dropped), "events": dropped,
            "rule": ("prereg S2 'within verified windows'; > "
                     f"{EDGE_TOL_S} s outside every verified session; "
                     "recorded in phase0/deviations.md")}
    ev_meta["n_merged_away"] = n_merged
    wmeta = {
        "window_file": f"phase1/windows/{win_file}",
        "window_file_sha256": sha256_file(WIN / win_file),
        "n_sessions": int(len(a)),
        "sites": sorted({s for s, _, _ in site_edges}),
        "position": {"ra_deg": ra, "dec_deg": dec, "note": pos_note},
        "bary": {"ephemeris": bary.EPHEMERIS, "scale": "BJD_TDB",
                 "axis": "windows converted; published TOAs already "
                         "barycentric infinite-frequency"},
        "converted_window_sha256": hashlib.sha256(
            np.ascontiguousarray(a).tobytes()
            + np.ascontiguousarray(b).tobytes()).hexdigest(),
        "mjd_first_bary": float(a[0]), "mjd_last_bary": float(b[-1]),
        "containment": cont,
    }
    return t, (a, b), {"events": dict(ev_meta, n_events=int(len(t))),
                       "windows": wmeta}


# ------------------------------------------------------------ harness

def check_validation_gate():
    txt = VALIDATION.read_text()
    assert "ALL PASS" in txt.splitlines()[-1], (
        "kernel validation gate not passed: see "
        "phase1/validation_output_confirmatory.txt")
    return {"file": "phase1/validation_output_confirmatory.txt",
            "sha256": sha256_file(VALIDATION),
            "kernel_c_sha256": sha256_file(
                ROOT / "phase1" / "_scankernel.c"),
            "result": "ALL PASS"}


class Ckpt:
    def __init__(self, path):
        self.path = Path(path)
        self.done = {}
        if self.path.exists():
            with open(self.path) as f:
                for line in f:
                    k, v = json.loads(line)
                    self.done[(k[0], (k[1], int(k[2]), k[3]))] = v
        self.f = open(self.path, "a")

    def scoped(self, campaign):
        done = {k[1]: v for k, v in self.done.items() if k[0] == campaign}

        def record(key, value):
            self.done[(campaign, key)] = value
            done[key] = value
            self.f.write(json.dumps(
                [[campaign, key[0], key[1], key[2]], value]) + "\n")
            self.f.flush()
        return record, done


def assemble(results, pin, gate, ref):
    lam_star, lam_arg = -np.inf, None
    for name, blk in results.items():
        if blk["scan"]["lambda"] > lam_star:
            lam_star, lam_arg = blk["scan"]["lambda"], name
    out = {
        "generated_utc": datetime.now(timezone.utc).isoformat(
            timespec="seconds"),
        "prereg": {"tag": "prereg-h1-v1.0", "commit": "277fc8b",
                   "spec": "phase1/CONFIRMATORY_PLAN.md"},
        "note": ("Observed statistics only. NO false-alarm probabilities: "
                 "the Section 6.2 calibration (>=1000 sims/family x full "
                 "search over all six pairs) is a deferred cluster job."),
        "config": {"p_min_d": FULL["p_min"],
                   "sigma_min_d": FULL["sigma_min"],
                   "tau_grid_d": FULL["tau_grid"],
                   "m1_kw": FULL["m1_kw"],
                   "merge_threshold_s": MERGE_S},
        "kernel_validation": gate,
        "reference_conversion_assert": ref,
        "campaigns": results,
        "study_wide": {"lambda_star": (float(lam_star) if lam_arg
                                       else None),
                       "campaign": lam_arg,
                       "n_campaigns_done": len(results),
                       "complete": len(results) == len(CAMPAIGNS)},
    }
    with open(OUT, "w") as f:
        json.dump(out, f, indent=1)
    return out


def main():
    import os
    from concurrent.futures import ProcessPoolExecutor, as_completed
    ap = argparse.ArgumentParser()
    ap.add_argument("--campaigns", default=None,
                    help="comma-separated subset (default: all six, "
                         "cheapest first)")
    ap.add_argument("--dry-run", action="store_true",
                    help="construct events/windows and print summaries; "
                         "no scan")
    ap.add_argument("--workers", type=int,
                    default=max(1, (os.cpu_count() or 3) - 2),
                    help="worker processes for independent scan units "
                         "(results identical at any worker count)")
    args = ap.parse_args()
    names = (args.campaigns.split(",") if args.campaigns
             else list(CAMPAIGNS))
    for n in names:
        assert n in CAMPAIGNS, f"unknown campaign {n}"

    pin = load_pin()
    ref = assert_reference_conversion(pin)
    print(f"[gate] reference conversion OK "
          f"(|err| = {ref['abs_err_d']:.2e} d)")

    if args.dry_run:
        for name in names:
            t, win, meta = build_campaign_inputs(name, pin)
            e, w = meta["events"], meta["windows"]
            c = w["containment"]
            print(f"{name}: rows={e['table_rows']} "
                  f"events={e['n_events']} merged_away="
                  f"{e['n_merged_away']} sessions={w['n_sessions']} "
                  f"sites={','.join(w['sites'])} "
                  f"span={win[1][-1] - win[0][0]:.2f} d "
                  f"edge_marginal={c['n_edge_marginal']} "
                  f"(max_excursion={c['max_excursion_s']:.2f} s)")
        return

    gate = check_validation_gate()
    print(f"[gate] kernel validation: {gate['result']}")

    ckpt = Ckpt(CKPT)
    inputs, units = {}, []
    for name in names:
        _record, done = ckpt.scoped(name)
        t, win, meta = build_campaign_inputs(name, pin)
        inputs[name] = (t, win, meta)
        span = float(win[1][-1] - win[0][0])
        u = pending_units(name, span, FULL, done)
        units.extend(u)
        print(f"[{name}] n_events={meta['events']['n_events']} "
              f"span={span:.1f} d pending_units={len(u)}", flush=True)
    units.sort(key=lambda u: -u[4])               # costliest first
    print(f"[pool] {len(units)} pending units on {args.workers} workers",
          flush=True)

    t0c = time.time()
    if units:
        with ProcessPoolExecutor(max_workers=args.workers) as ex:
            futs = {ex.submit(run_unit, u[:4]): u for u in units}
            n_done = 0
            for fut in as_completed(futs):
                key_args, val = fut.result()
                name, kind, idx, model_str = key_args
                record, _ = ckpt.scoped(name)
                record((kind, idx, model_str), val)
                n_done += 1
                print(f"[unit {n_done}/{len(units)}] {name} {kind} "
                      f"oct={idx} {model_str} wall="
                      f"{val['walltime_s']:.0f}s", flush=True)

    results = {}
    if OUT.exists():
        with open(OUT) as f:
            results = json.load(f).get("campaigns", {})
    for name in names:
        _record, done = ckpt.scoped(name)
        t, win, meta = inputs[name]
        scan = assemble_campaign(t, win, FULL, done)
        scan["peaks_ranked"] = flag_peaks(
            scan["peaks_ranked"], win, scan["span_days"],
            load_alias_artifact(name))
        results[name] = dict(meta, scan=scan)
        print(f"[{name}] Lambda = {scan['lambda']:.4f} "
              f"(ll: { {k: round(float(v), 3) for k, v in scan['ll'].items()} })",
              flush=True)
    out = assemble(results, pin, gate, ref)
    out["study_wide"]["pool_walltime_s"] = round(time.time() - t0c, 1)
    with open(OUT, "w") as f:
        json.dump(out, f, indent=1)
    sw = out["study_wide"]
    print(f"study-wide Lambda* = {sw['lambda_star']:.4f} "
          f"({sw['campaign']}); complete={sw['complete']}")


if __name__ == "__main__":
    main()
