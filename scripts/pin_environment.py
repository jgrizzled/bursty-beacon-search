#!/usr/bin/env python3
"""Pin the H1 software environment (prereg_h1.md freeze checklist; manifest
Section 6): package versions, the DE440 ephemeris file hash, the astropy
sites registry content hash and resolved observatory coordinates, and the
frozen supplementary station coordinates of phase1/bary.py.

Exercises the real conversion path (phase1.bary.topo_utc_to_bjd_tdb) so the
hashed ephemeris file is the one the confirmatory run will load, and
records a reference conversion (Effelsberg -> FRB 20200120E VLBI position)
as a regression anchor for the full-scale run.

Output: phase0/environment_pin.json (committed freeze artifact).
"""

import hashlib
import json
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "phase1"))


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    import astropy
    import erfa
    import numpy
    import scipy
    from astropy.coordinates import solar_system_ephemeris
    from astropy.utils.data import download_file

    import bary

    pin = {
        "recorded_utc": datetime.now(timezone.utc).isoformat(
            timespec="seconds"),
        "platform": platform.platform(),
        "python": sys.version.split()[0],
        "packages": {"astropy": astropy.__version__,
                     "erfa": erfa.__version__,
                     "numpy": numpy.__version__,
                     "scipy": scipy.__version__},
        "lockfiles": ["uv.lock", "phase0/requirements-lock.txt"],
    }

    # Solar-system ephemeris: force the load through the real code path,
    # then hash the kernel file astropy actually resolved.
    with solar_system_ephemeris.set(bary.EPHEMERIS):
        kernel = solar_system_ephemeris.kernel
    kpath = Path(kernel.daf.file.name)
    pin["ephemeris"] = {
        "name": bary.EPHEMERIS,
        "kernel_file_resolved": str(kpath),
        "size_bytes": kpath.stat().st_size,
        "sha256": sha256(kpath),
    }

    # Sites registry: hash the sites.json astropy downloads, and record the
    # resolved geocentric coordinates for every registry site we use.
    sites_path = Path(download_file(
        "http://data.astropy.org/coordinates/sites.json", cache=True))
    pin["sites_registry"] = {
        "url": "http://data.astropy.org/coordinates/sites.json",
        "sha256": sha256(sites_path),
        "resolved_sites_itrf_m": {},
    }
    for site in ["FAST", "effelsberg", "nancay", "chime", "parkes"]:
        loc = bary.get_location(site)
        x, y, z = (float(v.value) for v in loc.geocentric)
        pin["sites_registry"]["resolved_sites_itrf_m"][site] = [x, y, z]

    # Frozen supplementary coordinates (observatories absent from the
    # registry), as recorded in phase1/bary.py with provenance.
    supp = {k: list(v) for k, v in bary.SUPPLEMENTARY_XYZ_M.items()}
    stk = bary.get_location("stockert")
    supp["stockert"] = [float(v.value) for v in stk.geocentric]
    pin["supplementary_sites_itrf_m"] = {
        "values": supp,
        "provenance": ("NRAO SCHED locations.dat (GSF2016a; Torun ITRF2000);"
                       " Westerbork RT0 as RT-1 proxy (<1 us); Stockert from"
                       " published geodetic position (see phase1/bary.py)"),
        "error_bound_note": ("observatory-position error affects the "
                             "barycentric conversion by <= ~21 ms "
                             "(Earth-radius light time), vs sigma_v,min "
                             "= 60 s"),
    }

    # Reference conversion (regression anchor): Effelsberg, FRB 20200120E
    # VLBI position (09h57m54.69935s +68d49'00.8529", Kirsten et al. 2022),
    # topocentric MJD 59593.650 (storm-session start).
    ra = (9 + 57 / 60 + 54.69935 / 3600) * 15.0
    dec = 68 + 49 / 60 + 0.8529 / 3600
    bjd = bary.topo_utc_to_bjd_tdb(59593.650, bary.get_location(
        "effelsberg"), ra, dec)
    pin["reference_conversion"] = {
        "site": "effelsberg", "ra_deg": ra, "dec_deg": dec,
        "mjd_utc_topo": 59593.650, "bjd_tdb_inf_freq": float(bjd),
        "note": ("FRB 20200120E storm-session start; the full-scale run "
                 "asserts this value to 1e-8 d before converting windows"),
    }

    pin["repository_commit"] = "[recorded at tag]"

    out = ROOT / "phase0" / "environment_pin.json"
    with open(out, "w") as f:
        json.dump(pin, f, indent=1)
    print(json.dumps({k: pin[k] for k in ("packages", "ephemeris",
                                          "reference_conversion")},
                     indent=1))
    print(f"written: {out}")


if __name__ == "__main__":
    main()
