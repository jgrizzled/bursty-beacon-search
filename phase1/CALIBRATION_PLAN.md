# Section 6.2 calibration — execution specification

_Companion to the frozen prereg (`phase0/prereg_h1.md` Section 6.2, tag
`prereg-h1-v1.0`). The statistical procedure is frozen there; this
document fixes every execution detail left open — seeds, the Laplace
implementation, family order, batching, and the stop-rule evaluation —
and is committed BEFORE any production simulation runs. Implementation:
`phase1/calibration.py`; cluster distribution: `cluster/run.py`._

## Observed statistic being calibrated

Λ\* = 86.78456251617922 (study-wide maximum, Effelsberg 20200120E), from
the committed `phase1/confirmatory_results.json`. `collate` reads it from
that artifact, never from a hand-typed constant.

## Inputs

- `phase1/calibration_inputs/` — committed constructed event lists and
  barycentred windows for the six campaigns (SHA-256 provenance in
  `INPUTS.json`; construction cross-checked exactly against the
  confirmatory scan). Simulation and scanning never touch `data/raw/`
  and need no astropy.
- `phase1/null_fits.json` — committed output of
  `calibration.py fit-nulls`. Fitted log-likelihoods are required to
  equal the confirmatory scan's M0/M1/M4/M5 ll table exactly (identical
  optimizer, prereg 6.2 step 1); verified at fit time 2026-08-11.

## Frozen-procedure implementation choices

1. **Search configuration**: identical to the observed scan
   (`p_min = 1 h`, `σ_min = 60 s`, `pl.frozen_tau_grid()`, M1 grid
   200 × 24). Nuisance parameters are refit in every simulation by the
   same code paths (`pl.m0_ll`, `pl.m1_scan`, `pl.m4_fit`, `pl.m5_fit`).
2. **Laplace draws** (prereg 6.2 step 2). Parameterizations:
   M0 `[ln λ]` (analytic var 1/N); M1 `[ln P_a, δ, t0_frac, ln λ_in,
ln λ_out]`; M4 `[ln k, ln r]`; M5 `[ln α, ln β]`. Covariance =
   inverse of the symmetrized central-finite-difference Hessian of −ll
   at the MLE. Grid-profiled structural directions (M1) are locally
   flat, so raw FD curvature there is meaningless; eigenvalues are
   floored so no eigendirection has standard deviation exceeding
   `LAPLACE_STD_CAP = 5` FD steps, with FD steps tied to the frozen grid
   resolution (half a period-grid step in ln P_a, half a δ-grid gap,
   half a phase-grid step). Draws are truncated at the frozen bounds by
   resampling (≤ 200 tries, then clipping). M1 campaigns with
   n_out = 0 keep λ_out fixed at 0.
3. **Seeding / determinism.** Stream for (family, campaign, sim) uses
   `np.random.default_rng([20260811, family_id, campaign_id, sim])` with
   `family_id ∈ {M0:0, M1:1, M4:4, M5:5}` and campaign ids 0–5 in the
   order sepoct, Nançay, AstroFlash, TMRT, Effelsberg, FAST 20240114A.
   The parameter draw and the event stream consume this one generator in
   that order, so every simulated stream is a pure function of
   (family, campaign, sim) — independent of batch size, worker count,
   host, or execution order. Any simulation is therefore exactly
   replicable on a single machine
   (`calibration.py run --family F --sims k-(k+1)`).
4. **Batched kernel.** Scans use `scankernel.scan_scanner_batch`
   (`scan_period_multi` in `_scankernel.c`): S streams sharing one
   window function per kernel pass, sharing only stream-independent
   exposure work. Outputs are bit-identical to per-stream
   `scan_scanner_c` calls (same cell order, per-stream pruning state,
   first-in-scan-order argmax); validated by
   `scripts/validate_fastscan.py` section [6] with exact float equality
   (`phase1/validation_output_batch.txt`, ALL PASS, 2026-08-11).
   Measured speedup 1.5–2.4× by octave/model.
   **Segmented sweep (added 2026-08-12, before any production run).**
   `scan_period_multi` additionally jumps over whole runs of t0 between
   breakpoints (an interval edge crossing an exposure-polyline node or
   any stream's event phase; counts constant, exposure affine within a
   run) when every stream provably fails the same `e_in >= e_star[n]`
   prune test the dense walk applies at each point — endpoint exposures
   minus a rigorous rounding guard (exposure-flat runs are bitwise
   constant; no guard needed). Runs that might compete are walked with
   the dense-path arithmetic verbatim, so outputs stay bit-identical:
   this is a traversal shortcut, not a change of evaluation. Engaged
   per sigma by a density heuristic; forceable on/off via
   `scankernel.set_seg_mode` / `BBS_SEG_MODE` (all modes give identical
   results). Validated with exact float equality against the unchanged
   single-stream kernel by `validate_fastscan.py` sections [6]–[7]
   (`phase1/validation_output_seg.txt`, ALL PASS, 2026-08-12) and on
   the real windows with production M4 streams by
   `scripts/bench_segscan.py`. Measured warm-chunk speedup (S=16, M4
   streams): ×3.4 Effelsberg, ×1.9 TMRT, ×1.0 on the event-dense FAST
   campaigns; ≈×1.2 study-wide (the FAST 20240114A campaign is ≈2/3 of
   total cost and its per-stream event density leaves no skippable
   runs). Production batch
   `DEFAULT_BATCH = 16`; scan units are (campaign, octave, model,
   chunk, sim batch), with per-model chunk counts set by the cost rule
   `ceil(n_f · t_hi · w_model / 780,000 period-days)` (w_M3 = 5) so all
   units cost roughly equal wall time; chunk results combine in chunk
   order under strict `>`.
5. **Kernel gate (every host).** Any build of `_scankernel.c` — every
   cluster host builds its own — must pass `validate_fastscan.py`
   (ALL PASS) before computing units; per-host validation outputs are
   collected as run artifacts. Cross-platform float differences (libm)
   would only appear as last-ulp Λ differences; the per-host validation
   plus the FAP's threshold-count definition make this immaterial, and
   any exact replication check must be run on matching hardware.
6. **Family order and staged budget.** Families run one at a time:
   **M4 → M5 → M1 → M0**, ordered by expected storm-mimicry (cost
   containment only; the conservative-maximum FAP over completed
   families is order-independent). Per the frozen staged budget each
   family completes 1,000 sims (indices 0–999); the stop rule is then
   evaluated: if Λ\* < the family's empirical 99th percentile
   (equivalently FAP_F > 0.01), the calibration stops and FAP ≫ 10⁻³ is
   reported with the completed families' distributions. Otherwise the
   next family runs; only if all four families complete stage 1 with
   Λ\* above every 99th percentile does the 10,000-sim extension
   trigger.
7. **Collation.** `calibration.py collate` merges per-shard summary
   JSONLs: per family, the null distribution of per-sim study-wide
   maximum Λ (each sim's full six-campaign frozen search), FAP_F =
   (# sims with max Λ ≥ Λ\*) / N, percentiles, stop-rule status, and
   FAP = max over completed families. Output:
   `phase1/calibration_results.json`, committed with the per-host
   validation artifacts and shard checkpoints.

## Cluster execution (sharded; `cluster/run.py`)

Simulations are homogeneous, so hosts get pre-assigned contiguous sim
ranges (no work queue): terraform provisions N cpx62 hosts; each host
receives the current git HEAD, builds and validates the kernel, and runs
`calibration.py run --family F --sims lo-hi --workers 16 --batch 16` as
a detached systemd unit with unit-level checkpointing. The orchestrator
polls per-host `status_*.json`, downloads summaries and checkpoints,
collates, and destroys the fleet. A failed host's shard is simply rerun
(resumes from its checkpoint). Single-machine replication uses the same
`run` command with any sim range — the cluster layer adds nothing to the
science path.

## Cost basis (measured 2026-08-11)

Observed full-search cost ≈ 175 Apple-core-h/sim; batching ≈ 1.6–1.8×
end-to-end; cpx62 ≈ 2× better price/performance than ccx63 (user
benchmark). Stage-1 single family ≈ €1.5–2.5k and ~1–2 weeks on a
30–60 VM fleet; final fleet sizing decided at launch.

Re-measured 2026-08-12 with the segmented kernel (warm-chunk marginal
sampling over all octaves, S=16, production M4 streams, Apple M4):
≈106 core-h/sim study-wide vs ≈129 on the same sampling without
segmentation (×1.21); per campaign, fast20240114A ≈ 65% of total
(unchanged), Effelsberg ×3.4, TMRT ×1.9. Sampling-based — treat the
frozen 175 core-h/sim as the conservative planning number and expect
the savings to land mostly in wall time on the sparse campaigns'
units. Measured M3/M2 cost ratio: 5.3 on fast20240114A (dominant),
10–19× on the cheaper campaigns — `w_M3 = 5` retained (unit
granularity only; per-sim results are chunk-invariant).
