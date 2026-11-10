"""Cross-encoder verifier baseline (retrieve, then evaluate, as in GPTCache).

For every query, the nearest pool entries under BGE-M3 are rescored by a
multilingual cross-encoder (BAAI/bge-reranker-v2-m3), which reads the new
request and the stored request together. run_cache.py then serves the
candidate with the highest cross-encoder score if that score passes a
threshold (chosen on dev like every other threshold). The model is used as
released, without fine-tuning.

On our CPU the cross-encoder scored about 2.5 pairs per second per four
threads, so the default verifies only the single nearest candidate (``--top
1``): the verifier decides whether BGE-M3's best match may be served. A
candidate whose normalised text is identical to the query is not scored; it
is an exact hit and always served. Pairs are scored in length order, in
chunks that are saved as they finish, so an interrupted run resumes.

Writes results/ce_{lang}_{split}[_{tag}].npz with ``cand`` (query x top pool
indices), ``score`` (sigmoid of the cross-encoder logit; 1 for identical
texts) and ``pool`` (pool size, checked by run_cache.py).

Usage: python experiments/verifier.py --lang fa --split dev [--top 1]
"""

from __future__ import annotations

import argparse
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments"))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import torch  # noqa: E402

from run_cache import RULE_INTENTS, load_pool  # noqa: E402

MODEL = "BAAI/bge-reranker-v2-m3"
REVISION = "953dc6f6f85a1b2dbfca4c34a2796e7dde08d41e"
CHUNK = 256


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--lang", required=True, choices=["fa", "en"])
    parser.add_argument("--split", required=True, choices=["dev", "test"])
    parser.add_argument("--retriever", default="bgem3")
    parser.add_argument("--top", type=int, default=1)
    parser.add_argument("--threads", type=int, default=8)
    parser.add_argument("--exclude-intents", default="")
    parser.add_argument("--tag", default="")
    args = parser.parse_args()
    torch.set_num_threads(args.threads)
    results = ROOT / "results"
    frame = pd.read_csv(results / f"massive_{args.lang}.csv", keep_default_na=False)
    frame["row"] = np.arange(len(frame))
    if args.exclude_intents:
        pattern = re.compile(RULE_INTENTS if args.exclude_intents == "rules" else args.exclude_intents)
        frame = frame[~frame.intent.map(lambda intent: bool(pattern.match(intent)))]
    pool = load_pool(frame)
    queries = frame[frame.partition == args.split].reset_index(drop=True)
    values = np.load(results / f"emb_{args.lang}_{args.retriever}.npy")
    cosine = values[queries.row.to_numpy()] @ values[pool.row.to_numpy()].T
    cand = np.argsort(-cosine, axis=1)[:, : args.top]
    del cosine

    tag = f"_{args.tag}" if args.tag else ""
    out = results / f"ce_{args.lang}_{args.split}{tag}.npz"
    partial = results / f"ce_{args.lang}_{args.split}{tag}.partial.npy"
    pairs = [(q, k) for q in range(len(queries)) for k in range(args.top)]
    texts = [(queries.utt.iat[q], pool.utt.iat[int(cand[q, k])]) for q, k in pairs]
    identical = np.asarray([queries.norm.iat[q] == pool.norm.iat[int(cand[q, k])] for q, k in pairs])
    flat = np.full(len(pairs), np.nan, dtype=np.float64)
    flat[identical] = 1.0
    if partial.is_file():
        saved = np.load(partial)
        if saved.shape == flat.shape:
            flat = np.where(np.isnan(saved), flat, saved)
    todo = [i for i in np.argsort([len(a) + len(b) for a, b in texts], kind="stable") if np.isnan(flat[i])]
    print(f"{args.lang}/{args.split}: {len(pairs)} pairs, {int(identical.sum())} identical, {len(todo)} to score",
          flush=True)

    from sentence_transformers import CrossEncoder

    model = CrossEncoder(MODEL, revision=REVISION, device="cpu", max_length=96)
    started = time.time()
    for start in range(0, len(todo), CHUNK):
        chunk = todo[start:start + CHUNK]
        logits = model.predict([texts[i] for i in chunk], batch_size=32, show_progress_bar=False,
                               activation_fn=torch.nn.Identity(), convert_to_numpy=True)
        flat[chunk] = 1.0 / (1.0 + np.exp(-np.asarray(logits, dtype=np.float64)))
        np.save(partial, flat)
        done = start + len(chunk)
        print(f"  {done}/{len(todo)} scored ({time.time() - started:.0f}s)", flush=True)
    score = flat.reshape(len(queries), args.top)
    np.savez(out, cand=cand, score=score.astype(np.float32), pool=len(pool), model=MODEL, revision=REVISION,
             retriever=args.retriever, top=args.top)
    partial.unlink(missing_ok=True)
    print(f"{args.lang}/{args.split}: wrote {out.name} in {time.time() - started:.0f}s", flush=True)


if __name__ == "__main__":
    main()
