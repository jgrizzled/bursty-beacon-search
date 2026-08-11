# Section 6.2 calibration cluster

Sharded execution of `phase1/calibration.py` on a Hetzner cpx51 fleet.
Execution spec: `phase1/CALIBRATION_PLAN.md`. The cluster layer only
distributes sim ranges — every result is exactly reproducible on a
single machine with
`uv run python phase1/calibration.py run --family F --sims LO-HI`.

## Layout

```
run.py    orchestrator (stdlib only, runs locally)
infra/    terraform: N x cpx51 + firewall (from hetz-compute template)
state/    local run state: per-host downloads, collated output (gitignored)
```

## Prerequisites

- `terraform` and `git` on PATH; python3; `uv` (for the final collate).
- `infra/terraform.tfvars` — copy `terraform.tfvars.example`; fill in
  the Hetzner API token, ssh public key, allowed IP, `instance_count`.
- The matching ssh private key available (ssh-agent or `~/.ssh`).
- A committed HEAD: hosts receive the last commit, not the working tree.

## Run (per family, in the CALIBRATION_PLAN order)

```sh
python3 cluster/run.py --family M4 --sims 0-1000
```

Each host: cloud-init → git push of HEAD → `uv sync` → kernel build →
`validate_fastscan.py` gate (a host that does not print ALL PASS never
computes units; outputs are downloaded as artifacts) → detached
systemd shard → unit-checkpointed scanning. Kill/rerun `run.py` freely;
shards resume from their checkpoints. Failed hosts leave the fleet up
for inspection; rerun retries them.

Collated output: `state/calibration_M4.json` (FAP_F, percentiles,
frozen stop-rule status). Commit-worthy artifacts after a family
completes: the collated JSON, per-host `validation_output_host.txt`,
and the per-host summaries.
