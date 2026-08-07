# Pre-Registration H2/H3: Morphology and Full-Cutout Archival Search

_Version 0.4-draft — incorporates the Phase 0 novelty-audit findings ([novelty_audit.md](novelty_audit.md)). **H1 has been split into its own separately frozen preregistration, [prereg_h1.md](prereg_h1.md)**, so Phase 1 gates on `prereg-h1-v1.0` while this document remains an explicitly draft H2/H3 specification. It becomes frozen at git tag `prereg-h2h3-v1.0`, before any confirmatory target data for H2/H3 are examined._

_Scope decision (2026-08-07): this project uses public data only. All collaboration- or request-gated data products (candidate graveyards, request-only baseband, proprietary archives) are out of confirmatory scope and deferred to the post-project follow-up phase of [project_plan.md](../notes/project_plan.md)._

_Derives from [The_Bursty_Beacon_Search.md](../notes/The_Bursty_Beacon_Search.md) (Sections 4.3, 8, 9, 10) and [project_plan.md](../notes/project_plan.md) (Phases 1–3)._

## Status and freeze policy

- This document is versioned in git. The freeze is the git tag `prereg-h2h3-v1.0`.
- After freeze, changes require a new major version with a written justification, and any analysis run under a superseded version must be reported as exploratory, not confirmatory.
- **No confirmatory target data may be examined before freeze.** Permitted before freeze: published papers; catalog metadata used only to verify availability and schema; instrument documentation; and development/control datasets explicitly designated in Section 6. Every development/control dataset examined before freeze is permanently excluded from confirmatory testing under this version.
- This draft is **explicitly not frozen** and does not gate Phase 1. It gates Phases 2–3, and remains draft until the remaining H2/H3 freeze items (processing-chain freezes, pair-sampling design, holdout definition, quantile stability, statistic appendices, and the per-instrument selection-function matrix) are closed.

## 1. Hypotheses under test

**H1 (repeater scanner model)** is specified, with its exact likelihoods, sample rules, grids, statistic, and calibration procedure, in the standalone [prereg_h1.md](prereg_h1.md), frozen independently as `prereg-h1-v1.0`. It is listed here only for completeness of the hypothesis family.

**H2 (copy-exact morphology).** At least one cataloged source in the Galactic single-pulse / RRAT / FRB streams emits burst pairs whose morphological similarity, under channel-commutative transformations only, exceeds the calibrated natural null at global significance.

**H3 (attached off-manifold structure).** At least one saved candidate cutout contains structured emission outside the dedispersed-pulse window (including inverted or non-ν⁻² sweeps) inconsistent with noise and RFI nulls.

The expected outcome for all three is null; the confirmatory product of a null is a constraint per Section 14 of the research note.

## 2. Statistics proposed for freeze

### 2.1 Repeater timing (H1)

Moved in full to [prereg_h1.md](prereg_h1.md): exact M0–M5 likelihoods, event and time definitions, confirmatory sample restricted to campaigns with complete public observing logs, duty-cycle-tied grids, frozen alias sets, the single likelihood-ratio statistic, staged maximum-statistic calibration, contamination control, synthetic acceptance tests, and the prospective-validation rule.

### 2.2 Copy-exactness (H2) — transformed pairwise correlation

For each pair of dedispersed, locally normalized components x₁, x₂ (within one event or across events of one source):

R = max over θ of ⟨x₂, T_θ x₁⟩ / (‖x₂‖ ‖T_θ x₁‖)

**Primary transformation family proposed for freeze, T_θ (channel-commutative under a scalar LTI response, per note Section 4.3):**

1. time delay (continuous, sub-sample by Fourier shift);
2. overall amplitude scale, absorbed analytically by the normalization in R rather than counted as a searched parameter;
3. smooth frequency-dependent gain (low-order polynomial in log ν, order ≤ 3);
4. compositions of the above.

Polarization rotation or swap is a **calibrated secondary analysis**, not part of the primary channel-commutative family. It may become confirmatory only if the applicable Jones/Mueller calibration, transformation parameterization, and proof or assumption of commutation are frozen before the relevant data are examined; otherwise it remains exploratory.

**Explicitly excluded from the confirmatory search** (exploratory only, flagged as such): time reversal, time dilation, non-ν⁻² dispersion re-mapping, spectral inversion, and any code/symbol-level transformation. These do not commute with an unknown LTI propagation channel or expand the trials space beyond the calibrated budget.

**Prior-art boundary (per the novelty audit):** the untransformed coherent delayed copy—s(t) + ε·s(t−τ), equal ε in both polarizations, delays ~0.3 μs–100 ms—was searched on 172 FRBs by Leung/Kader et al. 2022 (PRD 106, 043016/043017) with null result. The plain delay-plus-scale part of our family overlaps that searched region and is retained as a control/completeness search, not claimed as novel. Novelty claims apply only to the additional, explicitly frozen transformed-repetition tests.

**Null conditioning (mandatory):** the copy-exactness null distribution is conditioned on (a) pair time-lag relative to the source's measured or estimated scintillation timescale — pairs within one scintillation time are analyzed separately and flagged propagation-suspect; (b) S/N of both components; (c) effective time resolution after dispersion smearing. The primary statistic is computed on spectrum-marginalized (frequency-collapsed) waveforms, with the joint time-frequency version reported as a secondary statistic; where scattering is measurable, a descattered variant is also computed. Rationale: ISM impulse-response imprinting, scintillation spectral correlation, and the FRB 20240114A "carbon-copy" pair phenomenology (arXiv:2602.16409 vs 2607.02939) are documented natural routes to high pairwise similarity.

**Coherence discriminator:** for any high-R pair with voltage data, the Kader et al. 2025 test is applied — propagation-induced similarity correlates in |power| but not in phase; a genuine coherent copy correlates in both. Phase-incoherent pairs are demoted to propagation candidates.

Secondary statistics proposed for freeze on the same data:

- ΔL (minimum-description-length): L_natural − L_structured, with the natural model class and structured model class fixed in an appendix before freeze.
- Repeated-timing-motif score: repeated subsequences in the symbolized component sequence {t_k, w_k, F_k, ν_k} under translation and single global scaling.

### 2.3 Full-cutout-extent search (H3)

On every saved cutout, over its full retained time extent: matched-filter bank of chirps with dispersion sweeping ±(0 to 2×) the trigger DM including negative values, plus a generic structure detector (spectral-kurtosis-normalized power in the off-pulse region), thresholded against per-instrument off-pulse null distributions.

## 3. Data and search order proposed for freeze

Confirmatory archives, in order, per project plan Phase 1/3:

1. Campaign burst tables + published observing-session logs for the H1 sample ([prereg_h1.md](prereg_h1.md) Section 3).
2. Public Galactic single-pulse / pulsar / RRAT cutout streams (H2, H3).
3. Public total-intensity FRB dynamic spectra including full cutout extents (H2, H3).
4. Cross-observatory time-coincidence match of public candidate lists (supporting evidence only).

The concrete list of archives and version identifiers is fixed in [data_manifest.md](data_manifest.md) at freeze time, drawn from the Phase 0 inventory in [data_product_matrix.md](data_product_matrix.md). Primary H2/H3 candidates: the MeerTRAP Galactic-transient release (Zenodo 10.5281/zenodo.14646142), CHIME Cat 1/2 waterfalls, and the DSA-110 event archive. The CHIME/FRB Catalog 2 event table (DOI 10.11570/25.0066) supports H2/H3 morphology and rate checks; its use for confirmatory H1 timing is deferred to the post-project follow-up because the required time-resolved $W(t)$ is collaboration-gated (cumulative exposure maps do not satisfy the window requirement).

## 4. Held-out validation proposed for freeze

For H2/H3, each archive is split 50/50 by a deterministic hash of the event identifier (SHA-256 of the catalog ID, even/odd first byte). The search half may be examined freely under the frozen statistics; any candidate advanced from the search half must satisfy a separately frozen replication criterion in the confirmation half or an independent archive before being reported above Level 1 of the note's Section 9 evidence hierarchy. Cross-event pairs may be formed only within one split. Timing candidates (H1) do not use this event-hash split; their prospective temporal validation rule (cutoff, minimum additional exposure, minimum event count, stopping rule) is frozen in [prereg_h1.md](prereg_h1.md) Section 10.

## 5. Significance procedure proposed for freeze

- **Local p-values** from per-statistic null distributions built with only the hypothesis-appropriate, freeze-specified controls among: time-scrambled controls, frequency-scrambled controls, off-source/off-pulse data, and matched injected natural-transient simulations (cutout-level injection per project plan Phase 2). Any scrambling must preserve the relevant exposure, clustering, selection, and instrumental structure under its null.
- **Global false-alarm probability** is obtained from the distribution of the maximum statistic after rerunning the complete frozen search on each null simulation or valid permutation. The maximum spans all included sources/events, component pairs, transformation points, and statistics (H2: three statistics; H3: two statistics; the H1 equivalent is specified in [prereg_h1.md](prereg_h1.md) Section 6). A multiplicative trials-count approximation may be reported only as a diagnostic, not used for the confirmatory threshold.
- Reporting thresholds: candidates reported with global FAP < 1e-3 flagged for follow-up; the full ranked list published regardless of significance; both local and global FAPs stated for every reported number.
- The copy-exactness screening threshold is set from the designated calibration campaign (Section 6) at the upper-tail $1-10^{-4}=0.9999$ quantile of the empirical natural null per pair, before any confirmatory RRAT/FRB data are examined. This screening threshold does not replace the study-wide maximum-statistic calibration above.

## 6. Calibration prerequisites (gates before the archival sweep)

1. **Copy-exactness calibration:** distribution of R computed on the following designated calibration ladder (public products to be enumerated in the manifest; see [data_product_matrix.md](data_product_matrix.md)), spanning the known fat-tail mechanisms:
   - MeerKAT TPA single-pulse census (1,192 pulsars, typically ~1,000 pulses each, full Stokes; processed release normally 16 frequency channels and 1,024 phase bins per period)—population null for ordinary pulsars, including strong/weak scintillation regimes;
   - Parkes Transient DB II (165k single pulses) — archival-era instrumental null;
   - B1937+21 and Crab giant-pulse baseband — the propagation-imprint regime (unresolved impulses sharing the ISM impulse response within one scintillation time);
   - FAST FRB 20201124A atlas and the specifically enumerated public FRB 20240114A burst sets—the repeating-FRB development-control regime including documented "carbon-copy" pairs. Any event or source used here is excluded from the confirmatory H2 sample under v1.0.

   Gate: if the null has a fat tail attributable to scintillation, propagation imprinting, or instrumental correlation such that the 0.9999 quantile exceeds R = 0.95 under any adequately sampled lag/S/N/resolution condition, H2's statistic is redesigned before v1.0; if v1.0 has already been frozen, the redesign requires v2.0 before any confirmatory claim. Minimum calibration counts and uncertainty intervals for this quantile must be frozen before v1.0.
2. **Timing-model recovery:** moved to [prereg_h1.md](prereg_h1.md) Section 9 (synthetic acceptance tests gating the `prereg-h1-v1.0` tag).
3. **Injection recovery for H3:** synthetic attached components injected into real off-pulse cutout noise. The detection threshold is set by the frozen false-alarm criterion; the fluence at which recovery reaches 90% is then measured and reported. If the faintest published component lies below that sensitivity, the shortfall is reported rather than changing the threshold after seeing the injections.

## 7. Deviations log

Any deviation from this specification is recorded in `phase0/deviations.md` with date, reason, and whether affected analyses are demoted to exploratory.

---

_To be completed before the `prereg-h2h3-v1.0` freeze: the H2/H3 sections of [data_manifest.md](data_manifest.md) (archives, files, checksums, schemas, licenses, time standards, and versions); the frozen H2 processing chain and pair-sampling design; MDL and H3 statistic appendices; calibration-source and development-control lists; the per-instrument selection-function matrix for each confirmatory archive; and exact software commit hashes. H1 freeze artifacts are tracked in [prereg_h1.md](prereg_h1.md)._
