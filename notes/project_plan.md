# Bursty Beacon Search: Project Plan

_High-level research plan for executing the program described in [The_Bursty_Beacon_Search.md](The_Bursty_Beacon_Search.md). Sequences the work in that note's Sections 8 and 12 by data-access latency, cost-to-insight ratio, and methodological credibility._

## Guiding principles

1. **Data access latency drives the schedule.** Public data is available today; candidate graveyards and baseband archives require collaborations that take months to negotiate. Work needing only published data goes first. Collaboration conversations start early, in parallel, because they sit on the critical path for later phases.
2. **Cheapest high-value tests first.** The exposure-folded scanner-model test on known-repeater burst times requires only published arrival times and exposure functions. It is the first real science, not a late-phase item.
3. **Methodological credibility over speed.** The biggest failure mode is not missing a signal — it is producing an unconvincing candidate. A broad transformation search over thousands of events is a trials-factor minefield (note Section 10.7). Statistics and transformation families are frozen by pre-registration *before* looking at data.
4. **Injection-recovery splits into two different activities.**
   - *Cutout-level injection* (synthetic tagged packets in real noise cutouts) is cheap, sets detection thresholds, validates segmentation code, and is a prerequisite — built into the toolkit from day one.
   - *Pipeline-level injection* (estimating per-instrument trigger and save probabilities) is only needed to interpret nulls and rank design families. It requires collaborator cooperation anyway, and can lag the first search passes without harm. It lives in Phase 4.
5. **Every phase produces a standalone astrophysics deliverable.** Repeater timing constraints, single-pulse correlation population studies, and selection-function reconstructions are publishable regardless of technosignature outcome. This keeps the project fundable under the expected outcome, which is a null.

---

## Phase 0 — Literature review and novelty audit

_Timescale: weeks, not months. No code beyond small scripts._

Verify the note's central empirical claims about what has *not* been done — each is a project-killer if wrong:

- **Scanner-model folding of repeater timing.** Has anyone folded repeater burst times through exposure functions against periodic-scanner or paired-pass models? The CHIME/FRB repeater periodicity literature (FRB 20180916B's 16.35-day activity window; the ~157-day candidate period for FRB 121102) is adjacent — confirm the scanner-model variant specifically is untested.
- **Pulsar single-pulse statistics.** What does the single-pulse and microstructure literature already say about pulse-to-pulse correlation distributions? This is both the null model for the copy-exactness statistic and a check that no natural source already exhibits copy-exact behavior.
- **Lensing-echo and voltage-autocorrelation searches.** What has already been covered on FRB baseband data? This bounds the "simple delayed copy" region already searched (note Section 6.1).
- **Public data inventory.** What actually exists and in what form: CHIME/FRB catalogs and waterfall data, RRAT catalogs (RRATalog), pulsar single-pulse archives, Breakthrough Listen data products, published baseband samples. This is the start of the note's Stage 0 data-product matrix (Section 8.3).

**Pre-registration deliverable:** a written, versioned specification of the statistics, the transformation families to be searched (channel-commutative only, per note Section 4.3), and the significance procedure — frozen before any archival data is examined.

**Go/no-go:** if the novelty audit shows the key statistics have already been computed and are null, the plan is re-scoped before tool investment.

---

## Phase 1 — The repeater timing test (first publishable result)

_Requires only published data. First real science output._

Implement the window-function-aware likelihood (note Section 8.9) and run scanner-model and paired-pass comparisons on the public known-repeater sample:

- homogeneous Poisson source;
- activity-window repeater;
- periodic scanner with phase uncertainty;
- paired-pass scanner (short confirmation lag plus long sweep period);
- clustered natural repeater.

Handle transit-instrument cadence aliasing explicitly (sidereal-day comb in the exposure function; note Section 5.1).

**Why first:** pure published data; exercises the exposure-function machinery needed throughout the project; produces a standalone paper regardless of outcome — a null is a genuine, never-published constraint on scanning-beacon models.

**Validation:** simulated event streams drawn through the real exposure windows. No pipeline-level injection needed.

---

## Phase 2 — Core analysis toolkit, with calibration built in

_The note's Phase A, with two additional requirements._

Build on public dynamic spectra:

- standardized data model and minimal event record (note Appendix A);
- component segmentation across multiple time resolutions;
- transformed cross-correlation restricted first to channel-commutative families;
- minimum-description-length scoring;
- full-time-extent search of saved cutouts for attached off-manifold structure;
- repeated-timing-motif (grammar) search.

**Requirement 1 — calibrate copy-exactness on pulsars first.** Pulsars provide thousands of pulses from known-stochastic sources: that is the null distribution for the copy-exactness statistic, and characterizing it is legitimate astrophysics on its own. Only after this calibration does the statistic run on RRATs and FRBs.

**Requirement 2 — cutout-level injection from day one.** Synthetic tagged packets injected into real noise cutouts set thresholds and validate the segmentation and correlation code before any search claims are made.

**Go/no-go:** if the pulsar calibration shows the copy-exactness null distribution has a fat tail (scintillation or instrumental pulse-to-pulse correlation), the statistic is redesigned before any archival claims.

---

## Phase 3 — First archival sweep (public data)

Run the frozen, calibrated statistics over public archives, with Galactic-dispersion streams weighted highest per the geometry argument of note Section 4.4:

1. Galactic single-pulse, pulsar, and RRAT streams (primary region);
2. public total-intensity FRB dynamic spectra, including full cutout extents;
3. cross-observatory time-coincidence matching (same-event simultaneity, not only recurrence).

**Trials-factor discipline:** held-out validation — search half the archive, confirm on the other half. Report local and global false-alarm probabilities. Scrambled-data controls and matched natural populations carry the significance burden at this stage.

**Deliverables:** ranked candidate list with calibrated significance; well-characterized null distributions; any Level-1+ anomalies per the evidence hierarchy of note Section 9.

**Expectation setting:** the likely primary output is null distributions and perhaps a few morphological anomalies. The evidence hierarchy keeps candidate claims calibrated.

---

## Phase 4 — Collaborations: graveyards, baseband, pipeline-level injection

_Opened by Phase 1–3 results; long-lead conversations initiated back in Phase 1._

- **Candidate graveyards** (note Phase B): rejected, low-dispersion, pulsar-associated, and RFI-classified candidates; selection-function reconstruction; candidate-veto audit.
- **Baseband analyses** (note Phase C): coherent re-dedispersion, cyclostationarity, deterministic voltage tests, Jones/Mueller polarization relations, the chirp phase-transfer-function test of note Appendix C.
- **Pipeline-level injection-recovery** (note Section 11): per-instrument trigger/save/recover probabilities for each design family. Placed here because it requires collaborator pipelines, and because its outputs — selection functions per design family — are exactly what converts the Phase 3 null into publishable limits (note Section 14).

**Deliverables:** hidden-event yield estimates; design-family upper limits stating exactly which data product each applies to; a short list of events warranting independent review.

---

## Phase 5 — Live commensal trigger

_The note's Phase E._

- operate on saved candidates rather than raw full-rate data initially;
- flag transformed self-similarity; request extended buffer retention;
- preserve polarization and voltage data when possible;
- initiate rapid follow-up for high-ranking events.

**Promoted item:** advocating widened saved-cutout windows (several seconds around each trigger) at operating pipelines is a policy ask, not a technical one, and cheap — float it during Phase 4 collaboration conversations rather than waiting for Phase 5. It preserves attached off-manifold components going forward.

---

## Risks

| Risk | Mitigation |
| --- | --- |
| Trials factor / forking paths — the existential methodological risk | Pre-registration (Phase 0) plus held-out validation (Phase 3) |
| Copy-exactness null uglier than hoped (scintillation/instrumental correlation) | Pulsar calibration precedes any archival sweep; redesign gate in Phase 2 |
| Data access stalls the back half of the project | Treat collaborations as long-lead procurement, initiated in Phase 1 |
| Project judged only by technosignature outcome | Standalone astrophysics deliverable required from every phase |
| Key statistic turns out to be already-published | Phase 0 novelty audit is a hard gate before tool investment |

---

## Summary sequence

> Literature and novelty check first; the free repeater-timing test second; tools with built-in cutout-level calibration third; the archival sweep fourth; and the expensive pipeline-level injection-recovery deferred until there are collaborators and a null worth converting into limits.
