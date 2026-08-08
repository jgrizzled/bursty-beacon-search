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
| 5. Phase-residual structure search (H4) | No prior search of coherently dedispersed FRB voltage phase for repeated or deterministic modulation was identified; nearest prior art is intensity-domain (Majid 2021 ACF microstructure) and phase-as-veto (Kader 2025). Public-data caveat: the thesis first target has no public voltages. |

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

**Scoped Phase 1 claim (use this wording):** this audit identified no prior application of the complete scanner hypothesis test—strict plus paired-pass, exposure-folded, alias-aware, and compared against explicit natural point-process models. The strict-periodicity limiting case is directly or indirectly constrained for some well-observed sources and period ranges (including 1.5–100 d for FRB 20180916B, plus within-session short-timescale searches). Must-cite-and-distinguish: CHIME/FRB 2020 (Nature 582, 351) and CHIME/FRB 2023 (ApJ 947, 83).

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

**No sensitive searches were identified for:** copies related by calibrated phase rotation, polarization inversion/swap, spectral remapping, or coding; cyclostationarity with demonstrated sensitivity (the located FRB test—Price et al. 2019 on FRB 180301—was shown by its own injection test to have no sensitivity at the burst's S/N); or determinism tests on the field itself (located 2026 shot-noise work fits stochastic models but does not test the deterministic alternative). Cyclic spectroscopy is mature for pulsars (Demorest 2011 onward); this audit identified no application to one-off FRBs.

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

**Finding: supported — no phase-domain structure search was identified; the nearest prior art is intensity-domain or phase-as-veto.**

Complete pass over every voltage-data paper on FRB 20200120E, the H4 first target (all verified from full texts or arXiv sources, 2026-08-07):

- **Majid et al. 2021** (DSN DSS-63, 62.5 ns baseband): coherent dedispersion, matched filtering to 62.5 ns, profiles resolving components ≲ 100 ns, L/R circular profiles, dynamic spectra, and an **intensity autocorrelation** yielding ~2.3 µs quasi-periodic microstructure — the nearest prior art, and intensity-domain only.
- **Kirsten et al. 2022** (EVN voltages): voltage→filterbank burst search; SFXC coherent-dedispersion **correlation** for astrometry. No phase-structure analysis.
- **Nimmo et al. 2022** (Nat. Astron.): profiles to 31.25 ns, intensity ACFs and power spectra, brightness temperatures, full polarimetry (Faraday spectra, RM, PA). All intensity/Stokes-domain.
- **Nimmo et al. 2023** (MNRAS burst storm, 60 bursts): morphology, structure-resolved DM, energy and wait-time distributions, **TOA-level periodicity (null)** — arrival-time periodicity, not carrier phase.
- **Pearlman et al. 2025** (Nat. Astron.): coherent-dedispersion profiles to 31.25 ns, radio–X-ray coincidence; periodicity searched on X-ray photons only.

General FRB voltage prior art (extending audit item 3): the Leung/Kader 2022 delayed-copy autocorrelation and the Kader et al. 2025 phase-coherence discriminator use voltage phase **as a propagation veto** (power-correlated but phase-incoherent ⇒ scintillation), not as a search space for deliberate structure; cyclostationarity has no demonstrated FRB sensitivity (Price et al. 2019 self-reported); no determinism tests on the field were located; cyclic spectroscopy is mature for pulsars (Demorest 2011) with no FRB application identified.

**SETI prior art on the first target:** no published SETI/technosignature analysis of FRB 20200120E or M81 was located (targeted searches plus a BL Open Data Archive API check — no matching target). Closest: Gajjar et al. 2021 (RNAAS), a GBT 4–8 GHz burst search by BL-affiliated authors, framed purely as FRB science, null, no data release.

**Scoped H4 claim (use this wording):** this audit identified no prior search of coherently dedispersed FRB voltage phase for repeated or deterministic modulation structure. Must-cite-and-distinguish: Kader et al. 2025 (phase coherence as veto), Majid et al. 2021 (intensity-ACF quasi-periodicity), Leung/Kader 2022 (delayed-copy boundary), Demorest 2011 (pulsar cyclic spectroscopy).

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

_Status: skeleton. The audit above was run as a targeted search on 2026-08-07; the exact strings and screening decisions were not logged at execution time. Before any publication-facing "first"/"never searched" claim, the searches must be **re-executed and logged** into this appendix. Until then, all novelty language uses the adopted hedge: "not identified in the literature searched through 2026-08-07." The defensible claim remains the **combination** (explicit scanner/natural generative-model comparison + paired-pass structure + time-resolved exposure folding + long-baseline alias-aware sub-day coverage), not periodicity searching in general._

### A.1 Databases and date ranges

- arXiv (astro-ph.HE, astro-ph.IM), ADS, and journal full text; searched 2026-08-07; coverage through that date.
- CHIME/FRB verification performed on full LaTeX sources (arXiv:2601.09399, 2605.08410, 2301.08762), not abstracts.
- **[TODO before submission]** exact search strings and field restrictions per database; inclusion/exclusion criteria; backward/forward citation-chaining procedure and depth; stated update date immediately before submission.

### A.2 Screened-paper list (compiled from the audit above; exclusion reasons [TODO])

Timing/periodicity: CHIME/FRB 2020 (Nature 582, 351; arXiv:2001.10275) · Rajwade et al. 2020 (arXiv:2003.03596) · Cruces et al. 2021 (arXiv:2008.03461) · Aznam et al. 2025 (A&A) · Li et al. 2021 (FAST 121102) · Niu et al. 2024 (arXiv:2310.08971) · Du et al. 2025 (arXiv:2503.12013) and challenge (arXiv:2505.14219) · Oppermann, Yu & Pen 2018 (MNRAS 475, 5109) · CHIME/FRB Catalog 2 (arXiv:2601.09399) · Cook et al. 2026 (arXiv:2605.08410) · CHIME 25-repeater catalog (arXiv:2301.08762) · FRB 20191221A (Nature 607, 256; retracted 2026).

SETI/beacon strategy: Lingam & Loeb 2017 · Benford, Benford & Benford 2010 · Gray 2021 · BLIPSS-type folding searches.

Single-pulse statistics: Rickett 1975 · Jenet et al. 1998 · Cordes 1976 (ApJ 208, 944) · Lam et al. 2019 · Weltevrede et al. 2006/2007 · Hankins & Eilek 2007 · Soglasnov et al. 2004 · FAST J1913+1330 (arXiv:2306.02855) · B0329+54 per-phase-bin correlations (arXiv:2601.17299) · Main et al. 2022 · Kerr 2015 · Stanton 2025 (Acta Astronautica).

Propagation/copy mechanisms: FRB 20240114A carbon-copy debate (arXiv:2602.16409; arXiv:2607.02939) · Lin et al. 2023 (arXiv:2305.13274) · B2217+47 echoes (arXiv:1802.03473) · Nimmo et al. 2022.

Echo/voltage searches: Leung et al. 2022 + Kader et al. 2022 (PRD 106, 043017/043016) · Kader et al. 2025 (arXiv:2512.11969) · Wucknitz, Spitler & Pen 2021 · Pastor-Marazuela 2024/2025 review · Sammons et al. 2020 · Chang et al. 2024 · Price et al. 2019 (FRB 180301) · Demorest 2011.

FRB 20200120E / H4 prior art (added 2026-08-07): Bhardwaj et al. 2021 (arXiv:2103.01295) · Majid et al. 2021 (arXiv:2105.10987) · Kirsten et al. 2022 (arXiv:2105.11445) · Nimmo et al. 2022 (arXiv:2105.11446) · Nimmo et al. 2023 (arXiv:2206.03759) · Pearlman et al. 2025 (arXiv:2308.10930) · Zhang et al. 2024 (arXiv:2310.00908) · Trudu et al. 2022 (arXiv:2204.05050) · Gajjar et al. 2021 (arXiv:2107.09445).

**[TODO before submission]** complete this into a full bibliography with stable DOI/arXiv links for every entry, plus per-paper screening disposition (included/excluded and why).

### A.3 Update procedure

The searches in A.1 are re-run, and this appendix re-dated, immediately before each submission; new hits are dispositioned in A.2 and any affected novelty claim re-scoped before the manuscript text is finalized. The watch items of Section 7 are checked at the same time.
