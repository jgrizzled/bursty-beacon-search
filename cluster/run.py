#!/usr/bin/env python3
"""Run the Section 6.2 calibration for one null family on a Hetzner
cpx62 fleet (execution spec: phase1/CALIBRATION_PLAN.md).

Work model: the sim range is cut into batches of --batch sims (the
kernel's stream batch); batches form a queue. Each host runs one batch
at a time as a detached systemd unit and pulls the next when done, so
fast hosts do more and throttled hosts do less. The fleet only ever
shrinks: it is created no larger than the number of pending batches,
idle hosts are destroyed the moment the queue is empty, and dead hosts
are reaped -- nobody sits idle on the meter waiting for stragglers.

Flow:
  1. terraform apply for min(--hosts, pending batches) workers
     (hosts.auto.tfvars.json holds the id set; removing an id destroys
     exactly that VM)
  2. per host, in background threads (SETUP_PARALLEL wide): wait for
     cloud-init; push the current git HEAD; uv sync; build the scan
     kernel; run scripts/validate_fastscan.py -- a host may not compute
     units unless its own build prints ALL PASS (output collected per
     batch). A host is dispatched the moment its OWN gate passes; there
     is no fleet-wide setup barrier.
  3. dispatch loop: assign batches to idle ready hosts, poll status
     files, download finished batches, retire idle/dead hosts

Failure handling (all automatic):
  - unit died but host reachable (crash, OOM, reboot): restart the unit;
    it resumes from its on-host unit checkpoint (up to MAX_RESTARTS,
    then the host is retired and the batch requeued)
  - host unreachable past UNREACHABLE_LIMIT polls: batch requeued,
    VM destroyed (--keep-failed leaves it up for inspection)
  - a requeued batch with no idle host left spawns a fresh replacement
    VM (bounded by --hosts and a finite replacement budget), so a late
    failure never needs an operator rerun and no host idles as a spare
  - unit checkpoints are pulled to state/ckpt/ every CKPT_PULL_EVERY
    polls, and a requeued batch is seeded with its staged checkpoint on
    the next host, so work survives even a permanently dead VM
  - a batch that fails on BATCH_ATTEMPTS_MAX hosts aborts the run
    (systematic problem, not host weather)

Resumable at every stage: terraform state tracks servers,
state/assignments.json remembers what each host is running, downloaded
batches are skipped, and shards resume from checkpoints. Ctrl-C and
rerun at any point. Batch results are deterministic functions of
(family, sim), so re-running a batch anywhere (including locally)
reproduces it exactly; duplicate computation is at worst wasted money,
never wrong data.

Sizing note: 1,000 sims at --batch 16 is 63 batches, so more than 63
hosts cannot be fed; use --batch 8 (125 batches) for larger fleets --
measured per-sim kernel cost is within ~8% of batch 16 on the dominant
campaign and cheaper on the sparse ones. Prefer a host count that
divides the batch count evenly (e.g. 125 hosts for one wave, 63 for
two): M4 ran 125 batches on 99 hosts and spent 3 extra wall-days on a
26-batch second wave. Total cost is wave-shape-invariant; wall time is
not.

Usage:
  python3 cluster/run.py --family M4 --sims 0-1000 --hosts 30
"""

import argparse
import json
import os
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
INFRA_DIR = HERE / "infra"
STATE_DIR = HERE / "state"
FLEET_FILE = INFRA_DIR / "hosts.auto.tfvars.json"
ASSIGN_FILE = STATE_DIR / "assignments.json"

SSH_USER = "admin"
REMOTE_BARE = "/home/admin/app.git"
REMOTE_TREE = "/home/admin/app"
REMOTE_STATE = "/home/admin/calib_state"
REMOTE_UV = "/home/admin/.local/bin/uv"
UNIT = "calib-shard"

POLL_SECONDS = 30
CLOUD_INIT_TIMEOUT = 1800       # boot + package_upgrade, mirror-limited
SETUP_TIMEOUT = 3600            # uv sync + kernel build + validation
UNREACHABLE_LIMIT = 40          # polls (~20 min) before a host is dead
MISSING_LIMIT = 3               # polls with no unit + no status
MAX_RESTARTS = 3                # unit restarts per (host, batch)
BATCH_ATTEMPTS_MAX = 3          # distinct hosts per batch before abort
CKPT_PULL_EVERY = 10            # polls between checkpoint pulls

SSH_OPTS = [
    "-o", "BatchMode=yes",
    "-o", "StrictHostKeyChecking=no",
    "-o", "UserKnownHostsFile=/dev/null",
    "-o", "LogLevel=ERROR",
    "-o", "ConnectTimeout=10",
    # ConnectTimeout only bounds the TCP handshake; keepalives bound an
    # established session that blackholes mid-command (the failure mode
    # that would otherwise stall the whole poll loop for TCP-retransmit
    # timescales).
    "-o", "ServerAliveInterval=15",
    "-o", "ServerAliveCountMax=4",
]
SSH_TIMEOUT = 300               # hard cap on any single ssh command
PROBE_PARALLEL = 16             # concurrent per-host polls
SETUP_PARALLEL = 16             # concurrent host setups (git push + build)


def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def batch_key(family, blo, bhi):
    return f"{family}_{blo}-{bhi}"


def batch_dir(family, blo, bhi):
    return STATE_DIR / "results" / batch_key(family, blo, bhi)


def staged_ckpt(family, blo, bhi):
    return STATE_DIR / "ckpt" / f"units_{batch_key(family, blo, bhi)}.jsonl"


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


def fleet_ids():
    if FLEET_FILE.exists():
        return list(json.loads(FLEET_FILE.read_text())["host_ids"])
    return []


def ensure_fleet(ids):
    """Converge the fleet to exactly `ids` (destroys removed hosts) and
    return the host list sorted by index."""
    ensure_init()
    FLEET_FILE.write_text(json.dumps({"host_ids": sorted(ids, key=int)}))
    terraform("apply", "-auto-approve", "-input=false")
    out = json.loads(terraform("output", "-json", capture=True))
    hosts = sorted(out["hosts"]["value"], key=lambda h: h["index"])
    return hosts, out["ssh_port"]["value"]


def maybe_destroy():
    if not (INFRA_DIR / "terraform.tfstate").exists():
        return
    ensure_init()
    terraform("destroy", "-auto-approve", "-input=false")
    if FLEET_FILE.exists():
        FLEET_FILE.unlink()


# ---------------------------------------------------------------------- ssh

def ssh_run(host, port, remote_cmd, check=True, timeout=SSH_TIMEOUT,
            stdin=None):
    """Run one remote command. A timeout is reported the same way an
    unreachable host is (returncode 255 / CalledProcessError), so every
    caller's existing failure path covers it."""
    cmd = ["ssh", "-p", str(port), *SSH_OPTS,
           f"{SSH_USER}@{host['ipv4']}", remote_cmd]
    try:
        return subprocess.run(cmd, check=check, capture_output=True,
                              text=True, timeout=timeout, input=stdin)
    except subprocess.TimeoutExpired:
        err = f"ssh timed out after {timeout}s"
        if check:
            raise subprocess.CalledProcessError(255, cmd, "", err)
        return subprocess.CompletedProcess(cmd, 255, "", err)


def wait_cloud_init(host, port):
    deadline = time.time() + CLOUD_INIT_TIMEOUT
    while True:
        # `--wait` blocks through package_upgrade, so this one command is
        # allowed the whole cloud-init budget rather than SSH_TIMEOUT.
        r = ssh_run(host, port, "cloud-init status --wait", check=False,
                    timeout=CLOUD_INIT_TIMEOUT)
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


def start_job(host, port, family, lo, hi, workers, batch, campaigns=None):
    """(Re)start the shard unit for one batch; the shard resumes from
    whatever unit checkpoint exists in REMOTE_STATE."""
    inner = (
        f"{REMOTE_UV} run --project {REMOTE_TREE} python "
        f"{REMOTE_TREE}/phase1/calibration.py run --family {family} "
        f"--sims {lo}-{hi} --workers {workers} --batch {batch} "
        f"--state-dir {REMOTE_STATE}"
        + (f" --campaigns {campaigns}" if campaigns else ""))
    ssh_run(
        host, port,
        f"sudo systemctl stop {UNIT}.service 2>/dev/null; "
        f"sudo systemctl reset-failed {UNIT}.service 2>/dev/null; "
        f"mkdir -p {REMOTE_STATE} && "
        f"sudo systemd-run --quiet --unit={UNIT} --uid={SSH_USER} "
        f"--gid={SSH_USER} --working-directory={REMOTE_TREE} "
        f"--property=Restart=no {inner}")


def seed_checkpoint(host, port, family, blo, bhi):
    """Upload a previously pulled unit checkpoint so a batch reassigned
    to this host resumes instead of recomputing."""
    p = staged_ckpt(family, blo, bhi)
    if not p.exists() or p.stat().st_size == 0:
        return
    name = f"units_{batch_key(family, blo, bhi)}.jsonl"
    ssh_run(host, port,
            f"mkdir -p {REMOTE_STATE} && cat > {REMOTE_STATE}/{name}",
            stdin=p.read_text())
    log(f"[{host['name']}] seeded checkpoint "
        f"({p.stat().st_size // 1024} KiB) for {batch_key(family, blo, bhi)}")


# ----------------------------------------------------------------- monitor

def parse_json(text):
    try:
        return json.loads(text)
    except (json.JSONDecodeError, ValueError):
        return None


def probe(host, port, family, lo, hi):
    try:
        r = ssh_run(
            host, port,
            f"systemctl show {UNIT}.service --property=ActiveState,Result "
            f"2>/dev/null; echo @@@; "
            f"cat {REMOTE_STATE}/status_{family}_{lo}-{hi}.json 2>/dev/null; "
            f"echo",
            check=False)
    except OSError as e:                  # never let one host kill the poll
        return {"phase": "unreachable", "detail": str(e)[:200]}
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


def pull_checkpoint(host, port, family, blo, bhi):
    name = f"units_{batch_key(family, blo, bhi)}.jsonl"
    try:
        r = ssh_run(host, port, f"cat {REMOTE_STATE}/{name}", check=False)
    except OSError:                  # best-effort: the poll retries later
        return
    if r.returncode != 0 or not r.stdout:
        return
    p = staged_ckpt(family, blo, bhi)
    p.parent.mkdir(parents=True, exist_ok=True)
    if p.exists() and p.stat().st_size >= len(r.stdout):
        return                       # never regress the staged copy
    tmp = p.with_suffix(".tmp")
    tmp.write_text(r.stdout)
    tmp.rename(p)


def download_batch(host, port, family, blo, bhi):
    """Fetch a finished batch; only complete downloads are accepted."""
    key = batch_key(family, blo, bhi)
    d = batch_dir(family, blo, bhi)
    tmp = d.with_name(d.name + ".tmp")
    tmp.mkdir(parents=True, exist_ok=True)
    for pat in (f"summaries_{key}.jsonl", f"units_{key}.jsonl",
                f"status_{key}.json"):
        r = ssh_run(host, port, f"cat {REMOTE_STATE}/{pat}")
        (tmp / pat).write_text(r.stdout)
    r = ssh_run(host, port,
                f"cat {REMOTE_TREE}/phase1/validation_output_host.txt",
                check=False)
    (tmp / "validation_output_host.txt").write_text(r.stdout)
    (tmp / "computed_by.txt").write_text(f"{host['name']} {host['ipv4']}\n")
    n = sum(1 for _ in open(tmp / f"summaries_{key}.jsonl"))
    if n != bhi - blo:
        raise RuntimeError(
            f"{host['name']}: batch {key} claims done but summaries have "
            f"{n}/{bhi - blo} sims")
    if d.exists():
        for f in d.iterdir():
            f.unlink()
        d.rmdir()
    tmp.rename(d)


def batch_done_locally(family, blo, bhi):
    p = batch_dir(family, blo, bhi) / \
        f"summaries_{batch_key(family, blo, bhi)}.jsonl"
    if not p.exists():
        return False
    return sum(1 for _ in open(p)) == bhi - blo


# ------------------------------------------------------------ orchestration

def make_batches(lo, hi, batch):
    return [(b, min(b + batch, hi)) for b in range(lo, hi, batch)]


def load_assignments():
    if ASSIGN_FILE.exists():
        return {k: tuple(v) for k, v in
                json.loads(ASSIGN_FILE.read_text()).items()}
    return {}


def save_assignments(assign):
    ASSIGN_FILE.parent.mkdir(parents=True, exist_ok=True)
    ASSIGN_FILE.write_text(json.dumps(
        {k: list(v) for k, v in assign.items()}))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--family", required=True,
                    choices=["M0", "M1", "M4", "M5"])
    ap.add_argument("--sims", default="0-1000",
                    help="half-open sim index range LO-HI (default 0-1000, "
                         "the frozen stage-1 budget)")
    ap.add_argument("--hosts", type=int, default=30,
                    help="fleet size cap; the fleet is never larger than "
                         "the number of pending batches")
    ap.add_argument("--workers", type=int, default=16)
    ap.add_argument("--batch", type=int, default=16,
                    help="sims per batch = per work unit (kernel stream "
                         "batch); 8 feeds fleets larger than 63 hosts")
    ap.add_argument("--campaigns", default=None,
                    help="comma-separated campaign subset passed to the "
                         "shards -- SMOKE TESTS ONLY (a production family "
                         "run must scan all six campaigns); use a sim "
                         "range outside the 0-1000 stage-1 budget so the "
                         "partial results cannot be mistaken for it")
    ap.add_argument("--keep-infra", action="store_true",
                    help="skip the final terraform destroy")
    ap.add_argument("--keep-failed", action="store_true",
                    help="leave dead hosts up for inspection instead of "
                         "destroying them")
    args = ap.parse_args()
    lo, hi = (int(x) for x in args.sims.split("-"))

    r = subprocess.run(["git", "status", "--porcelain"], cwd=REPO,
                       capture_output=True, text=True)
    if r.stdout.strip():
        log("note: uncommitted changes present; hosts receive HEAD, "
            "not the working tree")

    if args.campaigns:
        log(f"WARNING: campaign subset {args.campaigns} -- smoke test "
            f"only; these results are NOT stage-1 calibration sims")

    batches = make_batches(lo, hi, args.batch)
    queue = [b for b in batches
             if not batch_done_locally(args.family, *b)]
    log(f"{len(batches)} batches of <={args.batch} sims, "
        f"{len(queue)} pending")
    if args.hosts > len(batches):
        log(f"note: --hosts {args.hosts} > {len(batches)} batches; a "
            f"smaller --batch would let more hosts contribute")

    # Fleet: keep hosts whose recorded assignment is still pending (they
    # hold checkpoints), then fill up to the cap with fresh ids.
    assign = load_assignments()          # host id -> (blo, bhi)
    assign = {k: v for k, v in assign.items()
              if tuple(v) in {tuple(b) for b in queue}}
    n_target = min(args.hosts, len(queue))
    ids = sorted(assign, key=int)[:n_target]
    nxt = 0
    while len(ids) < n_target:
        if str(nxt) not in ids:
            ids.append(str(nxt))
        nxt += 1
    if not queue:
        hosts = []
    else:
        log(f"Applying terraform for {len(ids)} host(s)...")
        hosts, port = ensure_fleet(ids)
        log(", ".join(f"{h['name']}={h['ipv4']}" for h in hosts))

    # Per-host runtime state: 'batch' (or None), strike/restart counters.
    for h in hosts:
        hid = str(h["index"])
        h["id"] = hid
        h["batch"] = assign.get(hid)
        h["strikes"] = 0
        h["restarts"] = 0
        h["alive"] = True
        h["ready"] = False
    if any(h["batch"] for h in hosts):
        for h in hosts:
            if h["batch"]:
                log(f"  {h['name']}: resuming batch "
                    f"{batch_key(args.family, *h['batch'])}")
    queued = [b for b in queue
              if tuple(b) not in {tuple(h["batch"]) for h in hosts
                                  if h["batch"]}]
    attempts = {tuple(b): 0 for b in queue}

    def prepare(host):
        try:
            log(f"[{host['name']}] waiting for cloud-init...")
            wait_cloud_init(host, port)
            push_code(host, port)
            setup_host(host, port)
        except Exception as e:            # dead on arrival: reap below
            log(f"[{host['name']}] setup FAILED: {e}")
            host["alive"] = False

    # Setup runs in background threads and each host is dispatched (or,
    # for a resumed batch, polled) as soon as its OWN gate passes -- no
    # fleet-wide barrier. At 99 hosts a barrier left the whole fleet
    # idle ~45 min behind the slowest setup. Daemon threads so an abort
    # never blocks process exit on an in-flight setup.
    prep_sem = threading.Semaphore(SETUP_PARALLEL)

    def prepare_async(host):
        with prep_sem:
            if host["alive"]:
                prepare(host)
                if host["alive"]:
                    host["ready"] = True

    for h in hosts:
        threading.Thread(target=prepare_async, args=(h,),
                         daemon=True).start()

    kept_failed = []                      # ids kept up via --keep-failed
    replacements_left = 2 * max(args.hosts, 1)
    next_id = max([int(h["id"]) for h in hosts], default=-1) + 1
    polls = 0
    n_downloaded = len(batches) - len(queue)

    def requeue(host, reason):
        b = host["batch"]
        host["batch"] = None
        host["alive"] = False
        if b:
            attempts[tuple(b)] += 1
            if attempts[tuple(b)] >= BATCH_ATTEMPTS_MAX:
                raise RuntimeError(
                    f"batch {batch_key(args.family, *b)} failed on "
                    f"{BATCH_ATTEMPTS_MAX} hosts; aborting (systematic "
                    f"failure, not host weather)")
            queued.insert(0, b)
        log(f"[{host['name']}] {reason}; "
            + (f"requeued {batch_key(args.family, *b)}" if b else
               "no batch assigned"))

    while True:
        # -------- dispatch: idle live hosts pull from the queue
        for h in hosts:
            if h["alive"] and h["ready"] and h["batch"] is None and queued:
                b = queued.pop(0)
                try:
                    seed_checkpoint(h, port, args.family, *b)
                    start_job(h, port, args.family, b[0], b[1],
                              args.workers, args.batch, args.campaigns)
                except subprocess.CalledProcessError as e:
                    queued.insert(0, b)
                    h["strikes"] += 1
                    log(f"[{h['name']}] dispatch failed "
                        f"({str(e)[:120]}); will retry")
                    continue
                h["batch"] = b
                h["restarts"] = 0
                h["strikes"] = 0
                log(f"[{h['name']}] started "
                    f"{batch_key(args.family, *b)}")
        save_assignments({h["id"]: h["batch"] for h in hosts
                          if h["alive"] and h["batch"]})

        # -------- retire: idle hosts with nothing to do, and dead hosts
        for h in hosts:                  # e.g. setup failed mid-resume
            if not h["alive"] and h["batch"]:
                requeue(h, "host died holding a batch")
        drop = [h for h in hosts
                if (not h["alive"]) or (h["batch"] is None and not queued)]
        if drop:
            for h in drop:
                if not h["alive"] and args.keep_failed:
                    kept_failed.append(h["id"])
                    log(f"[{h['name']}] dead; kept up (--keep-failed)")
                else:
                    log(f"[{h['name']}] "
                        + ("dead; destroying"
                           if not h["alive"] else "idle; destroying"))
            hosts = [h for h in hosts if h not in drop]
            keep = [h["id"] for h in hosts] + kept_failed
            if keep:
                ensure_fleet(keep)
            else:
                maybe_destroy()

        # -------- replace: requeued work with nobody idle gets a fresh VM
        if queued:
            idle = sum(1 for h in hosts
                       if h["alive"] and h["batch"] is None)
            need = min(len(queued) - idle, args.hosts - len(hosts),
                       replacements_left)
            if need > 0:
                new_ids = [str(next_id + k) for k in range(need)]
                next_id += need
                replacements_left -= need
                log(f"spawning {need} replacement host(s): "
                    + ", ".join(new_ids))
                all_hosts, port = ensure_fleet(
                    [h["id"] for h in hosts] + kept_failed + new_ids)
                fresh = [dict(h, id=str(h["index"]), batch=None,
                              strikes=0, restarts=0, alive=True,
                              ready=False)
                         for h in all_hosts
                         if str(h["index"]) in new_ids]
                for h in fresh:
                    threading.Thread(target=prepare_async, args=(h,),
                                     daemon=True).start()
                hosts.extend(fresh)

        if not hosts:
            if queued:
                raise RuntimeError(
                    f"{len(queued)} batches pending, no live hosts, and "
                    f"the replacement budget is exhausted; rerun to "
                    f"retry with a fresh fleet")
            break

        time.sleep(POLL_SECONDS)
        polls += 1

        # -------- poll running hosts (concurrently: a serial cycle over
        # a large fleet costs minutes and lets one slow host delay
        # everyone's dispatch)
        # Not-yet-ready hosts are excluded even when resuming a batch:
        # their shard keeps running on-host regardless, and polling one
        # mid-setup could race a unit restart against a kernel rebuild.
        active = [h for h in hosts
                  if h["alive"] and h["ready"] and h["batch"]]
        if active:
            with ThreadPoolExecutor(
                    max_workers=min(PROBE_PARALLEL, len(active))) as pool:
                states = list(pool.map(
                    lambda h: probe(h, port, args.family, *h["batch"]),
                    active))
        else:
            states = []
        progress = []                    # (host, done, total, elapsed_s)
        to_pull = []                     # (host, batch) checkpoint pulls
        for h, st in zip(active, states):
            b = h["batch"]
            if st["phase"] == "done":
                try:
                    download_batch(h, port, args.family, b[0], b[1])
                except (subprocess.CalledProcessError, RuntimeError,
                        OSError) as e:
                    h["strikes"] += 1
                    log(f"[{h['name']}] download failed ({e}); retrying")
                    if h["strikes"] >= UNREACHABLE_LIMIT:
                        requeue(h, "download kept failing")
                    continue
                n_downloaded += 1
                log(f"[{h['name']}] {batch_key(args.family, *b)} done, "
                    f"downloaded ({n_downloaded}/{len(batches)}; "
                    f"{len(queued)} queued)")
                staged_ckpt(args.family, *b).unlink(missing_ok=True)
                h["batch"] = None
                h["strikes"] = 0
            elif st["phase"] == "running":
                h["strikes"] = 0
                s = st.get("status") or {}
                if s.get("units_total"):
                    progress.append(
                        (h, s.get("units_done", 0), s["units_total"],
                         s.get("elapsed_s", 0)))
                if polls % CKPT_PULL_EVERY == 0:
                    to_pull.append((h, b))
            elif st["phase"] in ("failed", "missing"):
                h["strikes"] += 1
                if st["phase"] == "failed" or h["strikes"] >= MISSING_LIMIT:
                    if h["restarts"] < MAX_RESTARTS:
                        h["restarts"] += 1
                        h["strikes"] = 0
                        log(f"[{h['name']}] unit died "
                            f"({st.get('detail', 'no status')}); restart "
                            f"{h['restarts']}/{MAX_RESTARTS} (resumes "
                            f"from checkpoint)")
                        try:
                            start_job(h, port, args.family, b[0], b[1],
                                      args.workers, args.batch,
                                      args.campaigns)
                        except subprocess.CalledProcessError:
                            requeue(h, "restart failed")
                    else:
                        pull_checkpoint(h, port, args.family, b[0], b[1])
                        requeue(h, "unit kept dying")
            elif st["phase"] == "unreachable":
                h["strikes"] += 1
                if h["strikes"] % 10 == 0:
                    log(f"[{h['name']}] unreachable "
                        f"({h['strikes']}/{UNREACHABLE_LIMIT})")
                if h["strikes"] >= UNREACHABLE_LIMIT:
                    requeue(h, "unreachable too long")

        # -------- fleet summary every poll; per-host detail (and the
        # checkpoint pulls, which are the bulky transfers) less often
        if progress:
            done_u = sum(p[1] for p in progress)
            tot_u = sum(p[2] for p in progress)
            log(f"fleet: {len(progress)} running {done_u}/{tot_u} units, "
                f"{n_downloaded}/{len(batches)} batches downloaded, "
                f"{len(queued)} queued")
        if polls % CKPT_PULL_EVERY == 0:
            for h, done_u, tot_u, el in progress:
                log(f"[{h['name']}] {batch_key(args.family, *h['batch'])}: "
                    f"{done_u}/{tot_u} units ({el / 3600:.1f} h)")
        if to_pull:
            with ThreadPoolExecutor(
                    max_workers=min(PROBE_PARALLEL, len(to_pull))) as pool:
                list(pool.map(
                    lambda hb: pull_checkpoint(hb[0], port, args.family,
                                               *hb[1]),
                    to_pull))

    missing = [b for b in batches
               if not batch_done_locally(args.family, *b)]
    if missing:
        log(f"{len(missing)} batches incomplete; rerun to finish: "
            + ", ".join(batch_key(args.family, *b) for b in missing[:5]))
        sys.exit(1)

    log("All batches done; collating...")
    dirs = ",".join(str(batch_dir(args.family, *b)) for b in batches)
    subprocess.run(
        ["uv", "run", "python", str(REPO / "phase1" / "calibration.py"),
         "collate", "--state-dirs", dirs,
         "--out", str(STATE_DIR / f"calibration_{args.family}.json")],
        cwd=REPO, check=True)
    if args.keep_infra:
        log("--keep-infra set, skipping destroy")
    elif kept_failed:
        log(f"{len(kept_failed)} failed host(s) kept up for inspection; "
            f"destroy with: terraform -chdir={INFRA_DIR} destroy")
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
