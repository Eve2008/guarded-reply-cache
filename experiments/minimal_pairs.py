"""Minimal pairs: utterances that differ in exactly one word.

Some pairs mean the same thing, others ask for another intent («... روشن کن» /
«... خاموش کن») or the same intent with another argument. A similarity
threshold can only work if similarity separates the groups. We report, per
similarity, the AUC of that separation, how often each guard blocks each
group, and, for comparison at equal cost, the share of each group that a
threshold blocks when it is set to block the same share of same-meaning pairs
as the induced guard.

Pairs are drawn from the distinct canonical forms of the dev and test
requests that have at least two words; the lexicons are induced from the
training split exactly as in run_cache.py.

Usage: python experiments/minimal_pairs.py --lang fa
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from sklearn.metrics import roc_auc_score  # noqa: E402

from grc.signature import FREQ_MAX_DF, frequency_lexicon, lexicon_signature  # noqa: E402
from grc.text import deployed_signature_fa, trigrams  # noqa: E402

sys.path.insert(0, str(ROOT / "experiments"))
from run_cache import induce, load_pool  # noqa: E402


def pairs(frame: pd.DataFrame) -> list[tuple[int, int]]:
    buckets: dict[str, list[int]] = defaultdict(list)
    tokens = [text.split() for text in frame.canon]
    for index, words in enumerate(tokens):
        if len(words) < 2:
            continue
        for position in range(len(words)):
            key = " ".join(words[:position] + ["*"] + words[position + 1:])
            buckets[key].append(index)
    found = set()
    for members in buckets.values():
        if len(members) > 60:
            continue
        for a in range(len(members)):
            for b in range(a + 1, len(members)):
                i, j = members[a], members[b]
                if frame.canon.iat[i] != frame.canon.iat[j]:
                    found.add((min(i, j), max(i, j)))
    return sorted(found)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--lang", required=True)
    parser.add_argument("--models", default="minilm,e5,mpnet,bgem3")
    args = parser.parse_args()
    results = ROOT / "results"
    full = pd.read_csv(results / f"massive_{args.lang}.csv", keep_default_na=False)
    full["row"] = np.arange(len(full))
    frame = full[full.partition != "train"].drop_duplicates("canon").reset_index(drop=True)
    pool = load_pool(full)
    lexicon, _ = induce(pool)
    induced = lexicon_signature(lexicon)
    frequent = lexicon_signature(frequency_lexicon(pool.canon.tolist(), FREQ_MAX_DF))

    found = pairs(frame)
    rows = []
    for i, j in found:
        a, b = frame.iloc[i], frame.iloc[j]
        if a.eqkey == b.eqkey:
            kind = "same_meaning"
        elif a.action != b.action:
            kind = "different_intent"
        else:
            kind = "different_argument"
        ta, tb = trigrams(a.canon), trigrams(b.canon)
        row = {"a": a.utt, "b": b.utt, "kind": kind, "intent_a": a.intent, "intent_b": b.intent,
               "tri": len(ta & tb) / len(ta | tb),
               "blocked_ind": induced(a.canon) != induced(b.canon),
               "blocked_freq": frequent(a.canon) != frequent(b.canon)}
        if args.lang == "fa":
            row["blocked_dep"] = deployed_signature_fa(a.canon) != deployed_signature_fa(b.canon)
        row["ra"], row["rb"] = int(a.row), int(b.row)
        rows.append(row)
    table = pd.DataFrame(rows)
    for key in [m for m in args.models.split(",") if m]:
        path = results / f"emb_{args.lang}_{key}.npy"
        if not path.is_file():
            continue
        values = np.load(path)
        table[key] = np.sum(values[table.ra.to_numpy()] * values[table.rb.to_numpy()], axis=1)

    report = {"pairs": len(table), "counts": table.kind.value_counts().to_dict(), "auc": {}, "block_rate": {},
              "lexicon_size": len(lexicon), "matched_threshold": {}}
    same = table.kind == "same_meaning"
    kinds = ("different_intent", "different_argument")
    for method in [c for c in ("tri", "minilm", "e5", "mpnet", "bgem3") if c in table]:
        report["auc"][method] = {
            kind: round(float(roc_auc_score(np.r_[np.ones(same.sum()), np.zeros((table.kind == kind).sum())],
                                            np.r_[table[method][same], table[method][table.kind == kind]])), 4)
            for kind in kinds if (table.kind == kind).any()
        }
        report["median_similarity_" + method] = table.groupby("kind")[method].median().round(4).to_dict()
    for guard in [c for c in ("blocked_ind", "blocked_freq", "blocked_dep") if c in table]:
        report["block_rate"][guard] = table.groupby("kind")[guard].mean().round(4).to_dict()
    # A threshold that blocks the same share of same-meaning pairs as the induced guard.
    target = float(table.blocked_ind[same].mean())
    for method in [c for c in ("tri", "minilm", "e5", "mpnet", "bgem3") if c in table]:
        tau = float(np.quantile(table[method][same], target))
        report["matched_threshold"][method] = {
            "tau": round(tau, 4), "same_meaning": round(float((table[method][same] < tau).mean()), 4),
            **{kind: round(float((table[method][table.kind == kind] < tau).mean()), 4) for kind in kinds}}
    table.drop(columns=["ra", "rb"]).to_csv(results / f"minimal_pairs_{args.lang}.csv", index=False)
    (results / f"minimal_pairs_{args.lang}.json").write_text(json.dumps(report, ensure_ascii=False, indent=1))
    print(json.dumps(report, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
