# M4 stage-1 calibration run notes

Executed per `phase1/CALIBRATION_PLAN.md` / `phase0/prereg_h1.md` Section 6.2.
Command: `python3 cluster/run.py --family M4 --sims 0-1000 --batch 8 --hosts 99`
(sims 0..999, 125 batches of 8, frozen seeds, batch size fixed for the family).

## Result

- Lambda* = 86.78456251617922 (read by collate from
  `phase1/confirmatory_results.json`, never hand-typed).
- n = 1000 null sims: **0 of 1000 reached Lambda*** -> empirical FAP_M4 = 0.0
  (< 1/1000). Null percentiles: P50 = -19.29, P90 = 12.16, P99 = 26.89,
  P99.9 = 35.93.
- `stage1_complete = true`, `stop_rule_triggered = false`: Lambda* far exceeds
  the M4 99th percentile, so the frozen stop rule does NOT end the
  calibration. Frozen family order continues M4 -> M5 -> M1 -> M0.

## Fleet and timeline

- 99 Hetzner cpx62 (16 vCPU EPYC Genoa, 30 GB), one shard per host,
  `--workers 16`. Launched Wed 2026-08-12 ~12:16 PDT; shards dispatched
  ~13:15 after per-host setup; wave 1 (99 batches) completed by Sat morning;
  wave 2 (26 batches on 26 hosts, other 73 hosts destroyed on idle)
  completed Mon 2026-08-17 09:12 PDT. Collation + full teardown automatic;
  `terraform state list` verified empty afterward.
- Compute: 7,227 host-hours summed over the 125 per-batch shard clocks
  (~58 h median per batch; per-sim cost ~116 host-core-h, i.e. between the
  106 core-h measured basis and the 175 core-h planning number).
  Cost ~EUR 1,373 compute + ~EUR 60-100 setup/idle/false-start overhead
  ~= EUR 1.45k total, inside the EUR 1.5-2.5k plan envelope.

## Incidents (all resolved, none affecting results)

1. **ufw rate-limit vs orchestrator (launch blocker).** The cloud-init
   template's `ufw limit 50022/tcp` REJECTs the 6th new connection per 30 s
   per source; run.py's setup burst tripped it on all 99 hosts
   ("Connection refused" at the validation gate). The single-host smoke test
   had passed only because `cloud-init status --wait` split its burst across
   two 30 s windows. Fixed in commit 32babf4 (plain `ufw allow`; source
   filtering is the Hetzner cloud firewall's job) and hotfixed on the live
   fleet. ~30 min / ~EUR 10 lost.
2. **Control-box power outages (Sat).** The orchestrator died twice with the
   local machine; on-host shards (detached systemd units) computed through
   both gaps, so zero compute was lost. run.py resumed from
   `state/assignments.json` + on-host checkpoints each time; a cron watchdog
   (removed after completion) guarded the remainder of the run.
3. **Host weather: none.** Zero unreachable hosts, unit deaths, requeues, or
   download failures across the entire run. All 125 per-host validation
   gates ended ALL PASS (`validation/` here; enforced before any unit ran).

## Archived artifacts

- `phase1/calibration_results.json` — collated stage-1 output (copy of
  `cluster/state/calibration_M4.json`).
- `summaries/` — per-batch six-model ll tables, one JSONL line per sim;
  verified: 1000 unique sims 0..999, every batch `done` at 11456/11456 units.
- `validation/` — per-batch host validation gate output (all end ALL PASS).
- `manifest.tsv` — batch -> host/IP, shard walltime, completion time.
- Unit checkpoints (11 MB x 125 = 1.4 GB) are NOT committed (size); they
  remain in `cluster/state/results/` locally. Any sim is exactly
  reproducible via
  `uv run python phase1/calibration.py run --family M4 --sims k-(k+1)`.
