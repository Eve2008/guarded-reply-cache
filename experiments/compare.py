"""Each policy against its reference, with thresholds chosen on dev and applied to test.

For every budget, the threshold of each policy is the one that maximises the
safe-hit rate on the dev split within the unsafe-hit budget; it is then
applied unchanged to the test split. Default thresholds need no choice and
are compared directly.

Two kinds of 95% interval are reported for the difference candidate minus
reference:

* ``*_ci``: paired bootstrap over test queries with the dev-chosen thresholds
  held fixed (2,000 resamples). It ignores the variance of threshold choice.
* ``*_ci_nested``: dev and test queries are resampled together, both
  thresholds are chosen again on each dev resample, and the difference is
  measured on the paired test resample (2,000 resamples). This includes the
  variance of threshold choice.

References: ``base`` for ``base+guard`` variants, ``bgem3`` for ``ce`` (the
verifier reranks BGE-M3 candidates), ``ce`` for ``ce+ind`` and ``minilm`` for
``minilmft``.

Usage: python experiments/compare.py --lang fa --criterion intent [--tag norules]
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
GRID = np.round(np.arange(0.30, 1.0001, 0.0025), 4)
BUDGETS = {"intent": (0.01, 0.02), "strict": (0.02, 0.05)}
DEFAULTS = {"tri": (0.8,), "emb": (0.7, 0.8, 0.9), "ce": (0.5,), "margin": ()}
REPS = 2000


def family(method: str) -> str:
    base = method.split("+")[0]
    if "+pet" in method:
        return "margin"
    if base == "ce":
        return "ce"
    return "tri" if base == "tri" else "emb"


def reference(method: str) -> str | None:
    if method == "ce":
        return "bgem3"
    if method == "minilmft":
        return "minilm"
    if "+" in method:
        return method.split("+")[0]
    return None


def arrays(runs: pd.DataFrame, method: str, column: str) -> tuple[np.ndarray, np.ndarray]:
    group = runs[runs.method == method].sort_values("q")
    score = np.where(np.isfinite(group.score.to_numpy()), group.score.to_numpy(), -1.0)
    return score, group[column].to_numpy().astype(bool)


def indicators(score: np.ndarray, correct: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    hit = score[:, None] >= GRID[None, :]
    return (hit & correct[:, None]).astype(np.float32), (hit & ~correct[:, None]).astype(np.float32)


def choose(safe: np.ndarray, unsafe: np.ndarray, budget: float) -> np.ndarray:
    """Column index of the best threshold per row (rows = resamples); -1 if none fits."""

    ok = unsafe <= budget + 1e-12
    value = np.where(ok, safe, -1.0)
    # Highest safe-hit rate; among ties the highest threshold (last column).
    best = value.max(axis=1, keepdims=True)
    tie = (value == best) & ok
    index = GRID.size - 1 - np.argmax(tie[:, ::-1], axis=1)
    return np.where(ok.any(axis=1), index, -1)


def dev_threshold(score: np.ndarray, correct: np.ndarray, budget: float) -> float | None:
    safe, unsafe = indicators(score, correct)
    column = choose(safe.mean(axis=0)[None, :], unsafe.mean(axis=0)[None, :], budget)[0]
    return None if column < 0 else float(GRID[column])


def evaluate(score: np.ndarray, correct: np.ndarray, tau: float) -> tuple[np.ndarray, np.ndarray]:
    hit = score >= tau
    return (hit & correct).astype(np.float64), (hit & ~correct).astype(np.float64)


def ci(values: np.ndarray) -> list[float]:
    values = values[np.isfinite(values)]
    return [round(float(np.percentile(values, 2.5)), 6), round(float(np.percentile(values, 97.5)), 6)]


def nested(dev: dict, test: dict, budget: float, rng: np.random.Generator) -> dict[str, list[float]]:
    n_dev, n_test = len(dev["ref"][0]), len(test["ref"][0])
    w_dev = np.stack([np.bincount(rng.integers(0, n_dev, n_dev), minlength=n_dev) for _ in range(REPS)])
    w_test = np.stack([np.bincount(rng.integers(0, n_test, n_test), minlength=n_test) for _ in range(REPS)])
    w_dev, w_test = w_dev.astype(np.float32) / n_dev, w_test.astype(np.float32) / n_test
    out = {}
    for name in ("ref", "cand"):
        dev_safe, dev_unsafe = indicators(*dev[name])
        column = choose(w_dev @ dev_safe, w_dev @ dev_unsafe, budget)
        test_safe, test_unsafe = indicators(*test[name])
        rows = np.arange(REPS)
        safe = np.where(column >= 0, (w_test @ test_safe)[rows, np.maximum(column, 0)], np.nan)
        unsafe = np.where(column >= 0, (w_test @ test_unsafe)[rows, np.maximum(column, 0)], np.nan)
        out[name] = (safe, unsafe)
    return {"d_safe_ci_nested": ci(out["cand"][0] - out["ref"][0]),
            "d_unsafe_ci_nested": ci(out["cand"][1] - out["ref"][1]),
            "unsafe_ref_ci_nested": ci(out["ref"][1]), "unsafe_cand_ci_nested": ci(out["cand"][1])}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--lang", required=True)
    parser.add_argument("--criterion", default="intent", choices=["intent", "action", "strict"])
    parser.add_argument("--tag", default="")
    args = parser.parse_args()
    criterion = "intent" if args.criterion == "action" else args.criterion
    column = "action_ok" if criterion == "intent" else "correct"
    tag = f"_{args.tag}" if args.tag else ""
    test = pd.read_csv(RESULTS / f"runs_{args.lang}_test{tag}.csv")
    dev = pd.read_csv(RESULTS / f"runs_{args.lang}_dev{tag}.csv")
    n = test.q.nunique()
    rng = np.random.default_rng(7)
    idx = rng.integers(0, n, size=(REPS, n))
    methods = [m for m in test.method.unique() if not m.startswith("exact")]
    rows = []
    for cand in methods:
        ref = reference(cand)
        if ref is None or ref not in set(methods) or not (dev.method == cand).any():
            continue
        points = []
        if family(cand) == family(ref):
            points += [(f"default {t}", t, t) for t in DEFAULTS[family(cand)]]
        for budget in BUDGETS[criterion]:
            t_ref = dev_threshold(*arrays(dev, ref, column), budget)
            t_cand = dev_threshold(*arrays(dev, cand, column), budget)
            if t_ref is not None and t_cand is not None:
                points.append((f"dev-chosen U<={budget}", t_ref, t_cand))
        for label, t_ref, t_cand in points:
            s0, u0 = evaluate(*arrays(test, ref, column), t_ref)
            s1, u1 = evaluate(*arrays(test, cand, column), t_cand)
            d_safe = s1[idx].mean(axis=1) - s0[idx].mean(axis=1)
            d_unsafe = u1[idx].mean(axis=1) - u0[idx].mean(axis=1)
            entry = {
                "lang": args.lang, "criterion": criterion, "reference": ref, "candidate": cand,
                "base": cand.split("+")[0], "guard": cand.split("+", 1)[1] if "+" in cand else "",
                "point": label, "tau_plain": t_ref, "tau_guard": t_cand,
                "safe_plain": round(s0.mean(), 6), "safe_guard": round(s1.mean(), 6),
                "unsafe_plain": round(u0.mean(), 6), "unsafe_guard": round(u1.mean(), 6),
                "d_safe": round(float(s1.mean() - s0.mean()), 6), "d_safe_ci": ci(d_safe),
                "d_unsafe": round(float(u1.mean() - u0.mean()), 6), "d_unsafe_ci": ci(d_unsafe),
                "unsafe_ratio": round(u0.mean() / u1.mean(), 4) if u1.mean() > 0 else None,
                "safe_ratio": round(s0.mean() / s1.mean(), 4) if s1.mean() > 0 else None,
            }
            if label.startswith("dev-chosen"):
                budget = float(label.split("=")[-1])
                entry.update(nested({"ref": arrays(dev, ref, column), "cand": arrays(dev, cand, column)},
                                    {"ref": arrays(test, ref, column), "cand": arrays(test, cand, column)},
                                    budget, rng))
            rows.append(entry)
    table = pd.DataFrame(rows)
    table.to_csv(RESULTS / f"compare_{args.lang}_{criterion}{tag}.csv", index=False)
    with pd.option_context("display.width", 250, "display.max_rows", 400, "display.max_columns", 30):
        print(table[["candidate", "point", "safe_plain", "safe_guard", "unsafe_plain", "unsafe_guard", "d_safe",
                     "d_safe_ci"] + (["d_safe_ci_nested"] if "d_safe_ci_nested" in table else [])].to_string(index=False))


if __name__ == "__main__":
    main()
