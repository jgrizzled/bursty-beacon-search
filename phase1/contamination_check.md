# Section 7 contamination check — confirmatory H1 scan (2026-08-11)

Prereg (`phase0/prereg_h1.md` Section 7, frozen at `prereg-h1-v1.0`)
requires every timing candidate to be cross-checked against cataloged
pulsars and RRATs within the localization region and instrument sidelobe
geometry, and against published campaign RFI/instrument-state logs,
before being reported.

**Scope.** No campaign can produce a prereg 6.3 candidate yet — the
Section 6.2 FAP calibration is deferred to the cluster. This check is run
now against the peaks that *would* be candidates if their FAP came in
below 10⁻³: the FRB 20200120E (Effelsberg) peaks driving the study-wide
Λ* = +86.78, whose non-alias-flagged runner-ups (T ≈ 8.88, 20.73, 31.11,
62.08 d; Δll < 0.5 below the alias-flagged 2.96 d maximum) are the
would-be candidates. The only other positive campaign, TMRT 20240114A
(Λ = +0.56), is likelihood-indistinguishable from its natural models and
its top peak is flagged by the live spectral-window rule; no peak there
would be a candidate at any plausible calibration.

## FRB 20200120E (Effelsberg campaign)

1. **Pulsar/RRAT cone search** (2026-08-11, pulsar survey scraper
   `pulsar.cgca-hub.org`, aggregating ATNF psrcat + survey-level
   discoveries incl. RRATs): radius 2° around 09:57:54.699 +68:49:00.85,
   DM 87.75 ± 100 (i.e. any Galactic DM) → **0 matches**. A direct ATNF
   psrcat radius query was attempted but the web form ignored the radius
   constraint; the scraper cone search (which wraps psrcat) is the
   recorded result. The Effelsberg L-band primary beam is ~9.4′ FWHM;
   the 2° search covers far sidelobes.
2. **Foreground physics:** DM 87.75 pc cm⁻³ exceeds the maximum Galactic
   contribution along this high-latitude sightline (~40–50 pc cm⁻³,
   NE2001/YMW16; Bhardwaj et al. 2021), excluding any Galactic
   pulsar/RRAT interpretation of the burst stream itself.
3. **Localization:** mas-precision VLBI localization to a globular
   cluster of M81 (Kirsten et al. 2022, Nature 602, 585) excludes
   near-field RFI and chance foreground point sources for the bursts
   used in the timing test.
4. **RFI / instrument state:** the burst list is the frozen composed
   Nimmo 2023 + Pearlman 2024 set (manifest 1.7a) — published,
   DM-consistent detections; no RFI or instrument-state exceptions
   affecting burst timing are reported in those papers for the sessions
   involved. Scheduling structure (the PRECISE ~11.4 d revisit rhythm
   and day-rational combs) is handled by the frozen alias set, which
   flags the Λ*-defining 2.96 d peak itself (sidereal/3).

**Interpretation recorded with the result (not a candidate claim):** the
Effelsberg likelihood surface is a plateau — narrow-visit (σ_v ≈ 30–60
min) solutions at mutually unrelated periods reach ll within 0.5 of the
maximum. This is the storm-fitting degeneracy anticipated by the
manifest 1.7a power caveat (53/69 events in one ~2 h session): any
period placing one visit pair on the storm fits equally well. Whether
Λ* = 86.78 is at all unusual under bursty natural processes folded
through these windows is exactly the question the Section 6.2
calibration answers; no significance is asserted or implied here.

**Outcome:** no contamination source identified; the check passes for
every would-be-candidate peak. Candidacy remains undetermined pending
FAP calibration.
