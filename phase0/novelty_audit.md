# Phase 0 — Literature Review and Novelty Audit

_Working audit completed 2026-08-07. Audits the four project-killer claims from [project_plan.md](../notes/project_plan.md) Phase 0 against the published literature (searches run across arXiv, ADS, and journals; the CHIME/FRB verification below is from full LaTeX sources, not abstracts), plus — added the same day after the rev3 thesis update — a fifth item covering the H4 phase-residual search. This is a targeted novelty audit, not yet a reproducible systematic review: search strings, screening criteria, and a complete bibliography must be recorded before publication-facing novelty claims are frozen._

## Consolidated verdict: **CONDITIONAL GO**

The scientific program remains viable, but the claims do not all survive unchanged: H1's novelty claim requires narrower framing, and the proposed Phase 1 analysis remains conditional on time-resolved exposure data.

| Audit item | Verdict |
| --- | --- |
| 1. Scanner-model folding of repeater timing | No paired-pass scanner test was identified. Strict scanner periodicity is partially constrained, so the claim must be scoped as a model comparison rather than a first periodicity search. |
| 2. Pulsar single-pulse copy-exactness | No population-level anomaly statistic was identified; the stochasticity premise is supported; known fat-tail mechanisms must be built into the null. |
| 3. Lensing-echo / voltage-autocorrelation coverage | The simple delayed-copy region has published coverage with measurable bounds. No sensitive transformed-repetition, cyclostationarity, or voltage-determinism search was identified. |
| 4. Public data inventory | Phase 2–3 have substantial public inputs. Phase 1 burst epochs are public, but the timestamped observing windows required by the proposed likelihood remain unverified. |
| 5. Phase-residual structure search (H4) | Rescoped 2026-08-07 (A.4 re-execution): Price 2019 published a single-burst, insensitive cyclostationary modulation search on dedispersed FRB voltages, and Choza 2024 published an M81-center narrowband SETI search (excludes the FRB position). The surviving novelty: cross-burst phase-trajectory/structure searches on a repeater, sensitivity-calibrated phase-domain tests, and any coverage of the FRB 20200120E position. Public-data caveat: the thesis first target has no public voltages. |

No hypothesis needs to be abandoned. However, the H1 novelty language—and potentially its confirmatory source sample—must be re-scoped, and Phase 1 cannot begin as a confirmatory analysis until its observing-window verification and statistical-specification gates are closed (both now specified in [prereg_h1.md](prereg_h1.md)). Required amendments to the pre-registration are listed in Section 7.

---

## 1. Scanner-model folding of repeater timing

**Claim audited:** no one has folded repeater burst times through exposure functions against periodic-scanner or paired-pass models.

**Finding: no paired-pass scanner test was identified; the strict-scanner test is partially occupied and the claim must be scoped.**

What exists — the activity-window periodicity literature is exposure-aware but tests a different hypothesis class:

- CHIME/FRB 2020 (Nature 582, 351; arXiv:2001.10275) established the canonical method on FRB 20180916B: fold burst times at trial periods 1.5–100 d, Pearson χ² over 4–16 phase bins with expected counts **weighted by the phase-binned exposure** (E_i = p·T_i), sidereal-day subharmonics N=1–5 excised, significance from 10⁶ mock arrival sets drawn through the real exposure map. Result: 16.35 d period with a ~24%-duty-cycle *activity window* — explicitly not strict point-process periodicity.
- FRB 121102: Rajwade et al. 2020 (arXiv:2003.03596, Lomb-Scargle, window function treated as a bias); Cruces et al. 2021 (arXiv:2008.03461, epoch folding); ~157–161 d, ~50–60% duty cycles.
- Aznam et al. 2025 (A&A) is the most explicitly exposure-folded periodogram (per-phase-bin exposure weighting plus an inactivity-fraction periodogram), run on 17 low-count CHIME repeaters — still activity-window framing.
- Short-timescale strict searches (ms–1000 s) exist only *within* contiguous sessions (Li et al. 2021, 1652 FAST bursts; Niu et al. 2024, arXiv:2310.08971, four hyperactive repeaters — all null). The Du et al. 2025 1.7-s claim for FRB 20201124A (arXiv:2503.12013) was challenged by arXiv:2505.14219.
- Oppermann, Yu & Pen 2018 (MNRAS 475, 5109) is the methodological ancestor of exposure-aware point-process likelihoods (Weibull renewal with session windows) — a clustering model, not a scanner.
- SETI side: Lingam & Loeb 2017 (light sails) *predicts* beam-sweep repetition but never tested it; Benford³ 2010 predicts month–year revisits, no test; Gray 2021 argues for planetary-day cadences, strategy only; BLIPSS-type searches fold raw time series of pointings, not catalog burst epochs. **This audit identified no technosignature paper applying a scanning-beacon timing likelihood to a repeater catalog.**

**Residual-risk closure (full-text verification of the three riskiest papers):** CHIME/FRB Catalog 2 (arXiv:2601.09399) contains **zero** periodicity analysis — it positions itself as the input dataset (4,539 bursts, 981 from 83 repeaters, plus exposure maps). Cook et al. 2026 (arXiv:2605.08410, 80 repeaters) contains **zero** periodicity analysis (rates, DM drift, population modeling only; Weibull cited but never fitted). The 25-repeater catalog's (arXiv:2301.08762) entire periodicity content is one sentence: a "preliminary" per-source χ² search, null, unsurprising at ≤12 bursts/source, no published parameters or upper limits.

**Combinations not identified in the literature searched through 2026-08-07:**

1. Likelihood-based **model comparison** among the specified generative point processes (strict visit scanner vs. activity window vs. Weibull-clustered), rather than rejection of a uniform null;
2. a **paired-lag scanner model** in which a short confirmation lag recurs on a longer sweep period;
3. a **long-baseline, exposure-folded sub-day scanner search**. Short-timescale searches within contiguous observing sessions do exist, as noted above; the unoccupied claim is the combination of sub-day period, discontinuous exposure, alias-aware likelihood, and scanner-model comparison;
4. this combined analysis on the modern 80+-repeater sample, whose published periodicity coverage is limited.

**Scoped Phase 1 claim (use this wording; must-cite list extended 2026-08-07 per A.4):** this audit identified no prior application of the complete scanner hypothesis test—strict plus paired-pass, exposure-folded, alias-aware, and compared against explicit natural point-process models. The strict-periodicity limiting case is directly or indirectly constrained for some well-observed sources and period ranges (including 1.5–100 d for FRB 20180916B, plus within-session short-timescale searches). Must-cite-and-distinguish: CHIME/FRB 2020 (Nature 582, 351), CHIME/FRB 2023 (ApJ 947, 83), and **Zhang et al. 2025 (arXiv:2507.14708)** — the first joint multi-session short-period (ms–tens of minutes) search on a repeater (FRB 20240114A), performed **without** exposure folding on its short-timescale searches and without scanner models, i.e., the nearest neighbor to (and clearly distinct from) this analysis.

---

## 2. Pulsar single-pulse statistics (copy-exactness null model)

**Claim audited:** natural single pulses are stochastic; no natural source emits copy-exact pulses; the copy-exactness statistic is uncomputed.

**Finding: premise supported; no population-level use of the proposed anomaly statistic was identified; the null has known fat-tail mechanisms that must be designed around.**

The stochasticity premise is strongly supported by five decades of literature:

- The canonical null is Rickett 1975 amplitude-modulated noise (pulse = Gaussian noise × stochastic envelope), verified down to 80 ns for J0437−4715 (Jenet et al. 1998).
- **Cordes 1976 (ApJ 208, 944) is the key direct precedent:** cross-correlated microstructure of successive subpulses in B2016+28 and found *no* pulse-to-pulse correlation of the micropulse pattern — fine structure is regenerated stochastically every rotation.
- Jitter statistics (Lam et al. 2019: rms single-pulse jitter ≈ 1% of phase across 43 MSPs), modulation-index surveys (Weltevrede 2006/2007), and MSP profile-stabilization requirements (10⁵–10⁶ pulses) all quantify strong per-pulse variability.
- Giant pulses are not copies: Crab nanoshots are stochastic in number, spacing, and polarization (Hankins & Eilek 2007); B1937+21 GPs are near-featureless ≤15 ns single spikes (Soglasnov et al. 2004).
- RRATs: adjacent-pulse morphology is "extremely variable" (FAST studies of J1913+1330, arXiv:2306.02855).

**This audit identified no published population-level distribution of pairwise waveform correlation used as an anomaly statistic.** The ingredients exist scattered (per-phase-bin correlations for B0329+54, arXiv:2601.17299; burst-pair *spectral* correlation for scintillometry, Main et al. 2022; PCA/VAE clustering of single pulses for timing/classification), but no located radio SETI program uses morphological identity (rather than periodicity) as the artificiality criterion. Nearest conceptual precedent identified: Stanton 2025 (Acta Astronautica) flagged one pair of near-identical *optical* pulses—single event, no formalized population statistic.

**Fat-tail mechanisms the null must absorb (Phase 2 redesign-gate inputs):**

1. **FRB 20240114A "carbon-copy" burst pairs (2026, active debate):** arXiv:2602.16409 reports morphologically near-identical pairs with "spectral memory" (plasma-lens interpretation); arXiv:2607.02939 rebuts (chance among >10,000 bursts). Either way this is a documented natural/propagation route to near-copies and the single biggest threat to a naive statistic. This literature is actively quantifying burst-pair similarity and could formalize an equivalent statistic soon — a reason to move promptly and to cite-and-differentiate.
2. **ISM impulse-response imprinting:** any unresolved impulsive event takes on the shape of the ISM impulse response, which is stable over the scintillation timescale — distinct events within that window can be near-copies in time profile (Lin et al. 2023, arXiv:2305.13274).
3. **Scintillation spectral correlation** within τ_d ~ minutes (Main et al. 2022; Nimmo et al. 2022).
4. **ISM echoes** producing persistent correlated components for weeks (B2217+47, arXiv:1802.03473).
5. **Drifting/mode-changing memory** and discrete shape states (Kerr 2015).
6. **RFI pipelines already use "too identical" as an RFI veto** — the informal inverse of our flag; RFI is the dominant instrumental contaminant for high-correlation pairs.
7. **Low-S/N / coarse-resolution degeneracy** — all width-limited pulses look alike.

Design consequence: the copy-exactness null must be conditioned on **pair time-lag (relative to the scintillation timescale), S/N, and effective resolution**, and the statistic should be computed on descattered or spectrum-marginalized waveforms. This is incorporated into the pre-registration (Section 6 below).

---

## 3. Lensing-echo and voltage-autocorrelation coverage

**Claim audited:** the "simple delayed copy" region is already searched (bounding note Section 6.1); transformed repetition is not.

**Finding: supported within the audited literature on both halves, with the located searched region more precisely bounded.**

The only systematic voltage-coherent FRB echo-search program identified in this audit is the CHIME/FRB lens-interferometry program:

- Leung et al. 2022 + Kader et al. 2022 (PRD 106, 043017/043016): autocorrelation of coherently dedispersed complex voltages of **172 FRBs / 114 sightlines** (400–800 MHz, ~100 ms recordings, 1.25 ns field resolution). Matched filter for exactly one hypothesis: an attenuated, achromatic, phase-coherent, **untransformed** delayed copy s(t) + ε·s(t−τ), with equal copy amplitude required in both polarizations. Delays ~0.3 μs–100 ms; sensitivity ε × S/N ≳ 0.03. No detections.
- Kader et al. 2025 (arXiv:2512.11969): the one candidate resolved as diffractive scintillation — power-correlated but **phase-incoherent**. This is the published exemplar of coherent-vs-incoherent copy discrimination and a template for our veto stack.
- Cross-burst voltage cross-correlation (are two bursts copies of each other?) was proposed by Wucknitz, Spitler & Pen 2021; this audit identified no application to real data, consistent with the Pastor-Marazuela 2024/2025 review.
- Intensity-domain: Sammons et al. 2020 (echoes ≥15 μs, ASKAP); Chang et al. 2024 (CHIME Cat-1 intensity ACF; one 3.4σ candidate double image).

**No sensitive searches were identified for:** copies related by calibrated phase rotation, polarization inversion/swap, spectral remapping, or coding; cyclostationarity with demonstrated sensitivity (the located FRB test—Price et al. 2019 on FRB 180301—was shown by its own injection test to have no sensitivity at the burst's S/N); or determinism tests on the field itself (located 2026 shot-noise work fits stochastic models but does not test the deterministic alternative). Cyclic spectroscopy is mature for pulsars (Demorest 2011 onward); its only located FRB application is the single insensitive Price et al. 2019 test (wording tightened 2026-08-07 per A.4).

**Cautionary note for all periodicity/repetition claims:** the CHIME FRB 20191221A sub-second periodicity (Nature 607, 256) was **retracted in 2026** — contamination from pulsar PSR J0248+6021. Known-source contamination checks belong in every timing analysis.

---

## 4. Public data inventory

**Claim audited:** enough public data exists to execute Phases 1–3.

**Finding: substantial public data exist, but Phase 1 has an unresolved exposure-window gate.** The detailed initial inventory is in [data_product_matrix.md](data_product_matrix.md). Highlights:

- **Phase 1 (repeater timing):** CHIME/FRB Catalog 2 supplies 4,539 burst records, including 981 from 83 repeaters, plus cumulative per-source exposure and all-sky HEALPix exposure maps. Those maps integrate exposure over the catalog interval and do not by themselves provide the timestamped good-time intervals $W(t)$ required by the proposed likelihood. Compiled epoch and observing-session lists for selected repeaters may support a narrower public-data analysis if their start/stop logs are complete.
- **Phase 2–3 (morphology/copy-exactness):** substantial public inputs include the MeerKAT TPA processed single-pulse census (1,192 pulsars, full Stokes, normally 16 frequency channels and 1,024 phase bins per period, ~35 GB on Zenodo), Parkes Transient DB II (165,592 single pulses from 363 pulsars, 1.5 GB), the MeerTRAP Galactic-transient release (every detected pulse from 26 RRAT-like sources, 8.4 GB), CHIME Cat 1+2 waterfalls, DSA-110 full-Stokes filterbanks, CRAFT HTR full-Stokes data, and the FAST FRB 20201124A PSRFITS atlas (license restrictions apply). Exact files and schemas remain to be frozen in the manifest.
- **Voltage domain (Phase 3 pilot / Phase C):** CHIME/FRB Baseband Catalog 1 (140 FRBs, beamformed dual-pol complex voltages at 2.56 μs — the flagship public voltage dataset), BL FRB 121102 raw voltages (~400 TB in principle; 740 GB filterbanks directly downloadable), LOFAR complex-voltage data for FRB 20180916B, B1937+21 giant-pulse baseband (46 GB Zenodo) for propagation-imprint calibration.
- **Gaps and hazards:** FRBCAT and FRBSTATS are dead; realfast.io is down; chime-frb.ca is mid-rebuild (use CANFAR/CADC records directly); CHIME Catalog 2 *baseband* companion and the 2026 30-repeater data release are announced but not yet public; this audit identified no public RRAT voltage data; RRATalog is alive at a new home (rratalog.github.io, 337 sources).

---

## 5. Phase-residual structure search prior art (H4; added 2026-08-07 for the rev3 thesis)

**Claim audited:** no one has searched coherently dedispersed FRB voltage/carrier phase for repeated modulation patterns, deterministic phase structure, or communication-like coding (research note rev3 Sections 8.6 and 16.6; [preregistration.md](preregistration.md) Section 2.4).

**Finding (rescoped 2026-08-07 by the logged re-execution, Appendix A.4): partially supported — the absolute claim fails on two papers.** Price et al. 2019 (MNRAS 486, 3636, Section 3.6) performed cyclic spectroscopy on the coherently dedispersed voltages of FRB 180301, explicitly framed as a search for artificial modulation, with a null result and BPSK-injection sensitivity only at +20 dB — a published (single-burst, insensitive) modulation search on FRB voltage data. And Choza et al. 2024 (AJ; arXiv:2312.03943) ran a Breakthrough Listen narrowband Doppler-drift search of 97 galaxies including the M81 center. The surviving unoccupied space: phase-residual **trajectory/structure** searches (repeated modulation patterns, deterministic phase trajectories, low-description-length structure **across bursts of a repeater**), any phase-domain search with demonstrated sensitivity at burst S/N, and any technosignature analysis covering the FRB 20200120E position (Choza's M81-center GBT pointing has a ~9 arcmin L-band beam; the globular cluster lies ~19 arcmin projected from center).

Complete pass over every voltage-data paper on FRB 20200120E, the H4 first target (all verified from full texts or arXiv sources, 2026-08-07):

- **Majid et al. 2021** (DSN DSS-63, 62.5 ns baseband): coherent dedispersion, matched filtering to 62.5 ns, profiles resolving components ≲ 100 ns, L/R circular profiles, dynamic spectra, and an **intensity autocorrelation** yielding ~2.3 µs quasi-periodic microstructure — the nearest prior art, and intensity-domain only.
- **Kirsten et al. 2022** (EVN voltages): voltage→filterbank burst search; SFXC coherent-dedispersion **correlation** for astrometry. No phase-structure analysis.
- **Nimmo et al. 2022** (Nat. Astron.): profiles to 31.25 ns, intensity ACFs and power spectra, brightness temperatures, full polarimetry (Faraday spectra, RM, PA). All intensity/Stokes-domain.
- **Nimmo et al. 2023** (MNRAS burst storm, 60 bursts): morphology, structure-resolved DM, energy and wait-time distributions, **TOA-level periodicity (null)** — arrival-time periodicity, not carrier phase.
- **Pearlman et al. 2025** (Nat. Astron.): coherent-dedispersion profiles to 31.25 ns, radio–X-ray coincidence; periodicity searched on X-ray photons only.

General FRB voltage prior art (extending audit item 3): the Leung/Kader 2022 delayed-copy autocorrelation and the Kader et al. 2025 phase-coherence discriminator use voltage phase **as a propagation veto** (power-correlated but phase-incoherent ⇒ scintillation), not as a search space for deliberate structure; cyclostationarity has no demonstrated FRB sensitivity (Price et al. 2019 self-reported); no determinism tests on the field were located; cyclic spectroscopy is mature for pulsars (Demorest 2011), its only located FRB application being the single insensitive Price et al. 2019 test.

**SETI prior art on the first target (corrected 2026-08-07):** Choza et al. 2024 (AJ; arXiv:2312.03943) is a published Breakthrough Listen narrowband SETI search whose 97-galaxy sample includes MESSIER081 — a GBT pointing at the galaxy **center** (1.1–2.7, 4.0–11.2 GHz). It does not cover the FRB 20200120E globular cluster (~19 arcmin projected offset vs. a ~9 arcmin L-band beam) and is a narrowband CW search, not a burst or phase analysis. No technosignature analysis of FRB 20200120E itself, or of any data containing its position, was located (targeted searches plus a BL Open Data Archive API check — no matching target). Closest burst-domain work remains Gajjar et al. 2021 (RNAAS), a GBT 4–8 GHz burst search framed purely as FRB science, null, no data release.

**Scoped H4 claim (rescoped 2026-08-07 — use this wording):** this audit identified no prior search of coherently dedispersed FRB voltage phase for repeated modulation patterns across bursts, deterministic phase trajectories, or low-description-length phase structure — the sole published phase-domain modulation test (Price et al. 2019, cyclostationary analysis of one burst of FRB 180301) was null with self-reported sensitivity only at +20 dB, and no phase-domain search targets a repeater. Must-cite-and-distinguish: **Price et al. 2019 (single-burst insensitive cyclostationary search — the prior-art boundary in the phase domain)**, **Choza et al. 2024 (M81-center narrowband SETI, excludes the FRB position)**, Kader et al. 2025 (phase coherence as veto), Majid et al. 2021 (intensity-ACF quasi-periodicity), Leung/Kader 2022 (delayed-copy boundary), Demorest 2011 (pulsar cyclic spectroscopy).

**Data caveat feeding the plan:** the H4 first target under the rev3 spatial prior has **no public voltage data** — all FRB 20200120E voltage sets (PRECISE stations, Effelsberg DADA, DSN, CHIME internal) are request-only or internal ([data_product_matrix.md](data_product_matrix.md) Section 8). The public-scope H4 first target is therefore FRB 20180916B (CHIME Baseband Catalog 1 + LOFAR LTA), with the 20200120E requests deferred to the follow-up.

## 6. Bonus finding: the plan's ordering is viable, subject to the data gate

Two audit outcomes support the plan's sequencing logic, subject to a data-access gate. First, Catalog 2 provides the modern burst sample and this audit identified no CHIME/FRB periodicity analysis of that catalog, but a confirmatory Phase 1 likelihood still requires time-resolved observing windows rather than only cumulative maps. Second, the fat-tail mechanisms found in audit item 2 are exactly what the Phase 2 pulsar-calibration gate was designed to catch; the audit converts that gate from a hypothetical into a concrete checklist (scintillation conditioning, IRF imprinting, carbon-copy pairs).

## 7. Required pre-registration amendments

1. **H1 scoping:** frame as generative-model comparison, not a first-ever periodicity search; add the must-cite list; explicitly include the long-baseline, exposure-folded sub-day regime not identified in prior work, with alias-aware treatment.
2. **H2 null conditioning:** condition the copy-exactness null on pair time-lag relative to the scintillation timescale, S/N, and effective resolution; compute on spectrum-marginalized (and where possible descattered) waveforms; add the FRB 20240114A carbon-copy population and B1937+21/Crab GP data to the calibration ladder as propagation-imprint controls.
3. **Veto stack:** adopt the Kader 2025 phase-coherence test (power-correlated vs. phase-coherent) as the standard discriminator between propagation-correlated pairs and true coherent copies; add known-pulsar contamination checks (the 20191221A retraction lesson) to all timing analyses.
4. **Transformation space:** record Leung/Kader 2022 as the prior-art boundary. Plain delay plus scale overlaps that searched region and carries no novelty claim. Polarization rotations/swaps are not generally channel-commutative for an unknown Jones/Mueller response and must be restricted to a calibrated secondary analysis unless the commutation assumption is demonstrated.

Items 1–4 are reflected in the current preregistration drafts. The remaining freeze decisions are enumerated in the freeze checklists of [prereg_h1.md](prereg_h1.md) and [preregistration.md](preregistration.md).

## 8. Watch items

- The FRB 20240114A carbon-copy literature (arXiv:2602.16409 vs 2607.02939) — closest active work to our copy-exactness statistic; monitor for a formalized similarity statistic.
- CHIME/FRB Catalog 2 baseband companion paper (announced) — will multiply the public voltage sample, and could add nearby-host repeater voltages.
- Aznam-style composite periodograms—the community is moving toward exposure-folded methods; monitor whether the combined model-comparison, paired-pass, and long-baseline sub-day space remains unoccupied.
- Any public release of FRB 20200120E voltage data (Effelsberg DADA "on reasonable request," PRECISE VDIF/Mark5B, DSN baseband, CHIME internal baseband) — would promote the H4 first target from follow-up to in-scope.
- Phase-domain FRB analyses generally (e.g., cyclic spectroscopy applied to FRBs, or any carrier-phase modulation search) — would occupy the H4 novelty space; monitor before each submission.
- FRB 20240210A (~105 Mpc, currently non-repeating) and FRB 20240619D (host unknown, possibly nearby) — either could change the host-distance table (manifest Section 5).

## Appendix: search-protocol record (reproducibility appendix)

_Status: **re-executed and logged 2026-08-07** (same day as the original targeted pass) for audit items 1, 2, 3, and 5 — verbatim query strings, per-query screening decisions, and verdicts in Section A.4 below. Audit item 4 (public-data inventory) is closed by direct verification in `data_manifest.md` Section 1, not by literature search, and has no search log. Items 1, 2, and 3 returned **CLAIM HOLDS** (with wording adjustments applied to the audit body: Zhang et al. 2025 arXiv:2507.14708 added to the item-1 must-cite list; the Price 2019 cyclic-spectroscopy clause tightened in item 3; the FRB 20240114A carbon-copy literature noted as adjacent FRB-domain art for item 2). Item 5 returned **CLAIM NEEDS RESCOPING** and has been rescoped in the audit body: Price et al. 2019 Section 3.6 is a published (null, insensitive) cyclostationary modulation search on coherently dedispersed FRB voltage data, and Choza et al. 2024 is a published narrowband SETI search including the M81 galaxy center — both absolute negatives are withdrawn; the surviving H4 novelty is the phase-residual/trajectory structure search on a repeater's dedispersed voltages and the untouched FRB 20200120E position. The re-execution engine is a general-purpose web search (see A.4 caveat), so the pre-submission native-ADS re-run of A.3 is still required; until then, novelty language keeps the adopted hedge: "not identified in the literature searched through 2026-08-07." The defensible claim remains the **combination** (explicit scanner/natural generative-model comparison + paired-pass structure + time-resolved exposure folding + long-baseline alias-aware sub-day coverage), not periodicity searching in general._

### A.1 Databases and date ranges

- arXiv (astro-ph.HE, astro-ph.IM), ADS, and journal full text; searched 2026-08-07; coverage through that date.
- CHIME/FRB verification performed on full LaTeX sources (arXiv:2601.09399, 2605.08410, 2301.08762), not abstracts.
- Re-executed logged pass (2026-08-07): Section A.4 — exact query strings, per-query screening, verdicts.
- **[TODO before submission]** native ADS/arXiv fielded re-run of the A.4 strings; backward/forward citation-chaining procedure and depth; stated update date immediately before submission.

### A.2 Screened-paper list (compiled from the audit above; exclusion reasons [TODO])

Timing/periodicity: CHIME/FRB 2020 (Nature 582, 351; arXiv:2001.10275) · Rajwade et al. 2020 (arXiv:2003.03596) · Cruces et al. 2021 (arXiv:2008.03461) · Aznam et al. 2025 (A&A) · Li et al. 2021 (FAST 121102) · Niu et al. 2024 (arXiv:2310.08971) · Du et al. 2025 (arXiv:2503.12013) and challenge (arXiv:2505.14219) · Oppermann, Yu & Pen 2018 (MNRAS 475, 5109) · CHIME/FRB Catalog 2 (arXiv:2601.09399) · Cook et al. 2026 (arXiv:2605.08410) · CHIME 25-repeater catalog (arXiv:2301.08762) · FRB 20191221A (Nature 607, 256; retracted 2026).

SETI/beacon strategy: Lingam & Loeb 2017 · Benford, Benford & Benford 2010 · Gray 2021 · BLIPSS-type folding searches.

Single-pulse statistics: Rickett 1975 · Jenet et al. 1998 · Cordes 1976 (ApJ 208, 944) · Lam et al. 2019 · Weltevrede et al. 2006/2007 · Hankins & Eilek 2007 · Soglasnov et al. 2004 · FAST J1913+1330 (arXiv:2306.02855) · B0329+54 per-phase-bin correlations (arXiv:2601.17299) · Main et al. 2022 · Kerr 2015 · Stanton 2025 (Acta Astronautica).

Propagation/copy mechanisms: FRB 20240114A carbon-copy debate (arXiv:2602.16409; arXiv:2607.02939) · Lin et al. 2023 (arXiv:2305.13274) · B2217+47 echoes (arXiv:1802.03473) · Nimmo et al. 2022.

Echo/voltage searches: Leung et al. 2022 + Kader et al. 2022 (PRD 106, 043017/043016) · Kader et al. 2025 (arXiv:2512.11969) · Wucknitz, Spitler & Pen 2021 · Pastor-Marazuela 2024/2025 review · Sammons et al. 2020 · Chang et al. 2024 · Price et al. 2019 (FRB 180301) · Demorest 2011.

FRB 20200120E / H4 prior art (added 2026-08-07): Choza et al. 2024 (arXiv:2312.03943, M81-center BL search) · Bhardwaj et al. 2021 (arXiv:2103.01295) · Majid et al. 2021 (arXiv:2105.10987) · Kirsten et al. 2022 (arXiv:2105.11445) · Nimmo et al. 2022 (arXiv:2105.11446) · Nimmo et al. 2023 (arXiv:2206.03759) · Pearlman et al. 2025 (arXiv:2308.10930) · Zhang et al. 2024 (arXiv:2310.00908) · Trudu et al. 2022 (arXiv:2204.05050) · Gajjar et al. 2021 (arXiv:2107.09445).

**[TODO before submission]** complete this into a full bibliography with stable DOI/arXiv links for every entry, plus per-paper screening disposition (included/excluded and why).

### A.3 Update procedure

The searches in A.1 are re-run, and this appendix re-dated, immediately before each submission; new hits are dispositioned in A.2 and any affected novelty claim re-scoped before the manuscript text is finalized. The watch items of Section 7 are checked at the same time.

### A.4 Re-executed search logs (2026-08-07)

_Engine caveat: the queries below were executed through a general-purpose web search engine (WebSearch, Claude Code) with abstract/full-text screening via direct fetches of arXiv/journal pages, not through native ADS/arXiv fielded query syntax. Query strings are logged verbatim and screening decisions per query; the pre-submission A.3 re-run should translate these strings to native ADS syntax. Screening was performed against the preregistered include/exclude criteria stated at the head of each block. Each block was produced by an independent research pass on 2026-08-07 and is reproduced verbatim._

#### Item 1 — scanner-model repeater timing

Screening criteria: include if the paper (a) tests burst arrival times of repeating FRBs against a scanning/revisit/beacon model, (b) performs any periodicity search on repeater catalogs at sub-day periods across multiple observing sessions, or (c) proposes paired/double-pass temporal signatures for technosignatures. Exclude: single-session periodicity, activity-window-only searches (logged as known prior art), pulsar-only timing, theory without data analysis.

- **S1.1** `fast radio burst repeater burst arrival times scanning beacon model likelihood test` — Returned spectro-temporal morphology work (MNRAS 544,2537; arXiv:2412.12404) and Weibull wait-time modeling. No candidate hits.
- **S1.2** `FRB repeater sub-day periodicity search exposure-corrected multiple observing sessions` — Candidates: arXiv:2507.14708 (deep-screened, see table); arXiv:2512.24936 (screened, see table); arXiv:2503.12013 (known prior art, within-session); arXiv:2512.21889 (uGMRT 20220912A monitoring — exclude: rate study).
- **S1.3** `technosignature paired pulse double-pass revisit temporal signature SETI beacon` — Candidates: arXiv:2607.01666 (FAST 3I/ATLAS periodic technosignature — exclude: narrowband toward interstellar object; new post-2025); arXiv:2506.14744 (alert brokers — exclude); arXiv:2205.02964 (pulsed beacons — exclude: single-pointing). No paired-pulse/double-pass matches.
- **S1.4** `FRB 121102 short period search hours exposure function periodogram` — Returned Cruces 2021 window-function analysis and Li 2021-adjacent short-period differencing (known prior art). No new hits.
- **S1.5** `repeating fast radio burst point process model comparison Poisson Weibull likelihood periodic model selection` — Returned Oppermann-line Weibull works, zDM repetition modeling (arXiv:2306.17403), wait-time memory analyses (arXiv:2302.06802) — all natural point-process models, no scanner alternative. Exclude all; known-art class.
- **S1.6** `fast radio burst artificial origin beacon hypothesis statistical test arrival times SETI` — Returned Loeb light-sail theory, peryton integer-second KS tests. No candidate hits.
- **S1.7** `"exposure function" OR "exposure-corrected" folded periodicity fast radio burst repeater alias 2026` — Candidates: Aznam et al. 2025 A&A (known prior art); A&A 2026 chromatic activity windows of 20121102A/20180916B — exclude: activity-window class (new post-2025 instance); arXiv:2507.15790 — exclude.
- **S1.8** `FRB repeater lighthouse scanning transmitter periodicity technosignature hypothesis test` — "Lighthouse" hits are astrophysical orbital-beaming models; arXiv:2305.18527 (Galactic Center 11–100 s periodic technosignature search) — exclude: voltage periodic-signal search, not repeater catalog timing.
- **S1.9** `interstellar beacon revisit time duty cycle search strategy "sweep period" transient` — Returned Benford 2010, Gray (known prior art); Apai, Lin & Wagner arXiv:2607.12106 (optical laser-beacon strategy, Jul 2026) — exclude: theory/strategy, no data analysis; new post-2025 adjacent strategy work.
- **S1.10** `arXiv 2025 2026 fast radio burst bursts "scanning" OR "raster" OR "revisit" model arrival times Bayesian` — No scanner-model hits; arXiv:2505.14219 reappeared (known prior art).
- **S1.11** `FRB 20201124A OR 20220912A periodicity search "minutes" OR "hours" multi-epoch folding window function` — Candidates: arXiv:2310.08971 (known prior art; 0.001–1000 s, no exposure folding); arXiv:2512.23392 (screened, see table); "Two Periodic Activity Epochs in FRB 20201124A" — exclude: activity-window; arXiv:2210.03610 — exclude: within-episode spin search.
- **S1.12** `"composite periodogram" low-event-count fast radio burst repeaters Aznam arXiv` — Confirms Aznam et al. A&A March 2025 identity/scope. Known prior art; no scanner model.
- **S1.13** `"double pass" OR "paired detections" OR "repeat visit" beacon transmitter SETI detection statistics fast transient` — Returned MultiBeam Coincidence Matching (spatial, not temporal), BL GC broadband-beacon repetition rejection (arXiv:2104.14148 — exclude). No qualifying hits.

Deep screens:

| Paper | Screen result | Decision |
|---|---|---|
| arXiv:2507.14708 (FRB 20240114A long+short period search; 57–111 sessions) | Full text: short-timescale searches per-session and in ≤3-day segments, plus a joint multi-session TOA search (tens of ms–tens of minutes); **no exposure correction on any short-timescale search** (exposure used only for the 143.4-d analysis); **no beacon/scanner models**; no ~1 hr–1 d folding across discontinuous sessions | Exclude as contradiction; **nearest post-2025 neighbor** — added to must-cite list (Section 1) |
| arXiv:2512.24936 (FRB 20240114A, Dec 2025) | Single continuous 15,628-s session, periods ≥ 0.1 s, magnetar framing | Exclude: within-session class; added to prior-art list |
| arXiv:2512.23392 (20201124A phase-folding+MCMC, 2026) | Method paper on second-scale spin periods; no scanner/revisit model | Exclude; added to prior-art list |
| Apai, Lin & Wagner arXiv:2607.12106 (Jul 2026) | Optical laser-beacon strategy; no data analysis, no FRB content, no paired-pass signature | Exclude: strategy class (with Benford/Lingam-Loeb/Gray) |

New post-2025 items: arXiv:2507.14708, 2512.24936, 2512.23392, A&A 2026 chromatic activity windows, arXiv:2607.12106, 2607.01666 — none applies a scanner-model or paired-pass likelihood, none performs an exposure-folded sub-day search across discontinuous sessions.

**Verdict: CLAIM HOLDS** (with arXiv:2507.14708 promoted to the must-cite-and-distinguish list).

#### Item 2 — single-pulse copy-exactness

Screening criteria: include if (a) pulse-to-pulse waveform cross-correlation across a single-pulse population interpreted as anomaly, (b) copy-exactness proposed as a technosignature statistic, or (c) natural pulses claimed waveform-identical.

- **S2.1** `pulsar single pulse cross-correlation identical pulses technosignature` — arXiv:2601.17299 (B0329+54, ApJ 2026): correlates emission across frequencies **within the same pulse** — exclude (emission physics, within-pulse). Profile/variability studies — exclude.
- **S2.2** `pulse-to-pulse waveform correlation pulsar anomaly detection statistic` — PTA optimal-statistic papers (cross-pulsar, not cross-pulse) — exclude; Parkes Transient Events II single-pulse database (ApJS 2025) — infrastructure only, computes no copy statistic — exclude, noted.
- **S2.3** `"copy" OR "identical" single pulses pulsar SETI artificial repetition statistic` — Croft et al. ATA FAC autocorrelation SETI (ApJ 2018) — within-signal engineered-coherence statistic, not a pulse-population copy statistic — exclude, adjacent art. Osłowski single-pulse timing — exclude (jitter art).
- **S2.4** `RRAT single pulse morphology similarity clustering machine learning` — Vela single-pulse ML (arXiv:2108.13462), single-pulse classifiers (arXiv:1807.07164, 1603.09461) — candidate sifting/emission classes, no copy-exactness test — exclude.
- **S2.5** `Crab giant pulses cross-correlation between pulses waveform similarity repeated shapes` — Jessner 2010 ("contemporaneous" = same pulse at two frequencies) — exclude; K5 VLBI GP study (arXiv:0903.2652, within-pulse polarization/spectral correlation) — exclude. No paper correlates distinct GPs for copy detection.
- **S2.6** `technosignature statistic repeating identical radio bursts pulse shape 2025` — 3I/ATLAS (arXiv:2607.01666), Galactic Center (arXiv:2305.18527) periodic searches — exclude: periodicity, not waveform copy-exactness.
- **S2.7** `FRB repeating bursts "remarkably similar" morphology twin bursts correlation` — "Twin FRBs" (arXiv:2406.13704, cross-source near-identical one-offs) — exclude per protocol, noted; CHIME microsecond morphology of 35 repeaters (arXiv:2411.02870) — population statistics, no burst-pair cross-correlation — exclude, noted.
- **S2.8** `microstructure correlation between successive pulses pulsar memory pulse shape` — Cordes 1976 anchor confirmed (no pulse-to-pulse microstructure correlation); FAST interpulse microstructure (ApJS 2025, within-pulse) — exclude, prior art as claimed.
- **S2.9** `"carbon copy" bursts FRB pulsar single pulses` — No pulsar candidates; magnetar/GP energetics — exclude.
- **S2.10** `"carbon copies" OR "carbon copy" morphologically similar burst pairs repeating FRB CHIME` — arXiv:2607.02939 and arXiv:2602.16409 (FRB 20240114A carbon-copy bursts / spectral memory, plasma-lensing framing) — exclude per FRB-only rule; **noted: closest 2025–2026 development to a copy-similarity observable; FRB-specific, propagation-framed, no pulsar/RRAT analogue published**.
- **S2.11** `pulsar single pulse jitter statistics 2025 stochastic pulse shape variation millisecond pulsars` — FAST IPTA jitter (arXiv:2401.12426), MeerKAT jitter (arXiv:2101.08531), NANOGrav profile variability (arXiv:1810.08269) — stochastic noise-budget treatments, no pulse-pair similarity test — exclude; updates the stochasticity anchors.
- **S2.12** `Stanton HD 89389 identical pulses optical SETI starlight pulse pairs` — Stanton 2025 (Acta Astronautica): pairs of near-identical fast **optical** pulses from sun-like stars — exclude: optical photometry, non-pulsar, no population statistic; **noted as nearest criterion-(c) report in any band**.

New 2025–2026 items: FRB 20240114A carbon-copy papers (arXiv:2607.02939, 2602.16409); CHIME repeater microsecond morphology (arXiv:2411.02870); Parkes single-pulse database (ApJS 2025); B0329+54 inter-frequency correlations (arXiv:2601.17299); Stanton 2025. None computes a pulse-to-pulse waveform-correlation copy-exactness statistic over a pulsar/RRAT population; none proposes it as a technosignature.

**Verdict: CLAIM HOLDS** (caveat line added citing the FRB 20240114A carbon-copy literature as adjacent FRB-domain art).

#### Item 3 — transformed repetition and voltage-domain coverage

Screening criteria: include only papers analyzing complex voltage/baseband FRB data for repetition under a transformation beyond plain delay, injection-calibrated cyclostationarity/determinism tests, or cyclic spectroscopy applied to an FRB. Plain lensing-echo searches logged as known boundary; pulsar cyclic spectroscopy as known art.

- **S3.1** `FRB baseband voltage data search for transformed copies phase rotation repetition` — Michilli CHIME baseband pipeline (2021ApJ...910..147M) — exclude, infrastructure; CHIME polarization catalogs (arXiv:2401.17378, 2411.09045) — exclude, Stokes polarimetry; CHIME voltage morphologies (arXiv:2312.14133) — exclude, intensity-domain. No transformed-copy search.
- **S3.2** `fast radio burst cyclostationary signal analysis detection sensitivity` — Price et al. 2019 (arXiv:1901.07412) — known anchor ("no cyclic features apparent," no injection-calibrated sensitivity); UAV RF detection (2025) — exclude, non-astronomical; V-FASTR (arXiv:1605.07606) — exclude. No new FRB cyclostationarity paper with demonstrated sensitivity.
- **S3.3** `cyclic spectroscopy fast radio burst application` — Price 2019 only FRB application; Demorest-lineage pulsar work (arXiv:1106.3345) — known art.
- **S3.4** `FRB polarization swapped inverted copy echo search voltage data` — CHIME polarization catalogs, FRB 20180916B magneto-ionic (arXiv:2205.09221), 20240114A polarimetry (arXiv:2410.10172) — all property measurement, exclude; Kader/Leung PBH lensing (arXiv:2204.06001) — known boundary, plain delay.
- **S3.5** `fast radio burst frequency-shifted spectral remapping echo plasma lensing coherent search` — arXiv:2602.16409 (plasma-lensing spectral caustics, Feb 2026, new) — exclude, intensity morphology; arXiv:2407.04097 (multi-plane lensing phase-correlation simulations) — exclude, delayed-copy region; plasma-lensing interpretation papers — exclude.
- **S3.6** `FRB gravitational lensing search phase coherence baseband 2025 2026` — Kader et al., partial coherence from multipath, FRB 20220413B (arXiv:2512.11969, PRD, Dec 2025, new): time-lag + frequency-lag correlation of channelized voltages, propagation framing, no transformed-copy search, no injection calibration — exclude (boundary extension of the phase-coherence discriminator); FRB 20190320B lensing evidence (ApJ, 10.3847/1538-4357/ae22d3, new) — see S3.10; Kader 2022 PRD 106, 043016 — known boundary.
- **S3.7** `fast radio burst technosignature modulation coded signal baseband voltage SETI analysis` — Price 2019 (BPSK simulation, no sensitivity calibration at burst S/N) — known anchor; SETI@home front end (arXiv:2506.14718), 3I/ATLAS searches (arXiv:2603.19023, 2607.01666) — exclude, not FRB voltage data; blc1 framework — exclude, narrowband CW.
- **S3.8** `test determinism amplitude statistics received electric field radio burst Gaussianity intrinsic coherence` — Vela field statistics (astro-ph/0304429), polarimetry statistics (arXiv:0812.3461), visibility statistics (arXiv:1304.0803) — pulsar/generic AMN statistics, not an FRB determinism test — known art. No FRB field-determinism test.
- **S3.9** `Kader phase coherence discriminator FRB lensing 2025` — arXiv:2512.11969 — exclude per S3.6; wave-optical lensed FRBs (arXiv:2504.10523) — exclude, delayed-copy/wave-optics. 2025–2026 activity stays inside the lensing-echo boundary.
- **S3.10** `Evidence for Gravitational Lensing FRB 20190320B lens mass 420 solar masses method` — FRB 20190320B candidate (~424 M_sun, 58 CHIME baseband events) — exclude: plain delayed copy (Δt ≈ 1.24 ms, achromatic check); IMBH microlensing in Catalog 2 (arXiv:2605.19653, May 2026, new) — exclude, intensity-domain statistics.
- **S3.11** `correlate electric field waveforms between repeat bursts FRB 121102 identical waveform test` — FRB 121102 burst pairs (arXiv:1708.07234), time-frequency structure, repetition statistics — all intensity-domain; no cross-burst field-waveform correlation or determinism test exists.

New 2025–2026 items (none falsifying): arXiv:2512.11969 (delay-domain propagation, no transformed copies); FRB 20190320B lensing candidate (plain delayed copy); arXiv:2602.16409, 2605.19653 (intensity-domain lensing).

**Verdict: CLAIM HOLDS** (wording tightened: cyclic spectroscopy has "no FRB application beyond the single insensitive test in Price 2019"; nearest miss arXiv:2512.11969 remains inside the delay-domain propagation boundary).

#### Item 5 — phase-residual structure search (H4)

Screening criteria: include if the paper analyzes post-dedispersion residual phase of FRB (or magnetar-burst) voltage data for repeated/deterministic/coded structure, or performs any technosignature analysis targeting FRB 20200120E or M81. Exclude: phase used solely as propagation veto (logged), intensity-domain microstructure (logged), position-angle studies unless framed as coding.

- **S5.1** `FRB voltage data phase modulation search coded signal fast radio burst` — arXiv:2605.12098 (periodic emission-frequency modulation, 20240114A) — exclude: intensity/spectral domain, activity cycle; arXiv:2312.14133 — exclude. No phase-structure hits.
- **S5.2** `fast radio burst "phase" technosignature modulation "coherently dedispersed"` — **arXiv:1901.07412 (Price et al. 2019, MNRAS 486, 3636)** — flagged; full-text screen: Sec. 3.6 performs cyclic spectroscopy on the coherently dedispersed pulse, explicitly "to search for evidence of signal modulation that would suggest terrestrial origin—or indeed, emission from a technologically advanced extraterrestrial civilization." Null; BPSK injections sensitive only at +20 dB. **INCLUDE — direct prior art** (single-burst, insensitive, one-off FRB). arXiv:2407.04097 — exclude, lensing forecast.
- **S5.3** `"FRB 20200120E" SETI technosignature search M81` — Gajjar et al. 2021 RNAAS — known anchor (FRB-science framing); all other hits astrophysical — exclude.
- **S5.4** `M81 globular cluster technosignature Breakthrough Listen radio search` — AJ 169, 222 (2025) BL GBT archive search (3350 pointings) — flagged, M81 membership unstated; arXiv:2103.16250, 2304.02756 — exclude, no M81-specific claim.
- **S5.5** `Choza Breakthrough Listen "nearby galaxies" technosignature survey M81 target list` — **arXiv:2312.03943 (Choza et al. 2024, AJ, 97 nearby galaxies)** — flagged; target-table screen: Appendix B contains **MESSIER081 (3.63 Mpc)** — GBT narrowband Doppler-drift search of the galaxy **center** (1.1–2.7, 4.0–11.2 GHz). **INCLUDE — falsifies the absolute "no published SETI analysis of M81."** Caveat: nucleus pointing; FRB 20200120E's globular cluster lies ~19 arcmin projected from center vs. a ~9 arcmin L-band beam — not a search of the FRB position; narrowband CW, not phase analysis.
- **S5.6** `cyclostationary analysis fast radio burst voltage cyclic spectroscopy technosignature` — Only Price 2019 and pulsar cyclic spectroscopy (arXiv:1106.3345) — known anchors.
- **S5.7** `arXiv 2025 fast radio burst "phase residual" OR "phase trajectory" voltage deterministic structure search` — arXiv:2512.11969 (Kader et al., PRD 2025; "excess correlation only in absolute power and not in phase" — propagation veto) — known-art anchor, exclude as falsifier; arXiv:2411.02870, 2506.19006 — exclude, intensity-domain. No phase-as-search-space papers.
- **S5.8** `Kader 2025 FRB phase coherence scintillation follow-up artificial signal search` — arXiv:2512.11969; arXiv:2602.16409, 2607.00505 — all propagation physics, exclude. **No 2025–2026 paper repurposes phase coherence as a structure/coding search space.**
- **S5.9** `fast radio burst artificial origin information content coding analysis signal structure SETI paper` — arXiv:1903.12186 (terraformation theory) — exclude, no data; BL ML re-detection of 121102 — exclude, intensity-domain.
- **S5.10** `"FRB 20200120E" OR "M81" technosignature 2025 2026 search extraterrestrial` — No candidate hits; no FRB 20200120E-targeted technosignature paper in 2025–2026.
- **S5.11** `SGR 1935+2154 magnetar radio burst voltage phase modulation artificial signal analysis` — No candidate hits.
- **S5.12** `"cyclic spectroscopy" FRB 2024 2025 2026 burst modulation search voltage data` — Only Price 2019 resurfaces; 2024–2026 "modulation" hits (arXiv:2605.12098, 2507.14708, 2507.04609) are activity-periodicity/intensity studies — exclude. No post-2019 cyclic-spectroscopy follow-up on FRB voltages.

New relative to anchors: Kader et al. confirmed published (PRD; arXiv:2512.11969), phase-as-propagation-diagnostic framing intact; nothing after it repurposes voltage phase as a search space. Choza et al. 2024 predates the audit but was missing from the anchor list.

**Verdict: CLAIM NEEDS RESCOPING** — Price et al. 2019 Sec. 3.6 (published single-burst modulation search on dedispersed FRB voltages) and Choza et al. 2024 (published M81-center narrowband SETI search) falsify the two absolute negatives. Rescoped wording applied in Section 5: the surviving novelty is the cross-burst phase-residual/trajectory structure search on a repeater's dedispersed voltages, any sensitivity-calibrated phase-domain test, and any technosignature coverage of the FRB 20200120E position.
