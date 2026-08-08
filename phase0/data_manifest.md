# Data Manifest

_Freeze artifact required by [prereg_h1.md](prereg_h1.md) Section 8 and [preregistration.md](preregistration.md) Section 3. Nothing in this manifest is frozen until the corresponding tag (`prereg-h1-v1.0` for Section 1–2, `prereg-h2h3h4-v1.0` for Sections 3–5) exists. Fields marked **[pending]** must be completed — by downloading and hashing the file, or by schema inspection under the pre-freeze inspection policy — before the tag is created._

_Scope: public data only. Collaboration-gated products are excluded from this manifest entirely; they are listed for planning purposes in [data_product_matrix.md](data_product_matrix.md) and deferred to the post-project follow-up phase of [../notes/project_plan.md](../notes/project_plan.md)._

## Required fields per entry

Every data file entry must record: URL/DOI · exact filename(s) · version/release date · size · SHA-256 checksum · license · schema (column definitions, units) · time standard and reference frequency (for tables containing times) · target vs. positive-control vs. calibration vs. development-control status · whether the file was inspected before freeze, and why that inspection was permitted (schema/availability verification only).

For observing-log tables (H1), additionally: UTC start/stop of every session · session identifier · live/dead state · applied quality, commissioning, and sensitivity masks · instrument and pipeline configuration epochs · provenance (paper table, machine-readable supplement, or reconstruction code with its own hash).

---

## 1. H1 confirmatory candidates (pending verification against prereg_h1 S1–S5)

Status legend: candidate = named for verification; verified = meets S1–S5 with all fields complete; excluded = failed verification (reason recorded, entry retained).

### Verification summary (2026-08-07)

Live-web verification of all candidates was performed by parallel research passes on 2026-08-07. Outcome: **the restricted-sample route survives comfortably** — five source–campaign pairs are verified across three sources: 1.1b FAST 20201124A Sep–Oct (admitted under the revised S3 recorded in prereg_h1 Section 3.1), 1.2a Nançay 20220912A, 1.2c AstroFlash 20220912A, 1.3 FAST 20240114A, and 1.5 TMRT 20240114A. Two sources thus have independent-window campaign pairs (20220912A: Nançay+AstroFlash; 20240114A: FAST+TMRT), enabling the alias-clearing route of prereg_h1 Section 5.4 without any new data. Exclusions: 1.1a FAST 20201124A Apr–Jun and 1.2b FAST 20220912A (no session logs, both exhaustively checked); 1.4 Parkes 20240114A (burst-table provenance inadequate and window half-embargoed — excluded from confirmatory, designated exploratory; see 1.4 for the recorded decision). **The Section 1 verification pass is complete; no open sample decisions remain.** Recurring findings to handle at freeze: session logs typically live in in-paper tables (LaTeX/PDF) rather than data repositories, so frozen extraction scripts with hashes are required; and time conventions are heterogeneous across releases (topocentric vs. barycentric; 1.5 GHz vs. infinite-frequency reference; TEMPO2/DE438 vs. PINT), so the prereg's frozen conversion procedure must record the per-campaign inbound convention.

### 1.1a FRB 20201124A — FAST 2021 Apr–Jun campaign (verification 2026-08-07)

- Paper: Xu et al. 2022, Nature 609, 685 (arXiv:2111.11764). 1,863 bursts, ~45 burst-detecting near-daily sessions 2021-04-01 → 06-11 plus ~9 h of post-quench null sessions; 91 h total.
- Observing log: **fails S1 as published** — session epochs/durations appear only graphically (Figure 1f, "epochs and durations of all observations are shown in Figure 1"); no tabular or machine-readable log; post-quench sessions untabulated. PSRPKU mirror inaccessible (HTTP 412/403); a journal-side supplementary log could not be fully excluded (paywall) but the Data Availability statement points only to FAST DC, PSRPKU, Figshare.
- Burst table: Figshare DOI 10.6084/m9.figshare.19688854 v2, **CC-BY 4.0** — `FRB20201124A_FAST_2021AprMay_burstInfo.txt` (1,863 rows × 24 cols; site arrival time AND barycentric arrival time, both **@1500 MHz reference**, TEMPO2) + waiting-time file. Checksums **[pending]**.
- Status: **excluded** under S1 unless a session log surfaces (exclusion recorded; burst table remains useful for non-confirmatory development work only if later designated, which would bar the source from confirmatory use).

### 1.1b FRB 20201124A — FAST 2021 Sep–Oct campaign (RAA series) (verification 2026-08-07)

- Papers: Zhou et al. 2022, RAA 22, 124001 (arXiv:2210.03607; 624 analyzed bursts, TOAs at infinite frequency, barycentric, **DE438**) and Niu et al. 2022, RAA 22, 124004 (arXiv:2210.03610).
- Observing log: **meets S1 content requirements** — Niu et al. Table 1: date, **UTC start, MJD start, duration (s)** for all 18 sessions, MJD 59482.942361 → 59504.879861, including null sessions. PDF/journal table only; frozen extraction script + hash required.
- S2: >600 events — pass. S3: 18 sessions over ≈ 22 d — **passes under the revised S3 (≥ 14 d)**; the revision and its data-availability rationale are recorded in prereg_h1 Section 3.1 (decision taken 2026-08-07, before any period-search output existed).
- No repository data release found for this campaign (Papers I/II/IV texts contain no data-availability pointer); burst table and session log are in-paper tables (Zhou Table A.1, Niu Table 1) — frozen extraction scripts + hashes required.
- Status: **verified candidate** (pending extraction scripts and checksums).

### 1.2a FRB 20220912A — Nançay ÉCLAT campaign (verification 2026-08-07)

- Paper: Konijn et al. 2024, MNRAS 534, 3331 (arXiv:2407.10155). 696 bursts, 68 sessions (~1 h each), 2022-10 → 2023-04, ~61 h.
- Observing log: **meets S1 as published** — Zenodo 10.5281/zenodo.13889738 (CC-BY-4.0) contains `Observation times.txt`: one row per session with NUPPI scan ID, MJD start, integration length (s), DM, sampling. Verified by file fetch.
- Burst table: `NRT_full_burst_information.csv` in the same Zenodo record; TOAs barycentered to infinite frequency, **TDB** (Table 1 footnote). Checksums **[pending download]**.
- S2/S3: 696 events, 68 sessions, ~6-month baseline — passes.
- Status: **verified candidate** (strongest entry so far; pending checksum/schema freeze).

### 1.2b FRB 20220912A — FAST campaign (verification 2026-08-07)

- Paper: Zhang et al. 2023, ApJ 955, 142 (arXiv:2304.14665). 1,076 bursts, 17 sessions, 8.67 h, 2022-10-28 + ~54 days.
- Observing log: **fails S1 — verified absent (2026-08-07).** No per-session start/stop table in the paper (session lengths only graphical, Figure 1F), and the complete 951-file ScienceDB inventory (enumerated from the landing page's embedded JSON-LD) contains only 949 burst `.npy` cutouts + `FRB20220912A-Table.csv` (1,076 burst rows) + a format README — nothing session-level. Burst-file MJDs fall on exactly 17 integer days consistent with the paper's 17 sessions, but that gives detection times, not session windows; reconstructing W(t) from burst times is not permitted (it biases windows toward detections).
- Burst table: ScienceDB 10.57760/sciencedb.08058, **MIT license confirmed on the landing page**, anonymous download verified (CSV MD5 `317974979d1059c6d62567682bd31a3f` matches deposit metadata); TOAs barycentric at 1.5 GHz reference (timescale TDB/TCB unstated).
- Status: **excluded** (S1 exhaustively verified unmet). The source FRB 20220912A remains in the confirmatory sample via the Nançay campaign (1.2a).

### 1.2c FRB 20220912A — AstroFlash 25–32 m multi-telescope campaign (verification 2026-08-07)

- Paper: Ould-Boukattine et al. 2025, MNRAS (arXiv:2410.17024). 130 unique bursts (114 L-band + 16 P-band), MJD 59867.37–59982.82 (~117 d), 2,191.4 h across Stockert, Westerbork RT-1 (L and P band), Toruń (L and C), Onsala (C).
- Observing log: **meets S1 — verified machine-readable.** GitHub repo `astroflash-frb/frb20220912a-ouldboukattine-2025` (also archived as a zip inside Zenodo 10.5281/zenodo.11261763, CC-BY-4.0): `dbs/r117_camp_reduced.csv` — 508 sessions, one row each, with telescope code, `mjd_start`, `mjd_end`, band edges/center, recorded time; summed hours match the paper (2,191.4 vs 2,192). Includes non-detection sessions. Finer per-scan log `dbs/r117_fullcampaign.csv` (5,842 rows) adds pointing, sampling, backend. No per-session sensitivity column; per-setup SEFD/completeness in paper Table 1; per-scan RFI flags in `flags/`.
- Burst table: `dbs/FRB20220912A_table_paper.csv` (146 rows = paper Table 2), `toa` = **barycentric TDB infinite-frequency MJD**; per-component detail in `dbs/burst_stats_r117.csv`. **Caution:** `dbs/FRB20220912A-Table.csv` in the same repo is an unrelated literature compilation — do not confuse.
- **Deduplication caveat (frozen handling required):** 16 bursts are co-detected at two stations and appear as duplicate rows whose inter-station TOA offsets are systematically 0.10–0.55 s despite nominally barycentric TOAs (tr–wb ≈ 0.105 s, st–wb ≈ 0.51–0.55 s, st–tr ≈ 0.43 s). A 100 ms merge window will not catch these; deduplicate by the release's base burst ID. The systematic offsets are a per-station timing-convention discrepancy to note in the analysis (harmless at σ_v ≥ 60 s visit scales, but must be documented).
- S2: 130 unique events — pass. S3: 508 sessions over ~117 d — pass. Multi-telescope structure handled by the prereg's multi-campaign machinery (each station's window function enters separately, shared source parameters).
- Status: **verified candidate** (pending checksum/schema freeze; Zenodo zip is the citable frozen artifact, GitHub the working copy).

### 1.3 FRB 20240114A — FAST Key Science Project campaign (verification 2026-08-07)

- Papers: Zhang et al. 2025 (arXiv:2507.14707; core sample, 11,553 bursts, 57 sessions, 2024-01-28 → 08-29, 33.86 h) and Zhou et al. 2025 (arXiv:2507.14708; periodicity companion, SCPMA 69, 249512).
- Observing log: **meets S1 content requirements, best log in the whole sample** — Zhou Table 3: 111 sessions with **start AND stop MJD (6 decimals, ~0.1 s)**, duration, burst count, through 2025-10-01, **including zero-burst sessions** (source inactive in late 2025). Zhang Supp. Table 1 independently gives 57 sessions with topocentric start/stop MJD (9 decimals) **plus per-session frequency resolution and sampling time** (config changes are logged, e.g. 196.608 → 49.152 µs after session 1). Both logs exist only as in-paper LaTeX/PDF tables (verified absent from the ScienceDB deposit); frozen extraction script + hash required.
- Burst table: ScienceDB DOI 10.57760/sciencedb.Fastro.00030 (V2 2025-10-20), `FRB20240114A_SuppTab2.csv` (2.02 MB), **MIT license** — 11,553 bursts, **barycentric MJD at infinite frequency (PINT)**. Checksums **[pending download]**. Note the mixed convention: session logs topocentric, burst TOAs barycentric — handled by the frozen conversion procedure.
- Secondary product (not for confirmatory timing): FAST polarization catalog (arXiv:2603.20663; 17,356 detected / 6,131 cataloged over 97 sessions to 2025-05-30), ScienceDB Fastro.00040, **CC BY-NC-ND**, **topocentric MJD at 1.5 GHz**, no session log.
- Known sensitivity caveat: pointing changed 2024-02-15 (CHIME → MeerKAT position), affecting the first ~5 sessions; no per-session SEFD table published.
- S2: 11,553 events — pass. S3: 111 sessions over ~20 months — pass. S5: FAST localization — pass.
- Status: **verified candidate** (pending checksum/schema freeze and log-extraction script).

### 1.4 FRB 20240114A — Parkes/Murriyang campaign (verification 2026-08-07)

- **Identification corrected:** the campaign paper is Uttarkar et al., arXiv:2602.16409 ("A fast radio burst cyclone in technicolour") — the same paper designated a carbon-copy/plasma-lensing development control in Section 3. The previously listed arXiv:2508.15615 is a Tianma (TMRT) campaign, moved to Section 1.5.
- Campaign: 5,526 bursts (S/N ≥ 7.5), MJD 60342–60827 (2024-02-02 → 2025-06-01), ~154 h on-source over ~70–85 epochs; projects PX127 and P1338.
- Observing log: Extended Data Table 1 lists **every epoch including non-detections** with date, integer MJD, on-source hours, receiver, per-epoch DM/RM — but **day-level only; no UTC start/stop** (fails S1 as published). Exact session start times are reconstructable from public CSIRO DAP raw-file metadata (PSRFITS filenames encode UTC start; e.g. collection csiro:63659, DOI 10.25919/d8sk-5z59, CC-BY 4.0, `accessLevel: Public`); stop times from file durations/headers. Later P1338 semesters (2024OCTS, 2025APRS) remain embargoed (~public early 2027), truncating the reconstructable window.
- Burst table: **no complete machine-readable release.** GitHub `pavanuttarkar/FRB20240114A` → `data_20sigma_sorted.json` covers only the S/N > 20 subset (~1,100 bursts) with UTC + MJD ToAs; **no license, no DOI, no barycentering statement**; timestamps referenced to the top of each subband (paper Methods). Stated codebase repo link is 404. Extended Data Table 3 gives MJD ToAs for ~20 bursts only.
- Session-level config: per-epoch receiver (UWL/MARS) in ED Table 1; global backend config, SEFD, fluence completeness, RFI-rejection counts in Methods; no per-session dead-time or sensitivity table.
- DAP reconstruction feasibility (assessed 2026-08-07, all claims verified by live API fetches): the campaign maps onto 77 public PX127 collections (all CC-BY, csiro:61623→63671) and 119 embargoed P1338 collections (`accessLevel: Project Team`, first tranche expected public ~late 2026). Public metadata yields **50 distinct observing dates / 53 main scans** (2024-02-02 → 2024-09-30, ≈60–70% of the paper's epochs, ~50% of the calendar interval): UTC start from `uwl_YYMMDD_HHMMSS` filenames (verified against a PSRFITS header via ranged read), stop times from file size × verified data rate, target identification from the collection `.log` link-target paths (`.../FRB20240114A/...`). The embargoed half exposes nothing, not even scan times.
- **Decision (2026-08-07, pre-freeze): excluded from the confirmatory sample; designated exploratory.** Rationale: (a) the only machine-readable burst table is an unlicensed GitHub JSON covering the S/N > 20 subset with an unstated barycentering convention — inadequate provenance for a confirmatory input; (b) the reconstructable window covers only half the campaign; (c) the confirmatory need Parkes would serve (independent window on 20240114A) is already met by the verified TMRT campaign. Revisit under a new prereg version if the authors publish a licensed, complete TOA table or the embargo lifts with the archived data clarifying conventions — both expected by ~late 2026, follow-up territory.

### 1.5 FRB 20240114A — TMRT 2.25/8.60 GHz campaign (verification 2026-08-07)

- Paper: Wang, Yan, Shen et al. 2025, ApJ 992, 185 (arXiv:2508.15615; DOI 10.3847/1538-4357/adfece, **open access CC-BY 4.0**). Shanghai Tianma 65-m; 155 bursts at 2.25 GHz (none at 8.6 GHz).
- Observing log: **meets S1 — verified machine-readable.** Table 2 MRT (`apjadfecet2_mrt.txt` from the ApJ article, fetched anonymously): all **66 sessions** O01–O66 with **topocentric UTC start to 1 s + duration (s)**, full-pol flag, burst count, rate — **including 32 zero-burst sessions**; 2024-01-29 → 2025-02-15 (382-day baseline; note the ~4-month gap 2024-02→06 from TMRT mission commitments). arXiv/PDF truncates the table to 20 rows — the ApJ MRT is the frozen artifact.
- Burst table: Table 3 MRT (`apjadfecet3_mrt.txt`), 155 rows, TOA = **barycentric MJD at infinite frequency** (DM 527.7, stated DM constant, EVN position; TOA at FWTM midpoint). Same mixed topocentric-log/barycentric-burst convention as the FAST release.
- Session-level config: per-session full-pol flag; pointing epochs documented (O01–O05 CHIME position ~5% S-band sensitivity loss; O06–O08 MeerKAT; O09+ EVN); O41/O43 lost 8.6 GHz only; global: DIBAS, 65.536 µs, ~98.6 MHz effective at S-band, SEFD ~46 Jy, TransientX 7σ, fluence threshold 0.72 Jy ms.
- Burst-cutout deposit: China-VO PaperData DOI 10.12149/101581 — `archives.zip` (7.89 MB, 155 PSRCHIVE `.ar` files), downloaded anonymously; no on-request restriction anywhere.
- S2: 155 events — pass. S3: 66 sessions, 382 d — pass. S5: EVN position — pass.
- Status: **verified candidate.** Also serves as the materially-different-window instrument for clearing alias-contaminated FAST 20240114A peaks (prereg_h1 Section 5.4).

_Verification note: five source–campaign pairs are verified (1.1b, 1.2a, 1.2c, 1.3, 1.5), so the freeze-pause condition of prereg_h1 Section 3.2 is not triggered. All sample decisions are resolved; what remains for freeze is mechanical (downloads, checksums, extraction scripts, software pinning)._

_Addendum (2026-08-07, rev3 nearest-host pass): a sixth pair was verified after the thesis update introduced the host-distance prior — FRB 20200120E Effelsberg (Section 1.7). Six pairs total._

### 1.7 FRB 20200120E — Effelsberg monitoring campaign (verification 2026-08-07, rev3 nearest-host pass)

- Motivation: nearest-host repeater (M81 globular cluster, 3.6 Mpc) — the first target under the rev3 extragalactic spatial prior (research note Section 16.4). Verified by a live pass over all published campaigns for this source; every alternative fails S1 or S2 (CHIME: 4 bursts, no session log, source explicitly excluded from the 2023/2026 repeater catalogs "reported separately"; DSN Majid 2021: 1 burst, 1 session; Haoping Zhang 2024: 1 burst, text-only epochs; Northern Cross: 0 bursts, cumulative exposure only; FAST: geometrically impossible at dec ≈ +68.8°, outside FAST's −14°…+66° range).
- Papers: Nimmo et al. 2023, MNRAS 520, 2281 (arXiv:2206.03759; "burst storm," 60 bursts) — primary; Kirsten et al. 2022, Nature 602, 585 (arXiv:2105.11445; PRECISE-era, B1–B5, 15-run log); Pearlman et al. 2024, Nature Astronomy (arXiv:2308.10930; refined TOAs B1–B9, best-format log).
- Observing log: **meets S1 content requirements** — Nimmo Table `tab:observations`: 42 Effelsberg sessions, start MJD (topocentric) + duration (hr) + backend + burst count, **all non-detection sessions included**, MJD 59265.708–59693.655 (~428 d). Complete LaTeX table in the arXiv source (no CSV/Zenodo version exists); frozen extraction script + hash required.
- Burst table: Nimmo longtable `tab:burst_properties`: **60 TOAs, barycentric TDB at infinite frequency**, DM 87.7527, VLBI position; LaTeX-only, extraction script required. Kirsten adds the same B1–B5 at PRECISE stations; Pearlman `tab:radio_burst_properties` gives **refined re-barycentred B1–B9** (the Kirsten/Nimmo-2022 B1–B5 TOAs used a superseded position, ~3–4 ms error — immaterial at σ_v ≥ 60 s visit scales but the Pearlman values are adopted where duplicated).
- **Frozen handling required (recorded now, decided before tag):** (a) session-window construction — Nimmo's "duration" is not guaranteed on-source time for PRECISE-era runs (interleaved calibrators); where the Pearlman log (23 sessions with UTC start AND end + on-source exposure, 2020-12→2021-05) overlaps, Pearlman's on-source windows take precedence; later sessions use Nimmo start+duration with the overstated-exposure caveat noted; the Kirsten PR163A stop = Nimmo start inconsistency (MJD 59347.625) resolved at extraction time and documented. (b) Cross-table burst deduplication by published burst ID (B1–B5/B1–B9 appear in up to three tables). (c) Kirsten's four non-Effelsberg PRECISE runs (PR160A/162A/164A/165A) enter W(t) as separate-station windows only if their station and on-source semantics can be pinned; otherwise dropped (conservative).
- S1: pass (with the frozen construction rule). S2: 60 events — pass; **statistical-power caveat: 53/60 bursts lie within one ~2 h storm session on 2022-01-14**, so most events constrain only within-session structure; recorded for the null-interpretation section, not a sample-eligibility issue. S3: 42 sessions, ~428 d — pass. S4: no published activity-window period (periodicity searches on published TOAs are null) — pass. S5: mas-scale VLBI localization — pass.
- Supporting deposits (not H1 inputs): Zenodo 10.5281/zenodo.7555187 — 16.6 GB Stokes-I 5.12 μs filterbanks for all 60 bursts, and Zenodo 10.5281/zenodo.5666802 — Nimmo 2022 products down to 31.25 ns (both intensity-domain: H2-relevant at top host-distance priority, **not** H4 — the source has no public voltage data; product matrix Section 8); Zenodo 10.5281/zenodo.13359005 — Pearlman dynamic spectra (npy/npz).
- Status: **verified candidate** (pending extraction scripts, checksums, and the frozen session-window construction rule).

### 1.6 Frozen files and checksums (downloaded and verified 2026-08-07)

All files below are stored under `data/raw/` (gitignored; re-fetchable from the recorded URLs) and were verified against publisher-side checksums where the repository publishes them (Zenodo MD5, ScienceDB MD5 — all matched). Session logs extracted from these inputs live in `phase1/windows/` with `PROVENANCE.json` recording input/output SHA-256 pairs, produced by the frozen script `scripts/extract_session_logs.py`.

| Campaign | File | Size (B) | SHA-256 | Source verification |
| --- | --- | --- | --- | --- |
| Nançay 20220912A | `Observation times.txt` | 38,430 | `b2c258e1…86df02b43`* | Zenodo MD5 `0ee30dce…` matched |
| Nançay 20220912A | `NRT_full_burst_information.csv` | 10,415,063 | `42554557…bed34d7e` | Zenodo MD5 `fa907570…` matched |
| Nançay 20220912A | `Supplementary Material (online).csv` | 34,405 | `8f2a6e5b…6b93a72` | Zenodo MD5 `6c762d54…` matched |
| Nançay 20220912A | `NRT_bursts_with_corrected_drift.csv` | 84,469 | `205dcb67…a9a4a7db` | Zenodo MD5 `ae602879…` matched |
| AstroFlash 20220912A | `r117_camp_reduced.csv` | — | `a5f406af…651e149b` | GitHub `main`; archived in Zenodo repo-zip MD5 `03141af2…` |
| AstroFlash 20220912A | `r117_fullcampaign.csv` | — | `86ead8bc…9bec9640` | ditto |
| AstroFlash 20220912A | `FRB20220912A_table_paper.csv` | — | `239dd751…454ea838` | ditto |
| AstroFlash 20220912A | `burst_stats_r117.csv` | — | `b8bb46de…8bbb5264` | ditto |
| TMRT 20240114A | `apjadfecet2_mrt.txt` (66-session log) | — | `1f975bbc…1401dfe2` | ApJ CDN, open access |
| TMRT 20240114A | `apjadfecet3_mrt.txt` (155-burst table) | — | `6b9eea7b…20bad867` | ApJ CDN, open access |
| TMRT 20240114A | `archives.zip` (155 `.ar` cutouts) | 8,274,920 | `19b4066d…3e4f3bb` | China-VO r101581, anonymous download |
| FAST 20240114A | `FRB20240114A_SuppTab2.csv` (11,553 bursts) | 2,115,004 | `656b2e1d…44e5ab22` | ScienceDB MD5 `a17712f4…` matched; fileId `b2d11e6f…` |
| arXiv source | `2507.14707.tar.gz` (Zhang Supp. Table 1) | 3,959,052 | `dd1e9620…4647ed45` | arXiv e-print |
| arXiv source | `2507.14708.tar.gz` (Zhou Table 3) | 6,743,039 | `e654afe2…ce070bdb5` | arXiv e-print |
| arXiv source | `2210.03607.tar.gz` (Zhou 2022 burst table) | 94,175,772 | `72e63a2a…d659591` | arXiv e-print |
| arXiv source | `2210.03610.tar.gz` (Niu Table 1) | 25,076,478 | `af4769d4…5b851b3` | arXiv e-print |

\* Full 64-hex digests are recorded programmatically in `phase1/windows/PROVENANCE.json` and reproducible via `shasum -a 256`; the table abbreviates for readability.

**Extracted session logs (`phase1/windows/`, all row counts matching the published session counts exactly):** `fast20240114A_zhou111_sessions.csv` (111), `fast20240114A_zhang57_sessions.csv` (57), `fast20201124A_sepoct_sessions.csv` (18), `tmrt20240114A_sessions.csv` (66), `nancay20220912A_sessions.csv` (68 — filtered from the 240-row multi-target ÉCLAT log by the `2309+4842` pointing), `astroflash20220912A_sessions.csv` (508, verbatim).

**FAST 20201124A Sep–Oct burst table (extracted 2026-08-07):** `phase1/windows/fast20201124A_sepoct_bursts.csv`, 625 rows = **624 unique numbered bursts** (burst No. 108 on 2021-09-28 has two component rows) from `Tex/tab_each_burst.tex`; per-day counts 29/57/169/369. TOAs barycentric MJD at infinite frequency (DE438). **Selection caveat to carry into the analysis:** the paper's prose reports 30/62/208/447 = 747 *detected* bursts; the appendix tabulates only the 624 analysis-quality bursts. The confirmatory event list is the tabulated one; the 123-burst shortfall is the paper's own quality cut and must be stated with any rate-sensitive result for this campaign.

**Still to fetch for H1 freeze:** positive-control tables (Section 2).

## 2. H1 positive controls (excluded from confirmatory testing)

**Window-model policy for controls (recorded 2026-08-07):** positive controls validate parameter recovery (prereg_h1 Section 9, test 4); they make no confirmatory claim. Approximate window models (e.g. daily CHIME transits weighted by published up-time) are therefore permitted here, clearly labeled, even though window reconstruction is banned for confirmatory sources.

### 2.1 FRB 20180916B — complete

- CHIME/FRB 2020 (Nature 582, 351): arXiv source tarball 2001.10275, SHA-256 `d886aa76…8e4d95ef4`. TOA table extracted to `phase1/windows/control_chime20180916B_toas.csv`: **38 sub-burst rows = CHIME's 28 bursts**. Grouping-convention note: CHIME groups per trigger event (components can span > 100 ms), so our frozen 100 ms rule yields 35 events from the same rows — immaterial for the M1 period-recovery test, recorded for transparency.
- Window model: approximate daily-transit windows per the controls policy above.
- Sand et al. 2023 compilation (DOI 10.11570/20.0002) — optional supplement, not required.

### 2.2 FRB 20121102A — complete

- **Cruces et al. 2021 (arXiv:2008.03461) tables extracted 2026-08-07** (tarball SHA-256 `0c4b194b…a1a6c2bb4`): `control_cruces121102_sessions.csv` — all 33 tabulated sessions (EFF/AO/GBT, UTC start + duration + event count, 2017-09 → 2020-06; the paper's "34 epochs" adds earlier published Hardy/Houben epochs not tabulated); `control_cruces121102_bursts.csv` — 36 Effelsberg burst MJDs. Sufficient for the ~157–161 d M1 recovery test; the Braga 2025 compilation is no longer needed.
- Li et al. 2021 FAST 1,652-burst table: downloaded and verified — `FRB121102_1652burstList.csv` (ScienceDB 10.11922/sciencedb.01092, CC0), MD5 matches deposit, SHA-256 `6a38c154…35a6ef87`. Single ~47-day campaign; short-baseline recovery checks.

## 3. H2/H3/H4 calibration ladder (draft; frozen at `prereg-h2h3h4-v1.0`)

Per preregistration Section 6. Every source/event used here is permanently excluded from the confirmatory H2 sample.

| Set | Role | Access | Fields |
| --- | --- | --- | --- |
| MeerKAT TPA Single-Pulse Census (1,192 pulsars, full Stokes; effective release resolution 16 channels / 1,024 phase bins) | population null, incl. scintillation regimes | Zenodo 10.5281/zenodo.18980771, CC-BY | files/checksums **[pending]** |
| Parkes Transient DB II (165,592 pulses, 363 pulsars) | archival-era instrumental null | CSIRO DAP 10.25919/34am-zx04 | **[pending]** |
| B1937+21 giant-pulse baseband | propagation-imprint regime | Zenodo 10.5281/zenodo.7901384 | **[pending]** |
| Crab GP voltage snippet (Dwingeloo) | propagation-imprint regime | Zenodo 10.5281/zenodo.13143544 | **[pending]** |
| FAST FRB 20201124A atlas | repeating-FRB development control | ScienceDB 10.57760/sciencedb.j00113.00076, **CC-BY-NC-ND** (license constraint on redistribution/figures) | **[pending]** |
| FRB 20240114A published burst sets (carbon-copy pairs) | documented near-copy fat tail | per arXiv:2602.16409 / 2607.02939 releases | **[pending]** |

## 4. H2/H3/H4 confirmatory archives (draft; frozen at `prereg-h2h3h4-v1.0`)

| Archive | Streams | Access | Fields |
| --- | --- | --- | --- |
| MeerTRAP Galactic-transient release (26 RRAT-like sources, all pulses, ±0.5 s pads) | primary Galactic region | Zenodo 10.5281/zenodo.14646142, CC-BY | **[pending]** |
| CHIME/FRB Catalog 1 waterfalls | FRB dynamic spectra | CANFAR CISTI.CANFAR/21.0007 | **[pending]** |
| CHIME/FRB Catalog 2 event table + dynamic spectra | FRB dynamic spectra, morphology/rates | CANFAR 10.11570/25.0066 | **[pending]** |
| DSA-110 event archive (full-Stokes filterbanks, ~0.67 s extent) | FRB, full cutout extent | per-event CaltechDATA DOIs | **[pending]** |
| CRAFT HTR DR1 (35 FRBs, IQUV, re-binnable) | FRB high-time-resolution | DOI 10.25917/1rg2-c612, CC-BY | **[pending]** |
| CHIME/FRB Baseband Catalog 1 (140 FRBs) | Phase 4 public-baseband pilot | CANFAR 10.11570/23.0029 (known gap: ~10 repeater-burst products missing) | **[pending]** |

## 5. Host-distance priority table (rev3 extragalactic prior; frozen at `prereg-h2h3h4-v1.0`)

_The frozen sub-priority input for the FRB streams (preregistration Section 3 item 3; research note Sections 8.2 and 16.4): repeaters localized to hosts, ordered by distance, nearest first. Compiled from a live census 2026-08-07 (all localization claims verified against the cited papers). Only three confirmed repeaters are localized within 200 Mpc. Sources beyond the nominal ~80 Mpc beam-filling horizon remain in scope — the horizon is gain-dependent — with the closer expectation noted in interpretation._

| Rank | FRB | Host | Distance | Localization ref | Public voltage? |
| --- | --- | --- | --- | --- | --- |
| 1 | 20200120E | M81 globular cluster | 3.6 Mpc | Kirsten et al. 2022 (Nature 602, 585) | Partial — see Section 1.7 note and the product matrix |
| 2 | 20181030A | NGC 3252 | ~20 Mpc | Bhardwaj et al. 2021 (ApJL 919, L24) | No (CHIME-internal baseband only; absent from the public baseband catalog, verified) |
| 3 | 20180916B | SDSS J015800.28+654253.0 (z = 0.0337) | 149 Mpc | Marcote et al. 2020 (Nature 577, 190) | **Yes** — CHIME Baseband Catalog 1 includes its bursts (DOI 10.11570/23.0029, verified); LOFAR complex voltages via LTA [P] |
| 4+ | 20200223B (~270 Mpc) · 20190303A (~290) · 20180814A (~310) · 20220912A (~360) · 20201124A (~420–450) · 20190110C (~590) · 20240114A (~630) · 20240209A (~680) · 20121102A (~970) | — | beyond 200 Mpc | Ibik 2024; Michilli 2023; Ravi 2023; Fong 2021; CHIME/KKO 2025; Tendulkar 2017 | per product matrix |

Watch list (checked and excluded 2026-08-07, re-verify at each freeze): FRB 20240210A (Seyfert host at ~105 Mpc — currently a non-repeater; enters at rank 3 if it ever repeats); FRB 20250316A (NGC 4141, ~40 Mpc — one-off despite deep exposure); FRB 20240619D (hyperactive MeerTRAP repeater, host unknown, z estimated 0.042–0.240 — the top unresolved candidate for a nearby slot).

## 6. Software environment (pinned at each freeze)

- Working environment (recorded 2026-08-07, finalized at tag): Python 3.12.2, numpy 2.5.1, scipy 1.18.0, astropy 8.0.1 — full transitive lock in `phase0/requirements-lock.txt` (`.venv` local, gitignored).
- Repository commit: **[pending at tag]**
- Solar-system ephemeris: DE440, file hash **[pending at tag — recorded when the barycentric window conversion is wired into the full-scale run]**
- Observatory coordinates: astropy sites registry version **[pending at tag]**

## 7. Pre-freeze inspection log

_Every file opened before the relevant tag is listed here with date, purpose, and the policy clause permitting it (schema/availability verification; positive-control designation; calibration/development-control designation). Confirmatory target data may not appear in this log._

| Date | File | Purpose | Permitted because |
| --- | --- | --- | --- |
| 2026-08-07 | Figshare 10.6084/m9.figshare.19688854: `burstInfo.txt`, `WaitingTime.txt` (FRB 20201124A Apr–Jun) | S1–S5 verification: row count, column schema, MJD span, time-standard headers | Availability/schema verification and S2/S3 counts required by prereg_h1 §3.2; no timing-structure statistics computed; source subsequently **excluded** under S1 anyway |
| 2026-08-07 | GitHub `pavanuttarkar/FRB20240114A/data_20sigma_sorted.json` (Parkes) | S1–S5 verification: schema, coverage (S/N>20 subset only), time fields | Availability/schema verification; campaign fails S1 as published; no timing-structure statistics computed |
| 2026-08-07 | Zenodo 10.5281/zenodo.13889738: `Observation times.txt` (Nançay 20220912A) | S1 verification: session-log schema and completeness | Observing-log inspection is not burst data; required to verify S1 |
| 2026-08-07 | arXiv LaTeX sources 2507.14707/2507.14708 (`obs_inf.tex`, Table 3) and 2210.03607/2210.03610 tables | S1 verification: session-log columns, row counts, MJD ranges | Published-paper content; observing logs, not burst data |
| 2026-08-07 | ScienceDB 10.57760/sciencedb.08058: full file inventory, `README.md`, `FRB20220912A-Table.csv` (FAST 20220912A) | S1 verification: exhaustive check for a session log; file-MJD day distribution computed | Availability/schema verification of a campaign then **excluded** from the confirmatory sample; no timing-structure statistics computed |
| 2026-08-07 | AstroFlash repo `dbs/` CSVs (session logs, `FRB20220912A_table_paper.csv`, `burst_stats_r117.csv`) | S1/S2 verification and event-grouping check: session sums, unique-burst count, co-detection duplicate identification (required computing minimum pairwise TOA separations) | Log inspection plus the grouping check mandated by prereg_h1 §2.1/§3.1; the pairwise-separation computation was limited to duplicate detection; no periodicity or clustering statistics computed |
| 2026-08-07 | ApJ MRTs `apjadfecet2_mrt.txt` (66-session log), `apjadfecet3_mrt.txt` (155-burst table); China-VO `archives.zip` file listing (TMRT 20240114A) | S1/S2 verification: session count/sums, burst count, per-session burst totals, deposit accessibility | Log inspection and availability/schema verification; burst-table row count only; no timing-structure statistics computed |
| 2026-08-07 | CSIRO DAP: 196 collection detail records, 77 PX127 `.log` files and file listings, one ranged PSRFITS header read (Parkes 20240114A) | DAP-reconstruction feasibility: scan dates/times, target paths, config verification | Observatory/session metadata, not burst data; campaign subsequently **excluded** from confirmatory sample |
| 2026-08-07 | Freeze downloads (Section 1.6): burst tables and session logs for the five verified campaigns; CSV header lines viewed; session-log extraction run with row-count verification | Checksum recording and extraction-script validation required by the freeze checklist | Download + hash does not examine content; inspection limited to header/schema lines and published session logs; no burst-time statistics computed |
| 2026-08-07 | arXiv LaTeX sources 2206.03759 (Nimmo observation + burst tables), 2105.11445 (Kirsten run + burst tables), 2308.10930 (Pearlman radio-obs + burst tables), 2103.01295, 2105.10987, 2310.00908; Zenodo 7555187 / 13359005 file listings (FRB 20200120E) | Rev3 nearest-host S1–S5 verification: session counts/spans, burst counts, time-standard footnotes, cross-table TOA consistency (duplicate identification and the PR163A start/stop inconsistency) | Availability/schema verification and the S2/S3 counts required by prereg_h1 §3.2; duplicate/consistency checks limited to identification; no periodicity, clustering, or timing-structure statistics computed |
