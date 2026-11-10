"""Choose the lexicon-induction hyper-parameters on the dev split only.

Objective (unchanged from version 1): mean safe-hit rate at a 1% intent-level
unsafe budget over the guarded trigram and guarded MiniLM caches, on the
Persian dev split. The test split is never read here.

Neighbour counts depend on *k* only, so they are computed once per *k*; every
(c, r) is then a filter on those counts, exactly as ``induce_lexicon`` applies
it. The script also tunes the label-free baseline lexicon (every word whose
pool document frequency is at most F) with the same objective, and records
the strict-level objective (2% budget) for every setting as a sensitivity
check; it does not choose by it.

Writes results/tuning_{lang}.csv, results/tuning_freq_{lang}.csv and
results/tuning_intentlabels_{lang}.csv (induction from intent labels, c = 3).

Usage: python experiments/tune_lexicon.py --lang fa
"""

from __future__ import annotations

import argparse
import itertools
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments"))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from grc.match import best_match, deployed_constraints, equal_ids, jaccard, signature_ids, topk_neighbours  # noqa: E402
from grc.signature import induce_lexicon, lexicon_signature  # noqa: E402

GRID = {"k": [5, 10, 20], "min_count": [2, 3, 5, 10], "min_ratio": [0.7, 0.8, 0.9, 0.95, 1.0]}
FREQ = [1, 2, 3, 5, 10, 20, 50, 100]
TAUS = np.round(np.arange(0.30, 1.0001, 0.0025), 4)


def budget_safe(score: np.ndarray, correct: np.ndarray, budget: float) -> float:
    """Largest safe-hit rate whose unsafe-hit rate is within the budget (as analyze.py)."""

    best = None
    for tau in TAUS:
        hit = score >= tau
        safe, unsafe = (hit & correct).mean(), (hit & ~correct).mean()
        if unsafe <= budget and (best is None or safe > best[0] or (safe == best[0] and tau > best[1])):
            best = (safe, tau)
    return float(best[0]) if best else float("nan")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--lang", default="fa")
    args = parser.parse_args()
    results = ROOT / "results"
    frame = pd.read_csv(results / f"massive_{args.lang}.csv", keep_default_na=False)
    frame["row"] = np.arange(len(frame))
    pool = frame[frame.partition == "train"].drop_duplicates("canon", keep="first")
    pool = pool[pool.canon != ""].reset_index(drop=True)
    dev = frame[frame.partition == "dev"].reset_index(drop=True)
    print(f"{args.lang}: pool {len(pool)}, dev {len(dev)}", flush=True)

    codes = pd.factorize(pd.concat([dev.eqkey, pool.eqkey]))[0]
    equivalent = equal_ids(codes[: len(dev)], codes[len(dev):])
    codes = pd.factorize(pd.concat([dev.action, pool.action]))[0]
    same_intent = equal_ids(codes[: len(dev)], codes[len(dev):])
    codes = pd.factorize(pd.concat([dev.canon, pool.canon]))[0]
    canon_exact = equal_ids(codes[: len(dev)], codes[len(dev):])
    codes = pd.factorize(pd.concat([dev.norm, pool.norm]))[0]
    norm_exact = equal_ids(codes[: len(dev)], codes[len(dev):])
    rows = np.arange(len(dev))

    tri = jaccard(dev.canon.tolist(), pool.canon.tolist())
    length_ok = deployed_constraints(dev.canon.str.split().str.len().to_numpy(),
                                     pool.canon.str.split().str.len().to_numpy())
    emb = np.load(results / f"emb_{args.lang}_minilm.npy")
    cosine = emb[dev.row.to_numpy()] @ emb[pool.row.to_numpy()].T

    def objective(signature) -> dict[str, float]:
        table: dict[frozenset[str], int] = {}
        mask = equal_ids(signature_ids([signature(t) for t in dev.canon], table),
                         signature_ids([signature(t) for t in pool.canon], table))
        out = {}
        for name, scores, exact, allowed in (("tri", tri, canon_exact, length_ok & mask),
                                             ("minilm", cosine, norm_exact, mask)):
            index, score = best_match(scores, exact=exact, allowed=allowed)
            score = np.where(np.isfinite(score), score, -1.0)
            out[f"shr_{name}+ind"] = budget_safe(score, same_intent[rows, index], 0.01)
            out[f"strict_{name}+ind"] = budget_safe(score, equivalent[rows, index], 0.02)
        out["objective"] = (out["shr_tri+ind"] + out["shr_minilm+ind"]) / 2
        out["objective_strict"] = (out["strict_tri+ind"] + out["strict_minilm+ind"]) / 2
        return out

    texts = pool.canon.tolist()
    pool_scores = jaccard(texts, texts)
    np.fill_diagonal(pool_scores, -np.inf)
    records, intent_records = [], []
    for k in GRID["k"]:
        neighbours = topk_neighbours(pool_scores, k)
        _, stats = induce_lexicon(texts, pool.eqkey.tolist(), neighbours, min_count=1, min_ratio=0.0)
        # Sensitivity check: the same induction from intent labels instead of answer-equivalence keys.
        _, intent_stats = induce_lexicon(texts, pool.action.tolist(), neighbours, min_count=1, min_ratio=0.0)
        for r in GRID["min_ratio"]:
            lexicon = frozenset(t for t, (d, s) in intent_stats.items() if d >= 3 and d / (d + s) >= r)
            record = {"k": k, "min_count": 3, "min_ratio": r, "labels": "intent", "lexicon": len(lexicon),
                      **objective(lexicon_signature(lexicon))}
            intent_records.append(record)
            print(f"  intent labels k={k:<2} r={r:<4} lexicon {len(lexicon):>5}  objective {record['objective']:.4f}"
                  f"  strict {record['objective_strict']:.4f}", flush=True)
        for c, r in itertools.product(GRID["min_count"], GRID["min_ratio"]):
            lexicon = frozenset(t for t, (d, s) in stats.items() if d >= c and d / (d + s) >= r)
            record = {"k": k, "min_count": c, "min_ratio": r, "lexicon": len(lexicon),
                      **objective(lexicon_signature(lexicon))}
            records.append(record)
            print(f"  k={k:<2} c={c:<2} r={r:<4} lexicon {len(lexicon):>5}  objective {record['objective']:.4f}"
                  f"  strict {record['objective_strict']:.4f}", flush=True)
    del pool_scores
    table = pd.DataFrame(records).sort_values(["objective", "k", "min_count"], ascending=[False, True, True])
    table.to_csv(results / f"tuning_{args.lang}.csv", index=False)

    frequency = Counter(word for text in texts for word in set(text.split()))
    freq_records = []
    for limit in FREQ:
        lexicon = frozenset(word for word, count in frequency.items() if count <= limit)
        record = {"max_df": limit, "lexicon": len(lexicon), **objective(lexicon_signature(lexicon))}
        freq_records.append(record)
        print(f"  frequency-only df<={limit:<3} lexicon {len(lexicon):>5}  objective {record['objective']:.4f}"
              f"  strict {record['objective_strict']:.4f}", flush=True)
    pd.DataFrame(freq_records).to_csv(results / f"tuning_freq_{args.lang}.csv", index=False)
    pd.DataFrame(intent_records).to_csv(results / f"tuning_intentlabels_{args.lang}.csv", index=False)
    print(table.head(10).to_string(index=False))


if __name__ == "__main__":
    main()
