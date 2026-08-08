# Bursty Beacon Search: Project Plan

_High-level research plan for executing the program described in [The_Bursty_Beacon_Search.md](The_Bursty_Beacon_Search.md). Sequences the work in that note's Sections 8 and 12 by data-access latency, cost-to-insight ratio, and methodological credibility._

_Scope decision (2026-08-07): **this project is public-data-only.** Everything requiring collaboration, data requests, proprietary access, or observatory policy engagement is deferred to a post-project follow-up (Section "Post-project follow-up" below) and a second paper. This removes all external-access items from the critical path._

## Guiding principles

1. **Public data only; collaboration is the follow-up paper.** Candidate graveyards, request-only baseband, proprietary archives, time-resolved CHIME exposure products, pipeline-level injection, and live-trigger deployment are all collaboration-gated and therefore out of scope for this project. The consequence is accepted explicitly: the H1 confirmatory sample is restricted to campaigns with complete published observing logs, and Phase 3 nulls are reported with cutout-level (not pipeline-level) selection caveats.
2. **Cheapest high-value tests first.** The exposure-folded scanner-model test runs on published burst tables plus published per-session observing logs. Verifying that those logs exist at the required schema — not merely cumulative exposure maps — is the Phase 1 data gate, enforced in [prereg_h1.md](../phase0/prereg_h1.md).
3. **Methodological credibility over speed.** The biggest failure mode is not missing a signal — it is producing an unconvincing candidate. A broad transformation search over thousands of events is a trials-factor minefield (note Section 10.7). Statistics and transformation families are frozen by pre-registration *before* looking at data. H1 freezes separately (`prereg-h1-v1.0`) from H2/H3/H4 (`prereg-h2h3h4-v1.0`) so Phase 1 is not blocked on morphology decisions.
4. **Injection-recovery splits into two different activities.**
   - *Cutout-level injection* (synthetic tagged packets in real noise cutouts) is cheap, sets detection thresholds, validates segmentation code, and is a prerequisite — built into the toolkit from day one.
   - *Pipeline-level injection* (estimating per-instrument trigger and save probabilities) requires collaborator pipelines and is deferred to the follow-up. Until then, null results are stated as constraints conditional on the published selection functions, with the caveat quantified where the CHIME public injections release permits.
5. **Every phase produces a standalone astrophysics deliverable.** Repeater timing constraints, single-pulse correlation population studies, and archive characterization are publishable regardless of technosignature outcome. This keeps the project fundable under the expected outcome, which is a null.

---

## Phase 0 — Literature review, novelty audit, preregistration

_Substantially complete as of 2026-08-07; see [novelty_audit.md](../phase0/novelty_audit.md)._

Remaining Phase 0 work:

- finish the H1 freeze artifacts and synthetic acceptance tests in [prereg_h1.md](../phase0/prereg_h1.md);
- complete [data_manifest.md](../phase0/data_manifest.md) with verified files, checksums, schemas, and licenses;
- complete the literature-search protocol appendix (dated search strings, screening criteria, bibliography) before any publication-facing novelty claim;
- commit Phase 0 files and create the `prereg-h1-v1.0` tag.

**Go/no-go:** already exercised — the audit produced a conditional go with H1 rescoped as a generative-model comparison.

---

## Phase 1 — The repeater timing test (first publishable result)

_Public-data scope: confirmatory sample restricted to repeater campaigns with complete published observing-session logs — six source–campaign pairs verified (manifest Section 1): the hyperactive repeaters 20220912A (Nançay, AstroFlash), 20240114A (FAST, TMRT), 20201124A (FAST Sep–Oct), and, under the rev3 nearest-host prior, 20200120E (Effelsberg, M81 at 3.6 Mpc — the thesis-preferred target). Known periodic repeaters (20180916B, 121102) serve as positive controls. The hyperactive sources sit at ~350–600 Mpc, beyond the rev3 nominal beam-filling horizon; they remain confirmatory (the horizon is gain-dependent) with the closer expectation stated in interpretation. The full CHIME Catalog 2 83-repeater analysis is deferred to the follow-up, where time-resolved exposure can be requested._

Implement the window-function-aware likelihood and run the frozen M0–M5 comparison of [prereg_h1.md](../phase0/prereg_h1.md):

- M0 homogeneous Poisson; M1 activity-window; M2 periodic scanner; M3 paired-pass scanner; M4 Weibull-clustered; M5 session-nonstationary (gamma-mixed Poisson) robustness model.
- Scheduling-comb aliasing handled by frozen per-source alias sets (solar and sidereal rationals plus spectral-window peaks).
- Study-wide false-alarm calibration by full-search rerun on simulations from each fitted natural model; conservative-maximum rule across null families.

**Pre-analysis data gate:** for every included source, freeze the exact good-time intervals, masks, time standard, arrival-time conversion, and event-grouping rules in the manifest. Integrated exposure totals do not satisfy this gate.

**Why first:** the analysis exercises the exposure-function machinery needed throughout the project and produces a standalone paper regardless of outcome — a null constrains the explicitly defined scanner-model family over the searched (T, σ_v, τ_c) space on the best-sampled repeaters in the literature.

**Validation:** simulated event streams drawn through the real observing windows (prereg_h1 Section 9). No pipeline-level injection needed.

---

## Phase 2 — Core analysis toolkit, with calibration built in

_The note's Phase A, with two additional requirements. Public data throughout._

Build on public dynamic spectra:

- standardized data model and minimal event record (note Appendix A);
- component segmentation across multiple time resolutions;
- transformed cross-correlation restricted first to channel-commutative families;
- minimum-description-length scoring;
- full-time-extent search of saved cutouts for attached off-manifold structure;
- repeated-timing-motif (grammar) search.

**Requirement 1 — calibrate copy-exactness on pulsars first.** Pulsars provide thousands of pulses from known-stochastic sources: that is the null distribution for the copy-exactness statistic, and characterizing it is legitimate astrophysics on its own. Calibration ladder per the preregistration Section 6: MeerKAT TPA census (at its effective released resolution), Parkes Transient DB II, B1937+21/Crab giant-pulse baseband (propagation-imprint regime), and the designated repeating-FRB development controls including the FRB 20240114A carbon-copy sets. Only after this calibration does the statistic run on RRATs and FRBs.

**Requirement 2 — cutout-level injection from day one.** Synthetic tagged packets injected into real noise cutouts set thresholds and validate the segmentation and correlation code before any search claims are made.

**Go/no-go:** if the pulsar calibration shows the copy-exactness null distribution has a fat tail (scintillation, propagation imprinting, or instrumental correlation) such that the frozen quantile gate fails, the statistic is redesigned before any archival claims.

---

## Phase 3 — First archival sweep (public data)

Run the frozen, calibrated statistics over public archives. Under the rev3 two-builder mapping (note Section 16.4) the two delivery streams are co-primary: Galactic-dispersion streams for the galactic builder class (note Section 4.4), the genuine-FRB repeater catalog for the extragalactic class:

1. Galactic single-pulse, pulsar, and RRAT streams (galactic-builder primary region — MeerTRAP Galactic-transient release first);
2. public total-intensity FRB dynamic spectra, including full cutout extents (CHIME Cat 1/2 waterfalls, DSA-110, CRAFT HTR), with repeaters localized to nearby hosts searched first, ordered by host distance (frozen host-distance table in the manifest; sources beyond the nominal ~80 Mpc beam-filling horizon stay in scope — the horizon is gain-dependent — with the closer expectation noted in any interpretation);
3. cross-observatory time-coincidence matching of public candidate lists (same-event simultaneity, not only recurrence; per note Section 16.5 this weight is scale-dependent and serves the galactic class primarily).

**Trials-factor discipline:** held-out validation — search half the archive, confirm on the other half (deterministic event-hash split per the preregistration). Report local and global false-alarm probabilities. Scrambled-data controls and matched natural populations carry the significance burden at this stage.

**Deliverables:** ranked candidate list with calibrated significance; well-characterized null distributions; any Level-1+ anomalies per the evidence hierarchy of note Section 9.

**Expectation setting:** the likely primary output is null distributions and perhaps a few morphological anomalies. The evidence hierarchy keeps candidate claims calibrated. Nulls are stated per data product with cutout-level selection caveats (pipeline-level selection functions arrive only in the follow-up).

---

## Phase 4 — Public-baseband pilot, headlined by the phase-residual search

_The public-data subset of the note's Phase C, plus the rev3 phase-residual (H4) search of note Sections 8.6 and 16.6. No requests, no collaborations._

Apply voltage- and polarization-domain tests to the public voltage sets identified in the data-product matrix:

- **Phase-residual structure search (H4)** — the rev3 headline test: after coherent dedispersion and channel equalization, search residual carrier phase for repeated modulation patterns, non-random phase trajectories, and low-description-length structure across bursts (preregistration Section 2.4; calibration gate Section 6.4). Public-data first target: **FRB 20180916B**, the nearest-host repeater with public voltages (CHIME Baseband Catalog 1 bursts; LOFAR complex voltages for band diversity), then the full CHIME baseband sample. FRB 20200120E — the thesis's first-priority target — has **no public voltage data** (verified 2026-08-07: PRECISE, Effelsberg DADA, DSN, and CHIME voltage sets are all request-only or internal; the public Zenodo products are intensity filterbanks down to 31.25 ns), so its phase-residual search is a follow-up request; its public intensity products still enter the Phase 3 H2 sweep at top host-distance priority.
- CHIME/FRB Baseband Catalog 1 (140 FRBs) — coherent re-dedispersion, complex-voltage auto/cross-correlation beyond the plain-delay region already searched by Leung/Kader 2022, cyclostationarity with demonstrated (injected) sensitivity, and the Kader 2025 phase-coherence discriminator as the standard propagation veto;
- BL FRB 121102 voltages — band-diverse checks;
- B1937+21 / Crab giant-pulse baseband — propagation-imprint and phase-null calibration (shared with Phase 2 and the H4 calibration gate);
- the cold-plasma phase-transfer-function test of note Appendix C on the highest-S/N public events, as the zeroth-order case of the phase-residual search.

**Deliverables:** transformed-repetition and determinism bounds on the public voltage sample; phase-residual structure bounds — the excluded (modulation depth, S/N) region from the H4 injection grid, with a null independently publishable as a constraint on coherent burst-emission physics; a short list of events warranting deeper (follow-up-phase) data requests, with the FRB 20200120E voltage sets at the top.

---

## Paper boundary

Phases 0–4 constitute the project and the first paper(s): the H1 timing result, the calibrated copy-exactness population study, the public-archive sweep, and the public-baseband bounds.

---

## Post-project follow-up (second paper; everything collaboration-gated)

All items below require data requests, memoranda, or observatory engagement. None blocks the phases above. Long-lead conversations can begin opportunistically once Phase 1–3 results exist to motivate them.

- **Time-resolved CHIME exposure (H1 at full scale):** request daily-or-finer good-time intervals and sensitivity masks for the Catalog 2 interval; rerun the frozen H1 machinery on the 83-repeater sample under a new major preregistration version.
- **Candidate graveyards** (note Phase B): rejected, low-dispersion, pulsar-associated, and RFI-classified candidates; selection-function reconstruction; candidate-veto audit; hidden-event yield estimates.
- **FRB 20200120E voltage requests (the rev3 first target at depth):** Effelsberg burst-storm DADA voltages ("available on reasonable request" per the published data statement), PRECISE station VDIF/Mark5B raw voltages (held by the AstroFlash team; absent from the public EVN archive, 404-verified), DSN DSS-63 baseband, and CHIME internal per-burst baseband. Under the rev3 collapsed architecture this is the single highest-value request in the follow-up; the Phase 4 FRB 20180916B result motivates it either way.
- **Request-only baseband and voltage archives** (note Phase C at depth): CRAFT VCRAFT voltages, MeerTRAP filterbanks/voltages, BL MeerKAT stamps, FAST Data Center bulk retrieval, Vela UTAS archive.
- **Pipeline-level injection-recovery** (note Section 11): per-instrument trigger/save/recover probabilities per design family — the machinery that converts Phase 3 nulls into design-family limits (note Section 14) tighter than the cutout-level caveats of the first paper.
- **Live commensal trigger** (note Phase E): operate on saved candidates, flag transformed self-similarity, request extended buffer retention, preserve polarization/voltage data, initiate rapid follow-up.
- **Cutout-window policy advocacy:** widened saved-cutout windows (several seconds around each trigger) at operating pipelines — a low-cost policy ask that preserves attached off-manifold components going forward; floated alongside the other collaboration conversations.

---

## Risks

| Risk | Mitigation |
| --- | --- |
| Trials factor / forking paths — the existential methodological risk | Split preregistrations frozen before data (Phase 0) plus held-out validation (Phase 3) |
| Copy-exactness null uglier than hoped (scintillation/instrumental correlation) | Pulsar calibration precedes any archival sweep; redesign gate in Phase 2 |
| Restricted H1 sample limits power (few sources, campaign-length baselines) | Reported as an explicit constraint on the scoped family; the full-sample analysis is the follow-up's headline, under a new prereg version |
| H1 candidate campaigns fail observing-log verification | Freeze pauses and sample criteria are revisited pre-freeze (prereg_h1 Section 3.2); no scan runs on unverified windows |
| Nulls weakened by unknown pipeline selection | Stated per data product with cutout-level caveats; CHIME public injections release used where applicable; full selection functions deferred to follow-up |
| Project judged only by technosignature outcome | Standalone astrophysics deliverable required from every phase |
| Key statistic turns out to be already-published | Phase 0 novelty audit is a hard gate before tool investment; watch items monitored (carbon-copy literature) |

---

## Summary sequence

> Literature and novelty check first; the repeater-timing test on publicly logged campaigns second — now including the nearest-host target FRB 20200120E; tools with built-in cutout-level calibration third; the public archival sweep fourth, with the two builder classes' streams co-primary and FRB repeaters ordered by host distance; the public-baseband pilot fifth, headlined by the phase-residual (H4) search with FRB 20180916B as the nearest public-voltage target; and everything requiring collaboration — graveyards, request-only voltages (FRB 20200120E's first among them), pipeline-level injection, full-sample CHIME timing, and the live trigger — deferred to a post-project follow-up motivated by the first paper's results.
