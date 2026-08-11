#!/usr/bin/env python3
"""Run the Section 6.2 calibration for one null family on a Hetzner
cpx62 fleet (execution spec: phase1/CALIBRATION_PLAN.md).

Flow:
  1. terraform apply (idempotent -- existing servers are reused)
  2. wait for cloud-init on every host
  3. push the current git HEAD to every host; uv sync; build the scan
     kernel; run scripts/validate_fastscan.py -- the host may not compute
     units unless its own build prints ALL PASS (output collected)
  4. start each host's shard as a detached systemd unit:
     calibration.py run --family F --sims lo-hi --workers W --batch B
  5. poll shard status files, reporting crashes and progress
  6. download summaries + unit checkpoints + validation outputs, collate
     (calibration.py collate), terraform destroy

Resumable at every stage: terraform state tracks servers; a host's unit
checkpoint resumes its shard; downloaded per-host results under state/
mark shards complete. Ctrl-C and rerun at any point. Shard results are
deterministic functions of (family, sim), so re-running a shard anywhere
(including locally) reproduces it exactly.

Usage:
  python3 cluster/run.py --family M4 --sims 0-1000
"""

import argparse
import json
import os
import re
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
INFRA_DIR = HERE / "infra"
STATE_DIR = HERE / "state"

SSH_USER = "admin"
REMOTE_BARE = "/home/admin/app.git"
REMOTE_TREE = "/home/admin/app"
REMOTE_STATE = "/home/admin/calib_state"
REMOTE_UV = "/home/admin/.local/bin/uv"
UNIT = "calib-shard"

POLL_SECONDS = 30
CLOUD_INIT_TIMEOUT = 1200
SETUP_TIMEOUT = 3600            # uv sync + kernel build + validation
UNREACHABLE_LIMIT = 40
MISSING_LIMIT = 3

SSH_OPTS = [
    "-o", "BatchMode=yes",
    "-o", "StrictHostKeyChecking=no",
    "-o", "UserKnownHostsFile=/dev/null",
    "-o", "LogLevel=ERROR",
    "-o", "ConnectTimeout=10",
]


def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def shard_dir(index):
    return STATE_DIR / "results" / f"host-{index}"


# ---------------------------------------------------------------- terraform

def terraform(*args, capture=False):
    cmd = ["terraform", f"-chdir={INFRA_DIR}", *args]
    if capture:
        return subprocess.run(cmd, check=True, capture_output=True,
                              text=True).stdout
    subprocess.run(cmd, check=True)


def ensure_init():
    if not (INFRA_DIR / ".terraform" / "terraform.tfstate").exists():
        terraform("init", "-input=false")


def tf_apply():
    ensure_init()
    terraform("apply", "-auto-approve", "-input=false")
    out = json.loads(terraform("output", "-json", capture=True))
    return out["hosts"]["value"], out["ssh_port"]["value"]


def maybe_destroy():
    if not (INFRA_DIR / "terraform.tfstate").exists():
        return
    ensure_init()
    terraform("destroy", "-auto-approve", "-input=false")


# ---------------------------------------------------------------------- ssh

def ssh_run(host, port, remote_cmd, check=True, timeout=None):
    cmd = ["ssh", "-p", str(port), *SSH_OPTS,
           f"{SSH_USER}@{host['ipv4']}", remote_cmd]
    return subprocess.run(cmd, check=check, capture_output=True,
                          text=True, timeout=timeout)


def wait_cloud_init(host, port):
    deadline = time.time() + CLOUD_INIT_TIMEOUT
    while True:
        r = ssh_run(host, port, "cloud-init status --wait", check=False)
        if r.returncode in (0, 2):
            return
        if r.returncode != 255:
            raise RuntimeError(
                f"cloud-init failed on {host['name']}: {r.stdout}{r.stderr}")
        if "Permission denied" in r.stderr:
            raise RuntimeError(
                f"ssh auth to {host['name']} failed ({r.stderr.strip()}); "
                f"is the private key for terraform.tfvars' ssh_public_key "
                f"available (ssh-agent or ~/.ssh)?")
        if time.time() > deadline:
            raise RuntimeError(
                f"timed out waiting for ssh/cloud-init on {host['name']}")
        time.sleep(10)


# ------------------------------------------------------------------ deploy

def push_code(host, port):
    ssh_run(host, port, f"git init -q --bare {REMOTE_BARE}")
    env = {**os.environ, "GIT_SSH_COMMAND": "ssh " + " ".join(SSH_OPTS)}
    subprocess.run(
        ["git", "push", "--force", "--quiet",
         f"ssh://{SSH_USER}@{host['ipv4']}:{port}{REMOTE_BARE}",
         "HEAD:refs/heads/main"],
        cwd=REPO, env=env, check=True, capture_output=True, text=True)
    ssh_run(
        host, port,
        f"mkdir -p {REMOTE_TREE} && "
        f"git --git-dir={REMOTE_BARE} --work-tree={REMOTE_TREE} "
        f"checkout -qf main")


def setup_host(host, port):
    """uv sync, kernel build, and the mandatory per-host validation gate
    (CALIBRATION_PLAN item 5). Skipped when the host already holds a
    passing validation for the current kernel source."""
    marker = f"{REMOTE_TREE}/phase1/validation_output_host.txt"
    r = ssh_run(host, port,
                f"cd {REMOTE_TREE} && "
                f"sha256sum phase1/_scankernel.c > /tmp/kern.sha && "
                f"cmp -s /tmp/kern.sha /home/admin/validated_kernel.sha && "
                f"tail -1 {marker} 2>/dev/null", check=False)
    if r.returncode == 0 and r.stdout.strip().endswith("ALL PASS"):
        log(f"[{host['name']}] kernel already validated, skipping setup")
        return
    r = ssh_run(
        host, port,
        f"set -e; cd {REMOTE_TREE} && "
        f"{REMOTE_UV} sync --frozen >/dev/null 2>&1 && "
        f"./scripts/build_scankernel.sh >/dev/null && "
        f"{REMOTE_UV} run python scripts/validate_fastscan.py "
        f"> {marker} 2>&1; tail -1 {marker}",
        check=False, timeout=SETUP_TIMEOUT)
    if not r.stdout.strip().endswith("ALL PASS"):
        raise RuntimeError(
            f"{host['name']}: kernel validation gate FAILED "
            f"({r.stdout.strip()[-200:]} {r.stderr.strip()[-200:]})")
    ssh_run(host, port,
            f"cd {REMOTE_TREE} && "
            f"sha256sum phase1/_scankernel.c > /home/admin/validated_kernel.sha")
    log(f"[{host['name']}] setup done, validation ALL PASS")


def start_job(host, port, family, lo, hi, workers, batch):
    inner = (
        f"{REMOTE_UV} run --project {REMOTE_TREE} python "
        f"{REMOTE_TREE}/phase1/calibration.py run --family {family} "
        f"--sims {lo}-{hi} --workers {workers} --batch {batch} "
        f"--state-dir {REMOTE_STATE}")
    ssh_run(
        host, port,
        f"sudo systemctl reset-failed {UNIT}.service 2>/dev/null; "
        f"mkdir -p {REMOTE_STATE} && "
        f"sudo systemd-run --quiet --unit={UNIT} --uid={SSH_USER} "
        f"--gid={SSH_USER} --working-directory={REMOTE_TREE} "
        f"--property=Restart=no {inner}")


# ----------------------------------------------------------------- monitor

def parse_json(text):
    try:
        return json.loads(text)
    except (json.JSONDecodeError, ValueError):
        return None


def probe(host, port, family, lo, hi):
    r = ssh_run(
        host, port,
        f"systemctl show {UNIT}.service --property=ActiveState,Result "
        f"2>/dev/null; echo @@@; "
        f"cat {REMOTE_STATE}/status_{family}_{lo}-{hi}.json 2>/dev/null; "
        f"echo",
        check=False)
    if r.returncode != 0:
        return {"phase": "unreachable", "detail": r.stderr.strip()[:200]}
    parts = (r.stdout.split("@@@") + [""])[:2]
    unit = dict(l.split("=", 1) for l in parts[0].strip().splitlines()
                if "=" in l)
    status = parse_json(parts[1]) or {}
    active = unit.get("ActiveState", "")
    if status.get("phase") == "done":
        return {"phase": "done", "status": status}
    if active in ("active", "activating"):
        return {"phase": "running", "status": status}
    if active == "failed":
        return {"phase": "failed",
                "detail": f"systemd unit failed (Result={unit.get('Result')})"}
    if status.get("phase") == "scanning":
        return {"phase": "failed",
                "detail": "shard process died mid-scan (unit gone)"}
    return {"phase": "missing"}


def download_shard(host, port, family, lo, hi):
    d = shard_dir(host["index"])
    d.mkdir(parents=True, exist_ok=True)
    for pat in (f"summaries_{family}_{lo}-{hi}.jsonl",
                f"units_{family}_{lo}-{hi}.jsonl",
                f"status_{family}_{lo}-{hi}.json"):
        r = ssh_run(host, port, f"cat {REMOTE_STATE}/{pat}")
        (d / pat).write_text(r.stdout)
    r = ssh_run(host, port,
                f"cat {REMOTE_TREE}/phase1/validation_output_host.txt",
                check=False)
    (d / "validation_output_host.txt").write_text(r.stdout)


def shard_done_locally(index, family, lo, hi):
    p = shard_dir(index) / f"summaries_{family}_{lo}-{hi}.jsonl"
    if not p.exists():
        return False
    n = sum(1 for _ in open(p))
    return n == hi - lo


# ------------------------------------------------------------ orchestration

def shard_ranges(lo, hi, n_hosts, batch):
    """Contiguous ranges, sized in multiples of batch (except the last)."""
    total = hi - lo
    per = -(-total // n_hosts)
    per = -(-per // batch) * batch
    out = []
    cur = lo
    for _ in range(n_hosts):
        nxt = min(cur + per, hi)
        out.append((cur, nxt))
        cur = nxt
        if cur >= hi:
            break
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--family", required=True,
                    choices=["M0", "M1", "M4", "M5"])
    ap.add_argument("--sims", default="0-1000",
                    help="half-open sim index range LO-HI (default 0-1000, "
                         "the frozen stage-1 budget)")
    ap.add_argument("--workers", type=int, default=16)
    ap.add_argument("--batch", type=int, default=16)
    ap.add_argument("--keep-infra", action="store_true")
    args = ap.parse_args()
    lo, hi = (int(x) for x in args.sims.split("-"))

    r = subprocess.run(["git", "status", "--porcelain"], cwd=REPO,
                       capture_output=True, text=True)
    if r.stdout.strip():
        log("note: uncommitted changes present; hosts receive HEAD, "
            "not the working tree")

    log("Applying terraform...")
    hosts, port = tf_apply()
    log(f"{len(hosts)} host(s): "
        + ", ".join(f"{h['name']}={h['ipv4']}" for h in hosts))
    ranges = shard_ranges(lo, hi, len(hosts), args.batch)
    hosts = hosts[:len(ranges)]
    for h, (slo, shi) in zip(hosts, ranges):
        h["lo"], h["hi"] = slo, shi
        log(f"  {h['name']}: sims {slo}..{shi - 1}")

    def prepare(host):
        i = host["index"]
        if shard_done_locally(i, args.family, host["lo"], host["hi"]):
            log(f"[{host['name']}] shard already downloaded, skipping")
            return
        log(f"[{host['name']}] waiting for cloud-init...")
        wait_cloud_init(host, port)
        push_code(host, port)
        setup_host(host, port)
        st = probe(host, port, args.family, host["lo"], host["hi"])
        if st["phase"] == "done":
            log(f"[{host['name']}] shard already finished on host")
        elif st["phase"] == "running":
            log(f"[{host['name']}] shard already running, resuming watch")
        else:
            start_job(host, port, args.family, host["lo"], host["hi"],
                      args.workers, args.batch)
            log(f"[{host['name']}] started sims "
                f"{host['lo']}..{host['hi'] - 1}")

    with ThreadPoolExecutor(max_workers=min(16, len(hosts))) as pool:
        list(pool.map(prepare, hosts))

    terminal = {}
    strikes = {h["index"]: 0 for h in hosts}
    while len(terminal) < len(hosts):
        for host in hosts:
            i = host["index"]
            if i in terminal:
                continue
            if shard_done_locally(i, args.family, host["lo"], host["hi"]):
                terminal[i] = "done"
                continue
            st = probe(host, port, args.family, host["lo"], host["hi"])
            if st["phase"] == "done":
                download_shard(host, port, args.family, host["lo"],
                               host["hi"])
                log(f"[{host['name']}] shard done, downloaded")
                terminal[i] = "done"
            elif st["phase"] == "failed":
                log(f"[{host['name']}] FAILED: {st['detail']}")
                terminal[i] = "failed"
            elif st["phase"] == "running":
                strikes[i] = 0
                s = st.get("status") or {}
                if s.get("units_total"):
                    log(f"[{host['name']}] {s.get('units_done', 0)}/"
                        f"{s['units_total']} units "
                        f"({s.get('elapsed_s', 0) / 3600:.1f} h)")
                else:
                    log(f"[{host['name']}] running (starting up)")
            elif st["phase"] == "unreachable":
                strikes[i] += 1
                if strikes[i] >= UNREACHABLE_LIMIT:
                    terminal[i] = "failed"
                    log(f"[{host['name']}] FAILED: unreachable")
            else:
                strikes[i] += 1
                if strikes[i] >= MISSING_LIMIT:
                    terminal[i] = "failed"
                    log(f"[{host['name']}] FAILED: no unit and no status")
        if len(terminal) < len(hosts):
            time.sleep(POLL_SECONDS)

    failed = sorted(i for i, ph in terminal.items() if ph != "done")
    if failed:
        log(f"Shards failed on hosts {failed}. Leaving servers up; rerun "
            f"to resume, or destroy with: "
            f"terraform -chdir={INFRA_DIR} destroy")
        sys.exit(1)

    log("All shards done; collating...")
    dirs = ",".join(str(shard_dir(h["index"])) for h in hosts)
    subprocess.run(
        ["uv", "run", "python", str(REPO / "phase1" / "calibration.py"),
         "collate", "--state-dirs", dirs,
         "--out", str(STATE_DIR / f"calibration_{args.family}.json")],
        cwd=REPO, check=True)
    if args.keep_infra:
        log("--keep-infra set, skipping destroy")
    else:
        log("Destroying terraform resources...")
        maybe_destroy()
    log("Done")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrupted. State is saved; rerun to resume.",
              file=sys.stderr)
        sys.exit(130)
