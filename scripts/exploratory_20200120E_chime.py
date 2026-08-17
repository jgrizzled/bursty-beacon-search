"""Exploratory (non-confirmatory) analyses of the FRB 20200120E Λ*-driving
fit, recorded in phase0/deviations.md (2026-08-17) BEFORE the M5 stage-1
calibration run. Two analyses:

  A. Subharmonic decomposition of the effelsberg20200120E likelihood
     plateau: every ranked peak period is an integer subharmonic of the
     separation between the N31 storm and the N38 burst pair, and every
     peak's visits contain the same 53 events (51-burst storm core + the
     N38 double), relegating the other 16 bursts to the free background.

  B. Out-of-sample fold of the CHIME/FRB Catalog 2 bursts of the source
     through each non-alias-flagged peak's fitted (T, sigma_v, tau_c, t0),
     with the fitted-model prediction for the in-visit fraction.

Inputs: frozen repo artifacts (phase1/confirmatory_results.json,
phase1/windows/effelsberg20200120E_{bursts,sessions}.csv) plus the CHIME
Catalog 2 table (outside the frozen sample; integrated-only exposure, so
it cannot enter the confirmatory analysis under prereg S1):

  ~/chimefrb/catalog2/table/chimefrbcat2.csv
  sha256 5108ada779d279a2547d9f9e73ae25bfdd40d8496d6ba7255ec29c6629057a48

Usage: uv run python scripts/exploratory_20200120E_chime.py
"""

import csv
import json
import os
import sys

import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "phase1"))

from bary import get_location, topo_utc_to_bjd_tdb  # noqa: E402
import pipeline  # noqa: E402

CHIME_CSV = os.path.expanduser("~/chimefrb/catalog2/table/chimefrbcat2.csv")

# Frozen VLBI position (environment_pin.json)
RA_DEG, DEC_DEG = 149.47791395833332, 68.81690358333332


def load_effelsberg():
    res = json.load(open(os.path.join(REPO, "phase1/confirmatory_results.json")))
    camp = res["campaigns"]["effelsberg20200120E"]
    b = list(csv.DictReader(open(os.path.join(
        REPO, "phase1/windows/effelsberg20200120E_bursts.csv"))))
    te = np.array([float(r["toa_mjd_bary_tdb_inffreq"]) for r in b])
    sid = np.array([r["session_id"] for r in b])
    s = list(csv.DictReader(open(os.path.join(
        REPO, "phase1/windows/effelsberg20200120E_sessions.csv"))))
    loc = get_location("effelsberg")
    a = np.asarray(topo_utc_to_bjd_tdb(
        np.array([float(r["mjd_start_topo"]) for r in s]), loc, RA_DEG, DEC_DEG), float)
    bb = np.asarray(topo_utc_to_bjd_tdb(
        np.array([float(r["mjd_end_topo"]) for r in s]), loc, RA_DEG, DEC_DEG), float)
    o = np.argsort(a)
    return camp, te, sid, (a[o], bb[o])


def load_chime():
    """CHIME Cat2 rows with repeater_name FRB20200120E, excluded_flag == 0,
    topocentric infinite-frequency TOAs barycentered via the frozen path."""
    rows = [r for r in csv.DictReader(open(CHIME_CSV))
            if r["repeater_name"] == "FRB20200120E"]
    kept = [r for r in rows if r["excluded_flag"] == "0"]
    mjd = np.array([float(r["mjd_inf"]) for r in kept])
    bary = np.asarray(topo_utc_to_bjd_tdb(
        mjd, get_location("chime"), RA_DEG, DEC_DEG), float)
    return [r["tns_name"] for r in kept], bary, len(rows) - len(kept)


def main():
    camp, te, sid, win = load_effelsberg()
    tref = float(win[0][0])
    live = pipeline.live_time(win)
    peaks = camp["scan"]["peaks_ranked"]
    storm = sid == "N31"
    ts = np.sort(te[storm])
    n38_first = te[sid == "N38"].min()
    sep = n38_first - ts[0]

    print("=== A. Subharmonic decomposition (storm->N38 separation "
          f"{sep:.4f} d) ===")
    for p in peaks:
        T, sig, tau, t0 = (p["T_d"], p["sigma_v_d"], p["tau_c_d"], p["t0_d"])
        iv = [(0.0, sig)] if tau is None else [(0.0, sig), (tau, tau + sig)]
        n_in, m = pipeline.counts_in(te, T, tref + t0, iv)
        n = sep / T
        print(f"T={T:9.4f} d {p['model']}  sep/T={n:8.4f} "
              f"(n={round(n)}, dev {abs(n - round(n)) / n:6.2%})  "
              f"in-visit {n_in}/69 [storm-core {int((m & storm).sum())}, "
              f"N38 {int((m & (sid == 'N38')).sum())}]  "
              f"alias={p['alias_flag']}")

    names, bary, n_excl = load_chime()
    print(f"\n=== B. CHIME Cat2 out-of-sample fold ({len(names)} bursts, "
          f"{n_excl} excluded_flag row(s) dropped) ===")
    print("bursts:", ", ".join(f"{n}@{t:.4f}" for n, t in zip(names, bary)))
    for p in peaks:
        if p["alias_flag"]:
            continue
        if p["delta_ll_vs_natural_x2"] < 85.0:  # the would-be candidates
            continue
        T, sig, tau, t0 = (p["T_d"], p["sigma_v_d"], p["tau_c_d"], p["t0_d"])
        iv = [(0.0, sig)] if tau is None else [(0.0, sig), (tau, tau + sig)]
        e_in = pipeline.periodic_overlap(win, T, tref + t0, iv)
        n_in, _ = pipeline.counts_in(te, T, tref + t0, iv)
        lam_v, lam_b = n_in / e_in, (69 - n_in) / (live - e_in)
        duty = sig / T * len(iv)
        # Non-day-commensurate period => CHIME transit exposure is
        # phase-uniform; fitted-model in-visit probability per detection:
        odds = lam_v * duty / (lam_b * (1.0 - duty))
        p_in = odds / (1.0 + odds)
        k_in, _ = pipeline.counts_in(bary, T, tref + t0, iv)
        print(f"T={T:9.4f} d {p['model']}  duty={duty:6.3%}  "
              f"lam_v={lam_v:7.0f}/d lam_b={lam_b:4.2f}/d  "
              f"P(in-visit)={p_in:.2f}  observed {k_in}/{len(bary)}  "
              f"P(0/{len(bary)})={(1 - p_in) ** len(bary):.1e}")


if __name__ == "__main__":
    main()
