#!/usr/bin/env python3
"""Export the frozen calibration inputs (prereg_h1 Section 6.2 support).

Writes phase1/calibration_inputs/: per campaign, the constructed
confirmatory event list (barycentric MJD + burst id) and the barycentred
window function, plus INPUTS.json with provenance (source checksums,
construction code SHA, per-campaign counts, and the converted-window
SHA-256 that must match phase1/confirmatory_results.json).

Purpose: the Section 6.2 calibration re-derives nothing from data/raw --
simulation and scanning need only (events, windows). Committing these
derived inputs makes cluster hosts independent of the raw downloads and
of astropy (the barycentric conversion happens exactly once, here), and
gives single-machine replicators a self-contained starting point.

The event times are cross-checked against confirmatory.build_campaign_inputs
(exact equality) so this export cannot drift from the scan's construction.
"""

import csv
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "phase1"))
import bary  # noqa: E402
import confirmatory as cf  # noqa: E402

OUT = ROOT / "phase1" / "calibration_inputs"


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    OUT.mkdir(exist_ok=True)
    pin = cf.load_pin()
    ref = cf.assert_reference_conversion(pin)
    manifest = {
        "generated_utc": datetime.now(timezone.utc).isoformat(
            timespec="seconds"),
        "prereg": {"tag": "prereg-h1-v1.0",
                   "purpose": "Section 6.2 calibration inputs"},
        "construction": "phase1/confirmatory.py build_campaign_inputs "
                        "(frozen event rules, prereg 2.1/2.2; exact-equality "
                        "cross-check asserted at export)",
        "code_sha256": {
            "confirmatory.py": sha256_file(ROOT / "phase1" /
                                           "confirmatory.py"),
            "export_script": sha256_file(__file__),
        },
        "reference_conversion_assert": ref,
        "campaigns": {},
    }
    for name in cf.CAMPAIGNS:
        # Reference construction (times + windows + meta).
        t_ref, (a, b), meta = cf.build_campaign_inputs(name, pin)

        # Independent id-carrying reconstruction, asserted equal.
        ev_fn, win_fn, poskey = cf.CAMPAIGNS[name]
        if poskey == "20200120E":
            rc = pin["reference_conversion"]
            ra, dec = rc["ra_deg"], rc["dec_deg"]
        else:
            ra, dec = cf.sex_to_deg(*cf.POSITIONS_SEX[poskey])
        toa, weight, ids, ev_meta = ev_fn()
        site_edges, _win_file = win_fn()
        if ev_meta.get("toa_frame") == "topo_utc":
            sites = {s for s, _, _ in site_edges}
            loc = bary.get_location(next(iter(sites)))
            toa = bary.topo_utc_to_bjd_tdb(np.asarray(toa, float), loc,
                                           ra, dec)
        t_all, _n_merged, ev_ids = cf.merge_events(toa, weight, ids)
        keep = np.isin(t_all, t_ref)
        t, ev_ids = t_all[keep], [i for i, k in zip(ev_ids, keep) if k]
        assert len(t) == len(t_ref) and np.array_equal(
            np.sort(t), np.sort(t_ref)), f"{name}: construction mismatch"

        with open(OUT / f"{name}_events.csv", "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["event_id", "toa_mjd_bary"])
            for i, x in zip(ev_ids, t):
                w.writerow([i, f"{float(x):.12f}"])
        with open(OUT / f"{name}_windows.csv", "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["mjd_start_bary", "mjd_end_bary"])
            for aj, bj in zip(a, b):
                w.writerow([f"{float(aj):.12f}", f"{float(bj):.12f}"])
        manifest["campaigns"][name] = {
            "n_events": int(len(t)),
            "n_sessions": int(len(a)),
            "span_days": float(b[-1] - a[0]),
            "events_file": f"{name}_events.csv",
            "events_sha256": sha256_file(OUT / f"{name}_events.csv"),
            "windows_file": f"{name}_windows.csv",
            "windows_sha256": sha256_file(OUT / f"{name}_windows.csv"),
            "converted_window_sha256_float64":
                meta["windows"]["converted_window_sha256"],
            "window_source": meta["windows"]["window_file"],
            "window_source_sha256": meta["windows"]["window_file_sha256"],
            "excluded_outside_windows": meta["events"].get(
                "excluded_outside_windows", {}).get("n", 0),
            "notes": "CSV times rounded to 1e-12 d (~86 ns), five orders "
                     "below sigma_v,min; the float64 window checksum above "
                     "is the confirmatory-scan artifact cross-reference",
        }
        print(f"{name}: {len(t)} events, {len(a)} sessions exported")
    with open(OUT / "INPUTS.json", "w") as f:
        json.dump(manifest, f, indent=1)
    print(f"manifest: {OUT / 'INPUTS.json'}")


if __name__ == "__main__":
    main()
