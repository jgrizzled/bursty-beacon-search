#!/bin/sh
# One-shot full-scale acceptance run for a fresh compute VM.
# Builds the kernel, gates on the equivalence validation, then launches
# the checkpointed full-scale suite detached (survives SSH disconnect).
# Resume after any interruption by re-running this script: completed
# tasks are skipped via phase1/acceptance_checkpoint_full.jsonl.
set -e
cd "$(dirname "$0")/.."

uv sync
./scripts/build_scankernel.sh

echo "== equivalence validation (gate) =="
uv run python scripts/validate_fastscan.py | tee phase1/validation_output.txt
grep -q "ALL PASS" phase1/validation_output.txt

WORKERS=$(( $(nproc) - 1 ))
echo "== launching full-scale acceptance run ($WORKERS workers) =="
nohup uv run python phase1/acceptance.py --scale full --workers "$WORKERS" \
  > phase1/acceptance_full_run.log 2>&1 &
echo "pid $! ; monitor with:"
echo "  tail -f phase1/acceptance_full_run.log"
echo "  wc -l phase1/acceptance_checkpoint_full.jsonl   # 4600 lines = done"
