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
- effelsberg20200120E: composed from three sources under the frozen
  handling rules of data_manifest.md Section 1.7 (implemented in
  build_eff20200120E_*): Pearlman 2024 on-source UTC windows take
  precedence where they exist (Dec 2020 - May 2021); Kirsten 2022
  PRECISE run windows next (original report; includes the documented
  PR163A resolution); remaining sessions from Nimmo 2023 start+duration.
  Bursts are deduplicated by published ID with Pearlman's refined TOAs
  adopted for B1-B5. Session times topocentric UTC; burst TOAs
  barycentric TDB at infinite frequency as published.
"""

import csv
import hashlib
import json
import re
import sys
from collections import Counter
from datetime import datetime
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


# --- FRB 20200120E (Effelsberg) frozen composition --------------------------
# Implements the three frozen handling rules of data_manifest.md Section 1.7:
# (a) Pearlman-precedence session-window construction, with the PR163A
#     start/stop inconsistency explicitly resolved and documented;
# (b) cross-table burst deduplication by published ID, Pearlman refined TOAs
#     adopted where duplicated (B1-B5);
# (c) Kirsten's four non-Effelsberg PRECISE runs dropped (station and
#     on-source semantics not pinnable from the publication).

MJD_EPOCH = datetime(1858, 11, 17)

_MONTHS = {"January": 1, "February": 2, "March": 3, "April": 4, "May": 5,
           "June": 6, "July": 7, "August": 8, "September": 9, "October": 10,
           "November": 11, "December": 12}

PR163A_NOTE = (
    "Frozen resolution of the PR163A start/stop inconsistency: Kirsten 2022 "
    "logs PR163A as MJD 59347.417-59347.625; Nimmo 2023 lists a session "
    "starting 59347.625 (duration 4.99 hr), i.e. Nimmo's start equals "
    "Kirsten's stop, whereas in all ten other runs shared by both logs "
    "Nimmo's start equals Kirsten's start. Adopted: the Kirsten window "
    "(original PRECISE run report; the Nimmo table is a re-compilation "
    "citing it). Zero bursts under either reading; the rejected alternative "
    "(Nimmo) window 59347.625-59347.833 is recorded in this note and the "
    "choice shifts 5 h of burst-free exposure by 5 h.")


def _utc_to_mjd(s):
    return (datetime.strptime(s, "%Y-%m-%d %H:%M:%S")
            - MJD_EPOCH).total_seconds() / 86400.0


def parse_nimmo_sessions(src):
    """Nimmo et al. 2023 (arXiv:2206.03759) tab:observations: 42 Effelsberg
    sessions, topocentric start MJD + duration (hr) + type + burst count."""
    rows, region = [], False
    for line in src.read_text(errors="ignore").splitlines():
        if r"\label{tab:observations}" in line:
            region = True
            continue
        if region and r"\end{tabular}" in line:
            break
        if not region:
            continue
        m = re.match(
            r"^\s*\{(59\d{3}\.\d{3})(?:\$\\mathrm\{\^\{([a-z])\}\}\$)?\}\s*&"
            r"\s*\{([\d.]+)\}\s*&\s*\{([^}]*)\}\s*&\s*\{(\d+)\}", line)
        if m:
            start, flag, dur, typ, n = m.groups()
            rows.append({"idx": len(rows) + 1, "start": float(start),
                         "dur_hr": float(dur), "obs_type": typ,
                         "n_bursts": int(n), "flag": flag or ""})
    assert len(rows) == 42, f"Nimmo sessions: got {len(rows)}, expected 42"
    return rows


def parse_nimmo_bursts(src):
    """Nimmo et al. 2023 tab:burst_properties longtable: 60 bursts, TOA
    barycentric TDB MJD at infinite frequency (VLBI position, DM 87.7527).
    Burst IDs restart at B1 within each observing-day group."""
    rows, region, day = [], False, None
    for line in src.read_text(errors="ignore").splitlines():
        if r"\begin{longtable}" in line:
            region = True
            continue
        if region and r"\end{longtable}" in line:
            break
        if not region:
            continue
        m = re.search(r"\\multicolumn\{4\}\{l\}\{(\d{4})\\,(\w+)\\,(\d+)\}",
                      line)
        if m:
            day = (f"{m.group(1)}{_MONTHS[m.group(2)]:02d}"
                   f"{int(m.group(3)):02d}")
            continue
        m = re.match(r"^\s*(B\d+)(?:\$[^$]*\$)?\s*&\s*\{?([\d.]+)\}?\s*&",
                     line)
        if m and day:
            rows.append({"day": day, "bid": m.group(1), "toa": m.group(2)})
    assert len(rows) == 60, f"Nimmo bursts: got {len(rows)}, expected 60"
    return rows


def parse_kirsten_runs(src):
    """Kirsten et al. 2022 (arXiv:2105.11445) tab:all-precise-runs-on-m81:
    15 PRECISE runs, start/stop MJD (no per-run station assignment)."""
    rows, region = [], False
    for line in src.read_text(errors="ignore").splitlines():
        if "tab:all-precise-runs-on-m81" in line:
            region = True
            continue
        if region and r"\end{tabular}" in line:
            break
        if not region:
            continue
        m = re.match(r"^\s*(PR\d+A)(?:\$[^$]*\$)?\s*&\s*(EK\d+[A-Z])?\s*&"
                     r"\s*([\d.]+)\s*&\s*([\d.]+)", line)
        if m:
            rows.append({"code": m.group(1), "evn": m.group(2) or "",
                         "start": float(m.group(3)),
                         "stop": float(m.group(4))})
    assert len(rows) == 15, f"Kirsten runs: got {len(rows)}, expected 15"
    return rows


def parse_kirsten_bursts(src):
    """Kirsten et al. 2022 tab:pol_properties: B1-B5 TOAs (barycentric TDB
    infinite frequency, superseded position -- see Pearlman dedup)."""
    rows, region = [], False
    for line in src.read_text(errors="ignore").splitlines():
        if "tab:pol_properties" in line:
            region = True
            continue
        if region and r"\end{tabular}" in line:
            break
        if not region:
            continue
        m = re.match(r"^\s*(B\d)\s*&\s*([\d.]+)\s*&", line)
        if m:
            rows.append({"bid": m.group(1), "toa": m.group(2)})
    assert len(rows) == 5, f"Kirsten bursts: got {len(rows)}, expected 5"
    return rows


def parse_pearlman_log(src):
    """Pearlman et al. 2024 (arXiv:2308.10930) tab:radio_obs: 23 sessions
    (15 Effelsberg + 8 CHIME) with on-source UTC start/end + exposure.
    Computed window midpoints are validated against the published mid-time
    column, which also validates the UTC->MJD conversion."""
    rows, region = [], False
    for line in src.read_text(errors="ignore").splitlines():
        if "caption{Radio observations" in line:
            region = True
            continue
        if region and r"\label{tab:radio_obs}" in line:
            break
        if not region:
            continue
        clean = re.sub(r"\\textbf\{([^}]*)\}", r"\1", line)
        if not re.match(r"^\s*(Effelsberg|CHIME)\s*&", clean):
            continue
        clean = clean.split("%")[0].replace("\\\\", "").strip()
        c = [x.replace("~", " ").replace(r"\&", "&").strip()
             for x in re.split(r"(?<!\\)&", clean)]
        rows.append({"tel": c[0], "utc_start": c[1], "utc_end": c[2],
                     "mjd_mid_pub": float(c[3]), "exp_min": float(c[4]),
                     "backend": c[7], "n_bursts": int(c[8])})
    assert len(rows) == 23, f"Pearlman log: got {len(rows)}, expected 23"
    for r in rows:
        r["start"] = _utc_to_mjd(r["utc_start"])
        r["end"] = _utc_to_mjd(r["utc_end"])
        assert r["end"] > r["start"], r
        mid = 0.5 * (r["start"] + r["end"])
        assert abs(mid - r["mjd_mid_pub"]) < 2e-4, \
            f"mid-time check failed: {r['utc_start']} -> {mid}"
    return rows


def parse_pearlman_bursts(src):
    """Pearlman et al. 2024 tab:radio_burst_properties: B1-B9 refined TOAs
    (barycentric TDB MJD at infinite frequency, VLBI position, DE405)."""
    rows, region = [], False
    for line in src.read_text(errors="ignore").splitlines():
        if "caption{Measured properties" in line:
            region = True
            continue
        if region and r"\label{tab:radio_burst_properties}" in line:
            break
        if not region:
            continue
        m = re.match(r"^\s*(B\d)\s*&\s*([\d.]+)\s*&", line)
        if m:
            rows.append({"bid": m.group(1), "toa": m.group(2)})
    assert len(rows) == 9, f"Pearlman bursts: got {len(rows)}, expected 9"
    return rows


def _eff20200120E_sessions(srcs):
    """Compose the frozen Effelsberg FRB 20200120E session list (rule a)."""
    nimmo_tex, kirsten_tex, pearlman_tex = srcs
    nim = parse_nimmo_sessions(nimmo_tex)
    kir = parse_kirsten_runs(kirsten_tex)
    pearl = [r for r in parse_pearlman_log(pearlman_tex)
             if r["tel"] == "Effelsberg"]
    assert len(pearl) == 15, f"Pearlman Effelsberg rows: {len(pearl)} != 15"

    def nwin(n):
        return (n["start"], n["start"] + n["dur_hr"] / 24.0)

    def ov(a, b):
        return a[0] < b[1] and b[0] < a[1]

    sessions = []
    # Precedence 1: Pearlman on-source windows (Dec 2020 - May 2021).
    for i, p in enumerate(pearl, 1):
        sup_n = [n for n in nim if ov((p["start"], p["end"]), nwin(n))]
        sup_k = [k for k in kir if ov((p["start"], p["end"]),
                                      (k["start"], k["stop"]))]
        assert len(sup_n) <= 1 and len(sup_k) <= 1, (p, sup_n, sup_k)
        for n in sup_n:
            # burst counts must agree between the two logs for one session
            assert n["n_bursts"] == p["n_bursts"], (n, p)
            n["consumed"] = True
        for k in sup_k:
            k["consumed"] = True
        sup = ("; supersedes " + ", ".join(
            [f"Nimmo row {n['idx']} (start {n['start']}, {n['dur_hr']} hr)"
             for n in sup_n]
            + [f"Kirsten {k['code']} ({k['start']}-{k['stop']})"
               for k in sup_k])) if (sup_n or sup_k) \
            else "; session absent from Nimmo and Kirsten logs"
        sessions.append({
            "session_id": f"P{i:02d}",
            "mjd_start": f"{p['start']:.6f}", "mjd_end": f"{p['end']:.6f}",
            "utc_start": p["utc_start"], "utc_end": p["utc_end"],
            "on_source_min": p["exp_min"], "dur_pub": "",
            "backend": p["backend"], "n_bursts": p["n_bursts"],
            "source": "pearlman2024_tab_radio_obs",
            "rule": "pearlman_precedence",
            "notes": "on-source UTC window (Pearlman 2024)" + sup,
            "_start": p["start"], "_end": p["end"]})

    # Precedence 2: Kirsten PRECISE runs not covered by Pearlman.
    # Effelsberg-pinned iff the run overlaps a Nimmo (Effelsberg-only) row;
    # PR163A pinned via the documented adjacency resolution.
    dropped = []
    for k in kir:
        if k.get("consumed"):
            continue
        if k["code"] == "PR163A":
            adj = [n for n in nim if abs(n["start"] - k["stop"]) < 5e-4]
            assert len(adj) == 1 and adj[0]["n_bursts"] == 0, adj
            adj[0]["consumed"] = True
            sessions.append({
                "session_id": "PR163A",
                "mjd_start": f"{k['start']:.3f}",
                "mjd_end": f"{k['stop']:.3f}",
                "utc_start": "", "utc_end": "", "on_source_min": "",
                "dur_pub": adj[0]["dur_hr"], "backend": adj[0]["obs_type"],
                "n_bursts": 0, "source": "kirsten2022_tab_precise_runs",
                "rule": "pr163a_resolution_kirsten_primary",
                "notes": PR163A_NOTE,
                "_start": k["start"], "_end": k["stop"]})
            continue
        sup_n = [n for n in nim if not n.get("consumed")
                 and ov((k["start"], k["stop"]), nwin(n))]
        if not sup_n:
            dropped.append(k["code"])
            continue
        assert len(sup_n) == 1, (k, sup_n)
        n = sup_n[0]
        n["consumed"] = True
        sessions.append({
            "session_id": k["code"],
            "mjd_start": f"{k['start']:.3f}", "mjd_end": f"{k['stop']:.3f}",
            "utc_start": "", "utc_end": "", "on_source_min": "",
            "dur_pub": n["dur_hr"], "backend": n["obs_type"],
            "n_bursts": n["n_bursts"],
            "source": "kirsten2022_tab_precise_runs",
            "rule": "kirsten_primary",
            "notes": (f"PRECISE run window (original report; matches Nimmo "
                      f"row {n['idx']}); VLBI run interleaves calibrators, "
                      f"on-source ~65% of span (Nimmo 2023 text); no "
                      f"on-source log available"),
            "_start": k["start"], "_end": k["stop"]})
    assert sorted(dropped) == ["PR160A", "PR162A", "PR164A", "PR165A"], \
        f"unexpected non-Effelsberg drop set: {dropped}"

    # Precedence 3: remaining Nimmo sessions, start + duration.
    for n in nim:
        if n.get("consumed"):
            continue
        start, end = nwin(n)
        note = "start+duration from Nimmo 2023 tab:observations"
        if "PRECISE" in n["obs_type"]:
            note += ("; VLBI run interleaves calibrators, on-source ~65% of "
                     "duration (Nimmo 2023 text); no on-source log available")
        if n["flag"] == "c":
            note += "; frequency resolution 0.4 MHz"
        if n["flag"] == "d":
            note += "; no raw voltages (incorrect observing set-up)"
        sessions.append({
            "session_id": f"N{n['idx']:02d}",
            "mjd_start": f"{n['start']:.3f}", "mjd_end": f"{end:.6f}",
            "utc_start": "", "utc_end": "", "on_source_min": "",
            "dur_pub": n["dur_hr"], "backend": n["obs_type"],
            "n_bursts": n["n_bursts"], "source": "nimmo2023_tab_observations",
            "rule": "nimmo_only", "notes": note,
            "_start": start, "_end": end})

    sessions.sort(key=lambda s: s["_start"])
    assert sum(s["n_bursts"] for s in sessions) == 69, \
        f"total bursts {sum(s['n_bursts'] for s in sessions)} != 69"
    return sessions


def build_eff20200120E_sessions(srcs):
    header = ["session_id", "mjd_start_topo", "mjd_end_topo", "utc_start",
              "utc_end", "on_source_min", "published_duration_hr", "backend",
              "n_bursts", "window_source", "window_rule", "notes"]
    rows = [[s["session_id"], s["mjd_start"], s["mjd_end"], s["utc_start"],
             s["utc_end"], s["on_source_min"], s["dur_pub"], s["backend"],
             s["n_bursts"], s["source"], s["rule"], s["notes"]]
            for s in _eff20200120E_sessions(srcs)]
    return header, rows


def build_eff20200120E_bursts(srcs):
    """Frozen FRB 20200120E burst list (rule b): 69 unique bursts = Pearlman
    B1-B9 (refined TOAs; B1-B5 deduplicated against Kirsten 2022 / Nimmo
    2022 by published ID) + Nimmo 2023's 60 storm-era bursts."""
    nimmo_tex, kirsten_tex, pearlman_tex = srcs
    sessions = _eff20200120E_sessions(srcs)
    nb = parse_nimmo_bursts(nimmo_tex)
    kb = {b["bid"]: b for b in parse_kirsten_bursts(kirsten_tex)}
    pb = parse_pearlman_bursts(pearlman_tex)

    def find_session(toa):
        # published TOAs are barycentric TDB, session windows topocentric
        # UTC; the offset is bounded by ~+-0.007 d (Roemer delay + TDB-UTC),
        # so containment is tested with a 0.01 d tolerance and must be
        # unique. Harmonization happens in the analysis pipeline.
        cand = [s for s in sessions
                if s["_start"] - 0.01 <= toa <= s["_end"] + 0.01]
        assert len(cand) == 1, (toa, [c["session_id"] for c in cand])
        return cand[0]

    rows = []
    for b in pb:
        s = find_session(float(b["toa"]))
        sup = kb.pop(b["bid"], None)
        shift = ""
        note = ("adopted TOA: Pearlman 2024 refined re-barycentring "
                "(corrected VLBI position, DE405, TDB, infinite frequency)")
        if sup is not None:
            shift = f"{(float(b['toa']) - float(sup['toa'])) * 86400e3:.3f}"
            assert 0.5 < abs(float(shift)) < 20, \
                f"{b['bid']}: unexpected TOA shift {shift} ms"
            note += ("; deduplicated by published burst ID against Kirsten "
                     "2022 tab:pol_properties (and Nimmo 2022), which used "
                     "a superseded source position; superseded TOA recorded")
        rows.append([b["bid"], b["toa"],
                     "pearlman2024_tab_radio_burst_properties",
                     s["session_id"], sup["toa"] if sup else "", shift, note])
    assert not kb, f"Kirsten bursts without Pearlman counterpart: {list(kb)}"
    for b in nb:
        s = find_session(float(b["toa"]))
        rows.append([f"{b['day']}-{b['bid']}", b["toa"],
                     "nimmo2023_tab_burst_properties", s["session_id"],
                     "", "",
                     "TOA barycentric TDB at infinite frequency "
                     "(VLBI position, DM 87.7527)"])
    assert len(rows) == 69, f"burst rows {len(rows)} != 69"
    tally = Counter(r[3] for r in rows)
    for s in sessions:
        assert tally.get(s["session_id"], 0) == s["n_bursts"], \
            (s["session_id"], tally.get(s["session_id"], 0), s["n_bursts"])
    header = ["burst_id", "toa_mjd_bary_tdb_inffreq", "source_table",
              "session_id", "toa_mjd_kirsten2022_superseded",
              "toa_shift_ms", "notes"]
    return header, rows


EFF20200120E_SRCS = (
    RAW / "arxiv_sources/src_2206.03759/paper_mnras.tex",
    RAW / "arxiv_sources/src_2105.11445/main.tex",
    RAW / "arxiv_sources/src_2308.10930/preprint.tex",
)

NOTES = {
    "effelsberg20200120E_sessions.csv": (
        "Composed under the frozen handling rules of data_manifest.md 1.7: "
        "(a) precedence Pearlman on-source UTC windows > Kirsten PRECISE run "
        "windows > Nimmo start+duration, applied where windows overlap; "
        "15 Pearlman + 3 Kirsten-only (PR161A, PR163A with the documented "
        "start/stop resolution, PR166A) + 28 Nimmo-only = 46 sessions. "
        "(c) Kirsten runs PR160A/PR162A/PR164A/PR165A dropped: they appear "
        "in no Effelsberg log and the publication does not pin their "
        "station or on-source semantics (conservative drop per manifest "
        "1.7c). Pearlman adds 4 sessions absent from Nimmo's log, including "
        "the 2021-04-30 EDD session containing bursts B6-B9."),
    "effelsberg20200120E_bursts.csv": (
        "69 unique bursts: Pearlman B1-B9 (B1-B5 deduplicated by published "
        "ID against Kirsten 2022/Nimmo 2022; Pearlman's re-barycentred TOAs "
        "adopted, superseded Kirsten TOAs and the 1-5 ms shifts recorded) "
        "plus Nimmo 2023's 60 bursts (IDs prefixed with observing date; "
        "no cross-table duplication exists for these). 53 of 69 lie in the "
        "single 2022-01-14 storm session (statistical-power caveat, "
        "manifest 1.7)."),
}


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
    ("effelsberg20200120E_sessions.csv", build_eff20200120E_sessions,
     EFF20200120E_SRCS, 46),
    ("effelsberg20200120E_bursts.csv", build_eff20200120E_bursts,
     EFF20200120E_SRCS, 69),
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
        srcs = src if isinstance(src, tuple) else (src,)
        prov["outputs"][out_name] = {
            "source": (str(srcs[0].relative_to(ROOT)) if len(srcs) == 1
                       else [str(s.relative_to(ROOT)) for s in srcs]),
            "source_sha256": (sha256(srcs[0]) if len(srcs) == 1
                              else [sha256(s) for s in srcs]),
            "rows": n, "expected_rows": expected,
            "output_sha256": sha256(OUT / out_name),
        }
        if out_name in NOTES:
            prov["outputs"][out_name]["construction"] = NOTES[out_name]
        print(f"{out_name}: {n} rows [{status}]")
    with open(OUT / "PROVENANCE.json", "w") as f:
        json.dump(prov, f, indent=2)
    print(f"PROVENANCE.json written; {failures} failures")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
