"""Fine-tune MiniLM on cache pairs from the training split (baseline in the
spirit of Gill et al. 2025b: a small encoder adapted to cache-hit decisions).

Training data come from the deduplicated training split only:

* anchor-positive pairs: two distinct training requests with the same
  answer-equivalence key (same intent and same slots);
* one hard negative per anchor: its nearest training request under the
  original encoder whose key differs.

Loss: multiple-negatives ranking (in-batch negatives plus the hard negative,
scale 20). Batches never hold two pairs with the same key, so an in-batch
"negative" is never an equivalent request. One epoch, AdamW, learning rate
2e-5 with 10% linear warm-up, batch 64, seed 13. The dev and test splits are
not used. The tuned encoder then embeds all 16,521 requests of the locale,
written to results/emb_{lang}_minilmft.npy and used like any other encoder.

The script uses plain PyTorch on the sentence-transformers modules, so it
needs neither ``datasets`` nor ``accelerate``.

Usage: python experiments/finetune_minilm.py --lang fa
"""

from __future__ import annotations

import argparse
import json
import random
import sys
import time
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments"))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import torch  # noqa: E402

from run_cache import MODELS, REVISIONS  # noqa: E402

SEED = 13
BATCH = 64
LR = 2e-5
SCALE = 20.0


def build_pairs(pool: pd.DataFrame, emb: np.ndarray, rng: random.Random) -> list[tuple[int, int, int]]:
    groups: dict[str, list[int]] = defaultdict(list)
    for index, key in enumerate(pool.eqkey):
        groups[key].append(index)
    keys = pool.eqkey.to_numpy()
    vectors = emb[pool.row.to_numpy()]
    triples = []
    for start in range(0, len(pool), 2048):
        block = vectors[start:start + 2048] @ vectors.T
        for offset, row in enumerate(block):
            anchor = start + offset
            members = [m for m in groups[keys[anchor]] if m != anchor]
            if not members:
                continue
            positive = rng.choice(members)
            order = np.argsort(-row)
            negative = next(int(j) for j in order if keys[j] != keys[anchor])
            triples.append((anchor, positive, negative))
    return triples


def batches(triples: list[tuple[int, int, int]], keys: np.ndarray, rng: random.Random) -> list[list[tuple]]:
    rng.shuffle(triples)
    out: list[list[tuple]] = []
    open_batches: list[tuple[list[tuple], set[str]]] = []
    for triple in triples:
        key = keys[triple[0]]
        for members, seen in open_batches:
            if key not in seen and len(members) < BATCH:
                members.append(triple)
                seen.add(key)
                break
        else:
            open_batches.append(([triple], {key}))
        full = [b for b in open_batches if len(b[0]) == BATCH]
        for b in full:
            out.append(b[0])
            open_batches.remove(b)
    out.extend(b[0] for b in open_batches if len(b[0]) >= 8)
    rng.shuffle(out)
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--lang", required=True, choices=["fa", "en"])
    parser.add_argument("--threads", type=int, default=8)
    args = parser.parse_args()
    torch.set_num_threads(args.threads)
    torch.manual_seed(SEED)
    rng = random.Random(SEED)
    results = ROOT / "results"
    frame = pd.read_csv(results / f"massive_{args.lang}.csv", keep_default_na=False)
    frame["row"] = np.arange(len(frame))
    pool = frame[frame.partition == "train"].drop_duplicates("canon", keep="first")
    pool = pool[pool.canon != ""].reset_index(drop=True)
    base = np.load(results / f"emb_{args.lang}_minilm.npy")
    triples = build_pairs(pool, base, rng)
    plan = batches(list(triples), pool.eqkey.to_numpy(), rng)
    texts = pool.utt.tolist()
    print(f"{args.lang}: {len(triples)} training triples in {len(plan)} batches", flush=True)

    from sentence_transformers import SentenceTransformer

    name, _prefix = MODELS["minilm"]
    model = SentenceTransformer(name, revision=REVISIONS["minilm"], device="cpu")
    model.train()
    optimizer = torch.optim.AdamW(model.parameters(), lr=LR)
    warmup = max(1, len(plan) // 10)
    schedule = torch.optim.lr_scheduler.LambdaLR(
        optimizer, lambda step: min((step + 1) / warmup, max(0.0, (len(plan) - step) / (len(plan) - warmup))))
    started = time.time()
    losses = []
    for step, batch in enumerate(plan):
        anchors = [texts[a] for a, _, _ in batch]
        candidates = [texts[p] for _, p, _ in batch] + [texts[n] for _, _, n in batch]
        features_a = model.tokenize(anchors)
        features_c = model.tokenize(candidates)
        emb_a = torch.nn.functional.normalize(model(features_a)["sentence_embedding"], dim=-1)
        emb_c = torch.nn.functional.normalize(model(features_c)["sentence_embedding"], dim=-1)
        logits = SCALE * emb_a @ emb_c.T
        loss = torch.nn.functional.cross_entropy(logits, torch.arange(len(batch)))
        optimizer.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()
        schedule.step()
        losses.append(float(loss))
        if step % 20 == 0 or step == len(plan) - 1:
            print(f"  step {step + 1}/{len(plan)} loss {np.mean(losses[-20:]):.4f} ({time.time() - started:.0f}s)",
                  flush=True)
    model.eval()
    with torch.no_grad():
        values = model.encode(frame.utt.tolist(), batch_size=128, normalize_embeddings=True,
                              show_progress_bar=False, convert_to_numpy=True)
    np.save(results / f"emb_{args.lang}_minilmft.npy", values.astype(np.float32))
    meta = {"lang": args.lang, "triples": len(triples), "batches": len(plan), "batch": BATCH, "lr": LR,
            "scale": SCALE, "seed": SEED, "epochs": 1, "base_model": name, "base_revision": REVISIONS["minilm"],
            "train_seconds": round(time.time() - started, 1), "final_loss_mean20": round(float(np.mean(losses[-20:])), 4),
            "first_loss_mean20": round(float(np.mean(losses[:20])), 4)}
    (results / f"finetune_{args.lang}.json").write_text(json.dumps(meta, indent=1))
    print(json.dumps(meta, indent=1))


if __name__ == "__main__":
    main()
