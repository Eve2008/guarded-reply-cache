"""Thresholds chosen with an upper confidence bound on the development error.

compare.py chooses the threshold whose development unsafe-hit rate is within
the budget. On test the budget was often exceeded. Here the threshold is the
one with the highest development safe-hit rate whose one-sided 95%
Clopper-Pearson upper bound on the development unsafe-hit rate is within the
budget. The script reports, for the same policies, the test safe-hit and
unsafe-hit rates under both rules.

Writes results/ucb_{lang}.csv.

Usage: python experiments/ucb_thresholds.py --lang fa
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import beta

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
GRID = np.round(np.arange(0.30, 1.0001, 0.0025), 4)
BUDGETS = {"intent": (0.01, 0.02), "strict": (0.02, 0.05)}
COLUMN = {"intent": "action_ok", "strict": "correct"}


def arrays(runs: pd.DataFrame, method: str, column: str) -> tuple[np.ndarray, np.ndarray]:
    group = runs[runs.method == method].sort_values("q")
    score = np.where(np.isfinite(group.score.to_numpy()), group.score.to_numpy(), -1.0)
    return score, group[column].to_numpy().astype(bool)


def choose(score: np.ndarray, correct: np.ndarray, budget: float, upper: bool) -> float | None:
    n = len(score)
    best = None
    for tau in GRID:
        hit = score >= tau
        safe = int((hit & correct).sum())
        unsafe = int((hit & ~correct).sum())
        bound = beta.ppf(0.95, unsafe + 1, n - unsafe) if upper else unsafe / n
        if bound <= budget and (best is None or safe > best[0] or (safe == best[0] and tau > best[1])):
            best = (safe, tau)
    return None if best is None else float(best[1])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--lang", required=True)
    args = parser.parse_args()
    dev = pd.read_csv(RESULTS / f"runs_{args.lang}_dev.csv")
    test = pd.read_csv(RESULTS / f"runs_{args.lang}_test.csv")
    methods = [m for m in test.method.unique()
               if m.split("+")[0] in ("tri", "minilm", "mpnet", "e5", "bgem3")
               and (("+" not in m) or m.split("+", 1)[1] in ("ind", "gate", "gate+ind"))]
    rows = []
    for criterion, budgets in BUDGETS.items():
        column = COLUMN[criterion]
        for method in methods:
            d_score, d_ok = arrays(dev, method, column)
            t_score, t_ok = arrays(test, method, column)
            for budget in budgets:
                for rule, upper in (("point", False), ("ucb95", True)):
                    tau = choose(d_score, d_ok, budget, upper)
                    if tau is None:
                        continue
                    hit = t_score >= tau
                    rows.append({"lang": args.lang, "criterion": criterion, "budget": budget, "method": method,
                                 "rule": rule, "tau": tau, "test_safe": float((hit & t_ok).mean()),
                                 "test_unsafe": float((hit & ~t_ok).mean())})
    table = pd.DataFrame(rows)
    table.to_csv(RESULTS / f"ucb_{args.lang}.csv", index=False)
    pivot = table.pivot_table(index=["criterion", "budget", "rule"], values=["test_safe", "test_unsafe"],
                              aggfunc="mean")
    print(pivot.round(4).to_string())
    over = table.assign(over=table.test_unsafe > table.budget + 1e-12).groupby("rule").over.agg(["sum", "count"])
    print(over.to_string())


if __name__ == "__main__":
    main()
