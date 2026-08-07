#!/usr/bin/env python3
"""Extract frozen H1 session logs (window functions W(t)) from the raw data
products recorded in phase0/data_manifest.md, into phase1/windows/.

Each output CSV is one confirmatory campaign's observing-session log, kept
close to the source structure (harmonization happens in the analysis
pipeline, not here). A PROVENANCE.json sidecar records the sha256 of every
input and output, row counts, and the source table identity, satisfying the
hashed-extraction-script requirement of prereg_h1.md Sections 3.2 and 8.

Session-log conventions preserved from each source (do not "fix" here):
- fast20201124A_sepoct: topocentric UTC start + duration (Niu et al. 2022 Table 1)
- fast20240114A_zhou111: topocentric MJD start/end corrected to infinite
  frequency (Zhou et al. 2025 Table 3)
- fast20240114A_zhang57: same convention, 57 sessions with per-session
  config (Zhang et al. 2025 Supp. Table 1)
- nancay20220912A: topocentric MJD start + integration seconds, filtered to
  the FRB 20220912A pointing (2309+4842) from the multi-target ECLAT log
- astroflash20220912A: per-session mjd_start/mjd_end per station (copied
  verbatim from r117_camp_reduced.csv)
- tmrt20240114A: topocentric UTC start + duration from the ApJ MRT
"""

import csv
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
OUT = ROOT / "phase1" / "windows"


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def write_csv(path, header, rows):
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)
    return len(rows)


def latex_cells(line):
    line = line.split("%")[0]
    line = line.replace(r"\\", "").strip()
    return [c.strip().rstrip("$").lstrip("$") for c in line.split("&")]


def extract_zhou111(src):
    """Zhou et al. 2025 (arXiv:2507.14708) Table 3: 111 FAST sessions."""
    rows = []
    in_table = False
    for line in src.read_text(errors="ignore").splitlines():
        if r"\begin{longtable}" in line:
            in_table = True
            continue
        if r"\end{longtable}" in line:
            in_table = False
            continue
        if in_table and re.match(r"^\s*\d{8}\s*&", line):
            c = latex_cells(line)
            # date, mjd_start, mjd_end, duration_hr, n_bursts, rate_per_hr
            rows.append([c[0], c[1], c[2], c[3], c[4], c[5]])
    return ["date_ut", "mjd_start_topo_inffreq", "mjd_end_topo_inffreq",
            "duration_hr", "n_bursts", "rate_per_hr"], rows


def extract_zhang57(src):
    """Zhang et al. 2025 (arXiv:2507.14707) Supp. Table 1: 57 FAST sessions
    with per-session config."""
    rows = []
    for line in src.read_text(errors="ignore").splitlines():
        if re.match(r"^\s*\d{8}\s*&", line):
            c = latex_cells(line)
            # date, mjd_start, mjd_end, freq_res_khz, tsamp_us, duration_hr,
            # n_detections, rate
            rows.append([c[0], c[1], c[2], c[3], c[4], c[5], c[6], c[7]])
    return ["date_ut", "mjd_start_topo_inffreq", "mjd_end_topo_inffreq",
            "freq_res_khz", "tsamp_us", "duration_hr", "n_bursts",
            "rate_per_hr"], rows


def extract_niu18(src):
    """Niu et al. 2022 (arXiv:2210.03610) Table 1: 18 FAST sessions,
    FRB 20201124A Sep-Oct 2021."""
    rows = []
    for line in src.read_text(errors="ignore").splitlines():
        m = re.match(
            r"^\s*(\d{4}-\d{2}-\d{2})\s*&\s*(\d{2}:\d{2}:\d{2})\s*&"
            r"\s*([\d.]+)\s*&\s*(\d+)\s*&\s*(\d+)", line.replace(r"\\", ""))
        if m:
            rows.append(list(m.groups()))
    return ["date_ut", "utc_start", "mjd_start_topo", "duration_s",
            "n_pulses"], rows


def extract_tmrt(src):
    """Wang et al. 2025 ApJ MRT (apjadfecet2_mrt.txt): 66 TMRT sessions.
    Fixed-width parse driven by the MRT byte-range descriptor."""
    lines = src.read_text(errors="ignore").splitlines()
    fields = []
    seps = [i for i, l in enumerate(lines) if re.match(r"^-{20,}", l)]
    for l in lines[: seps[-1]]:
        m = re.match(r"^\s*(\d+)\s*-\s*(\d+)\s+\S+\s+\S+\s+(\S+)", l)
        if m:
            fields.append((int(m.group(1)) - 1, int(m.group(2)), m.group(3)))
    rows = []
    for l in lines[seps[-1] + 1:]:
        if not l.strip():
            continue
        rows.append([l[a:b].strip() for a, b, _ in fields])
    return [n for _, _, n in fields], rows


def extract_nancay(src):
    """Konijn et al. 2024 'Observation times.txt', filtered to the
    FRB 20220912A pointing (2309+4842)."""
    rows = []
    for line in src.read_text(errors="ignore").splitlines():
        if "_2309+4842_" not in line:
            continue
        p = line.split()
        scan_id, mjd_start, dur_s = p[0], float(p[1]), float(p[2])
        rows.append([scan_id, f"{mjd_start:.6f}", dur_s,
                     f"{mjd_start + dur_s / 86400.0:.6f}"])
    return ["scan_id", "mjd_start_topo", "duration_s", "mjd_end_topo"], rows


def extract_astroflash(src):
    """Ould-Boukattine et al. 2025 r117_camp_reduced.csv, verbatim columns."""
    with open(src, newline="") as f:
        r = list(csv.reader(f))
    header, rows = r[0], r[1:]
    header[0] = "row_index"
    return header, rows


def extract_zhou2022_bursts(src):
    """Zhou et al. 2022 (arXiv:2210.03607) Table A.1: FRB 20201124A Sep 2021
    burst/sub-burst rows (TOA barycentric MJD at infinite frequency, DE438,
    per the paper). Day-group \\multicolumn headers carry the session date."""
    rows = []
    day = ""
    for line in src.read_text(errors="ignore").splitlines():
        m = re.search(r"\\multicolumn\{10\}\{c\}\{(\d{8}):", line)
        if m:
            day = m.group(1)
            continue
        if re.match(r"^\s*\d+\s*&", line):
            c = latex_cells(line)
            if len(c) == 10:
                rows.append([day] + c)
    return ["session_date", "burst_no", "toa_mjd_bary_inffreq", "nu_low_mhz",
            "nu_0_mhz", "nu_high_mhz", "bw_mhz", "w_sb_ms", "snr",
            "fluence_mjy_ms", "group"], rows


def extract_chime20180916B(src):
    """CHIME/FRB 2020 (arXiv:2001.10275) Extended Data Table 1: 28 bursts of
    FRB 20180916B (TOA barycentric MJD at infinite frequency, EVN position).
    POSITIVE CONTROL."""
    rows = []
    in_toa_table = False
    for line in src.read_text(errors="ignore").splitlines():
        if line.lstrip().startswith("%"):
            continue
        if "Best-fit parameters" in line:
            in_toa_table = True
        if in_toa_table and r"\end{table}" in line:
            break
        if not in_toa_table:
            continue
        m = re.match(r"^\s*(\d+)\s*&\s*([\d.]+)(?:\$\^\\ast\$)?\s*&\s*"
                     r"([\d.]+)", line)
        if m:
            rows.append(list(m.groups()))
    return ["burst_no", "toa_mjd_bary_inffreq", "dm_pccm3"], rows


def extract_cruces_sessions(src):
    """Cruces et al. 2021 (arXiv:2008.03461) Table 1: FRB 20121102A follow-up
    sessions (EFF/AO/GBT), UTC start + duration + event count, 2017-2020.
    POSITIVE CONTROL."""
    rows = []
    for line in src.read_text(errors="ignore").splitlines():
        m = re.match(
            r"^\s*(EFF|AO|GBT)\s*&\s*(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}(?::\d{2})?)"
            r"\s*&\s*(\d+)\s*&\s*(\d+)", line.replace(r"\\", ""))
        if m:
            rows.append(list(m.groups()))
    return ["telescope", "utc_start", "duration_s", "n_events"], rows


def extract_cruces_bursts(src):
    """Cruces et al. 2021 Table 2: 36 Effelsberg bursts of FRB 20121102A
    (MJD, topocentric-to-barycentric convention per paper). POSITIVE CONTROL."""
    rows = []
    for line in src.read_text(errors="ignore").splitlines():
        m = re.match(r"^\s*B(\d+)\s*&\s*([\d.]+)\s*&", line)
        if m:
            rows.append(list(m.groups()))
    return ["burst_no", "toa_mjd"], rows


JOBS = [
    ("fast20240114A_zhou111_sessions.csv", extract_zhou111,
     RAW / "arxiv_sources/src_2507.14708/2023-SCIYG-for_author.tex", 111),
    ("fast20240114A_zhang57_sessions.csv", extract_zhang57,
     RAW / "arxiv_sources/src_2507.14707/obs_inf.tex", 57),
    ("fast20201124A_sepoct_sessions.csv", extract_niu18,
     RAW / "arxiv_sources/src_2210.03610/table12.tex", 18),
    ("tmrt20240114A_sessions.csv", extract_tmrt,
     RAW / "tmrt_20240114A/apjadfecet2_mrt.txt", 66),
    ("nancay20220912A_sessions.csv", extract_nancay,
     RAW / "nancay_20220912A/Observation times.txt", 68),
    ("astroflash20220912A_sessions.csv", extract_astroflash,
     RAW / "astroflash_20220912A/r117_camp_reduced.csv", 508),
    ("fast20201124A_sepoct_bursts.csv", extract_zhou2022_bursts,
     RAW / "arxiv_sources/src_2210.03607/Tex/tab_each_burst.tex", None),
    # 38 sub-burst rows = CHIME's 28 bursts (their per-event grouping spans
    # >100 ms); our frozen 100 ms rule yields 35 events — convention
    # difference recorded in data_manifest.md Section 2.1.
    ("control_chime20180916B_toas.csv", extract_chime20180916B,
     RAW / "positive_controls/src_2001.10275/extended_data.tex", 38),
    ("control_cruces121102_sessions.csv", extract_cruces_sessions,
     RAW / "positive_controls/src_2008.03461/main.tex", None),
    ("control_cruces121102_bursts.csv", extract_cruces_bursts,
     RAW / "positive_controls/src_2008.03461/main.tex", 36),
]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    prov = {"script": "scripts/extract_session_logs.py",
            "script_sha256": sha256(__file__), "outputs": {}}
    failures = 0
    for out_name, fn, src, expected in JOBS:
        header, rows = fn(src)
        n = write_csv(OUT / out_name, header, rows)
        if expected is None:
            status = "OK (no fixed expectation; count recorded)"
        elif n == expected:
            status = "OK"
        else:
            status = f"MISMATCH (expected {expected})"
            failures += 1
        prov["outputs"][out_name] = {
            "source": str(src.relative_to(ROOT)),
            "source_sha256": sha256(src),
            "rows": n, "expected_rows": expected,
            "output_sha256": sha256(OUT / out_name),
        }
        print(f"{out_name}: {n} rows [{status}]")
    with open(OUT / "PROVENANCE.json", "w") as f:
        json.dump(prov, f, indent=2)
    print(f"PROVENANCE.json written; {failures} failures")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
