"""Draw the sample of unsafe hits released for human adjudication.

Population: every distinct (query, cached request) pair that some policy
served as a wrong hit under the strict criterion on the test split, at the
default thresholds (0.8 for trigrams and for every encoder), with and without
the induced guard. Sample: 200 pairs per language, allocated to the error
types of analyze.py in proportion to their share of the population (at least
5 per type when the type has that many), drawn with a fixed seed.

The adjudication columns are left empty. The paper does not report results
from this sample; it is released so that label noise can be estimated.

Writes results/audit_{lang}_sample.csv.

Usage: python experiments/audit_sample.py --lang fa
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
SEED = 20261110
SIZE = 200
POLICIES = ("tri", "minilm", "mpnet", "e5", "bgem3")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--lang", required=True)
    args = parser.parse_args()
    errors = pd.read_csv(RESULTS / f"unsafe_{args.lang}_test_strict.csv", keep_default_na=False)
    methods = set(POLICIES) | {f"{p}+ind" for p in POLICIES}
    population = errors[errors.method.isin(methods) & (errors.point == "default 0.8")]
    population = population.drop_duplicates(["query", "cached"]).reset_index(drop=True)
    shares = population.type.value_counts()
    quota = np.maximum(np.round(SIZE * shares / shares.sum()).astype(int), np.minimum(shares, 5))
    while quota.sum() > SIZE:
        quota[quota.idxmax()] -= 1
    rng = np.random.default_rng(SEED)
    parts = []
    for kind, count in quota.items():
        members = population[population.type == kind]
        parts.append(members.iloc[np.sort(rng.choice(len(members), size=int(count), replace=False))])
    sample = pd.concat(parts).reset_index(drop=True)
    sample = sample[["query", "cached", "query_intent", "cached_intent", "query_slots", "cached_slots", "type",
                     "identical"]]
    sample.insert(0, "id", np.arange(1, len(sample) + 1))
    sample["same_reply_ok (yes/no)"] = ""
    sample["label_error (yes/no)"] = ""
    sample["note"] = ""
    sample.to_csv(RESULTS / f"audit_{args.lang}_sample.csv", index=False, encoding="utf-8-sig")
    print(f"{args.lang}: population {len(population)} distinct wrong hits; sample {len(sample)}")
    print(sample.type.value_counts().to_string())


if __name__ == "__main__":
    main()
