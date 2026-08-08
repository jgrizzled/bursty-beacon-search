# The Bursty Beacon Search

_A research note on recipient-maximizing radio beacons and an archival search for their discovery-layer signals_

_Revision 3 — adds the intergalactic extension: the distance-cancellation result and beam-filling horizon, the capital-threshold structure, the two-builder stream mapping, and the collapsed phase-modulated discovery/message architecture. Revision 2 incorporated receiver-geometry and dispersion-budget analysis, transmitter cost modeling, the repetition-ladder design principle, and revised archive priorities._

## Executive summary

A rational interstellar beacon builder who wants to maximize the number of civilizations that detect the beacon faces a different optimization problem from one who wants to maximize information rate to a known receiver. The discovery signal must be detectable by unknown instruments, survive unknown real-time pipelines, be retained in a useful data product, attract attention, and support confirmation before institutional interest disappears.

The cost-optimized beacon framework developed by Benford, Benford, and Benford suggests that a powerful scanning beacon can economize by using a narrow beam and short dwell time. Our analysis sharpens that picture in several ways:

1. Capital should initially be allocated to range until the accessible volume saturates at the current scale. Beyond that point, additional beams, bands, or revisits become more valuable than still greater range—until revisit time falls below typical receiver session or transit timescales, after which marginal capital is better spent clearing the distance threshold to the next scale of targets. The general rule is **range, then cadence, then more range at the next scale**.
2. The recipient-maximizing dwell time is the minimum required to deliver an attention-grabbing packet to the target receiver class—of order $0.03$–$0.3\,\mathrm{s}$ when interstellar dispersion is natural, extending to a few seconds only where synthetic pre-chirp must be carried at low frequency. Shorter dwells permit faster scanning and shorter revisit periods, but because dwell depends on transmitter capital and technology assumptions that cannot be pinned down, it should be treated as a bounded range rather than a point prediction.
3. Revisit time is a central design variable. Multiple detections may be needed to establish artificiality, yet a revisit delayed by years or decades can exceed the attention span of institutions, surveys, personnel, and data-retention systems.
4. Episodic, narrow-field listeners contribute little to expected recipients. Their probability of being pointed at the correct location during a brief beacon visit is already small, and requiring multiple detections suppresses it further. Wide-field monitors dominate.
5. The discovery layer should therefore be designed primarily for wide-field radio astronomy systems, not for dedicated SETI receivers. Fast-transient science—especially searches for fast radio bursts and related events—is a major reason such systems exist.
6. A discovery signal must pass through the selection effects of transient pipelines. It should resemble a valid astrophysical transient closely enough to trigger and be saved, while preserving one or more features that can later establish artificiality.
7. Because the builder cannot know receiver band edges, session structures, or pipeline details, each design parameter should be anchored to universal physics of the receiver class—sky temperature, scattering, field-of-view economics, dispersion as the generic trigger feature—rather than to any particular civilization's instruments. Parameters that physics does not pin down should be carried as ranges, since they depend on transmitter economics the analysis should not pretend to know.
8. Sightline geometry is not tunable per recipient. For an in-plane transmitter, most recipients observe a total dispersion measure consistent with their own Galactic models, so the discovery event lands in Galactic single-pulse and RRAT-like phenomenology for a large fraction of receiver geometries regardless of design intent. Both the design and the archival search should treat that stream as primary for the galactic builder class.
9. Per-recipient energy cost is distance-invariant: beam footprint area and required effective isotropic radiated power both scale as $d^2$, so the cost per star delivered is fixed as long as the footprint stays filled with target stars. The cancellation holds out to a gain-dependent **beam-filling horizon** (tens of megaparsecs at plausible gains). What grows as $d^2$ is the per-pointing capital threshold, so intergalactic capability is an entry barrier, not a per-recipient rate cost.
10. An extragalactic (Local Volume) builder delivers events that observationally _are_ genuine fast radio bursts—real excess dispersion, real localization to a visible host galaxy—so artificiality rests entirely on the tags. This yields a two-builder structure: galactic builders land in Galactic single-pulse and RRAT streams, extragalactic builders in the genuine-FRB repeater catalog with hosts, and identical tag statistics search both.
11. At intergalactic scale, energy accounting collapses the separate discovery and message layers into one signal: phase modulation of the chirped carrier is invisible to intensity pipelines but carries kilobits to megabits per burst in voltage data at zero additional energy, and doubles as the strongest artificiality tag.

The leading candidate is a **tagged dispersed packet**: a positive-dispersion, broadband, low-gigahertz event whose total dispersion is dominated by the real interstellar medium and which contains one conventional high-significance trigger component plus two or more exact transformed copies inside the same retained capture. To most recipient geometries it presents as a Galactic single pulse or RRAT-like event rather than an extragalactic FRB. The trigger-level morphology should remain inside the region that fast-transient pipelines are designed to accept. Artificiality should be encoded in exact relationships that ordinary astronomy has little reason to test—channel-commutative transformed repetition, polarization coding, cyclostationarity, or deterministic voltage structure—with enough within-capture repetition that a single saved event is self-confirming. Confirmation opportunities should be distributed as a geometric ladder of timescales (intra-packet, intra-dwell, paired scan pass, sweep recurrence) so that some rung matches whatever observation structure an unknown receiver has.

The most promising archival targets are not necessarily spectacular events that everyone somehow ignored. They are signals that were **ordinary enough to trigger and be retained, but whose artificiality lies in a statistic that existing astronomy did not routinely calculate**. High-priority archives therefore include Galactic single-pulse and RRAT streams, the timing records of known repeating sources (which remain untested against exposure-folded scanner models), candidate-level transient stores including rejects, the full time extent of saved cutouts, public FRB dynamic spectra, and baseband samples.

This note develops the rationale for that conclusion and presents a staged archival search plan.

---

## 1. Background: from cost-optimized beacon to recipient-optimized beacon

The Benford cost-optimized beacon model treats an interstellar beacon as a capital allocation problem. A transmitter can trade aperture, peak power, operating cost, beam width, dwell time, scan rate, and revisit period. A narrow beam increases effective isotropic radiated power but covers only a small solid angle at a time. A scanning beacon must therefore choose how long to illuminate each direction and how often to return.

A cost optimum is not automatically a recipient optimum. To maximize expected recipients, the builder must account for the receiving population and the full chain between illumination and recognition.

A useful schematic objective is

$$
\mathbb{E}[N_{\mathrm{recipients}}]
=
\sum_j N_j\,
P_{\mathrm{band},j}
P_{\mathrm{sky},j}
P_{\mathrm{detect},j}
P_{\mathrm{trigger},j}
P_{\mathrm{save},j}
P_{\mathrm{notice},j}
P_{\mathrm{confirm},j},
$$

where $j$ indexes classes of receiving systems or civilizations. The factors represent, respectively, spectral overlap, sky coverage, physical detectability, pipeline triggering, useful retention, human or automated recognition, and eventual confirmation.

This formulation changes the optimization in several important ways.

### 1.1 Range first, then coverage and cadence

While the beacon range is smaller than the scale of the target population, increasing range can add many potential recipients. Once the whole Galaxy is within range, additional power no longer adds new Galactic targets. The marginal capital should then be compared across:

- additional beams;
- shorter revisit periods;
- additional frequency bands;
- better confirmation scheduling;
- increased bandwidth or robustness;
- and signal features that improve trigger or recognition probability.

A strict rule of “range, then beams” is therefore a strong first approximation, but after range saturation the builder should compare beams with spectral diversification and deliberate confirmation passes. There is also a stopping rule for that comparison: beam and cadence additions hit diminishing returns once the revisit time falls below typical receiver session or transit timescales, and beyond that pivot the marginal capital is better spent clearing the distance threshold to the next scale of targets. The allocation principle generalizes to **range, then cadence, then more range at the next scale**—developed quantitatively in the intergalactic extension of Section 16.

### 1.2 Short dwell can dominate long dwell

A long dwell increases received energy in one direction but slows the sweep. If the receiver is a sensitive wide-field transient monitor, the discovery event need not last for seconds. A dwell near $0.1\,\mathrm{s}$ or below can provide enough time for a packet containing several millisecond-scale components while allowing much faster sky coverage.

The key distinction is between **dwell time** and **individual pulse width**. A $0.1\,\mathrm{s}$ dwell need not be a smooth $0.1\,\mathrm{s}$ pulse. It can be a structured packet containing one or more $1$–$10\,\mathrm{ms}$ components within a total duration of tens of milliseconds.

These two quantities have very different epistemic status. The millisecond component width is pinned by receiver-side physics: at gigahertz frequencies and Galactic dispersion measures, intra-channel smearing forces effective widths near a millisecond for essentially any plausible channelization, so short-burst phenomenology is robust to unknown backend choices. Dwell time, by contrast, depends on transmitter capital and scan economics that cannot be predicted, and should be carried as a range—roughly $0.03\,\mathrm{s}$ to a few seconds—with the guiding principle that dwell is the minimum required to deliver an attention-grabbing packet to the wide-field receiver class.

### 1.3 Revisit time is part of detectability

A single unusual event may be insufficient to establish artificiality. Confirmation can require:

- a second event from the same position;
- recurrence with a consistent dispersion measure;
- repetition of an internal code;
- independent detection by another observatory;
- or a follow-up observation with a higher-gain instrument.

If the next visit occurs thirty years later, the original event may have been forgotten, the instrument decommissioned, the data product lost, the sky localization judged inadequate, or the institutional context changed. Thus the builder should maximize not only first-hit probability but also the chance of obtaining a second, institutionally connected hit.

A second beam can be used as a **trailing confirmation beam** that repeats the first beam's path after a short lag, so that an alert remains active when the second event arrives. A cheaper competitor achieves the same effect with no additional capital: a single beam whose scan pattern doubles back on itself after minutes to hours, at the cost of halving fresh-sky cadence. The optimal lag is plausibly short enough that both events land within one continuous observation or transit window, so the pair is captured by a single pointing.

More generally, because the builder cannot know receiver session lengths, alert latencies, or attention spans, repetition should not be concentrated at any single timescale. The robust structure is a **repetition ladder**: exact copies separated by milliseconds (within one packet), tens of milliseconds (within one dwell), minutes to hours (paired pass), and the sweep period itself (hours to months). The lower rungs make a single retained capture self-confirming, removing receiver session structure and institutional attention span from the critical path; the upper rungs establish the scanner model and defeat attention decay. The rungs serve different factors in the recipient chain: closely spaced pairs are weak _artificiality_ evidence, since natural repeaters cluster bursts, so the short rungs serve retention and notice while the long rungs serve artificiality and confirmation.

### 1.4 Why episodic narrow-field listeners contribute little

For a narrow dish or interferometric beam that observes only a tiny part of the sky, the probability of temporal and spatial alignment with a brief scanning beacon is small. If the listener also requires multiple detections, the probability falls approximately as a Poisson rare-event process.

For expected intercepted visits $\lambda$,

$$
P(K\geq 2)=1-e^{-\lambda}(1+\lambda).
$$

When $\lambda\ll 1$,

$$
P(K\geq 2)\approx \frac{\lambda^2}{2}.
$$

This quadratic suppression makes episodic listeners poor contributors to expected confirmed recipients. Wide-field monitors, continuous survey instruments, and commensal systems matter much more.

---

## 2. The receiver ecology: wide-field radio transient systems

A beacon builder cannot safely assume that many civilizations operate dedicated all-sky SETI monitors. It is more reasonable to assume that some civilizations build wide-field instruments for their own astrophysics, navigation, surveillance, plasma science, time-domain astronomy, or transient discovery.

On Earth, fast transients provide a strong motivation for wide-field radio systems. A narrow directional telescope has little chance of catching a rare, brief, unpredictable event. Wide instantaneous field of view, continuous operation, and automated detection pipelines are therefore valuable.

Radio is especially favorable because:

- coherent transmitters can achieve high effective isotropic radiated power;
- low-gigahertz instruments can obtain large fields of view at manageable aperture-element counts;
- interstellar dust is not a major obstacle at radio wavelengths;
- dispersion provides a physically meaningful trigger feature;
- and wide-field radio surveys already search for millisecond-to-second events.

The receiver-weighted optimum may therefore lie below the transmitter-cost optimum. The band should be derived from invariants of the receiver class rather than from any particular civilization's surveys: Galactic synchrotron sky temperature rises steeply below a few hundred megahertz, scattering and dispersion smearing degrade fast-transient science at low frequency, and field of view per unit collecting cost falls with increasing frequency. Any civilization pursuing millisecond coherent transients converges on roughly $0.5$–$2\,\mathrm{GHz}$ for these reasons, independent of terrestrial history.

Because sub-band choices within that window are not predictable, the robust design occupies a large fractional bandwidth—an octave or more—so that any receiver sampling a few-hundred-megahertz slice anywhere in the window records a fully broadband event. This replaces the anthropocentric goal of matching specific survey bands with the generalizable goal of saturating the physically motivated window.

---

## 3. Pipeline selection is part of the propagation channel

The physical interstellar channel is only one part of the end-to-end communication channel. A beacon also passes through a computational and institutional channel:

$$
\text{illumination}
\rightarrow
\text{digitization}
\rightarrow
\text{real-time trigger}
\rightarrow
\text{callback or buffer save}
\rightarrow
\text{candidate classification}
\rightarrow
\text{human or automated notice}
\rightarrow
\text{follow-up}
\rightarrow
\text{confirmation}.
$$

A signal can fail at any point.

Fast-transient systems commonly apply operations such as:

- radio-frequency-interference masking;
- zero-dispersion subtraction;
- positive-dispersion trial searches;
- matched filtering over a limited width range;
- signal-to-noise thresholds;
- width or dispersion-measure cuts;
- machine-learning classification;
- catalog-level rejection of known Galactic sources;
- and selective retention of voltage or baseband data.

The rational beacon builder cannot know exact implementations, but can infer broad regularities from the science that motivates the instruments. A robust discovery layer should therefore lie near the center of the expected trigger manifold, while placing its strongest artificiality evidence in secondary statistics preserved by the archived data.

This leads to a two-level design principle:

> **The outer envelope should get through the pipeline; the inner structure should establish artificiality.**

---

## 4. Candidate discovery-layer design: the tagged dispersed packet

The leading candidate is a broadband, positive-dispersion transient packet that resembles a natural dispersed burst at trigger resolution—an FRB for low-Galactic-dispersion sightlines, a Galactic single pulse or RRAT event for most others—but contains exact, low-probability structure at higher analytical resolution.

### 4.1 Nominal design

The following values are illustrative rather than definitive:

| Property                 | Nominal design region                                                                                    |
| ------------------------ | -------------------------------------------------------------------------------------------------------- |
| Receiver-facing band     | Physics-anchored window, roughly $0.5$–$2\,\mathrm{GHz}$                                                 |
| Occupied bandwidth       | An octave or more of fractional bandwidth, smoothly occupied                                             |
| Apparent dispersion      | Dominated by real interstellar dispersion from an in-plane transmitter; exact cold-plasma $\nu^{-2}$ law |
| Optional pre-chirp       | Modest, and only near the top of the band where its dwell cost is small                                  |
| Trigger-component width  | Roughly $1$–$10\,\mathrm{ms}$ observed (pinned by intra-channel smearing physics)                        |
| Complete packet duration | Tens of milliseconds                                                                                     |
| Main trigger component   | Simple, bright, broadband, near packet center                                                            |
| Additional components    | Two or more exact channel-commutative copies within one capture                                          |
| Implementation           | Chirped narrowband carrier tracing the dispersion track (Appendix C)                                     |
| Artificial tags          | Transformed repetition, polarization coding, deterministic voltage structure                             |
| Trigger margin           | Comfortably above survey threshold, but below saturation and within classifier training ranges           |
| Dwell time               | Roughly $0.03\,\mathrm{s}$ to a few seconds                                                              |
| Repetition schedule      | Ladder: intra-packet, intra-dwell, paired pass (minutes–hours), sweep period (hours–months)              |

Parameters pinned tightly here are pinned by receiver-side physics; parameters left as ranges are left loose because they depend on transmitter economics that should not be assumed.

### 4.2 Packet architecture

A useful packet could contain:

1. One conventional, high-significance trigger pulse near the temporal center.
2. Several weaker or comparable sub-bursts before and after it.
3. Two copies of an aperiodic temporal pattern.
4. A deterministic relationship between the copies, such as a phase rotation, polarization inversion, spectral remapping, or controlled delay transformation.
5. A signal-domain watermark that is not visible to the trigger but is recoverable from saved voltages.

The trigger component should receive enough fluence to guarantee that the packet is retained. Additional structure should not reduce trigger reliability so much that the signal becomes an out-of-distribution RFI candidate. Fluence should also not be maximal: very high signal-to-noise events can saturate or clip receivers and fall outside the training distribution of classifiers tuned on near-threshold candidates.

With two or more exact copies inside the retained cutout, a single capture carries its own repetition evidence. The receiver's session structure, alert latency, and institutional attention span are removed from the critical path for the artificiality question; revisits then serve only the scanner-model and long-baseline recurrence tests.

### 4.3 Why exact transformed repetition is attractive

Natural FRBs can be multi-component, periodic-looking, narrowband, drifting, scattered, polarized, or morphologically complex. Simple complexity is therefore weak evidence of artificiality.

Exact self-similarity under a simple transformation is more compelling. Let $x_1(t,\nu)$ and $x_2(t,\nu)$ be two dedispersed components. Search for a low-dimensional transformation $T_\theta$ such that

$$
x_2(t,\nu)\approx T_\theta[x_1(t,\nu)].
$$

A high normalized correlation after a simple transformation,

$$
R=\max_\theta
\frac{\langle x_2,T_\theta x_1\rangle}
{\|x_2\|\,\|T_\theta x_1\|},
$$

can indicate a relationship much more exact than ordinary morphological resemblance.

The transformation should be selected to avoid confusion with known propagation effects. A single delayed copy, for example, can resemble gravitational lensing or instrumental reflection. A sequence of copies with deliberate phase, polarization, or code transitions is less easily explained by passive propagation.

The transformation family should also commute with the propagation channel. Time delays and scalar amplitude scalings commute with an arbitrary linear time-invariant channel: a common scattering convolution applies identically to all components, so pairwise similarity survives without deconvolution. Polarization rotations or swaps commute only under restricted channel assumptions—for example, a polarization-independent response or a calibrated Jones/Mueller response known to commute with the tag—and otherwise belong in a calibrated secondary search. Time reversal does not commute with a causal scattering convolution, so reversal tags degrade exactly where scattering is strong and are recoverable only after channel deconvolution. A rational builder should favor transformations that commute with the expected channel, and the archival search should restrict its primary transformation space the same way, which directly reduces the trials factor of Section 10.7 rather than merely calibrating around it.

### 4.4 Positive dispersion as a trigger feature

Most fast-transient systems search positive dispersion because cold plasma delays low frequencies relative to high frequencies. The approximate delay across a band is

$$
\Delta t_{\mathrm{ms}}
\simeq
4.15\,\mathrm{DM}
\left(\nu_{\mathrm{low,GHz}}^{-2}-\nu_{\mathrm{high,GHz}}^{-2}\right).
$$

The beacon should rely on the interstellar medium for most of the apparent dispersion, which favors a transmitter sited in the Galactic plane: essentially every sightline out of the disk accumulates hundreds of $\mathrm{pc\,cm^{-3}}$ of real dispersion at no dwell cost. Synthetic pre-chirp is expensive at low frequency. At $0.4$–$0.8\,\mathrm{GHz}$, even $\mathrm{DM}=100\,\mathrm{pc\,cm^{-3}}$ of synthetic dispersion is a $\sim 2\,\mathrm{s}$ transmission sweep and $\mathrm{DM}=300$ is nearly $6\,\mathrm{s}$, in direct tension with sub-second dwell targets; at $1.2$–$1.5\,\mathrm{GHz}$ the same values cost only a few hundred milliseconds. A modest pre-chirp is therefore affordable only near the top of the band, as a hedge for unusually low-dispersion sightlines. Excessively large synthetic dispersion also risks exceeding ring-buffer or callback windows.

Sightline dispersion is furthermore not tunable per recipient. One signal serves all geometries, and the Galactic-maximum dispersion along the recipient's line of sight varies by orders of magnitude across the receiver population. A fixed pre-chirp that makes the event look extragalactic to a high-latitude recipient does nothing for a recipient in the plane, whose pipeline files the event in a Galactic single-pulse stream. For most recipient geometries the event reads as Galactic regardless of design intent. The robust design accepts this: the delivery channel is RRAT-like phenomenology, detected by the same dedispersion pipelines but archived in a different, less scrutinized stream. This shifts both the camouflage target of the design and the primary region of the archival search. These geometry conclusions apply to the galactic, in-plane builder class; for an extragalactic builder the excess dispersion and host association are genuine rather than apparent, and the phenomenology reverses (Section 16.4).

Negative dispersion or non-$\nu^{-2}$ chirps are potentially strong artificiality markers, but they are poor generic discovery signals because standard transient pipelines may never trigger on them. They are better suited to a secondary tag, a message layer, or a search in continuous raw archives. Critically, when such components trail a triggering packet by less than the retained cutout window, they are preserved by construction in ordinary candidate data products even though nothing can trigger on them; this attached case is a high-priority archival target (Sections 8.4 and 8.8), unlike the standalone case.

### 4.5 Multiple levels of evidence

An ideal packet creates a hierarchy:

1. **Total intensity:** a credible positive-dispersion fast transient.
2. **Dedispersed dynamic spectrum:** repeated or transformed substructure.
3. **Polarization:** a low-complexity code or exact component relationship.
4. **Complex voltage:** deterministic or cyclostationary structure inconsistent with incoherent emission.
5. **Interferometric beam response:** a celestial point source.
6. **Rapid revisit:** a second event from the same direction with the same code family.
7. **Long-term recurrence:** consistency with a scanning beacon schedule.

This hierarchy reduces dependence on any single receiver capability.

One item deserves promotion from confirmation checklist to design driver: simultaneous capture of the same event by two geographically separated wide-field systems on the _first_ visit eliminates the local-interference hypothesis immediately and substitutes for a revisit. It is the only factor in the recipient chain that relaxes revisit-time pressure. Fluence margin and octave-scale band occupancy are the design levers that raise simultaneous multi-receiver capture probability, and they do so without assuming anything about specific survey band edges. Correspondingly, the archival search should cross-match candidate-level archives _between_ observatories for time-coincident events, not only for recurrence.

The weighting of this hierarchy is scale-dependent. At extragalactic distances signal-to-noise margin costs quadratically in distance, so a rational builder transmits nearer threshold: multi-instrument simultaneity weakens as a design driver, and the within-capture self-confirmation rungs at the bottom of the repetition ladder carry correspondingly more of the confirmation burden (Section 16.5). This is a reweighting of the same hierarchy, not a new mechanism.

---

## 5. What should already have been noticed?

The absence of a recognized beacon is not equally informative for every design. Some signals would probably have attracted attention if they had been intercepted and saved at adequate fidelity. Others could plausibly sit in archives because the artificiality-bearing statistic was never examined.

The key phrase is **recorded at a sufficient statistic**.

A low-time-resolution intensity product can preserve dispersion and millisecond pulse timing while erasing phase, nanosecond structure, fine polarization behavior, or deterministic voltage relationships. A transient that did not trigger retention may have existed in a ring buffer for seconds and then vanished permanently.

### 5.1 A Bayesian null model

For design family $d$ and observing system $i$, let $\Lambda_{id}$ be the expected number of arrivals that were physically detectable during the system's actual live, in-band, on-source exposure.

Define

$$
g_{id}=p_{\mathrm{trigger}}p_{\mathrm{save}}p_{\mathrm{tag\ survives}},
$$

and let $o_{id}$ be the probability of durable notice under existing analyses, conditional on adequate archival retention.

The expected number of previous notices is

$$
\mu_{\mathrm{old}}(d)=\sum_i \Lambda_{id}g_{id}o_{id}.
$$

Under a Poisson approximation,

$$
P(\text{no previous notice}\mid d)=e^{-\mu_{\mathrm{old}}(d)}.
$$

This distinguishes two very different cases:

- A design that was almost certainly intercepted, retained, and recognizable is strongly disfavored by the null.
- A design that would have been unmistakable if captured may still be weakly constrained if the probability of capture was tiny.

For random scan phase and actual source exposure $H_{\mathrm{exp}}$, a rough interception expectation is

$$
\Lambda\approx \frac{H_{\mathrm{exp}}}{T_{\mathrm{revisit}}},
$$

provided the exposure is broken into intervals short compared with the revisit period. For transit instruments cadence aliasing is not negligible: the exposure function is a comb nearly periodic at the sidereal day, so scanner-period inference has strong aliases at rational multiples of it, and the approximation above fails when the revisit period is commensurate with the sidereal day. The window-function-aware likelihood of Section 8.9 must be used in those regimes.

Long revisit times make current non-detections weak evidence even for very conspicuous signals.

### 5.2 The archival-recovery expectation

Let $n_{id}$ be the probability that a new analysis would recover and recognize a previously unnoticed archived signal. Then

$$
\mu_{\mathrm{hidden}}(d)
=
\sum_i
\Lambda_{id}g_{id}(1-o_{id})n_{id}.
$$

A useful search-priority score is

$$
\mathcal{S}(d)
\propto
\frac{
\pi_{\mathrm{builder}}(d)
\,e^{-\mu_{\mathrm{old}}(d)}
\left(1-e^{-\mu_{\mathrm{hidden}}(d)}\right)
}{C_{\mathrm{search}}(d)},
$$

where $\pi_{\mathrm{builder}}(d)$ is the prior probability that a rational recipient-maximizing builder would choose the design and $C_{\mathrm{search}}(d)$ is the computational, access, and validation cost of searching for it.

This avoids two mistakes:

- treating every non-detection as equally informative;
- or prioritizing signals that no existing archive could possibly contain.

### 5.3 Four regions of the design space

| Archive probability | Previous-recognition probability | Interpretation                                           |
| ------------------- | -------------------------------: | -------------------------------------------------------- |
| High                |                             High | Constrained; perform a cheap completeness audit          |
| High                |                              Low | **Primary archival-search region**                       |
| Low                 |                             High | Better target for future live monitors than old archives |
| Low                 |                              Low | Lowest archival priority                                 |

The central opportunity is the second row: signals likely to have been saved but unlikely to have been tested for the relevant artificiality statistic.

---

## 6. Signal classes and their likely status

### 6.1 More likely to have been noticed, conditional on capture

The following families deserve some posterior downweighting when exposure and retention were substantial:

#### Overt mathematical patterns in ordinary dynamic spectra

A bright event containing many clearly resolved, exactly periodic pulses or an obvious repeated countable sequence would be visually striking. It could still be labeled unusual astrophysics or RFI rather than artificial, but its chance of attracting attention is relatively high.

#### Metronomic repetition within a single capture or observing session

A source firing many times at visibly regular intervals within one observation would produce a striking burst train and has a relatively high notice probability, conditional on capture.

Cataloged repetition from a fixed position and dispersion, by contrast, belongs in the primary search region rather than here. Recognition _as a repeater_ is exactly where notice stops: the source receives a name and a burst-statistics paper, and its arrival times are never tested against exposure-folded scanner models. Known repeaters are therefore treated in Section 6.2.

#### Simple delayed coherent copies

A single exact delayed copy in voltage data overlaps with searches for gravitational lensing and propagation echoes. Such searches do not exhaust all artificial-code possibilities, but they reduce the novelty of a plain two-copy autocorrelation signature.

#### Persistent narrowband drifting signals in heavily searched SETI data

Conventional radio SETI has concentrated heavily on narrowband, Doppler-drifting, persistent or scan-repeating signals. The searched parameter space remains incomplete, candidate triage is severe, and short bursts can be missed, but this family has a higher prior notice probability than many alternatives.

### 6.2 Plausibly sitting in archives

The strongest archival targets include:

#### Ordinary-looking FRBs with artificiality in a nonstandard relation

Examples include:

- exact normalized similarity between separated components;
- repeated aperiodic timing patterns;
- cross-component spectral transformations;
- a common codebook across separate events;
- anomalously low description length after dedispersion;
- polarization-state transitions with exact algebraic relations;
- cyclostationarity or deterministic electric-field statistics.

A human reviewer can classify such an event as “complex FRB” without ever calculating the relevant invariant.

#### Known repeaters untested against scanner models

Dozens of cataloged repeating sources have public burst times and published exposure functions. Activity-window periodicity has been searched; strict scanner-model periodicity folded through the exposure window, and paired-pass structure (a short lag followed by a much longer sweep period), generally have not. This is the cheapest high-value test in the entire plan and requires only published data. By the quadrant logic of Section 5.3, the known-repeater sample sits squarely in the high-archive, low-recognition row.

#### Galactic single pulses and RRATs with copy-exact morphology

The natural population in the Galactic-dispersion stream—pulsar single pulses and rotating radio transients—is intrinsically stochastic: individual pulses vary strongly in shape and only the long-term average profile is stable. A source emitting morphologically identical pulses, copy-exact at high time resolution, has no counterpart in Galactic single-pulse phenomenology, making exact copy invariance _more_ discriminating in this stream than in the FRB catalog. The relevant statistics are pulse-to-pulse correlation far above the pulsar population distribution, exact internal copy structure within saved cutouts, and RRAT timing residuals tested against scanner models rather than rotational ephemerides. The RRAT catalog is smaller, historically weirdness-tolerant, and far less scrutinized for these statistics than the FRB sample. Given the geometry argument of Section 4.4, this stream is where a galactic-builder beacon lands for most recipient geometries, and it should be the primary archival region for that builder class; the extragalactic builder class points instead back at the genuine-FRB repeater catalog (Section 16.4).

#### Candidate graveyards

High-value populations may include:

- events rejected for insufficient excess dispersion;
- Galactic single pulses;
- RRAT or pulsar-associated events;
- candidates labeled RFI despite a plausible celestial beam pattern;
- machine-learning rejects;
- low-significance callbacks;
- reviewer-disagreement cases;
- events omitted from polished catalogs;
- duplicate or grouping failures;
- and events that triggered intensity retention but not baseband retention.

A Galactic beacon is especially likely to be lost in a Galactic-source or low-excess-dispersion stream rather than in a published extragalactic FRB catalog.

#### Baseband events with transformed rather than simple repetition

Voltage archives may preserve decisive evidence that ordinary intensity products erase. The search should move beyond a simple echo and test for repeated blocks under controlled phase, polarization, frequency, or code transformations.

#### Short isolated events in SETI archives

Some SETI analyses use time-frequency products or persistence criteria that are poorly matched to $1$–$100\,\mathrm{ms}$ one-off signals. A transient can be present in the underlying high-resolution data yet absent by construction from the candidate products normally examined.

#### Off-manifold dispersion in continuous archives

Negative-dispersion or other unconventional chirps are excellent archival targets only when continuous filterbank or voltage data were retained. They are poor targets in systems that save data only after a standard positive-dispersion trigger.

---

## 7. Core archival-search hypothesis

The initial search should avoid overcommitting to one culturally specific code, such as primes or Fibonacci intervals. The broader target is a **self-similar dispersed transient**:

> A positive-dispersion, celestial, short-duration radio event that lies inside ordinary transient-selection boundaries but contains statistically improbable exact relationships among components, polarizations, frequencies, voltages, or repeated visits.

The event may sit in any retention stream—extragalactic FRB catalog, Galactic single-pulse stream, RRAT catalog, or reject pile—with the Galactic-dispersion streams weighted highest for the galactic builder class for the geometric reasons of Section 4.4, and the primary transformation space restricted to channel-commutative families for the reasons of Section 4.3. The stream mapping follows the builder's siting (Section 16.4): a galactic, in-plane builder lands in the Galactic single-pulse and RRAT streams for most recipient geometries, while an extragalactic (Local Volume) builder lands in the genuine-FRB repeater catalog, localized to a visible host. Identical tag statistics search both streams; only the retention stream and the host association differ.

The search should be model-guided but not template-fragile. It should test broad invariants that a recipient-maximizing builder could reasonably expect unfamiliar receivers to discover.

---

## 8. Archival search plan

### 8.1 Scientific objectives

The search has four primary objectives:

1. Identify archived events with common-dispersion multi-component structure.
2. Test whether any components are related by low-dimensional exact transformations.
3. Search for recurrence of the same structure or code family across events.
4. Quantify selection effects well enough to convert a null result into constraints on design families.

A fifth objective is methodological: build a reusable injection-and-recovery framework that can compare candidate beacon designs across realistic transient pipelines.

### 8.2 Data-source priority

The recommended order is:

1. **Known-repeater burst times and exposure functions** (public), for exposure-folded scanner-model and paired-pass tests.
2. **Galactic single-pulse, pulsar, and RRAT streams**, including copy-exactness statistics and scanner-model timing tests.
3. **Candidate-level fast-transient archives**, including rejects and reviewer-disagreement cases.
4. **Public total-intensity FRB dynamic spectra**, including the full time extent of every saved cutout.
5. **Cross-observatory event and candidate databases**, for same-event simultaneity as well as recurrence.
6. **Public or collaborative baseband and polarization samples**.
7. **High-time-resolution SETI filterbank and voltage archives**.
8. **Continuous raw archives suitable for standalone off-manifold dispersion searches**.

This order favors data products with both high retention probability and unexploited artificiality information, and it front-loads the tests that require only published data.

Under the extragalactic hypothesis (Section 16), the genuine-FRB repeater catalog is co-primary with the RRAT and Galactic single-pulse streams rather than subordinate to them. Within the repeater sample, an explicit sub-priority applies: repeaters localized to Local Volume hosts, ordered by host distance, nearest first.

### 8.3 Stage 0: archive and selection-function inventory

Before searching, construct a data-product matrix for each instrument:

| Field              | Required information                                      |
| ------------------ | --------------------------------------------------------- |
| Frequency coverage | Center frequency, bandwidth, channelization               |
| Time resolution    | Native and archived resolutions                           |
| Polarization       | Total intensity, Stokes products, complex voltages        |
| Sky exposure       | Source-dependent exposure, not calendar duration          |
| Trigger space      | Dispersion, width, significance, and classifier limits    |
| Retention policy   | Dynamic spectra, baseband, ring-buffer duration           |
| RFI processing     | Masking, zero-DM subtraction, kurtosis cuts, vetoes       |
| Candidate products | Accepted, rejected, low-DM, pulsar, RRAT, RFI streams     |
| Metadata           | Beam response, localization, observing state, calibration |
| Access constraints | Public, proprietary, or collaborative                     |

The inventory should explicitly identify which artificiality statistics survive each product.

### 8.4 Stage 1: positive-dispersion candidate-level search

This is the highest-priority stage.

For every candidate, including rejects:

1. Re-estimate dispersion over a fine local grid.
2. Dedisperse and form a standardized time-frequency cutout.
3. Detect and segment individual components over several time resolutions.
4. Fit shared and component-specific propagation parameters.
5. Measure pairwise temporal, spectral, and joint time-frequency similarity.
6. Search for repeated aperiodic timing motifs.
7. Search for low-dimensional transformations linking components.
8. Compare the signal's beam pattern with celestial and local-interference hypotheses.
9. Search the full time extent of every saved cutout for structured components outside the dedispersed-pulse window, including inverted or non-standard sweeps that could not have triggered but were retained by construction.
10. Rank events using calibrated null distributions and injection tests.

The search should preserve known-source associations rather than automatically veto them. A beacon direction can overlap a pulsar, supernova remnant, Galactic-plane source, or cataloged transient by chance or by deliberate targeting.

### 8.5 Stage 2: public total-intensity FRB search

Public dynamic spectra offer large event counts but limited information.

Recommended statistics include:

#### Component cross-correlation

After dedispersion and local normalization, compute maximum correlation over relative delay, amplitude scale, frequency-dependent gain, and modest spectral warps.

#### Repeated timing grammar

Represent a burst as component times $\{t_k\}$, widths $\{w_k\}$, fluences $\{F_k\}$, and spectral centroids $\{\nu_k\}$. Search for repeated subsequences under scaling or translation.

#### Minimum-description-length anomaly

Compare the number of bits needed to describe the event under a flexible natural-transient model with the number needed under a compact generative relation. A useful statistic is

$$
\Delta L = L_{\mathrm{natural}}-L_{\mathrm{structured}}.
$$

Large positive $\Delta L$ indicates that a simple relational model compresses the event unusually well.

#### Cross-event codebook search

Cluster component relations rather than only raw morphologies. Two events may have different scattering, gain, or observing bands while sharing the same abstract transformation sequence.

#### Periodicity without periodic-wave assumptions

Search for repeated packets and motifs without requiring a continuously periodic source. A scanning beacon may generate isolated events with long gaps.

### 8.6 Stage 3: baseband and polarization search

Baseband data permit the strongest tests.

Recommended analyses include:

- coherent re-dedispersion;
- complex-voltage autocorrelation and cross-correlation;
- cyclic spectral analysis;
- higher-order spectral statistics;
- repeated pseudonoise-block searches;
- exact phase-transition tests between components;
- Jones-matrix or Mueller-matrix relations between polarization states;
- deterministic modulation searches under unknown channel response;
- coherent phase-residual structure searches across bursts;
- and comparison of repeated blocks after adaptive channel equalization.

The interstellar and instrumental channel is often approximately constant over a packet lasting tens of milliseconds. This allows two components to be compared after estimating a common channel transfer function.

The phase-residual structure search deserves emphasis as an upgrade of the cold-plasma transfer-function test of Appendix C. That test asks whether the emitted field replicates the exact $\nu^{-2}$ phase law; the upgraded search goes further: after coherent dedispersion, search the residual carrier phase for repeated modulation patterns, non-random phase trajectories, and low-description-length structure across bursts. Under the collapsed architecture of Section 16.6, the entire message layer of an extragalactic beacon lives in exactly this statistic—in baseband archives that were recorded for scattering and emission-physics studies and have never been examined for deliberate phase structure.

A robust test should distinguish:

- incoherent astrophysical emission;
- passive multipath propagation;
- gravitationally lensed copies;
- instrumental reflections;
- terrestrial communication signals;
- and deliberately transformed repetition.

### 8.7 Stage 4: high-time-resolution SETI archive search

Search underlying filterbank or voltage products for isolated $1$–$100\,\mathrm{ms}$ events without requiring persistence across several multi-minute ON scans.

The search should cover:

- narrowband bursts;
- intermediate-band bursts;
- broadband positive-dispersion events;
- short chirps;
- frequency-hopping packets;
- and tagged packet structures.

Candidate ranking should not automatically penalize one-off behavior. A scanning beacon is expected to be intermittent from the observer's perspective.

### 8.8 Stage 5: off-manifold and trigger-failing signals

Two retention regimes must be distinguished. Off-manifold components _attached_ to a triggering packet—trailing the trigger by less than the retained cutout window—are preserved by construction in ordinary candidate products and are searched in Stage 1 via the full-cutout-extent step; they are high priority. This stage concerns _standalone_ off-manifold signals, for which only continuous archives can support a meaningful search. Candidate families include:

- negative dispersion;
- non-$\nu^{-2}$ dispersion laws;
- very narrow or very broad widths outside ordinary searches;
- simultaneous frequency blocks rather than smooth sweeps;
- sparse coded pulses;
- or events intentionally placed near known RFI masks.

These are scientifically interesting but lower-priority archival targets because retention probability is often poor.

### 8.9 Stage 6: recurrence and scan-cadence search

For every promising candidate, search for related events by:

- sky position;
- dispersion measure;
- packet morphology;
- transformation code;
- polarization relation;
- and possible revisit period.

A scanning beacon may revisit on a period $T$ but be observed only during irregular exposure windows. Use a window-function-aware likelihood rather than a simple periodicity test.

For event times $t_k$ and exposure function $W(t)$, compare models such as:

- a homogeneous Poisson transient source;
- an activity-window repeater;
- a periodic scanner with phase uncertainty;
- a paired-pass scanner with a short confirmation delay plus long recurrence;
- and a clustered natural repeater.

The paired-pass model is especially important. Search for a short lag $\tau_c$ between two events, followed by a much longer sweep period $T_s$.

---

## 9. Candidate scoring and evidence hierarchy

A single anomaly score is unlikely to be sufficient. Use a hierarchical evidence system.

### Level 0: pipeline-valid transient

- positive dispersion;
- acceptable width and signal-to-noise;
- plausible celestial beam pattern;
- no obvious local broadband coincidence.

### Level 1: morphological anomaly

- repeated components;
- unusually exact timing relations;
- strong transformed cross-correlation;
- repeated spectral envelopes;
- low description length.

### Level 2: signal-domain anomaly

- cyclostationarity;
- deterministic voltage repetition;
- exact phase or polarization transformations;
- code consistency across frequency subbands.

### Level 3: astrophysical-veto survival

- inconsistent with scintillation alone;
- inconsistent with scattering echoes;
- inconsistent with lensing under a passive-copy model;
- inconsistent with instrumental reflection;
- inconsistent with known pulsar emission or ordinary repeating-FRB behavior.

### Level 4: recurrence or independent confirmation

- same sky direction and dispersion;
- same relational code;
- rapid paired revisit;
- independent observatory detection;
- or recurrence compatible with a scanner model.

### Level 5: actionable technosignature candidate

- multiple independent artificiality indicators;
- robust localization;
- preserved raw data;
- reproducible analysis;
- and a follow-up plan capable of testing the hypothesis.

---

## 10. False positives and controls

A credible search must be designed around the strongest natural and instrumental alternatives.

### 10.1 Natural multi-component FRBs

Natural bursts can have complex morphology. Control by comparing against a large population matched in signal-to-noise, width, dispersion, scattering, and spectral occupancy.

### 10.2 Scintillation and plasma lensing

Propagation can create repeated or frequency-dependent structures. Use subband consistency, phase information, polarization behavior, and transformation complexity to distinguish passive propagation from deliberate coding.

### 10.3 Gravitational lensing

A lensed event can create highly similar delayed copies. A plain two-copy autocorrelation peak is therefore insufficient. Seek sequences of controlled transformations or code changes incompatible with passive copies.

### 10.4 Instrumental echoes and buffer artifacts

Instrumental reflections may create fixed delays across many events or beams. Search for the same delay in calibration sources, RFI events, and unrelated candidates. Require celestial localization and instrument-independent recurrence where possible.

### 10.5 Terrestrial radio-frequency interference

RFI can be structured and deterministic. Use:

- multi-beam localization;
- near-field versus far-field tests;
- coincidence across geographically separated observatories;
- dispersion-law accuracy;
- Doppler behavior;
- polarization consistency;
- and observatory housekeeping metadata.

Artificiality alone does not imply extraterrestrial origin.

### 10.6 Pulsars and rotating radio transients

Known-source association should be informative but not automatically disqualifying. Compare candidate timing with the source ephemeris, pulse phase, dispersion stability, and ordinary emission statistics.

### 10.7 Trials factors

A broad transformation search can find accidental high correlations. Calibrate significance with:

- time-scrambled controls;
- frequency-scrambled controls;
- off-source beams;
- injected natural-transient simulations;
- instrument-specific noise realizations;
- and held-out validation sets.

Report both local and global false-alarm probabilities.

---

## 11. Injection and recovery

A search cannot interpret a null without measuring sensitivity.

Build a synthetic signal library spanning:

- center frequency and bandwidth;
- dispersion measure and chirp law;
- pulse width and packet duration;
- number of components;
- relative timing and fluence;
- scattering and scintillation;
- spectral patchiness;
- polarization states;
- phase or code transformations;
- revisit patterns;
- and signal-to-noise ratio.

Inject these signals at several levels:

1. raw voltages, when possible;
2. channelized time-frequency data;
3. candidate cutouts;
4. and catalog-level features.

For each design $d$, estimate

$$
p_{\mathrm{trigger}}(d),\quad
p_{\mathrm{save}}(d),\quad
p_{\mathrm{recover}}(d),\quad
p_{\mathrm{rank}}(d),
$$

as functions of instrument and observing conditions.

The optimization target should be callback-and-recognition probability, not merely matched-filter signal-to-noise:

$$
d^*=\arg\max_d
\sum_i w_i
P_i(\mathrm{trigger}\cap\mathrm{save}\cap\mathrm{recognize}\cap\mathrm{confirm}\mid d).
$$

The weights $w_i$ represent the assumed population of receiver architectures.

---

## 12. Practical implementation phases

### Phase A: public-data pilot

Use public FRB dynamic spectra and public baseband samples to build the analysis framework.

Deliverables:

- standardized data model;
- component segmentation pipeline;
- transformed-correlation search restricted first to channel-commutative families;
- minimum-description-length score;
- exposure-folded scanner-model and paired-pass tests on the public known-repeater sample;
- full-time-extent search of public cutouts for non-triggering structure;
- pulse-to-pulse copy-exactness statistics calibrated on pulsar single-pulse populations;
- phase-residual structure search on nearby-galaxy repeaters with archived baseband, first target the M81 globular-cluster repeater FRB 20200120E (Section 16.4)—a null result is independently publishable as a constraint on burst emission physics;
- null calibration on natural events;
- and an initial ranked candidate list.

### Phase B: candidate-graveyard collaboration

Seek access to rejected, low-dispersion, pulsar-associated, and RFI-classified transient candidates.

Deliverables:

- selection-function reconstruction;
- search of non-cataloged candidates;
- candidate-veto audit;
- and estimates of hidden-event yield.

### Phase C: baseband technosignature analysis

Apply voltage- and polarization-domain searches to the highest-value events.

Deliverables:

- coherent reprocessing;
- cyclic-spectrum and repeated-block analyses;
- propagation and lensing vetoes;
- and a short list of events warranting independent review.

### Phase D: high-resolution SETI archive search

Search short-duration signals in underlying SETI data without persistence requirements.

Deliverables:

- burst-sensitive reprocessing;
- comparison with conventional narrowband results;
- and sensitivity curves for one-off scanning beacons.

### Phase E: live commensal trigger

Translate the archival statistics into a low-risk secondary live trigger that does not interfere with ordinary transient operations.

A suitable live system would:

- operate on saved candidates rather than raw full-rate data initially;
- flag transformed self-similarity;
- request extended buffer retention;
- advocate widened saved-cutout windows (several seconds around each trigger) in operating pipelines—a low-cost policy change that preserves attached off-manifold components going forward;
- preserve polarization and voltage data when possible;
- and initiate rapid follow-up for high-ranking events.

---

## 13. Search priorities under uncertainty

The project should not rank candidates only by apparent strangeness. It should combine:

- rational-builder prior;
- physical interception probability;
- trigger and archive probability;
- previous-notice probability;
- new-search recovery probability;
- false-positive burden;
- and search cost.

A practical ranking approximation is

$$
\mathrm{Priority}(d)
=
\frac{
\pi_{\mathrm{builder}}(d)
P_{\mathrm{captured}}(d)
P_{\mathrm{archived}}(d)
\left[1-P_{\mathrm{noticed\ already}}(d)\right]
P_{\mathrm{new\ recovery}}(d)
}{C_{\mathrm{search}}(d)}.
$$

This naturally favors the Goldilocks region:

- normal enough to trigger;
- unusual enough to contain a recoverable signature;
- preserved in common data products;
- but not already covered by adjacent astrophysical analyses.

---

## 14. Interpretation of a null result

A null search can constrain only the combination of beacon prevalence, scan cadence, signal design, exposure, and pipeline survival.

For a family $d$, a simple upper-limit model is

$$
P(0\mid \eta_d)=\exp[-\eta_d\,\mathcal{E}_d],
$$

where $\eta_d$ is an occurrence or illumination-rate parameter and $\mathcal{E}_d$ is an effective exposure incorporating physical sensitivity and pipeline efficiency.

The effective exposure should include

$$
\mathcal{E}_d
=
\sum_i
H_{i,\mathrm{sky}}
\,p_{i,\mathrm{band}}
\,p_{i,\mathrm{detect}}
\,p_{i,\mathrm{trigger}}
\,p_{i,\mathrm{save}}
\,p_{i,\mathrm{recover}}.
$$

A null result in published FRB catalogs does not constrain designs that would fall below catalog dispersion cuts, be rejected as Galactic, or require baseband information. A null result in a small baseband sample does not strongly constrain rare, long-revisit beacons. Every reported limit should therefore state exactly which design family and data product it applies to.

---

## 15. Implications for beacon builders

The archival analysis feeds back into the beacon-design problem.

A recipient-maximizing builder should probably use a **two-resolution tag**:

1. A modest intensity-domain breadcrumb that survives common millisecond dynamic-spectrum products.
2. A decisive phase or polarization code in higher-fidelity data.

The discovery packet should not place all evidence of artificiality in a data layer that only a small fraction of receivers retain. Conversely, it should not be so overtly coded at trigger resolution that conservative RFI systems reject it.

The builder should site the transmitter in the Galactic plane to obtain interstellar dispersion at no dwell cost, implement the packet as a chirped carrier for peak-power economy (Appendix C), and distribute exact repetition across a geometric ladder of timescales rather than concentrating it at one revisit period. Within-capture copies make single events self-confirming; the paired pass and sweep recurrence then carry the scanner-model evidence.

The builder should also consider a paired revisit schedule, whether via a trailing beam or a doubled-back scan pattern. A second visit during the active alert window may contribute more to confirmed recipients than a modest increase in fresh-sky scan rate.

The message layer can be more flexible. Once the discovery event has triggered attention and follow-up, a higher-gain receiver can search the same direction for a lower-power, longer-duration, broader-information signal. The discovery layer's job is not to carry a large message. Its job is to cause the receiving civilization to point, preserve, compare, and return.

This separate message layer is affordable only where margin is cheap. At intergalactic scale the energy accounting of Section 16.6 makes a per-target continuous message beam unaffordable, and the two layers collapse into one phase-modulated signal; the dedicated follow-on message channel described here becomes the home-galaxy premium tier.

---

## 16. The intergalactic extension

The analysis so far has treated the Galaxy as the target population, with range saturation at the Galactic scale as the point where capital pivots to cadence and coverage. Extending the recipient-maximizing objective beyond the Galaxy produces a result that at first looks like an error: for a beam pointed at another galaxy, distance cancels out of the per-recipient energy cost. This section develops that cancellation, its validity horizon, the capital-threshold structure it implies, and its consequences for phenomenology, confirmation, and message architecture. Throughout, the rev2 convention holds: physics-pinned quantities are stated tightly, economics-dependent quantities as order-of-magnitude scalings or thresholds.

### 16.1 The distance cancellation and the beam-filling horizon

Per-recipient energy cost is distance-invariant while the beam footprint is filled with target stars. For beam solid angle $\Omega$ at distance $d$, the footprint area is $\Omega d^2$, so the stars covered per pointing are

$$
N \approx \Sigma\,\Omega d^2,
$$

where $\Sigma$ is the target's stellar column density, while the required effective isotropic radiated power scales as $4\pi d^2 S_{\min}$. The cost per star delivered is therefore

$$
\frac{4\pi S_{\min}}{\Sigma\,\Omega},
$$

and **distance drops out**. A beam on a face-on external galaxy is in fact _better_ filled than a beam sweeping the Milky Way plane: there is no empty sightline and no over-served nearby star.

The cancellation has a validity horizon: it holds only while the footprint is smaller than the target galaxy. At gain $10^8$ the footprint reaches $\sim 30\,\mathrm{kpc}$—a full galaxy—near $\sim 80\,\mathrm{Mpc}$. Beyond this gain-dependent **beam-filling horizon**, every additional megaparsec is pure $d^2$ loss and per-recipient cost diverges. The rational program covers the Local Volume out to tens of megaparsecs and stops. Higher gain extends the horizon, but multiplies pointing count and aiming-precision requirements.

### 16.2 The capital threshold

The cancellation does not make intergalactic transmission cheap; it redistributes cost from many cheap pointings to few enormous ones. Per-pointing peak effective isotropic radiated power scales as $d^2$: a pointing at M31 ($780\,\mathrm{kpc}$) needs $\sim 6\times10^3$ times the power of a $10\,\mathrm{kpc}$ galactic pointing—of order $10^{28}\,\mathrm{W}$ peak as a true impulse—and Virgo-distance targets need $\sim 10^6$ times the galactic figure. The chirp implementation retains its $B/\Delta\nu \sim 10^3$–$10^5$ peak-power reduction (Appendix C), bringing the transmitter power to tens of petawatts at plausible gains for M31. Intergalactic capability is therefore an **entry barrier that grows as $d^2$, not a per-recipient rate cost**: below the threshold there are zero extragalactic recipients; above it, per-recipient economics are flat out to the beam-filling horizon.

Coverage economics above threshold are favorable. All Local Volume galaxies together subtend a tiny total solid angle, so a single beam with $\sim 0.1\,\mathrm{s}$ dwells revisits every pointing on $\sim 10^3$ galaxy targets in hours to days—comparable to or better than a Milky Way plane sweep. The total addressable audience grows three to four orders of magnitude within $\sim 20\,\mathrm{Mpc}$.

### 16.3 Capital allocation across scales

Two allocation results follow.

First, the pivot point for incremental builders: beam and cadence additions hit diminishing returns once revisit time drops below typical receiver session or transit timescales; after that, marginal capital goes to clearing the next distance threshold. This generalizes the allocation principle of Section 1.1 to **range, then cadence, then more range at the next scale**.

Second, straight-to-intergalactic builders still sweep the home galaxy. A facility that puts threshold fluence on M31 overshoots a $10\,\mathrm{kpc}$ pointing by $\sim 37\,\mathrm{dB}$; with distance-invariant per-star cost, rational energy allocation is proportional to audience, and the home galaxy ($\sim 10^{11}$ stars) is roughly one percent of the Local Volume audience. The home sweep therefore costs about one percent of the energy budget and a small slice of the schedule, while serving the only audience with light-travel times shorter by of order a megayear. Nobody skips it. The home galaxy becomes the **premium tier**: served at enormous free signal-to-noise margin, it can carry a full dedicated message layer locally even when the extragalactic program cannot (Section 16.6).

### 16.4 Phenomenology reversal: the two-builder structure

An intergalactic beacon does not _mimic_ a fast radio burst—it observationally **is** one: genuine excess dispersion (the real intergalactic medium contributes $\sim 0.2\,\mathrm{pc\,cm^{-3}}$ per megaparsec locally, plus real host contributions at both ends) and genuine localization to a visible host galaxy. The hostless-repeater anomaly of the galactic analysis vanishes, and artificiality must be carried entirely by the tags. The tags carry over unchanged: the repetition ladder, the channel-commutative transformation restriction, the chirp implementation, and octave-band occupancy all apply verbatim to the extragalactic case and need no re-derivation—the copies remain channel-commutative and exact, and the periodicity remains strict under exposure folding.

This produces a two-builder structure:

| Builder class                   | Delivery stream                       | Distinguishing anomaly                                                                  |
| ------------------------------- | ------------------------------------- | --------------------------------------------------------------------------------------- |
| Galactic (in-plane transmitter) | Galactic single-pulse / RRAT catalogs | Copy-exact morphology in a stochastic population; hostless if misfiled as extragalactic |
| Extragalactic (Local Volume)    | Genuine FRB repeater catalog, with host | Tags only: exact copies, strict periodicity, phase structure                            |

The corresponding search prior is spatial: extragalactic beacons are **coincident with nearby massive galaxies**. Sort the repeater sample by host distance, nearest first. The first target is the M81 globular-cluster repeater FRB 20200120E at $3.6\,\mathrm{Mpc}$—the nearest extragalactic repeater, environmentally anomalous, with baseband captures held by multiple observatories. This is a priority test target under a stated hypothesis, not a candidate claim: magnetar-in-old-population models for the source remain viable.

### 16.5 Margin erosion and confirmation reweighting

At extragalactic distances, signal-to-noise margin costs quadratically in distance, so the builder transmits nearer threshold. Multi-instrument simultaneity—a design driver in the galactic case (Section 4.5)—weakens accordingly, and within-capture self-confirmation, the repetition ladder's bottom rungs, carries more of the confirmation burden. This is a scale-dependent reweighting of the existing confirmation hierarchy, not a new mechanism.

### 16.6 The collapsed discovery/message architecture

Energy accounting kills the galactic-style two-layer design at intergalactic scale. The pulsed discovery layer runs at a duty cycle of order $10^{-6}$ per target; even a continuous message beam $30\,\mathrm{dB}$ weaker per target costs $\sim 10^3$ times the discovery layer's energy ($10^{-3}$ versus $10^{-6}$ in power times duty). Continuous message beams are what blows up—not the bursts.

The dominant option is to **collapse both layers into one physical signal with layered decodability**:

- The chirp implementation already sweeps a coherent carrier for $\sim 1\,\mathrm{s}$ per burst. **Phase-modulating that carrier is invisible in intensity data**—filterbanks discard phase—so triggering, morphology, and pipeline passage are unaffected; but it is a full data channel in voltage data. The capacity $B\,T\log_2(1+\mathrm{SNR})$ on the instantaneous bandwidth over the sweep duration gives $\sim 10^4$–$10^6$ bits per burst at **zero additional energy**.
- The phase modulation double-duties as the strongest artificiality tag in the design: deterministic, repeated, structured phase across bursts is unforgeable by plasma.
- A receiver-behavior invariant justifies relying on voltage capture, with the same epistemic status as the dedispersion-trigger argument of Section 4.4: any civilization that finds a repeating burst source commits voltage-capture campaigns to it, because coherent data is how burst microphysics is done. **Repeaters attract baseband recording.**
- The layers stratify within the same bursts: (i) intensity-domain burst parameters—sub-burst spacings, amplitude patterns, polarization angles—carry tens of bits per event, readable by any wide-field system: the bootstrap layer ("artificial, periodic, look closer"); (ii) phase-domain modulation is the message proper, kilobits to megabits per burst for voltage recorders; (iii) fountain-style coding across bursts lets any sufficient subset decode, robust to each recipient's sparse exposure sampling.
- Dedicated high-power message beams are reserved for the home galaxy, where margin is free (Section 16.3).

The lighthouse and the library are the same photons.

---

## 17. Main conclusions

1. The relevant optimization target is expected confirmed recipients, not raw detectability or transmitted information rate.
2. Wide-field radio transient monitors are the dominant plausible receiver class for brief scanning beacons.
3. The strongest discovery-layer candidate is a tagged dispersed packet in the physics-anchored $0.5$–$2\,\mathrm{GHz}$ window, occupying an octave or more of bandwidth, with dispersion dominated by the real interstellar medium, millisecond components, and two or more exact channel-commutative copies within tens of milliseconds.
4. The main trigger should look ordinary. Artificiality should be carried by exact transformed relationships that survive archiving but are not standard pipeline features, restricted to transformations that commute with the propagation channel.
5. For the galactic (in-plane) builder class, sightline geometry makes the event read as Galactic for most recipient geometries regardless of design intent, so RRAT-like phenomenology is the delivery channel and the Galactic single-pulse streams are the primary search region for that class; the extragalactic class points instead at the genuine-FRB repeater catalog (conclusion 13).
6. Repetition should be distributed across a ladder of timescales. Within-capture copies make a single retained event self-confirming, removing receiver session structure and attention span from the critical path; paired passes and sweep recurrence carry the scanner-model evidence. Long revisit times make current non-detections weak evidence.
7. Signals that would have been spectacular in standard intensity products deserve some downweighting, but only after actual exposure, trigger, and retention probabilities are included; recognition as a repeater does not count as recognition of artificiality.
8. The best archival-search region consists of signals likely to have been retained but unlikely to have been tested for their artificiality-bearing statistic.
9. Known-repeater timing records, Galactic single-pulse and RRAT streams, candidate-level archives including rejects, the full time extent of saved cutouts, and baseband samples are more valuable than polished FRB catalogs alone.
10. A broad search for self-similar dispersed transients is preferable to a narrow search for one human-chosen mathematical sequence, with channel-commutative transformation families searched first.
11. Transmitter cost should shape the rational-builder prior: the chirp implementation reduces peak power by orders of magnitude relative to a true impulse and supplies a voltage-domain tag for free, so chirp-implemented designs deserve higher weight.
12. Injection and recovery are essential. Without them, neither candidate ranking nor null-result interpretation is reliable.
13. Per-recipient energy cost is distance-invariant out to a gain-dependent beam-filling horizon at tens of megaparsecs, while the per-pointing capital threshold grows as $d^2$: intergalactic capability is an entry barrier, not a rate cost, and a builder above threshold covers the Local Volume at flat per-recipient economics while still sweeping the home galaxy as a premium tier.
14. The two builder classes map onto different retention streams—galactic builders onto Galactic single-pulse and RRAT streams, extragalactic builders onto the genuine-FRB repeater catalog with visible hosts—and identical tag statistics search both. The nearest-host repeaters, beginning with the M81 globular-cluster repeater, are the priority test targets under the extragalactic hypothesis.
15. At intergalactic scale the discovery and message layers collapse into one phase-modulated chirped signal: the message rides in carrier phase at zero additional energy, invisible to intensity pipelines but recoverable from baseband. The corresponding archival test is a phase-residual structure search in voltage archives recorded for scattering studies.

The practical search thesis is therefore:

> **Look for a celestial positive-dispersion burst—filed as an FRB, a Galactic single pulse, an RRAT, or a reject—that an ordinary transient pipeline was happy to save, but whose components, polarizations, voltages, or visit times obey an exact relation that ordinary astrophysics had no reason to test.**

---

## Appendix A: minimal event record

For reproducibility, each searched event should have a machine-readable record containing:

- observatory and instrument;
- observation identifier;
- UTC time and barycentric time where available;
- sky position and localization uncertainty;
- beam identifiers and beam-response information;
- frequency range and channel width;
- time resolution;
- dispersion measure and uncertainty;
- width, scattering, fluence, and signal-to-noise estimates;
- polarization availability;
- baseband availability;
- trigger and classifier outputs;
- catalog or rejection status;
- known-source associations;
- RFI masks and observatory-state metadata;
- all anomaly scores;
- software version and configuration;
- and provenance for every transformed data product.

## Appendix B: recommended first-pass algorithms

A computationally tractable first pass can use:

1. Fine-grid rededispersion.
2. Multi-scale one-dimensional component detection.
3. Dynamic-spectrum component extraction.
4. Pairwise normalized correlation under delay, gain, and smooth spectral warp.
5. Autocorrelation of component intervals and feature sequences.
6. Repeated-subsequence detection in symbolic component representations.
7. Compression or minimum-description-length scoring.
8. Beam-pattern celestial-likelihood scoring.
9. Cross-event nearest-neighbor search in relational-feature space.
10. Human review only after calibrated automated ranking.

## Appendix C: transmitter cost sketch

The rational-builder prior $\pi_{\mathrm{builder}}(d)$ should be weighted by transmitter cost, which the following scalings summarize.

For a receiver threshold flux density $S_{\min}$ (of order $1\,\mathrm{Jy}$ for a millisecond pulse in a compact wide-field array), the required effective isotropic radiated spectral density at range $d$ is

$$
\mathcal{S}
= S_{\min}\,4\pi d^2
\approx 1.2\times10^{16}\ \mathrm{W\,Hz^{-1}}
\left(\frac{S_{\min}}{1\,\mathrm{Jy}}\right)
\left(\frac{d}{10\,\mathrm{kpc}}\right)^{2}.
$$

A true broadband impulse must supply this density across the full occupied band $B$ simultaneously, giving a peak effective isotropic radiated power of order $\mathcal{S}B \sim 5\times10^{24}\,\mathrm{W}$ for $B = 400\,\mathrm{MHz}$.

A chirped narrowband carrier swept along the dispersion track deposits the same per-channel fluence sequentially. In any channelized intensity product the two are indistinguishable, but the total radiated energy is unchanged while the peak power falls by the ratio of occupied band to instantaneous bandwidth, $B/\Delta\nu \sim 10^{3}$–$10^{5}$. Transmitter aperture gain and the small duty cycle of a scanning schedule reduce time-averaged radiated power by further large factors.

The chirp implementation is therefore strongly favored on cost, and it supplies a deterministic voltage-domain tag at no additional expense: the emitted field either replicates the exact cold-plasma phase transfer function or deliberately does not, and either choice is testable in coherently captured baseband data. Design families whose peak-power requirements are orders of magnitude higher without compensating gains in expected recipients should be down-weighted in $\pi_{\mathrm{builder}}$.

Note also the interaction with Section 4.4: because synthetic dispersion is transmitted as sweep duration, the chirp's dwell cost is what makes low-band pre-chirp expensive; siting the transmitter in the Galactic plane transfers that cost to the interstellar medium.

**Intergalactic scalings (Section 16).** The threshold effective isotropic radiated power keeps the $d^2$ scaling above: an M31 pointing at $780\,\mathrm{kpc}$ requires $\sim 6\times10^3$ times the $10\,\mathrm{kpc}$ figure—of order $10^{28}\,\mathrm{W}$ peak as a true impulse, reduced to tens of petawatts of transmitter power by the chirp's $B/\Delta\nu$ factor at plausible gains—and Virgo-distance pointings require $\sim 10^6$ times the galactic figure. Against this per-pointing threshold stands the distance-invariant per-recipient cost: with target stellar column density $\Sigma$ and beam solid angle $\Omega$, the cost per star delivered is

$$
\frac{4\pi S_{\min}}{\Sigma\,\Omega},
$$

independent of $d$ while the footprint $\Omega d^2$ remains smaller than the target galaxy. The beam-filling horizon where this fails is gain-dependent: at gain $10^8$ the footprint spans $\sim 30\,\mathrm{kpc}$ near $\sim 80\,\mathrm{Mpc}$, beyond which per-recipient cost grows as $d^2$.

Duty-cycle accounting drives the collapsed architecture of Section 16.6: the pulsed discovery layer runs at power-times-duty of order $10^{-6}$ per target, while even a $30\,\mathrm{dB}$ weaker continuous message beam costs of order $10^{-3}$—a factor $\sim 10^3$ more energy. Phase modulation of the chirped carrier, by contrast, adds information at zero marginal energy: the carrier is already coherent for the $\sim 1\,\mathrm{s}$ sweep, phase is discarded by intensity products so trigger behavior is unchanged, and the channel capacity $B\,T\log_2(1+\mathrm{SNR})$ on the instantaneous bandwidth yields $\sim 10^4$–$10^6$ bits per burst in voltage data.

## Appendix D: primary reference

Benford, J., Benford, G., and Benford, D., “Messaging with Cost Optimized Interstellar Beacons,” arXiv:0810.3964: <https://arxiv.org/pdf/0810.3964>
