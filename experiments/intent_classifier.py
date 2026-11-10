"""Intent classifiers for the intent-gate baseline.

An LLM cache knows which intent (tool call, device action) each stored reply
carried, but it has to *predict* the intent of a new request. The intent gate
allows a hit only between a request and entries whose stored intent equals the
request's predicted intent. It uses the same labelled training split as the
induced lexicon.

One multinomial logistic regression per similarity, on that similarity's own
features, so the gate adds no encoding cost: the sentence embedding for the
encoders, and TF-IDF of character 1-4-grams of the normalised request for the
trigram cache. Trained on all 11,514 training requests; the regularisation
strength C is chosen on dev accuracy from {1, 10, 100}. Test labels are not used.

Writes results/intent_pred_{lang}_{base}.csv (row, base, predicted intent for
every dev and test request) and results/intent_clf_{lang}_{base}.json (C,
accuracies).

Usage: python experiments/intent_classifier.py --lang fa --bases tri,minilm,mpnet,e5,bgem3
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
C_GRID = (1.0, 10.0, 100.0)


def features(frame: pd.DataFrame, lang: str, base: str, train_rows: np.ndarray):
    if base == "tri":
        vectorizer = TfidfVectorizer(analyzer="char_wb", ngram_range=(1, 4), sublinear_tf=True, min_df=2)
        vectorizer.fit(frame.norm.iloc[train_rows])
        return vectorizer.transform(frame.norm)
    return np.load(RESULTS / f"emb_{lang}_{base}.npy")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--lang", required=True)
    parser.add_argument("--bases", default="tri,minilm,mpnet,e5,bgem3")
    args = parser.parse_args()
    frame = pd.read_csv(RESULTS / f"massive_{args.lang}.csv", keep_default_na=False)
    train = np.flatnonzero(frame.partition.to_numpy() == "train")
    dev = np.flatnonzero(frame.partition.to_numpy() == "dev")
    test = np.flatnonzero(frame.partition.to_numpy() == "test")
    labels = frame.intent.to_numpy()
    for base in [b for b in args.bases.split(",") if b]:
        # One file per (language, base), so bases can be trained in parallel and an
        # interrupted run keeps what it finished.
        out_path = RESULTS / f"intent_pred_{args.lang}_{base}.csv"
        meta_path = RESULTS / f"intent_clf_{args.lang}_{base}.json"
        started = time.time()
        x = features(frame, args.lang, base, train)
        best = None
        for c in C_GRID:
            model = LogisticRegression(C=c, max_iter=3000)
            model.fit(x[train], labels[train])
            accuracy = float((model.predict(x[dev]) == labels[dev]).mean())
            print(f"  {args.lang} {base:<9} C={c:<5} dev accuracy {accuracy:.4f}", flush=True)
            if best is None or accuracy > best[0]:
                best = (accuracy, c, model)
        accuracy, c, model = best
        rows = np.r_[dev, test]
        predicted = model.predict(x[rows])
        test_accuracy = float((predicted[len(dev):] == labels[test]).mean())
        meta = {"base": base, "C": c, "dev_accuracy": round(accuracy, 4), "test_accuracy": round(test_accuracy, 4),
                "seconds": round(time.time() - started, 1)}
        print(f"  {args.lang} {base:<9} chosen C={c}; test accuracy {test_accuracy:.4f}", flush=True)
        pd.DataFrame({"row": rows, "base": base, "pred": predicted}).to_csv(out_path, index=False)
        meta_path.write_text(json.dumps(meta, indent=1))


if __name__ == "__main__":
    main()
