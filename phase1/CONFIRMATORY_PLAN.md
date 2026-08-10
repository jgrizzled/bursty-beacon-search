# Confirmatory H1 scan — runner specification (post-tag, prereg-h1-v1.0)

The freeze exists (tag `prereg-h1-v1.0` = 277fc8b); confirmatory data may
now be scanned. Per prereg 6.1 the observed statistic is per source–campaign
Λ, maximized over the six pairs; FAPs come later from the Section 6.2
calibration (multi-server cluster, in development). Section 4.7 joint
multi-campaign likelihoods are not needed for Λ*; cross-campaign alias
clearing (5.4) is applied at the peak-report level.

## Per-campaign inputs (all verified; windows via scripts/compute_alias_sets.py loaders)

| Campaign | Burst table | TOA column | S/N | ID | site (bary.py) |
| --- | --- | --- | --- | --- | --- |
| nancay20220912A | `data/raw/nancay_20220912A/Supplementary Material (online).csv` | `Time of arrival (MJD)` (bary TDB inf-freq) | `S/N` | `Burst ID` | nancay |
| astroflash20220912A | `data/raw/astroflash_20220912A/FRB20220912A_table_paper.csv` | `toa` (bary TDB inf-freq) | `peak_sn` | `id` (dedup by base ID per prereg 2.1 — 146 rows → 130 unique, keep highest-S/N station row) | per-station (stockert/westerbork_rt1/torun/onsala85) |
| fast20240114A | `data/raw/fast_20240114A/FRB20240114A_SuppTab2.csv` | `MJD(bary@inf freq.)` | flux col as brightness proxy if no S/N (check `Flux(mJy)`) | `BurstID` | FAST |
| fast20201124A_sepoct | `phase1/windows/fast20201124A_sepoct_bursts.csv` | `toa_mjd_bary_inffreq` | `snr` | `burst_no` (row 108 has two component rows → merge rule) | FAST |
| tmrt20240114A | `data/raw/tmrt_20240114A/apjadfecet3_mrt.txt` fixed-width: bytes 1-4 Name, 6-20 Epoch (bary MJD inf-freq), 28-32 S/N | Epoch | S/N | Name | tianma65 (bary.py supplementary) |
| effelsberg20200120E | `phase1/windows/effelsberg20200120E_bursts.csv` | `toa_mjd_bary_tdb_inffreq` | (storm IDs; no cross-table dupes remain) | `burst_id` | effelsberg |

## Frozen construction rules (prereg 2.1/2.2)

1. Event = trigger event: merge rows with peak times < 100 ms apart (same
   campaign); event time = peak time of brightest component (S/N column).
   AstroFlash: dedup by published base burst ID FIRST (never time-window).
2. Windows: topocentric session edges → BJD_TDB via `phase1/bary.py`
   (DE440, per-campaign site, source position). Coarse (≲ arcmin) positions
   suffice: window-edge error < 0.2 s ≪ σ_v,min = 60 s — document in output.
   Positions: 20220912A 23:09:04.9 +48:42:25.4; 20240114A 21:27:39.8
   +04:19:45.6; 20201124A 05:08:03.5 +26:03:38.4; 20200120E 09:57:54.699
   +68:49:00.85 (VLBI, frozen in pin).
3. AstroFlash multi-station: each station's sessions convert with its own
   site; W(t) = concatenated GTIs (summed exposure, as in the alias
   artifacts); events = deduped union.
4. Scan: `scankernel.lambda_stat_c` per campaign with FULL config
   (p_min=1h, σ_min=60s, `pl.frozen_tau_grid()`, m1_kw n_periods=200
   n_phase=24). For a ranked peak list, run the M2/M3 scans per OCTAVE
   (monkeypatch `pl.scanner_grids` octave subsets, in order) recording each
   octave's (ll, arg); Λ per campaign = identical max. Flag every peak with
   `pl.alias_flag` (and cross-check against the committed alias artifacts).
5. Output: `phase1/confirmatory_results.json` — per campaign: n_events
   (before/after merge), converted-window checksums, per-octave M2/M3
   peaks with alias flags, ll table (M0/M1/M4/M5), Λ; study-wide
   Λ* = max. Reference conversion assert (environment_pin) before windows.
6. Compute: sepoct ≈ 20 min; FAST 20240114A grid is 46× sepoct (~8-15 h);
   TMRT/Effelsberg several h each; Nançay/AstroFlash ~1-2 h. Run
   sequentially in background, checkpoint per campaign (skip if its JSON
   section exists).
7. FAP/calibration (Section 6.2, 1,000+ sims/family × full search over all
   six pairs) is the cluster job — runner design must let the same
   per-campaign scan be driven by simulated streams unchanged.

Contamination check (Section 7: pulsar/RRAT catalogs, RFI logs) applies to
any reported candidate before publication.
