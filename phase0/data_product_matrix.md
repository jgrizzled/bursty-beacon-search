# Stage-0 Data-Product Matrix (public data, initial version)

_Compiled 2026-08-07 from live verification of endpoints and papers. Begins the inventory required by the research note Section 8.3; collaboration-gated products (Phase 4) are listed only where their existence matters for planning._

**Verification flags:** [V] endpoint or file verified live during compilation · [P] existence/policy verified via papers/docs only · [X] not public / could not be verified — treat as unavailable.

**Suitability codes:** T = burst-timing/exposure analyses · M = dynamic-spectrum morphology · V = voltage-domain.

## 1. CHIME/FRB

| Product | Contents | Resolution / pol | Access | Suitability | Flag |
| --- | --- | --- | --- | --- | --- |
| Catalog 1 (2021) + waterfalls | 536 FRBs (474 one-off, 62 bursts/18 repeaters); ~50-col table incl. per-source exposure; HDF5 waterfall per event (`wfall`, `calibrated_wfall`, model fits); ~35 MB/event, ~19 GB total | 0.983 ms, 16,384 ch (24.4 kHz), 400–800 MHz; Stokes I only | CANFAR DOI CISTI.CANFAR/21.0007; `cfod` pkg; direct CADC vault URLs verified | T (ms only), M (reference uniform set) | [V] |
| **Catalog 2 (2026)** | 4,539 bursts / 3,641 sources (2018-07→2023-09), incl. **981 bursts from 83 repeaters**; dynamic spectra; localization contours; cumulative all-sky exposure maps (upper/lower transit); per-event sensitivity thresholds | 0.983 ms / 24.4 kHz; no pol; catalog arrival times are topocentric MJD UTC and require a frozen barycentric conversion for H1 | CANFAR DOI 10.11570/25.0066; arXiv:2601.09399 (ApJS 283, 34). ~160 GB est. | **T candidate, conditional on time-resolved windows**, M (largest uniform sample) | [V paper / P files] |
| 25-repeater catalog (2023) | Burst times, dynamic spectra, per-source exposure through 2021-05-01 | 0.983 ms; no pol | CISTI.CANFAR/23.0004; arXiv:2301.08762 | T, M | [P files] |
| **Baseband Catalog 1** | 140 FRBs (2018-12→2019-07): per-event "singlebeam" HDF5 — complex beamformed dual-pol voltages, amplitude-calibrated + coherently dedispersed power | 2.56 μs × 1024 ch (390.6 kHz); full Stokes recoverable; raw array voltages NOT public | CANFAR DOI 10.11570/23.0029; Michilli et al. 2024 (ApJ 969, 145). Known gap: ~10 repeater-burst products missing (GitHub issue #103) | **V (flagship public voltage set)**, M (μs), T | [V] |
| Exposure products | Cat 1: cumulative HEALPix nside-4096 exposure maps (.npz, 2018–2019; don't degrade below nside 512) + per-source totals; Cat 2: cumulative maps 2018–2023 + sensitivity thresholds; repeaters-2023: per-source totals to 2021-05. These products do **not by themselves establish timestamped good-time intervals** $W(t)$. | — | In respective CANFAR records; tutorial at chime-frb-open-data.github.io/exposure/ | T for integrated-rate work; **insufficient alone for the Phase 1 alias-aware likelihood** | [V cumulative / X time-resolved] |
| Injections release | 5M synthetic FRBs + ~85k injected subset (Merryfield et al.) | — | DOI 10.11570/22.0005 | selection-function work | [V] |
| VOEvent service | Real-time alerts, ~13 s latency | — | chime-frb.ca/voevents (down during site rebuild; operation in Aug 2026 unconfirmed) | live follow-up only | [V exists / X current] |
| Catalog 2 baseband companion | announced, "forthcoming" | — | — | — | [X] |
| 30-new-repeaters (Cook 2026) data | no release identified | — | arXiv:2605.08410 | — | [X] |

Note: chime-frb.ca is mid-rebuild (placeholder on all routes); use CANFAR/CADC records and chime-frb-open-data.github.io directly.

## 2. Other FRB catalogs / datasets

| Product | Contents | Resolution / pol | Access | Suitability | Flag |
| --- | --- | --- | --- | --- | --- |
| TNS | Official FRB naming + metadata (position, UTC, DM, instrument); no data files | — | wis-tns.org, free API key | T (master index) | [V] |
| Blinkverse | Aggregator >9,500 bursts / 800+ sources; hosts FAST waterfalls (FRB 20121102A, 20201124A) unavailable elsewhere; browsing, not bulk download | varies | **blinkverse.zero2x.org** (old alkaidos.cn domain dead) | T, M (browse) | [V] |
| CRAFT HTR DR1 | 35 FRBs: cropped full-Stokes IQUV dynamic-spectrum numpy arrays, re-binnable from ~3 ns Nyquist; 142 files, ~9 GB, CC-BY | μs–ns-derived; full Stokes | DOI 10.25917/1rg2-c612 (open directory, verified); arXiv:2505.17497 | M (excellent), T; V partial (Stokes, not complex) | [V] |
| ASKAP lat50 + FRB 180924 | SIGPROC filterbanks (1.265 ms, 336×1 MHz, 36 beams); DiFX visibilities | ms; pseudo-Stokes I | CSIRO DAP DOIs 10.25919/5b6ae6b515850, 10.25919/5d09d22f2c004 | M, T | [V] |
| CRAFT raw VCRAFT voltages | per-antenna voltage dumps | 3 ns capable | request/collaboration only | V (Phase 4) | [X] |
| DSA-110 Event Archive | 50+ events (2022→2025-09, ongoing): calibrated full-pol IQUV SIGPROC filterbank, ~0.67 s around burst, pol-calibrated; CC-BY | 32.7 μs / 30.4 kHz, 6144 ch, 1.28–1.53 GHz | code.deepsynoptic.org/dsa110-archive → per-event CaltechDATA DOIs | M (cleanest public full-Stokes waterfalls), T | [V] |
| MeerTRAP FRBs | localization products only (Zenodo 4.4 MB); filterbanks/voltages request-only | — | 10.5281/zenodo.6047539 | — | [X bulk] |
| FAST FRB 20121102A (Li 2021) | burst-parameter tables for 1,652 bursts (MJD, DM, width, fluence), CC0 — **NOT raw spectra** (common misunderstanding) | — | ScienceDB 10.11922/sciencedb.01092 | **T (largest homogeneous burst-MJD set)** | [V] |
| FAST FRB 20201124A atlas | PSRFITS dynamic spectra + times + masks for 1,863-burst campaign, ~892 MB; **CC-BY-NC-ND** | 98.3 μs / 0.122 MHz native campaign specs | ScienceDB 10.57760/sciencedb.j00113.00076 | M (excellent; license limits), T | [V] |
| FAST archive generally | 12-mo proprietary then public; bulk retrieval via offline request (fastdc@nao.cas.cn) — no anonymous self-service | 49–98 μs, often 4 pol | NADC / FAST Data Center | Phase 4-adjacent | [P] |
| Dead: FRBCAT, FRBSTATS, realfast.io portal | — | — | frbcat.org offline; herta-experiment.org domain parked (CSV unrecoverable from GitHub); realfast.io down | do not depend on | [V-dead] |

## 3. RRAT / Galactic single-pulse streams (primary search region)

| Product | Contents | Resolution / pol | Access | Suitability | Flag |
| --- | --- | --- | --- | --- | --- |
| **RRATalog (relocated)** | 337 RRATs, live CSV (41 cols: P, Pdot, DM, position, burst rate, S1400, width) + per-source TOML; actively maintained | catalog only | **rratalog.github.io/rratalog** (old WVU URL redirects); Agarwal et al. 2026 (arXiv:2604.01203) | T (source selection, rate priors) | [V] |
| **MeerTRAP Galactic transients (Turner 2025)** | **Best public RRAT single-pulse dataset:** every detected pulse from 26 sources through 2024-07 as SIGPROC filterbank cutouts (±0.5 s pad) + dynamic spectra + profiles; 8.4 GB CC-BY | L-band 306 μs / UHF 482 μs, 1024 ch; Stokes I | Zenodo 10.5281/zenodo.14646142; arXiv:2501.08224 (MNRAS 537, 1070) | **M (primary-region pilot), T** | [V] |
| CHIME Galactic sources (Good 2021; Dong 2023) | 28 sources incl. ~18 RRATs, timing solutions for 8; **no public dynamic-spectrum release**; portal page offline | — | papers only | T (published solutions) | [X data] |
| FAST GPPS RRATs | 861-row discovery table (~97 RRATs), PNG plots; raw via FAST DC request after embargo | 49.2 μs native | zmtt.bao.ac.cn/GPPS (HTTP only) | T (P/DM/rates) | [V page / X pulses] |
| ATNF psrcat | TYPE(RRAT) → 220 entries; ephemerides; no burst rates | — | v2.8.1, psrqpy | T (ephemeris seed) | [V] |
| RRAT voltages | **none identified as public in this audit** | — | — | — | [X] |

## 4. Pulsar single-pulse archives (copy-exactness calibration)

| Product | Contents | Resolution / pol | Access | Suitability | Flag |
| --- | --- | --- | --- | --- | --- |
| **MeerKAT TPA Single-Pulse Census** | ~1,000 consecutive pulses each for 1,192 pulsars (incl. known RRATs); processed **full-Stokes PSRFITS**; ~35 GB CC-BY | Public single-pulse outputs: normally 1,024 phase bins per pulsar period and 16 frequency channels at L band. The input recorder used 38.28 μs sampling and 1,024 × 0.836 MHz channels; those are not the resolution of the processed release. | Zenodo 10.5281/zenodo.18980771; browse psrweb.jb.man.ac.uk/tpa/singlepulse; arXiv:2606.10807 | **M (primary calibration set, with source-dependent effective time resolution)**, T | [V] |
| TPA pulse-energy distributions | phase-resolved energy distributions, nulling; 9.6 GB | — | Zenodo 10.5281/zenodo.18982781 | null-model support | [V] |
| **Parkes Transient DB II** | 165,592 single pulses from 363 pulsars (1997–2001) with raw data segments; sqlite3+binary, only 1.5 GB | survey-era resolutions | CSIRO DAP 10.25919/34am-zx04; arXiv:2508.14403 | T, M (segment-level) | [V] |
| Parkes Pulsar Data Archive | ~2M files; PSRFITS search-mode (.sf, single-pulse-capable, up to full Stokes, 64 μs–1 ms) public after 18-mo embargo; UWL supported | varies | data.csiro.au/domain/atnf | T, M (archival depth) | [V] |
| **B1937+21 GP baseband** | dual-pol baseband snippets of giant pulses, 19 bands (`pulsarbat`); 45.9 GB zipped | baseband | Zenodo 10.5281/zenodo.7901384; arXiv:2305.13274 | **V (propagation-imprint fat-tail calibration)** | [V] |
| Crab GP voltage | Dwingeloo 0.2 s raw IQ snippet (16 MB, SigMF) — only unambiguous open Crab baseband; MWA ASVO VCS voltages public 18 mo post-obs (policy) | baseband | Zenodo 10.5281/zenodo.13143544; asvo.mwatelescope.org | V (small) | [V] / [P] |
| EPN profile database | 2,458 **average** profiles, 840 pulsars — no single pulses | — | psrweb.jb.man.ac.uk/epndb | template reference only | [V] |
| Vela UTAS single-pulse archive | ~800M pulses, ~1 PB, full Stokes — restricted/by-request, CC-BY-NC-ND | — | metadata public only | Phase 4-adjacent | [V-restricted] |

## 5. SETI archives

| Product | Contents | Resolution / pol | Access | Suitability | Flag |
| --- | --- | --- | --- | --- | --- |
| BL Open Data Archive | GBT/Parkes/APF: SIGPROC .fil, HDF5, **GUPPI .raw dual-pol voltages (selective retention, no public manifest — query per-target)**; HTR product ~349 μs / ~366 kHz; ~3 PB | HTR ms-capable; raw = full Stokes | breakthroughinitiatives.org/opendatasearch (searchable by file type incl. "baseband"); Lebofsky et al. 2019 | T/M where HTR exists; V where .raw kept | [V] |
| BL FRB 121102 (2017 GBT C-band) | 10 SIGPROC scans, ~740 GB direct download; raw baseband ~400 TB stated public in BLDR 1.0 | ~350 μs / 366 kHz, Stokes I; raw dual-pol | seti.berkeley.edu/frb-machine/technical.html | M, V (heavyweight) | [V] / [P raw] |
| BL MeerKAT (BLUSE) | >1.2M beams; per-antenna voltage "stamp" cutouts — **request-only** | — | arXiv:2607.23651 | Phase 4 | [X] |

## 6. Timing-window inputs (Phase 1 shortlist)

- **CHIME Cat 2 event times** [V paper / P files] — primary candidate; **not H1-ready until timestamped good-time intervals and sensitivity masks are obtained and verified**.
- FRB 20180916B: 28 TOAs (CHIME 2020 Ext. Data Table 1); Sand et al. 2023 (60 intensity + 45 baseband bursts + exposure to 2021-12; original release DOI 10.11570/20.0002); Apertif/LOFAR/uGMRT burst lists.
- FRB 20121102A: ~425 detection/non-detection epochs 2012–2023 compiled in Braga et al. 2025 (arXiv:2408.12567; Zenodo DOI to pin down [P]); Cruces 2021 Effelsberg logs; Li 2021 CC0 1,652-burst table; Hewitt 2022; Jahns 2023.
- Hyperactive repeaters for short-lag structure: FRB 20201124A (Xu 2022), 20220912A (Zhang 2023), 20240114A (Zhou 2025, arXiv:2507.14708; Parkes arXiv:2508.15615).
- RRATalog burst rates; Parkes Transient DB II timestamps.
- Caveat: aggregators (Blinkverse, TNS) lack per-observation exposure logs. Per-paper start/stop logs can define $W(t)$ for selected campaigns; cumulative CHIME HEALPix products cannot supply the missing timestamps.

## 7. Other stores

| Product | Note | Flag |
| --- | --- | --- |
| STARE2 FRB 200428 | CaltechDATA 10.22002/D1.1647; 65.5 μs total power; no voltage product identified in the public release | [V] |
| GReX | operating, 5 sites; 8.2 μs voltage dumps on trigger; **no public archive**, no detections yet | [X data] |
| realfast/VLA | candidates enter NRAO archive with no proprietary period (policy), but portal down, no browsable DB verified | [P/X] |
| LOFAR FRB 20180916B | complex-voltage dual-pol 5.12 μs / 195.3 kHz via LTA (public post-proprietary, account needed) — **low-frequency baseband** | [V/P] |
| NenuFAR FRB monitoring | no public release; waveforms usually deleted | [X] |
| SGR 1935+2154 | CHIME intensity release 10.11570/20.0006 [V]; no public baseband for any burst [X] | mixed |

## Cross-cutting summary

1. **Public voltage/baseband products identified and verified in this audit (not an exhaustive universal list):** CHIME Baseband Catalog 1 (140 FRBs) · BL GUPPI .raw incl. FRB 121102 · LOFAR LTA complex voltage (incl. FRB 20180916B) · B1937+21 GP baseband · Dwingeloo Crab snippet · MWA ASVO VCS (policy-level). Other products identified here are request-only.
2. **Public data appear sufficient for substantial Phase 2–3 work, subject to the frozen manifest and schema checks. Phase 1 is conditional.** Burst epochs and cumulative exposure products are public, but the time-resolved $W(t)$ required by the confirmatory scanner likelihood has not been verified as public. Per-campaign observing logs may support a narrower Phase 1 sample.
3. **Licensing watch:** FAST 20201124A atlas is CC-BY-NC-ND; UTAS Vela archive NC-ND/restricted.
4. **Named outages (2026-08):** chime-frb.ca (rebuild), FRBCAT, FRBSTATS, realfast.io, Blinkverse's old domain.
