# Deviations Log

_Applies to analyses run after the corresponding freeze tag: `prereg-h1-v1.0` for H1 analyses ([prereg_h1.md](prereg_h1.md)), `prereg-h2h3h4-v1.0` for H2/H3/H4 analyses ([preregistration.md](preregistration.md)). Append entries; do not rewrite prior entries._

No procedure deviations have been recorded. (The H2/H3/H4 preregistration remains a draft, so its pre-freeze revisions belong in version history, not in this log.)

| Date | Preregistration version | Change | Reason | Affected analyses/results | Classification after change | Commit |
| --- | --- | --- | --- | --- | --- | --- |

## Data-handling notes (post-tag, prereg-h1-v1.0; no frozen procedure changed)

Recorded per the S2 "within verified windows" criterion and the prereg 2.2 conversion rules as frozen; these are documented applications of frozen rules to published-data inconsistencies discovered at first confirmatory data contact (2026-08-09), not deviations. Full machine-readable detail is in `phase1/confirmatory_results.json` (per-campaign `events` / `windows.containment` blocks) and the `EDGE_TOL_S` comment in `phase1/confirmatory.py`.

1. **Nançay 20220912A TOA frame correction.** The `Supplementary Material (online).csv` column `Time of arrival (MJD)` is empirically **topocentric**, not barycentric TDB as annotated in `phase1/CONFIRMATORY_PLAN.md`: 639/640 merged events lie inside the topocentric session log (whose start values equal the candidate-file filterbank `tstart`s), while the barycentric reading places 84/640 outside the converted windows. Handled by the prereg 2.2 frozen path for topocentric inputs (topo UTC → BJD_TDB, DE440, Nançay site, frozen position). Residual reference-frequency ambiguity ≤ ~1 s ≪ σ_v,min = 60 s.
2. **Event exclusions under S2 "within verified windows"** (published burst table vs published session log inconsistencies; keeping such events would also bias Λ, since phase-folded models count them while the per-session M4/M5 likelihoods skip them):
   - Nançay **B602** (TOA 59900.827, the table's only 3-decimal entry): ≥ 160 s after its same-day session end on either time axis.
   - AstroFlash **B39-st, B67-st**: single-station Stockert rows ~5,000 s outside every logged scan of any station, in both the reduced 508-session log and the 5,842-row per-scan log. (Observation only: a −2 h shift would place both inside Stockert scans, but this does not match CET for the November burst; no repair applied.)
3. **Session-edge tolerance (30 s) for the prereg 4.1 containment check.** Two documented convention mismatches: (a) infinite-frequency TOAs can precede converted session starts by the intra-band dispersion sweep (~2.2 s max across the sample); (b) the FAST 20240114A release's published stop times end before its own last burst TOAs in ~33 sessions by up to 23.6 s (Zhou 111-row and Zhang 57-row logs agree to ~1 s, so this is nominal-vs-actual recording stop in the release). Events within 30 s (≪ σ_v,min = 60 s) are kept at their published times and reported (59 such events for FAST 20240114A, 1 for FAST 20201124A Sep–Oct); the frozen windows and TOAs are unmodified. Beyond 30 s, the S2 exclusion above applies, guarded by a max(3, 1%) abort against systematic frame errors.

