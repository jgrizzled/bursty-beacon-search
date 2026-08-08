# Pre-Registration H2–H4: Morphology, Full-Cutout, and Phase-Residual Archival Search

_Version 0.5-draft — incorporates the Phase 0 novelty-audit findings ([novelty_audit.md](novelty_audit.md)) and, as of 2026-08-07, the rev3 thesis extension ([The_Bursty_Beacon_Search.md](../notes/The_Bursty_Beacon_Search.md) Section 16): hypothesis H4 (phase-residual structure) and the host-distance sub-priority for the FRB streams. **H1 has been split into its own separately frozen preregistration, [prereg_h1.md](prereg_h1.md)**, so Phase 1 gates on `prereg-h1-v1.0` while this document remains an explicitly draft H2/H3/H4 specification. It becomes frozen at git tag `prereg-h2h3h4-v1.0`, before any confirmatory target data for H2/H3/H4 are examined._

_Scope decision (2026-08-07): this project uses public data only. All collaboration- or request-gated data products (candidate graveyards, request-only baseband, proprietary archives) are out of confirmatory scope and deferred to the post-project follow-up phase of [project_plan.md](../notes/project_plan.md)._

_Derives from [The_Bursty_Beacon_Search.md](../notes/The_Bursty_Beacon_Search.md) (Sections 4.3, 8, 9, 10) and [project_plan.md](../notes/project_plan.md) (Phases 1–3)._

## Status and freeze policy

- This document is versioned in git. The freeze is the git tag `prereg-h2h3h4-v1.0`.
- After freeze, changes require a new major version with a written justification, and any analysis run under a superseded version must be reported as exploratory, not confirmatory.
- **No confirmatory target data may be examined before freeze.** Permitted before freeze: published papers; catalog metadata used only to verify availability and schema; instrument documentation; and development/control datasets explicitly designated in Section 6. Every development/control dataset examined before freeze is permanently excluded from confirmatory testing under this version.
- This draft is **explicitly not frozen** and does not gate Phase 1. It gates Phases 2–4, and remains draft until the remaining H2/H3/H4 freeze items (processing-chain freezes, pair-sampling design, holdout definition, quantile stability, statistic appendices, the H4 phase-model appendix, and the per-instrument selection-function matrix) are closed.

## 1. Hypotheses under test

**H1 (repeater scanner model)** is specified, with its exact likelihoods, sample rules, grids, statistic, and calibration procedure, in the standalone [prereg_h1.md](prereg_h1.md), frozen independently as `prereg-h1-v1.0`. It is listed here only for completeness of the hypothesis family.

**H2 (copy-exact morphology).** At least one cataloged source in the Galactic single-pulse / RRAT / FRB streams emits burst pairs whose morphological similarity, under channel-commutative transformations only, exceeds the calibrated natural null at global significance.

**H3 (attached off-manifold structure).** At least one saved candidate cutout contains structured emission outside the dedispersed-pulse window (including inverted or non-ν⁻² sweeps) inconsistent with noise and RFI nulls.

**H4 (phase-residual structure).** At least one source with coherently captured voltage data exhibits, after coherent dedispersion and channel-response equalization, residual carrier-phase structure that is repeated or deterministic across bursts — repeated modulation patterns, non-random phase trajectories, or low-description-length phase structure — inconsistent with the emission, propagation, and instrumental phase nulls of Section 6.

_H4 motivation (research note rev3 Sections 8.6 and 16.6):_ under the collapsed discovery/message architecture, the entire message layer of an extragalactic beacon is phase modulation of the chirped carrier — invisible in intensity data, present in voltage data at zero marginal transmit energy. The corresponding archival statistic is exactly this one, in baseband recorded for scattering and emission-physics studies. Under the rev3 spatial prior, priority goes to repeaters localized to nearby hosts, nearest first. Data-availability verification (2026-08-07, [data_product_matrix.md](data_product_matrix.md) Section 8) found the thesis first target, FRB 20200120E, has no public voltage data — all its voltage sets are request-only and deferred to the follow-up — so the confirmatory public-scope H4 sample leads with FRB 20180916B (149 Mpc; CHIME Baseband Catalog 1 bursts, LOFAR complex voltages), then the remaining CHIME baseband sample. An H4 null is independently publishable as a constraint on coherent burst-emission physics.

The expected outcome for all four is null; the confirmatory product of a null is a constraint per Section 14 of the research note.

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

### 2.4 Phase-residual structure (H4) — statistics proposed for freeze

Per burst with complex voltage data: coherently dedisperse at a frozen per-source DM; estimate and remove a smooth channel/instrumental phase response (fit family and order frozen in the H4 appendix before any confirmatory data); form the residual analytic phase trajectory φ(t) and instantaneous-frequency residual over the burst's high-S/N support. Three statistics proposed for freeze:

1. **Cross-burst phase-trajectory correlation:** normalized correlation of residual phase (and instantaneous-frequency residual) between burst pairs of one source, maximized over time alignment and a constant phase offset only — the channel-commutative trials discipline of Section 2.2 carries over; no warps, no reversal, no code-level remapping in the confirmatory family.
2. **Phase MDL:** ΔL_φ = L_stochastic − L_structured, comparing a stochastic-phase model class (amplitude-modulated noise phase; phase random walk plus scintillation-screen rotation) against compact deterministic generators (repeated symbol blocks, polynomial chirp residuals beyond the ν⁻² law, small-alphabet phase-shift structure). Both model classes fixed in the H4 appendix before freeze.
3. **Surrogate determinism test:** nonlinear-prediction error on φ(t) compared against phase-randomized surrogates that preserve the intensity envelope and power spectrum.

**Relation to prior art:** the Kader et al. 2025 phase-coherence discriminator (power-correlated but phase-incoherent ⇒ propagation) is subsumed as a veto; H4 searches for the opposite signature — structure *in* phase. The cold-plasma transfer-function test (research note Appendix C) is the zeroth-order case: does the emitted field replicate the exact ν⁻² phase law; H4 generalizes it to structured departures. Novelty is conditional on the audit item 5 of [novelty_audit.md](novelty_audit.md).

**Null conditioning (as H2, mandatory):** pair time-lag relative to the scintillation timescale, S/N of both bursts, and effective post-dedispersion resolution. Phase statistics are computed only over samples above a frozen intensity threshold (phase of noise-dominated samples is meaningless and must not enter the statistic).

## 3. Data and search order proposed for freeze

Confirmatory archives, in order, per project plan Phase 1/3:

1. Campaign burst tables + published observing-session logs for the H1 sample ([prereg_h1.md](prereg_h1.md) Section 3).
2. Public Galactic single-pulse / pulsar / RRAT cutout streams (H2, H3) — the galactic-builder delivery stream (note Section 4.4).
3. Public total-intensity FRB dynamic spectra including full cutout extents (H2, H3) — co-primary with item 2 under the two-builder mapping (note Section 16.4); within the FRB streams, repeaters localized to nearby hosts are searched first, ordered by host distance (host-distance table frozen in the manifest).
4. Public voltage/baseband sets (H4; also the H2 coherence discriminator): the sets verified public in [data_product_matrix.md](data_product_matrix.md), with nearby-host repeater baseband first under the rev3 prior.
5. Cross-observatory time-coincidence match of public candidate lists (supporting evidence only; note Section 16.5 — the simultaneity weight is scale-dependent and serves the galactic builder class primarily).

The concrete list of archives and version identifiers is fixed in [data_manifest.md](data_manifest.md) at freeze time, drawn from the Phase 0 inventory in [data_product_matrix.md](data_product_matrix.md). Primary H2/H3 candidates: the MeerTRAP Galactic-transient release (Zenodo 10.5281/zenodo.14646142), CHIME Cat 1/2 waterfalls, and the DSA-110 event archive. The CHIME/FRB Catalog 2 event table (DOI 10.11570/25.0066) supports H2/H3 morphology and rate checks; its use for confirmatory H1 timing is deferred to the post-project follow-up because the required time-resolved $W(t)$ is collaboration-gated (cumulative exposure maps do not satisfy the window requirement).

## 4. Held-out validation proposed for freeze

For H2, H3, and H4, each archive is split 50/50 by a deterministic hash of the event identifier (SHA-256 of the catalog ID, even/odd first byte). The search half may be examined freely under the frozen statistics; any candidate advanced from the search half must satisfy a separately frozen replication criterion in the confirmation half or an independent archive before being reported above Level 1 of the note's Section 9 evidence hierarchy. Cross-event pairs may be formed only within one split. Timing candidates (H1) do not use this event-hash split; their prospective temporal validation rule (cutoff, minimum additional exposure, minimum event count, stopping rule) is frozen in [prereg_h1.md](prereg_h1.md) Section 10.

## 5. Significance procedure proposed for freeze

- **Local p-values** from per-statistic null distributions built with only the hypothesis-appropriate, freeze-specified controls among: time-scrambled controls, frequency-scrambled controls, off-source/off-pulse data, and matched injected natural-transient simulations (cutout-level injection per project plan Phase 2). Any scrambling must preserve the relevant exposure, clustering, selection, and instrumental structure under its null.
- **Global false-alarm probability** is obtained from the distribution of the maximum statistic after rerunning the complete frozen search on each null simulation or valid permutation. The maximum spans all included sources/events, component pairs, transformation points, and statistics (H2: three statistics; H3: two statistics; H4: three statistics; the H1 equivalent is specified in [prereg_h1.md](prereg_h1.md) Section 6). A multiplicative trials-count approximation may be reported only as a diagnostic, not used for the confirmatory threshold.
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
4. **Phase-residual null calibration and injection (H4):** the three H4 statistics computed on (a) B1937+21 and Crab giant-pulse baseband — the propagation-imprint phase null (shared with item 1); (b) off-pulse voltage segments from the same recordings — the instrumental/local-oscillator phase null; (c) simulated amplitude-modulated-noise bursts passed through measured channel responses — the emission-model phase null. Gate: if deterministic-looking phase structure arises in any natural or instrumental null at rates that would swamp the frozen threshold, the H4 statistics are redesigned before freeze. Injection: synthetic phase-modulated chirps (small-alphabet phase-shift blocks, fountain-coded block repetition across bursts) injected at a grid of modulation depths and S/N into real off-pulse voltage noise; the recoverable (depth, S/N) region is measured and reported with any H4 null. Voltage-domain events used for calibration here are excluded from the confirmatory H4 sample.

## 7. Deviations log

Any deviation from this specification is recorded in `phase0/deviations.md` with date, reason, and whether affected analyses are demoted to exploratory.

---

_To be completed before the `prereg-h2h3h4-v1.0` freeze: the H2/H3/H4 sections of [data_manifest.md](data_manifest.md) (archives, files, checksums, schemas, licenses, time standards, and versions, including the host-distance table and the verified nearby-host baseband products); the frozen H2 processing chain and pair-sampling design; MDL and H3 statistic appendices; the H4 appendix (channel-phase fit family and order, stochastic and structured phase model classes, intensity threshold for phase support); calibration-source and development-control lists; the novelty-audit item 5 result (phase-domain prior art) gating H4's novelty language; the per-instrument selection-function matrix for each confirmatory archive; and exact software commit hashes. H1 freeze artifacts are tracked in [prereg_h1.md](prereg_h1.md)._
