"""Section 6.2 study-wide false-alarm calibration (prereg_h1.md, frozen
at prereg-h1-v1.0; execution spec in phase1/CALIBRATION_PLAN.md).

For each natural null family F in {M0, M1, M4, M5}:
  1. fit F to each confirmatory source-campaign pair (real event data;
     post-tag, as the prereg specifies);
  2. draw per-simulation parameter sets from the Laplace approximation at
     the fit (truncated at the frozen parameter bounds);
  3. simulate event streams through the real (barycentred) window
     functions;
  4. rerun the complete frozen search -- all six campaigns, M2 and M3,
     full grids, identical optimizer -- on each simulation and record its
     study-wide maximum Lambda.

FAP_F = fraction of F-simulations with max Lambda >= Lambda*; the
confirmatory FAP is max_F FAP_F. Staged budget: 1,000 sims/family, stop
if Lambda* falls below any family's 99th percentile, else extend.

This module is cluster-agnostic: `run` executes any sim range on local
workers, so a single machine can replicate any subset exactly (per-sim
streams are deterministic functions of (family, campaign, sim index)
alone -- independent of batching, worker count, host, or execution
order). The cluster layer (cluster/run.py) only distributes sim ranges.

Inputs: phase1/calibration_inputs/ (committed constructed events +
barycentred windows; no data/raw or astropy needed) and
phase1/null_fits.json (committed output of `fit-nulls`).

Subcommands:
  fit-nulls                       fit all families x campaigns, write
                                  phase1/null_fits.json
  run --family M4 --sims 0-99     execute simulations (resumable;
      [--workers N] [--batch S]   unit checkpoint + per-sim summaries
      [--state-dir DIR]           under the state dir)
  collate [--state-dirs D1,D2,..] merge summaries, compute FAP table and
                                  the frozen stop-rule report
"""

import argparse
import csv
import hashlib
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pipeline as pl        # noqa: E402
import scankernel as sk      # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
INPUTS_DIR = ROOT / "phase1" / "calibration_inputs"
NULL_FITS = ROOT / "phase1" / "null_fits.json"
RESULTS = ROOT / "phase1" / "confirmatory_results.json"
DEFAULT_STATE = ROOT / "phase1" / "calibration_state"

# Frozen search configuration -- MUST equal phase1/confirmatory.py FULL
# (asserted by scripts/validate_fastscan.py remaining the shared gate and
# by the CALIBRATION_PLAN cross-reference).
FULL = dict(p_min=1.0 / 24.0, sigma_min=60.0 / pl.DAY_S,
            tau_grid=pl.frozen_tau_grid(),
            m1_kw=dict(n_periods=200, n_phase=24))

# Execution spec constants (CALIBRATION_PLAN.md; fixed before any
# production simulation).
SEED_ROOT = 20260811
FAMILIES = ("M0", "M1", "M4", "M5")
FAMILY_ID = {"M0": 0, "M1": 1, "M4": 4, "M5": 5}
CAMPAIGNS = ["fast20201124A_sepoct", "nancay20220912A",
             "astroflash20220912A", "tmrt20240114A",
             "effelsberg20200120E", "fast20240114A"]
CAMP_ID = {c: i for i, c in enumerate(CAMPAIGNS)}
DEFAULT_BATCH = 16          # sims per batched kernel call / unit
# Cost-based unit chunking: an octave's period grid is split per model
# into ceil(n_f * t_hi_d * MODEL_W / CHUNK_COST_PD) in-order chunks, so
# every unit costs roughly the same wall time (~0.5-1 vCPU-h at batch 16
# on cpx51) regardless of octave. Scan cost per period scales ~ with the
# octave period (t0 cells ~ T/sigma) and M3 is ~5x M2 (tau grid).
CHUNK_COST_PD = 780_000.0   # period-days per chunk, / model weight
MODEL_W = {"M2": 1.0, "M3": 5.0}
LAPLACE_STD_CAP = 5.0       # curvature floor: std <= 5 FD steps along
                            # any eigendirection (see CALIBRATION_PLAN)
DRAW_MAX_TRIES = 200


# ------------------------------------------------------------- inputs

_INPUTS = None


def load_inputs():
    global _INPUTS
    if _INPUTS is None:
        with open(INPUTS_DIR / "INPUTS.json") as f:
            manifest = json.load(f)
        data = {}
        for name in CAMPAIGNS:
            m = manifest["campaigns"][name]
            with open(INPUTS_DIR / m["events_file"], newline="") as f:
                t = np.array([float(r["toa_mjd_bary"])
                              for r in csv.DictReader(f)])
            with open(INPUTS_DIR / m["windows_file"], newline="") as f:
                rows = list(csv.DictReader(f))
            a = np.array([float(r["mjd_start_bary"]) for r in rows])
            b = np.array([float(r["mjd_end_bary"]) for r in rows])
            assert len(t) == m["n_events"] and len(a) == m["n_sessions"]
            data[name] = (np.sort(t), (a, b))
        _INPUTS = (manifest, data)
    return _INPUTS


def lambda_star():
    with open(RESULTS) as f:
        return float(json.load(f)["study_wide"]["lambda_star"])


# ---------------------------------------------------------- null fits
#
# Parameterizations (z = transformed coordinates for the Laplace step):
#   M0: z = [ln lam]                        analytic: var(ln lam) = 1/N
#   M1: z = [ln P_a, delta, t0_frac, ln lam_in, ln lam_out]
#   M4: z = [ln k, ln r]
#   M5: z = [ln alpha, ln beta]
# FD Hessian of -ll(z) at the MLE, symmetrized, eigenvalues floored so
# that no eigendirection has std > LAPLACE_STD_CAP x its FD step
# (grid-profiled structural directions are locally flat, so raw FD
# curvature there is meaningless; the floor pins their spread to the
# frozen grid resolution instead of letting a near-singular Hessian
# explode the draw). Draws are truncated at the frozen bounds by
# resampling (<= DRAW_MAX_TRIES, then clipping).


def m1_ll_explicit(t, win, P, delta, t0_abs, lin, lout):
    iv = [(0.0, delta * P)]
    e_in = pl.periodic_overlap(win, P, t0_abs, iv)
    n_in, _ = pl.counts_in(t, P, t0_abs, iv)
    e_tot = pl.live_time(win)
    n_out = len(t) - n_in
    e_out = e_tot - e_in
    ll = 0.0
    ll += n_in * np.log(max(lin, 1e-300)) - lin * e_in if n_in else -lin * e_in
    ll += (n_out * np.log(max(lout, 1e-300)) - lout * e_out
           if n_out else -lout * e_out)
    return ll


def m4_fit_full(t, win):
    from scipy.optimize import minimize
    n = len(t)
    r0 = n / pl.live_time(win)
    best = (-np.inf, None)
    for k0 in (0.3, 0.7, 1.0):
        for rm in (0.5, 1.0, 2.0):
            res = minimize(
                lambda p: -pl.m4_ll(t, win, np.clip(p[0], 0.05, 5.0),
                                    max(p[1], 1e-8)),
                x0=[k0, r0 * rm], method="Nelder-Mead",
                options={"maxiter": 300, "fatol": 1e-6})
            if -res.fun > best[0]:
                best = (-res.fun,
                        (float(np.clip(res.x[0], 0.05, 5.0)),
                         float(max(res.x[1], 1e-8))))
    return best


def m5_fit_full(t, win):
    from scipy.optimize import minimize
    rate = len(t) / pl.live_time(win)
    best = (-np.inf, None)
    for a0 in (0.3, 1.0, 3.0):
        res = minimize(
            lambda p: -pl.m5_ll(t, win, max(p[0], 1e-4), max(p[1], 1e-10)),
            x0=[a0, rate / a0], method="Nelder-Mead",
            options={"maxiter": 400, "fatol": 1e-6})
        if -res.fun > best[0]:
            best = (-res.fun,
                    (float(max(res.x[0], 1e-4)),
                     float(max(res.x[1], 1e-10))))
    return best


def fd_hessian(f, z0, steps):
    k = len(z0)
    H = np.zeros((k, k))
    f0 = f(z0)
    for i in range(k):
        ei = np.zeros(k)
        ei[i] = steps[i]
        H[i, i] = (f(z0 + ei) - 2 * f0 + f(z0 - ei)) / steps[i] ** 2
        for j in range(i + 1, k):
            ej = np.zeros(k)
            ej[j] = steps[j]
            H[i, j] = H[j, i] = (
                f(z0 + ei + ej) - f(z0 + ei - ej)
                - f(z0 - ei + ej) + f(z0 - ei - ej)
            ) / (4 * steps[i] * steps[j])
    return H


def laplace_cov(negll, z0, steps):
    """Covariance = floored inverse FD Hessian of -ll at the MLE."""
    H = fd_hessian(negll, np.asarray(z0, float), np.asarray(steps, float))
    H = 0.5 * (H + H.T)
    vals, vecs = np.linalg.eigh(H)
    floor = 1.0 / (LAPLACE_STD_CAP * float(np.max(steps))) ** 2
    vals = np.maximum(vals, floor)
    return (vecs * (1.0 / vals)) @ vecs.T


def fit_family(family, t, win):
    e_tot = pl.live_time(win)
    n = len(t)
    span = float(win[1][-1] - win[0][0])
    if family == "M0":
        lam = n / e_tot
        return {"ll": pl.m0_ll(t, win),
                "z": [float(np.log(lam))],
                "cov": [[1.0 / max(n, 1)]],
                "params": {"lam": lam}}
    if family == "M1":
        ll, arg = pl.m1_scan(t, win, span, FULL["p_min"], **FULL["m1_kw"])
        P, delta, frac = arg
        t0_abs = float(win[0][0]) + frac * P
        iv = [(0.0, delta * P)]
        e_in = pl.periodic_overlap(win, P, t0_abs, iv)
        n_in, _ = pl.counts_in(t, P, t0_abs, iv)
        n_out, e_out = n - n_in, e_tot - e_in
        lin = n_in / e_in if e_in > 0 else 0.0
        lout = n_out / e_out if e_out > 0 else 0.0
        z0 = [np.log(P), delta, frac,
              np.log(max(lin, 1e-12)), np.log(max(lout, 1e-12))]
        p_max = span / 3.0
        steps = [np.log(p_max / FULL["p_min"]) / (2 * FULL["m1_kw"]["n_periods"]),
                 0.025, 1.0 / (2 * FULL["m1_kw"]["n_phase"]),
                 1e-3, 1e-3]

        def negll(z):
            return -m1_ll_explicit(
                t, win, float(np.exp(z[0])),
                float(np.clip(z[1], 0.05, 0.95)),
                float(win[0][0]) + (z[2] % 1.0) * float(np.exp(z[0])),
                float(np.exp(z[3])), float(np.exp(z[4])))

        cov = laplace_cov(negll, z0, steps)
        return {"ll": float(ll), "z": [float(x) for x in z0],
                "cov": cov.tolist(),
                "params": {"P_a": P, "delta": delta, "t0_frac": frac,
                           "lam_in": lin, "lam_out": lout,
                           "n_in": int(n_in), "n_out": int(n_out)}}
    if family == "M4":
        ll, (k, r) = m4_fit_full(t, win)
        z0 = [np.log(k), np.log(r)]
        steps = [0.02, 0.02]
        cov = laplace_cov(
            lambda z: -pl.m4_ll(t, win,
                                float(np.clip(np.exp(z[0]), 0.05, 5.0)),
                                float(max(np.exp(z[1]), 1e-8))),
            z0, steps)
        return {"ll": float(ll), "z": [float(x) for x in z0],
                "cov": cov.tolist(), "params": {"k": k, "r": r}}
    if family == "M5":
        ll, (alpha, beta) = m5_fit_full(t, win)
        z0 = [np.log(alpha), np.log(beta)]
        steps = [0.02, 0.02]
        cov = laplace_cov(
            lambda z: -pl.m5_ll(t, win,
                                float(max(np.exp(z[0]), 1e-4)),
                                float(max(np.exp(z[1]), 1e-10))),
            z0, steps)
        return {"ll": float(ll), "z": [float(x) for x in z0],
                "cov": cov.tolist(),
                "params": {"alpha": alpha, "beta": beta}}
    raise ValueError(family)


def cmd_fit_nulls(args):
    manifest, data = load_inputs()
    out = {"generated_utc": datetime.now(timezone.utc).isoformat(
               timespec="seconds"),
           "seed_root": SEED_ROOT,
           "inputs_sha256": {n: manifest["campaigns"][n]["events_sha256"]
                             for n in CAMPAIGNS},
           "laplace": {"std_cap_steps": LAPLACE_STD_CAP,
                       "draw_max_tries": DRAW_MAX_TRIES},
           "fits": {}}
    for name in CAMPAIGNS:
        t, win = data[name]
        out["fits"][name] = {}
        for fam in FAMILIES:
            t0c = time.time()
            fit = fit_family(fam, t, win)
            fit["fit_walltime_s"] = round(time.time() - t0c, 1)
            out["fits"][name][fam] = fit
            print(f"{name} {fam}: ll={fit['ll']:.3f} "
                  f"params={fit['params']}", flush=True)
    with open(NULL_FITS, "w") as f:
        json.dump(out, f, indent=1)
    print(f"written: {NULL_FITS}")


# ------------------------------------------------------- simulation

_FITS = None


def load_fits():
    global _FITS
    if _FITS is None:
        with open(NULL_FITS) as f:
            _FITS = json.load(f)
    return _FITS


def in_bounds(family, p, span):
    if family == "M0":
        return p["lam"] > 0
    if family == "M1":
        return (FULL["p_min"] <= p["P_a"] <= span / 3.0
                and 0.05 <= p["delta"] <= 0.95
                and p["lam_in"] > p["lam_out"] >= 0)
    if family == "M4":
        return 0.05 <= p["k"] <= 5.0 and p["r"] > 0
    if family == "M5":
        return p["alpha"] > 0 and p["beta"] > 0
    raise ValueError(family)


def z_to_params(family, z):
    if family == "M0":
        return {"lam": float(np.exp(z[0]))}
    if family == "M1":
        return {"P_a": float(np.exp(z[0])), "delta": float(z[1]),
                "t0_frac": float(z[2] % 1.0),
                "lam_in": float(np.exp(z[3])),
                "lam_out": float(np.exp(z[4]))}
    if family == "M4":
        return {"k": float(np.exp(z[0])), "r": float(np.exp(z[1]))}
    if family == "M5":
        return {"alpha": float(np.exp(z[0])), "beta": float(np.exp(z[1]))}
    raise ValueError(family)


def clip_params(family, p, span):
    if family == "M1":
        p["P_a"] = float(np.clip(p["P_a"], FULL["p_min"], span / 3.0))
        p["delta"] = float(np.clip(p["delta"], 0.05, 0.95))
        if p["lam_in"] <= p["lam_out"]:
            p["lam_in"] = p["lam_out"] * 1.0000001 + 1e-12
    if family == "M4":
        p["k"] = float(np.clip(p["k"], 0.05, 5.0))
    return p


def draw_stream(family, campaign, sim):
    """Deterministic simulated stream for (family, campaign, sim):
    parameter draw from the Laplace fit, then one event stream through
    the real windows. Independent of batching/workers/host."""
    _, data = load_inputs()
    fits = load_fits()
    t_real, win = data[campaign]
    span = float(win[1][-1] - win[0][0])
    fit = fits["fits"][campaign][family]
    rng = np.random.default_rng(
        [SEED_ROOT, FAMILY_ID[family], CAMP_ID[campaign], sim])
    z0 = np.asarray(fit["z"], float)
    cov = np.asarray(fit["cov"], float)
    params = None
    for _ in range(DRAW_MAX_TRIES):
        z = rng.multivariate_normal(z0, cov, method="cholesky")
        cand = z_to_params(family, z)
        # zero-rate edge (e.g. n_out = 0): the MLE itself, kept fixed
        if family == "M1" and fit["params"]["n_out"] == 0:
            cand["lam_out"] = 0.0
        if in_bounds(family, cand, span):
            params = cand
            break
    if params is None:
        params = clip_params(family, z_to_params(family, z), span)
    if family == "M0":
        t = pl.sim_m0(rng, win, params["lam"])
    elif family == "M1":
        P = params["P_a"]
        t0_abs = float(win[0][0]) + params["t0_frac"] * P
        t = pl.sim_periodic(rng, win, P, t0_abs,
                            [(0.0, params["delta"] * P)],
                            params["lam_in"], params["lam_out"])
    elif family == "M4":
        t = pl.sim_m4(rng, win, params["k"], params["r"])
    else:
        t = pl.sim_m5(rng, win, params["alpha"], params["beta"])
    return np.sort(np.asarray(t, float)), params


# ------------------------------------------------------------ scanning

def octave_layout(span):
    _, octaves = pl.scanner_grids(span, FULL["p_min"], FULL["sigma_min"],
                                  detail=True)
    return octaves


def n_chunks_for(o, model):
    return max(1, int(np.ceil(len(o["f"]) * o["t_hi_d"] * MODEL_W[model]
                              / CHUNK_COST_PD)))


_STREAMS = {}


def cached_stream(family, campaign, sim):
    """Per-process stream cache: unit workers repeatedly need the same
    (family, campaign, sim) streams (identical across units by
    construction); regeneration (notably M4's sequential renewal draw on
    the FAST campaign) is worth caching."""
    key = (family, campaign, sim)
    if key not in _STREAMS:
        if len(_STREAMS) > 64:
            _STREAMS.clear()
        _STREAMS[key] = draw_stream(family, campaign, sim)[0]
    return _STREAMS[key]


def run_unit(args):
    """Worker: one checkpoint unit over a batch of sims.
    args = (family, campaign, kind, oct_idx, model_chunk, sim_lo, sim_hi).
    kind: "natural" or "chunk". Returns (args, per-sim value list)."""
    family, campaign, kind, oct_idx, model_chunk, lo, hi = args
    _, data = load_inputs()
    _t_real, win = data[campaign]
    span = float(win[1][-1] - win[0][0])
    streams = [cached_stream(family, campaign, s) for s in range(lo, hi)]
    t0c = time.time()
    if kind == "natural":
        vals = []
        for t in streams:
            ll0 = pl.m0_ll(t, win)
            ll1, _ = pl.m1_scan(t, win, span, FULL["p_min"],
                                **FULL["m1_kw"])
            ll4 = pl.m4_fit(t, win)
            ll5 = pl.m5_fit(t, win)
            vals.append({"ll_m0": float(ll0), "ll_m1": float(ll1),
                         "ll_m4": float(ll4), "ll_m5": float(ll5),
                         "n_events": int(len(t))})
        return args, {"sims": vals,
                      "walltime_s": round(time.time() - t0c, 1)}
    model, part = model_chunk.split("/")
    c, n_chunks = (int(x) for x in part.split("of"))
    o = octave_layout(span)[oct_idx]
    assert n_chunks == n_chunks_for(o, model), "chunk layout drift"
    sub = np.array_split(1.0 / o["f"], n_chunks)[c]
    orig = pl.scanner_grids
    try:
        pl.scanner_grids = (lambda *a_, _p=sub, **k_: [_p])
        res = sk.scan_scanner_batch(
            streams, win, span, FULL["p_min"], FULL["sigma_min"],
            paired=(model == "M3"),
            tau_grid=FULL["tau_grid"] if model == "M3" else None)
    finally:
        pl.scanner_grids = orig
    vals = [{"ll": float(r[0]), "arg": list(r[1]) if r[1] else None}
            for r in res]
    return args, {"sims": vals,
                  "walltime_s": round(time.time() - t0c, 1)}


class Ckpt:
    """Append-only JSONL checkpoint; parent process is the sole writer."""

    def __init__(self, path):
        self.path = Path(path)
        self.done = {}
        if self.path.exists():
            with open(self.path) as f:
                for line in f:
                    k, v = json.loads(line)
                    self.done[tuple(k)] = v
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.f = open(self.path, "a")

    def record(self, key, value):
        self.done[tuple(key)] = value
        self.f.write(json.dumps([list(key), value]) + "\n")
        self.f.flush()


def pending_units(family, campaigns, sim_lo, sim_hi, batch, done):
    units = []
    _, data = load_inputs()
    for campaign in campaigns:
        _t, win = data[campaign]
        span = float(win[1][-1] - win[0][0])
        layout = octave_layout(span)
        for blo in range(sim_lo, sim_hi, batch):
            bhi = min(blo + batch, sim_hi)
            key = (family, campaign, "natural", -1, "-", blo, bhi)
            if key not in done:
                units.append((key, 0.0))
            for i, o in enumerate(layout):
                for model in ("M2", "M3"):
                    n_chunks = n_chunks_for(o, model)
                    for c in range(n_chunks):
                        key = (family, campaign, "chunk", i,
                               f"{model}/{c}of{n_chunks}", blo, bhi)
                        if key in done:
                            continue
                        est = (len(o["f"]) / n_chunks) * o["t_hi_d"] \
                            * MODEL_W[model]
                        units.append((key, est))
    units.sort(key=lambda u: -u[1])
    return [u[0] for u in units]


def assemble_sims(family, campaigns, sim_lo, sim_hi, batch, done):
    """Per-sim summaries from completed units. Chunk results combine in
    chunk order with strict '>' (first-in-scan-order argmax parity)."""
    _, data = load_inputs()
    out = []
    for s in range(sim_lo, sim_hi):
        blo = sim_lo + ((s - sim_lo) // batch) * batch
        bhi = min(blo + batch, sim_hi)
        k = s - blo
        summary = {"family": family, "sim": s, "campaigns": {}}
        complete = True
        for campaign in campaigns:
            _t, win = data[campaign]
            span = float(win[1][-1] - win[0][0])
            nat_key = (family, campaign, "natural", -1, "-", blo, bhi)
            if nat_key not in done:
                complete = False
                break
            nat = done[nat_key]["sims"][k]
            lls = {"M2": -np.inf, "M3": -np.inf}
            args = {"M2": None, "M3": None}
            for i, o in enumerate(octave_layout(span)):
                for model in ("M2", "M3"):
                    n_chunks = n_chunks_for(o, model)
                    for c in range(n_chunks):
                        key = (family, campaign, "chunk", i,
                               f"{model}/{c}of{n_chunks}", blo, bhi)
                        if key not in done:
                            complete = False
                            break
                        v = done[key]["sims"][k]
                        if v["ll"] > lls[model]:
                            lls[model] = v["ll"]
                            args[model] = v["arg"]
                    if not complete:
                        break
                if not complete:
                    break
            if not complete:
                break
            nat_max = max(nat["ll_m0"], nat["ll_m1"], nat["ll_m4"],
                          nat["ll_m5"])
            lam = 2.0 * (max(lls["M2"], lls["M3"]) - nat_max)
            summary["campaigns"][campaign] = {
                "lambda": lam, "n_events": nat["n_events"],
                "ll": {"M0": nat["ll_m0"], "M1": nat["ll_m1"],
                       "M2": lls["M2"], "M3": lls["M3"],
                       "M4": nat["ll_m4"], "M5": nat["ll_m5"]},
                "m2_arg": args["M2"], "m3_arg": args["M3"]}
        if not complete:
            continue
        lam_max = max(v["lambda"] for v in summary["campaigns"].values())
        summary["study_wide_max_lambda"] = lam_max
        out.append(summary)
    return out


def cmd_run(args):
    from concurrent.futures import ProcessPoolExecutor, as_completed
    lo, hi = (int(x) for x in args.sims.split("-"))
    hi += 1 if args.inclusive else 0
    campaigns = (args.campaigns.split(",") if args.campaigns
                 else list(CAMPAIGNS))
    for c in campaigns:
        assert c in CAMPAIGNS, f"unknown campaign {c}"
    assert args.family in FAMILIES
    state = Path(args.state_dir)
    state.mkdir(parents=True, exist_ok=True)
    ckpt = Ckpt(state / f"units_{args.family}_{lo}-{hi}.jsonl")
    status_path = state / f"status_{args.family}_{lo}-{hi}.json"

    units = pending_units(args.family, campaigns, lo, hi, args.batch,
                          ckpt.done)
    total_units = len(units) + len(ckpt.done)
    print(f"[{args.family} sims {lo}..{hi - 1}] campaigns="
          f"{len(campaigns)} pending_units={len(units)} "
          f"workers={args.workers} batch={args.batch}", flush=True)

    t0c = time.time()

    def write_status(n_done, phase):
        status_path.write_text(json.dumps({
            "family": args.family, "sim_lo": lo, "sim_hi": hi,
            "phase": phase, "units_done": n_done,
            "units_total": total_units,
            "elapsed_s": round(time.time() - t0c, 1),
            "updated_utc": datetime.now(timezone.utc).isoformat(
                timespec="seconds")}))

    if units:
        with ProcessPoolExecutor(max_workers=args.workers) as ex:
            futs = {ex.submit(run_unit, u): u for u in units}
            n_done = len(ckpt.done)
            for fut in as_completed(futs):
                key, val = fut.result()
                ckpt.record(key, val)
                n_done += 1
                if n_done % 10 == 0 or n_done == total_units:
                    write_status(n_done, "scanning")
                print(f"[unit {n_done}/{total_units}] "
                      f"{key[1]} {key[2]} oct={key[3]} {key[4]} "
                      f"sims={key[5]}-{key[6] - 1} "
                      f"wall={val['walltime_s']:.0f}s", flush=True)

    summaries = assemble_sims(args.family, campaigns, lo, hi, args.batch,
                              ckpt.done)
    with open(state / f"summaries_{args.family}_{lo}-{hi}.jsonl",
              "w") as f:
        for s in summaries:
            f.write(json.dumps(s) + "\n")
    write_status(total_units, "done")
    lams = [s["study_wide_max_lambda"] for s in summaries]
    print(f"[{args.family}] {len(summaries)} sims complete; "
          f"max-Lambda quartiles: "
          f"{np.percentile(lams, [25, 50, 75, 99]).round(2).tolist()}"
          if lams else "no complete sims", flush=True)


def cmd_collate(args):
    state_dirs = ([Path(d) for d in args.state_dirs.split(",")]
                  if args.state_dirs else [DEFAULT_STATE])
    lam_star_v = lambda_star()
    per_family = {f: {} for f in FAMILIES}
    for d in state_dirs:
        for p in sorted(Path(d).glob("summaries_*.jsonl")):
            with open(p) as f:
                for line in f:
                    s = json.loads(line)
                    per_family[s["family"]][s["sim"]] = \
                        s["study_wide_max_lambda"]
    out = {"generated_utc": datetime.now(timezone.utc).isoformat(
               timespec="seconds"),
           "lambda_star": lam_star_v,
           "prereg": "prereg_h1.md Section 6.2 (conservative-maximum "
                     "rule; staged budget)",
           "families": {}}
    for fam in FAMILIES:
        sims = per_family[fam]
        if not sims:
            continue
        lams = np.array([sims[k] for k in sorted(sims)])
        n = len(lams)
        n_ge = int(np.sum(lams >= lam_star_v))
        fap = n_ge / n
        p99 = float(np.percentile(lams, 99)) if n >= 100 else None
        out["families"][fam] = {
            "n_sims": n, "n_ge_lambda_star": n_ge, "fap": fap,
            "percentiles": {str(q): float(np.percentile(lams, q))
                            for q in (50, 90, 99, 99.9)},
            "stage1_complete": n >= 1000,
            "stop_rule_triggered": bool(
                n >= 1000 and p99 is not None and p99 > lam_star_v),
        }
        print(f"{fam}: n={n} FAP_F={fap:.4f} "
              f"P99={p99 if p99 is None else round(p99, 2)} "
              f"stop={out['families'][fam]['stop_rule_triggered']}")
    if out["families"]:
        complete = [f for f in out["families"]
                    if out["families"][f]["stage1_complete"]]
        out["fap_conservative_max"] = (
            max(out["families"][f]["fap"] for f in complete)
            if complete else None)
        out["stop_rule"] = ("stop: Lambda* below the 99th percentile of "
                            "at least one completed family"
                            if any(out["families"][f]["stop_rule_triggered"]
                                   for f in complete)
                            else "not triggered on completed families")
    with open(args.out, "w") as f:
        json.dump(out, f, indent=1)
    print(f"written: {args.out}")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("fit-nulls")
    r = sub.add_parser("run")
    r.add_argument("--family", required=True, choices=FAMILIES)
    r.add_argument("--sims", required=True,
                   help="sim index range LO-HI (half-open)")
    r.add_argument("--inclusive", action="store_true",
                   help="treat --sims as inclusive of HI")
    r.add_argument("--campaigns", default=None)
    r.add_argument("--workers", type=int, default=None)
    r.add_argument("--batch", type=int, default=DEFAULT_BATCH)
    r.add_argument("--state-dir", default=str(DEFAULT_STATE))
    c = sub.add_parser("collate")
    c.add_argument("--state-dirs", default=None)
    c.add_argument("--out",
                   default=str(ROOT / "phase1" /
                               "calibration_results.json"))
    args = ap.parse_args()
    if args.cmd == "fit-nulls":
        cmd_fit_nulls(args)
    elif args.cmd == "run":
        import os
        if args.workers is None:
            args.workers = max(1, (os.cpu_count() or 3) - 2)
        cmd_run(args)
    else:
        cmd_collate(args)


if __name__ == "__main__":
    main()
