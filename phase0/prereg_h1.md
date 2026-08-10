# Pre-Registration H1: Repeater Scanner-Model Timing Test

_Version 0.1-draft of the standalone H1 preregistration, split from [preregistration.md](preregistration.md) so that Phase 1 can freeze independently of the H2/H3 decisions. It becomes frozen at git tag `prereg-h1-v1.0`._

_Scope decision (2026-08-07): this project uses public data only. The CHIME/FRB time-resolved exposure request is deferred to the post-project follow-up; the confirmatory sample here is restricted to sources with complete published observing-session logs. A full-Catalog-2 analysis under obtained good-time intervals is a follow-up-paper analysis under a future major version, not a permitted post-hoc extension of this one._

## Status and freeze policy

- Versioned in git; the freeze is the tag `prereg-h1-v1.0`.
- After freeze, changes require a new major version with written justification; analyses under superseded versions are exploratory.
- **No confirmatory target data may be examined before freeze.** Permitted before freeze: published papers; catalog metadata used only to verify availability and schema; instrument documentation; positive-control data designated in Section 3.3 (which are thereby excluded from the confirmatory sample); and synthetic data. Until the tag exists, only synthetic-data recovery and null-calibration checks may run.
- Remaining pre-freeze work is listed in the freeze checklist at the end of this document. This draft contains the complete H1 specification but is not frozen until the data manifest verification and synthetic acceptance tests of Sections 8–9 are complete.

## 1. Hypothesis

**H1 (repeater scanner model).** The burst arrival times of at least one source in the confirmatory sample, folded through its verified observing-window function, are better explained by a periodic-scanner (M2) or paired-pass-scanner (M3) point-process model than by every natural alternative (M0 homogeneous Poisson, M1 activity-window, M4 Weibull-clustered, M5 session-nonstationary), at study-wide false-alarm probability < 10⁻³.

_Scoping (per [novelty_audit.md](novelty_audit.md); must-cite list extended 2026-08-07 by the logged search re-execution, audit A.4):_ framed as a generative-model comparison, not a first-ever periodicity search. Must-cite-and-distinguish: CHIME/FRB 2020 (Nature 582, 351), CHIME/FRB 2023 (ApJ 947, 83), and Zhang et al. 2025 (arXiv:2507.14708 — joint multi-session short-period search on FRB 20240114A, without exposure folding or scanner models; the nearest neighbor to this analysis). The novel elements claimed are the complete likelihood comparison among the specified point processes, the paired-pass structure, and the exposure-folded, alias-aware sub-day regime on discontinuous campaign windows. Expected outcome: null; the confirmatory product of a null is a constraint on the M2/M3 family over the searched parameter space (research note Section 14).

_Builder-class framing (pre-freeze note, 2026-08-07; research note rev3 Section 16):_ the confirmatory sample consists of genuine-FRB repeaters with host associations — the delivery stream the rev3 thesis predicts for the extragalactic builder class, whose timing tags (exposure-folded strict periodicity, paired-pass structure) carry over unchanged from the galactic analysis. One distance caveat is recorded: the rev3 spatial prior favors hosts within the gain-dependent beam-filling horizon (tens of Mpc at plausible gains), while the verified-log sample sits at roughly 350–600 Mpc (20220912A z ≈ 0.077, 20201124A z ≈ 0.098, 20240114A z ≈ 0.13). These sources remain fully confirmatory — the horizon scales with transmitter gain and the sample is set by log availability, not by the prior — but the closer expectation must be stated as a scope limitation in any null interpretation, and nearer-host repeaters (first: FRB 20200120E in M81, 3.6 Mpc) are the thesis-preferred targets if a campaign satisfying S1–S5 is verified before freeze.

## 2. Unit of analysis and time definitions

### 2.1 Event definition

- The unit of analysis is one **trigger event**, not a fitted sub-burst row. Sub-burst components listed separately in a source table are merged into one event when their peak times (at the same instrument, same pointing) are separated by **< 100 ms**; the event time is the peak time of the brightest component. Rationale: the documented bimodal waiting-time distribution of hyperactive repeaters separates intra-event structure (≲ 100 ms) from independent bursts (≳ seconds); the merge threshold sits in the gap.
- **No cross-instrument event matching is performed in v1.0.** Each confirmatory analysis is per-campaign, per-instrument; the same source observed in two campaigns contributes two independent window functions and event lists, combined only at the likelihood level (Section 4.7). This removes the duplicate-matching rule from the critical path.
- **Within a multi-telescope campaign release**, bursts co-detected at more than one station are deduplicated by the release's own published burst identifier, never by a time-window merge (verified inter-station TOA offsets of 0.1–0.55 s in the AstroFlash release would defeat any sub-second window; manifest 1.2c). The retained row is the highest-S/N station's; each station's sessions still enter W(t) separately.
- Duplicate rows within one campaign table (same burst listed twice, e.g. in a main and supplementary table) are resolved in favor of the machine-readable table named in `data_manifest.md`.

### 2.2 Arrival-time processing

- **Inputs:** published per-burst topocentric arrival times with the reference frequency stated by the source paper, recorded per-campaign in `data_manifest.md`.
- **Dispersion correction:** arrival times are referred to infinite frequency using Δt = 4.15 ms × DM × ν_ref,GHz⁻², with one frozen per-source DM (the campaign-paper reference DM, recorded in the manifest). Per-burst DM variation is ignored; its effect (≲ tens of ms for the sampled sources) is included in the timing-jitter term of the synthetic recovery tests.
- **Barycentric conversion:** topocentric UTC → BJD_TDB using `astropy.time` with solar-system ephemeris **DE440** and observatory ITRF coordinates from the astropy sites registry (FAST, Parkes, Effelsberg, CHIME as applicable). Exact astropy/erfa versions are pinned in the manifest at freeze.
- **Localization-uncertainty propagation:** for each source, draw 256 sky positions from the published localization region (Gaussian or contour as published); recompute the barycentric correction for each draw; define σ_bary as the maximum over events of the standard deviation of the correction. The per-source minimum searchable period is P_floor = 20 × σ_bary (phase error < 5% of a period). Sources in this sample are interferometrically or FAST-localized (≲ arcminute), giving σ_bary ≪ 1 s, so P_floor is far below the 1-hour grid floor; the rule exists to make that check explicit and frozen.

## 3. Confirmatory sample

### 3.1 Inclusion criteria (frozen without reference to any period-search output)

A source–campaign pair enters the confirmatory sample iff all of:

- **S1 (window completeness):** a published, machine-readable observing log provides UTC start and stop for **every** session of the campaign covering the analyzed burst set, with live/dead status, meeting the manifest schema of Section 8. Cumulative exposure totals do not qualify. Sessions with unstated instrument configuration changes are marked dead.
- **S2 (event count):** ≥ 20 events (Section 2.1 definition) within verified windows.
- **S3 (window leverage):** ≥ 10 distinct sessions spanning a baseline ≥ 14 days.
  _Pre-freeze revision (2026-08-07): originally ≥ 30 days; relaxed on data-availability grounds after the verification pass showed the FAST 20201124A Sep–Oct 2021 campaign (18 sessions, ~22-day baseline) meets every other criterion. The revision was made before any period-search output existed on any candidate. It is safe by construction: the searchable period range self-limits through P_max = T_span/3 (Section 5.1), so a shorter baseline narrows the period grid rather than weakening the test._
- **S4 (not a known-periodic source):** sources with a published activity-window period are assigned to the positive-control set (Section 3.3), not the confirmatory sample.
- **S5 (localization):** P_floor < 1 h under Section 2.2.

### 3.2 Candidate confirmatory campaigns (verification pass completed 2026-08-07; see `data_manifest.md` Section 1)

Verified against S1 content requirements (final freeze pends checksums, extraction scripts, and schema hashes):

- **FRB 20220912A — Nançay ÉCLAT campaign** (Konijn et al. 2024): machine-readable session log and burst table on Zenodo (CC-BY); 696 bursts, 68 sessions, ~6-month baseline. **Verified.**
- **FRB 20240114A — FAST Key Science Project campaign** (Zhang et al. / Zhou et al. 2025): 111-session log with start/stop MJD including zero-burst sessions; 11,553-burst CSV (MIT) with barycentric infinite-frequency TOAs. **Verified.**
- **FRB 20201124A — FAST 2021 Sep–Oct campaign** (RAA series, Zhou/Niu et al. 2022): 18-session log with UTC start + duration including null sessions; 624 analyzed bursts with barycentric infinite-frequency TOAs (DE438). **Verified** under the revised S3 (Section 3.1 revision note).
- **FRB 20220912A — AstroFlash multi-telescope campaign** (Ould-Boukattine et al. 2025): 508-session machine-readable log (`mjd_start`/`mjd_end` per session, four stations, non-detections included) + 130-unique-burst table with TDB barycentric infinite-frequency TOAs (Zenodo/GitHub, CC-BY). **Verified.** Co-detected bursts are deduplicated by the release's base burst ID, not by time-window merging (systematic 0.1–0.55 s inter-station TOA offsets; see manifest 1.2c).
- **FRB 20240114A — TMRT campaign** (Wang et al. 2025, ApJ 992, 185): 66-session MRT log (UTC start + duration, zero-burst sessions included) + 155-burst barycentric table, all open-access. **Verified.** Provides the materially-different-window instrument for FAST 20240114A alias clearing (Section 5.4).
- **FRB 20200120E — Effelsberg monitoring campaign** (Nimmo et al. 2023, MNRAS 520, 2281; Kirsten et al. 2022 and Pearlman et al. 2024 as log/TOA supplements): composed 46-session Effelsberg window list over a ~495-day baseline (MJD 59199–59694) + **69** barycentric TDB infinite-frequency TOAs, extracted from complete LaTeX tables in the arXiv sources by the frozen script. **Verified 2026-08-07** in the rev3-motivated nearest-host pass (added pre-freeze, before any period-search output existed for this source; manifest 1.7). This is the thesis-preferred nearest-host target (M81, 3.6 Mpc). S4 pass: no published activity-window period. The frozen handling rules (Pearlman-precedence window construction, cross-table burst deduplication with Pearlman's refined B1–B5 TOAs, the documented PR163A resolution, non-Effelsberg-run drops) are implemented as asserted extraction code; outcomes in manifest 1.7a. _Pre-freeze revision (2026-08-07, at extraction, before any scan): the initially recorded 42-session/60-burst figures were the Nimmo table alone; the frozen composition adds Pearlman's four additional Effelsberg sessions (two Dec 2020; the 2021-04-30 EDD session containing B6–B9; one May 2021) and the B1–B9 events, since excluding events inside verified windows would bias W(t)._ Statistical-power caveat: 53/69 bursts lie in a single ~2 h storm session (manifest 1.7a).

Pending candidates (decisions recorded in the manifest before freeze):

- FRB 20201124A — FAST 2021 Apr–Jun campaign (Xu et al. 2022): **excluded** (no published session log; session timing is graphical only).
- FRB 20220912A — FAST campaign (Zhang et al. 2023): **excluded** — the complete ScienceDB file inventory was enumerated and contains no session log (manifest 1.2b).
- FRB 20240114A — Parkes/Murriyang campaign (Uttarkar et al., arXiv:2602.16409): **excluded from confirmatory; designated exploratory** (decision 2026-08-07, manifest 1.4). Fails S1 as published; the public-DAP window reconstruction covers only the pre-embargo half; and the only machine-readable burst table is an unlicensed, incomplete GitHub subset with unstated barycentering — inadequate confirmatory provenance. The independent-window role for 20240114A is filled by TMRT. Revisit in the follow-up when the embargo lifts (~late 2026).

Any candidate failing verification is excluded before freeze and the exclusion recorded. If fewer than two source–campaign pairs survive, the freeze is paused and the sample criteria revisited **before** any scan (recorded as a pre-freeze revision, not a deviation). Six pairs are currently verified, so this condition is not triggered.

**Cross-hypothesis contamination rule:** FRB 20240114A and FRB 20201124A also appear in the H2 calibration/development-control ladder ([preregistration.md](preregistration.md) Section 6), and the Parkes 20240114A campaign paper is itself the carbon-copy-pair study. H2 calibration work on these sources must not begin until `prereg-h1-v1.0` is tagged and the H1 scan of the affected sources has run; the H2 exclusion of development sources applies to H2 only and does not bar their use here, but the ordering constraint does.

### 3.3 Positive controls (excluded from confirmatory testing)

- FRB 20180916B (CHIME 2020 TOAs; Sand et al. 2023 compilation) — M1 must recover the published ~16.35 d activity window.
- FRB 20121102A (Braga et al. 2025 epoch compilation; Cruces et al. 2021 Effelsberg logs; Li et al. 2021 FAST table) — M1 must prefer an activity window in the published ~150–160 d range.

These validate the pipeline (Section 9); they cannot generate confirmatory candidates under this version.

## 4. Generative models and likelihoods

### 4.1 Observation process

For each source–campaign pair, the window function W(t) is the union of verified good-time intervals [a_j, b_j]. No per-session sensitivity weights are used in v1.0 (none are published at manifest schema quality for the candidate campaigns); binary live/dead only. Session-to-session sensitivity variation is absorbed by the M5 natural model (Section 4.6) — this is the frozen sensitivity treatment; a probabilistic missing-exposure model was considered and rejected because it would change the scientific model and could not be introduced after examining period-search output.

All models except M4 are inhomogeneous Poisson processes with intensity λ(t); the observed-process log-likelihood is

ℓ = Σ_k log λ(t_k) − Σ_j ∫_{a_j}^{b_j} λ(t) dt,

with events outside W impossible by construction. Every intensity below is piecewise-constant in t, so all integrals are exact interval-overlap sums; no numerical quadrature is used.

### 4.2 M0 — homogeneous Poisson

λ(t) = λ, with λ > 0. One parameter; MLE closed-form: λ̂ = N / |W|.

### 4.3 M1 — activity-window repeater

Phase φ(t) = ((t − t₀) mod P_a)/P_a;
λ(t) = λ_in for φ < δ, λ_out otherwise.
Parameters and bounds: P_a ∈ [P_floor, T_span/3]; δ ∈ [0.05, 0.95]; t₀ ∈ [0, P_a); λ_in > λ_out ≥ 0. This is the published-phenomenology benchmark, fitted as a natural model, not a discovery model.

### 4.4 M2 — periodic scanner

Visits are boxcars centered at t₀ + nT with full width σ_v:
λ(t) = λ_v + λ_b inside any visit window, λ_b outside.
Parameters and bounds: T from the grid of Section 5; σ_v from the grid of Section 5 with σ_v/T ≤ 0.5; t₀ ∈ [0, T); λ_v > 0; background λ_b ∈ [0, ∞). The background component is a free Poisson floor (it lets the data, not the analyst, decide how many events the visit structure must explain); M2 therefore nests M0, which is handled by the simulation-based calibration, not by asymptotic χ² assumptions.

### 4.5 M3 — paired-pass scanner

As M2, with each visit doubled: boxcars at t₀ + nT and t₀ + nT + τ_c, both of width σ_v.
Parameters: those of M2 plus τ_c from the grid of Section 5, restricted to **τ_c ≤ T/2** (frozen identifiability rule; a confirmation lag longer than half the sweep period is degenerate with a phase-shifted shorter-period scanner). Where the pair windows of adjacent visits overlap (possible at the τ_c = T/2 boundary with large σ_v), intensities add by point-process superposition; no cap.

### 4.6 M4 — Weibull-clustered repeater, and M5 — session-nonstationary Poisson

**M4:** Weibull renewal process with shape k and rate r, thinned by W(t), with the likelihood conditioned on the observation windows following the analytic treatment of Oppermann, Yu & Pen 2018 (MNRAS 475, 5109), including integration over unobserved events in exposure gaps. Parameters: k ∈ [0.05, 5], r > 0. (k = 1 recovers M0.)

**M5 (nonstationarity robustness):** per-session gamma-mixed Poisson. Each session j has rate λ_j drawn i.i.d. from Gamma(α, β), marginalized analytically: the session event count is negative-binomial with mean αβ·|w_j| and the within-session arrival times uniform. Parameters: α, β > 0. M5 absorbs session-to-session rate and sensitivity variation of arbitrary origin. **Promotion rule:** a scanner model is a candidate only if it beats M0, M1, M4, **and** M5; a candidate that survives the first three but dissolves under M5 is reported as nonstationarity-suspect, not promoted.

### 4.7 Multi-campaign sources

If one source has two verified campaigns, the joint log-likelihood is the sum over campaigns with shared source-level parameters (T, σ_v, τ_c, k, r, α, β, P_a, δ) and per-campaign nuisance parameters (λ, λ_v, λ_b, λ_in, λ_out, β) where instrument sensitivity differs; t₀ is shared (a scanner phase is a property of the source, with the period-ambiguity of phase alignment across campaign gaps handled by the grid, not by freeing t₀ per campaign).

### 4.8 Optimization

Grid dimensions (T, t₀, σ_v, τ_c) are searched exhaustively (Section 5). Continuous rate/shape parameters are maximized at each grid point by L-BFGS-B from a frozen 3-point multi-start per parameter (0.5×, 1×, 2× the moment-based initial estimate), bounds as above. The same optimizer settings run on real and simulated data.

## 5. Search grids and alias handling

### 5.1 Period bounds

- P_max = T_span/3 per source–campaign (minimum three full cycles inside the observed baseline; frozen identifiability rule — a nominal 10-yr bound is not identifiable here and is not used).
- P_min = max(1 h, 2σ_v,min, P_floor).

### 5.2 Visit-width and lag grids

- σ_v grid: logarithmic, factor 2, from σ_v,min = 60 s up to 0.5·T (evaluated per period octave).
- τ_c grid (M3): logarithmic, factor 1.5, from 60 s to min(12 h, T/2).
- t₀ grid: step σ_v/2 over [0, T) for each (T, σ_v).

### 5.3 Period-grid spacing (tied to duty cycle, not Rayleigh spacing)

The frequency grid f = 1/T is piecewise-uniform per octave. Requirement: the accumulated visit-epoch drift across the baseline from a one-step frequency error must not exceed half the narrowest visit width in that octave: with Δf the spacing and T_oct the octave's maximum period,

Δf = σ_v,min / (2 · T_oct · T_span).

This resolves the narrowest allowed visit duty cycle by construction. Grid completeness is verified by injection (Section 9): ≥ 95% of injected scanners must yield a likelihood maximum within one grid step of truth.

### 5.4 Alias regions (frozen before any scan)

For each source–campaign, compute the normalized spectral window |W̃(f)|² = |Σ_j ∫_{a_j}^{b_j} e^{2πift} dt|² / |W|² on the search grid. The frozen alias set is:

- all frequencies n·(p/q)·f_d for n ∈ {1, 2}, p, q ∈ {1, 2, 3}, for **both** f_d = sidereal-day and solar-day frequency (campaign instruments are scheduled on the solar day; transit combs are sidereal);
- all f > 2/T_span at which |W̃(f)|² > 0.2 (window-function peaks).

A likelihood peak within 2/T_span of any alias-set frequency is reported **alias-contaminated**: it appears in the ranked list but cannot become a confirmatory candidate without data from an instrument or campaign with a materially different window function. The alias set is computed and committed before the first scan of real data.

_Property noted during acceptance testing (2026-08-07): for short-baseline campaigns the 2/T_span tolerance makes the day-rational alias set blanket much of the multi-day frequency range (e.g. the 22-day FAST 20201124A campaign flags nearly everything between ~2 d and ~4 d periods). This is the rule operating as designed — short windows genuinely cannot exclude day-commensurate aliases — and it means alias-clear discovery space comes primarily from the long-baseline campaigns (FAST 20240114A: tolerance ≈ 0.003 d⁻¹) and from cross-campaign confirmation between instruments._

## 6. Primary statistic and significance procedure

### 6.1 Primary statistic

One statistic, frozen (AIC is not used):

Λ = 2 · [ max(ℓ̂_M2, ℓ̂_M3) − max(ℓ̂_M0, ℓ̂_M1, ℓ̂_M4, ℓ̂_M5) ],

where each ℓ̂ is the profile maximum over that model's full frozen parameter space. The study-wide observed statistic Λ* is the maximum of Λ over all confirmatory source–campaign pairs.

### 6.2 Study-wide false-alarm calibration

For each natural null family F ∈ {M0, M1, M4, M5}:

1. Fit F to each confirmatory source–campaign pair.
2. Draw parameter sets from the Laplace approximation to the likelihood at the fit (propagating fit uncertainty into the null); truncate at the parameter bounds.
3. Simulate event streams through the **real** window functions.
4. Rerun the complete frozen search (all sources, both scanner models, full grids, identical optimizer) on each simulation and record its study-wide maximum Λ.

Global FAP_F = fraction of F-simulations with max Λ ≥ Λ*. The confirmatory false-alarm probability is **FAP = max_F FAP_F** (conservative-maximum rule, frozen). No independence or trials-count approximation is used for the confirmatory number; a multiplicative trials estimate may be reported as a diagnostic only.

**Simulation budget (staged, frozen):** 1,000 simulations per family; if Λ* falls below the 99th percentile of any family's null maxima, stop (FAP ≫ threshold, reported as such); otherwise extend to 10,000 per family so the 10⁻³ threshold is resolved. Nuisance parameters are refit in every simulation by the identical pipeline.

### 6.3 Detection and reporting

- Candidate: FAP < 10⁻³, not alias-contaminated, and survives the contamination check of Section 7.
- The full ranked list (all sources, all peaks, local and global FAPs, alias flags) is published regardless of outcome.
- A null is reported as an upper limit over the searched (T, σ_v, τ_c) space per research-note Section 14, stating exactly the sample and window functions it applies to.

## 7. Contamination check

Every timing candidate is cross-checked, before being reported, against cataloged pulsars and RRATs (ATNF psrcat, RRATalog) within the localization region and the instrument's sidelobe geometry, and against the campaign's RFI and instrument-state logs where published (the FRB 20191221A retraction lesson).

## 8. Data manifest requirements

Before freeze, `data_manifest.md` must contain, for every confirmatory and positive-control campaign:

- source identifier and sky-position version;
- the machine-readable burst table: URL/DOI, filename, version, size, checksum, license, schema, time standard, reference frequency;
- the observing-log table: UTC start/stop of every session, session identifier, live/dead state, applied quality or commissioning masks, instrument/pipeline configuration epochs, provenance, checksum, and the code used to construct it;
- target vs. positive-control status;
- a record of which files were inspected before freeze and why that inspection was permitted (schema verification only).

## 9. Synthetic recovery acceptance tests (pre-tag gate)

All on synthetic data drawn through the real verified window functions; all must pass before `prereg-h1-v1.0` is tagged:

1. **Null uniformity:** under each of M0, M1, M4, M5, single-source local p-values are uniform (KS test p > 0.01 on 1,000 simulations). _Pre-freeze correction (2026-08-07): null parameters for these pre-tag tests are set from **published per-session rates** (public metadata), not from fits to confirmatory event times — fitting real event data before the tag would violate the freeze policy. The real-data-fit calibration of Section 6.2 runs after the tag, as specified._
2. **Scanner recovery:** injected M2/M3 streams across the grid with ≥ 25 in-visit events: ≥ 90% recovered with the likelihood maximum within one grid step of the injected (T, τ_c); ≥ 95% of injected periods captured by the grid (Section 5.3 completeness).
3. **Alias flagging:** injected scanners at sidereal- and solar-rational periods are alias-flagged by the frozen rule.
4. **Positive controls:** M1 recovers the published FRB 20180916B activity window (period within published uncertainty) and prefers a ~150–160 d window for FRB 20121102A.
5. **Timing jitter:** recovery is stable when injected arrival times carry the Section 2.2 DM-correction and localization jitter.

Acceptance results are committed with the freeze artifacts.

## 10. Prospective validation

- **Cutoff:** the freeze date of `prereg-h1-v1.0`.
- **Validation data:** bursts of a candidate's source published after the cutoff, from campaigns whose logs meet the Section 8 schema.
- **Minimums:** ≥ 15 new events and ≥ 25% additional verified exposure for the candidate source.
- **Stopping rule:** evaluate once, when the minimums are met or 24 months after freeze, whichever comes first.
- **Test:** on validation data only, likelihood ratio of the scanner model with (T, σ_v, τ_c) **fixed at discovery values** (phase propagated; t₀ refit within one visit width) against the natural models refit on the validation data; significance from natural-model simulations through the validation windows; pass threshold p < 0.01.
- If the minimums are not reached, the result is reported as discovery-set evidence, not independently confirmed.

## 11. Deviations

Post-freeze deviations are recorded in [deviations.md](deviations.md) with date, reason, and demotion status. Pre-freeze revisions live in git history.

---

## Remaining before `prereg-h1-v1.0` (freeze checklist)

- [x] Initial S1–S5 verification pass (2026-08-07): two source–campaign pairs verified (Nançay 20220912A; FAST 20240114A); outcomes and open decisions recorded in `data_manifest.md` Section 1.
- [x] S3 ruling: relaxed to ≥ 14 days pre-freeze on data-availability grounds (2026-08-07); FAST 20201124A Sep–Oct admitted.
- [x] Remaining sample checks (2026-08-07): 20220912A FAST ScienceDB — no session log, excluded; AstroFlash 20220912A — verified; TMRT 20240114A — verified. Five pairs verified in total.
- [x] Parkes 20240114A DAP-reconstruction decision (2026-08-07): **excluded from confirmatory, designated exploratory** — rationale in manifest 1.4. Sample verification is complete: five confirmed pairs, all decisions resolved.
- [x] Rev3 nearest-host verification pass (2026-08-07): FRB 20200120E Effelsberg campaign verified and added as the sixth pair (manifest 1.7); all published alternatives for this source fail S1 or S2. Pre-tag work added: extraction scripts for the Nimmo/Kirsten/Pearlman tables and the frozen session-window construction rule (Pearlman-precedence) of manifest 1.7.
- [x] FRB 20200120E freeze mechanics (2026-08-07): three arXiv tarballs fetched and checksummed (manifest 1.6); Nimmo/Kirsten/Pearlman tables extracted; the manifest-1.7 handling rules implemented as asserted code (Pearlman-precedence windows, ID-based dedup with Pearlman B1–B5 TOAs, documented PR163A resolution, conservative non-Effelsberg drops); frozen outputs `effelsberg20200120E_sessions.csv` (46) and `effelsberg20200120E_bursts.csv` (69) committed with PROVENANCE entries; outcomes in manifest 1.7a. All six window functions now exist in `phase1/windows/`.
- [ ] Download all frozen files; record checksums, schemas, licenses, and time standards in `data_manifest.md`; commit hashed extraction scripts for the in-paper session-log tables (Zhou Table 3, Zhang Supp. Table 1, Niu Table 1).
- [x] Pin software environment (2026-08-07): `scripts/pin_environment.py` → `phase0/environment_pin.json` — package versions + hashed lock, DE440 kernel SHA-256 (loaded through the real `phase1/bary.py` conversion path), sites-registry content hash + resolved ITRF coordinates, frozen supplementary station coordinates (Tianma, Toruń, Onsala, Westerbork RT-1 proxy, Stockert) with provenance, and a frozen reference conversion as a regression anchor. Repo commit remains a placeholder filled at tag time. Details in manifest Section 6.
- [x] Compute and commit per-source alias sets and grids (Section 5) from the verified windows (2026-08-07): `scripts/compute_alias_sets.py` → `phase1/grids/<campaign>_grid_alias.json` for all six pairs, computed on exactly the scan grid (`pipeline.scanner_grids`), before any scan of real data. Summary in manifest 1.8. The Section 5.4 blanket property is confirmed quantitatively: 42.8% of the 22-day FAST 20201124A grid is alias-flagged vs 1.2–3% for the long-baseline campaigns. (Also corrected pre-freeze: the acceptance harness's full-scale τ_c grid now matches the frozen Section 5.2 factor-1.5 rule via `pipeline.frozen_tau_grid`; an earlier draft used a 12-point geomspace.)
- [x] Run and commit the synthetic acceptance tests (Section 9) at full scale (completed 2026-08-09). **All Section 9 criteria pass**: t1 null uniformity for all four families (two-sample KS p = 0.61/0.042/0.33/0.46 for M0/M1/M4/M5), t2 scanner recovery 166/166 (M2) and 182/182 (M3) valid injections, t3 alias flagging, t4 positive controls (FRB 20180916B P̂ = 16.30 d vs 16.35; FRB 20121102A P̂ = 147.7 d within the coded tolerance of the 157–161 d window), t5 jitter stability. Artifacts: `phase1/acceptance_results_full.json` (with compute provenance), raw task checkpoint `phase1/acceptance_checkpoint_full.jsonl` (4,600 Λ evaluations), kernel equivalence validation `phase1/validation_output_full.txt`. Computed on a Hetzner ccx63 (48 vCPU, ~29 h final stint) with the exact C kernel (~235× the reference; every rebuild passed the equivalence gate before use). _Pre-tag correction (2026-08-09, before any real-data scan): the harness's t1 construction ranked one half against the other and applied a one-sample KS — a two-sample comparison against the wrong null, measured ~13% false-failure per family on random re-splits (it flagged M1 at p=0.001); replaced with the two-sample KS, calibrated at exactly the nominal 1% false-failure. Simulation results unchanged; correction recorded in `acceptance.py` and the artifact's provenance block._
- [x] Record the literature-search protocol appendix in [novelty_audit.md](novelty_audit.md) (2026-08-07): logged re-execution of the item 1/2/3/5 searches with verbatim query strings and per-query screening (audit Appendix A.4). Items 1–3 hold; item 5 was rescoped (Price 2019 single-burst cyclostationary search; Choza 2024 M81-center narrowband SETI) with the surviving H4 novelty stated in the audit. Zhang et al. 2025 (arXiv:2507.14708) added to the H1 must-cite list (Section 1 above). Native-ADS re-run remains a pre-submission item per audit A.3.
- [ ] Commit all Phase 0 files, confirm a clean diff, create the `prereg-h1-v1.0` tag.
