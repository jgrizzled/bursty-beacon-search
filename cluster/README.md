# Section 6.2 calibration cluster

Sharded execution of `phase1/calibration.py` on a Hetzner cpx62 fleet.
Execution spec: `phase1/CALIBRATION_PLAN.md`. The cluster layer only
distributes sim ranges — every result is exactly reproducible on a
single machine with
`uv run python phase1/calibration.py run --family F --sims LO-HI`.

## Layout

```
run.py    orchestrator (stdlib only, runs locally)
infra/    terraform: cpx62 workers keyed by id + firewall
state/    local run state: per-batch downloads, staged checkpoints,
          assignments, collated output (gitignored)
```

## Work model

The sim range is cut into batches of `--batch` sims (the kernel's
stream batch; 16 sims per batch → 63 batches for the 1,000-sim stage-1
budget). Batches form a queue; each host runs one batch at a time as a
detached systemd unit and pulls the next when done. Consequences:

- **Fleet sizing**: the fleet is created no larger than the number of
  pending batches, so `--hosts 99` with 63 batches provisions 63, not
  99. To actually feed ~99+ hosts, use `--batch 8` (125 batches);
  measured per-sim kernel cost is within ~8% of batch 16 on the
  dominant FAST campaign and *cheaper* on the sparse ones.
- **No idle spend**: a host whose queue is empty is destroyed
  immediately (terraform workers are keyed by id, so individual VMs
  can be removed); throttled stragglers just finish their own batch
  while everyone else has already been reaped.
- **Failures are self-healing**: a dead unit on a reachable host is
  restarted and resumes from its on-host unit checkpoint (this covers
  reboots); a host unreachable for ~20 min has its batch requeued and
  the VM destroyed (`--keep-failed` keeps it up for inspection). Unit
  checkpoints are pulled to `state/ckpt/` every ~5 min, and a requeued
  batch is seeded with the staged checkpoint on its next host. If a
  batch requeues with nobody idle, a fresh replacement VM is spawned
  (bounded by `--hosts` and a finite budget). A batch that fails on 3
  different hosts aborts the run — that is a bug, not host weather.
- **Duplicates are harmless**: batch results are deterministic
  functions of (family, sim), so a zombie host recomputing a batch can
  waste money but never corrupt data.

## Prerequisites

- `terraform` and `git` on PATH; python3; `uv` (for the final collate).
- `infra/terraform.tfvars` — copy `terraform.tfvars.example`; fill in
  the Hetzner API token, ssh public key, allowed IP. Fleet size is NOT
  set here (`run.py --hosts` manages `infra/hosts.auto.tfvars.json`).
- The matching ssh private key available (ssh-agent or `~/.ssh`).
- A committed HEAD: hosts receive the last commit, not the working tree.

## Run (per family, in the CALIBRATION_PLAN order)

```sh
python3 cluster/run.py --family M4 --sims 0-1000 --hosts 30
```

Each host: cloud-init → git push of HEAD → `uv sync` → kernel build →
`validate_fastscan.py` gate (a host that does not print ALL PASS never
computes units; outputs are downloaded with every batch) → detached
systemd shard → unit-checkpointed scanning. Kill/rerun `run.py` freely:
downloaded batches are skipped, `state/assignments.json` reattaches
running hosts, shards resume from checkpoints.

Collated output: `state/calibration_M4.json` (FAP_F, percentiles,
frozen stop-rule status). Commit-worthy artifacts after a family
completes: the collated JSON, per-batch `validation_output_host.txt`,
and the per-batch summaries.

## Smoke-testing the orchestration

A full batch is ~a day of VM time, so the end-to-end path (apply →
cloud-init → push → build → validation gate → unit → download →
collate → destroy) is exercised with `--campaigns`, which restricts the
shards to a campaign subset. `fast20201124A_sepoct` is 0.1% of the
study-wide scan cost, so a two-batch run finishes in minutes:

```sh
python3 cluster/run.py --family M4 --sims 9000-9004 --batch 2 \
    --hosts 1 --campaigns fast20201124A_sepoct
```

`--campaigns` is for this and nothing else — a production family run
must scan all six campaigns. Always give a smoke test a sim range
outside the 0–1000 stage-1 budget (as above), so its partial-search
summaries can never be collated as calibration sims, and delete
`state/results/<those batches>` afterwards.
