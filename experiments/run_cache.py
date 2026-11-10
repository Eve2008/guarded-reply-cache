"""Replay MASSIVE queries against a reply cache filled with the train partition.

For every policy and every query we record the best pool entry the policy
would consider, its score, and whether that entry is answer-equivalent to the
query (strict criterion) and has the same intent (intent criterion).
Thresholds are applied later (analyze.py), so one run yields the whole
hit/unsafe-hit trade-off.

Policies, for each base similarity (trigram Jaccard and each encoder):

* ``base``             nearest entry, no constraint;
* ``base+ind``         induced signature guard as a pre-filter (deployed design):
                       only entries with the query's signature are candidates;
* ``base+dep``         the deployed hand-written lexicon, same placement (Persian);
* ``base+freq``        label-free guard: every word in at most 20 pool entries is critical;
* ``base+indv``        induced guard as a veto: the unguarded nearest entry is
                       served only if it passes the guard, otherwise a miss;
* ``base+gate``        intent gate: only entries whose stored intent equals the
                       query's intent as predicted by intent_classifier.py;
* ``base+gate+ind``    gate and induced guard together;
* ``emb+pet_i/pet_s``  per-entry thresholds from labelled pool neighbours (an
                       offline analogue of vCache): the nearest entry is served
                       only if its cosine to the query exceeds the entry's own
                       threshold, the highest cosine between that entry and any
                       pool entry with a different intent (pet_i) or a different
                       answer-equivalence key (pet_s), plus a global margin. The
                       recorded score is 0.5 + cosine - entry threshold.
* ``ce``, ``ce+ind``   cross-encoder verifier (verifier.py): BGE-M3's nearest
                       candidate is rescored by a cross-encoder and served if the
                       score passes; the score is the verifier's logit mapped to
                       sigmoid(logit / 4), a monotone remap that keeps 0.5 at logit 0.

An exact match of the key (canonical form for trigrams, normalised request for
embeddings) always wins with score 1, as in the deployed cache.

Usage:
  python experiments/run_cache.py --lang fa --split test --models minilm,mpnet,e5,bgem3
  python experiments/run_cache.py --lang fa --split test --models minilm,bgem3 \
      --exclude-intents rules --tag norules
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from grc.match import (best_match, deployed_constraints, equal_ids, jaccard, signature_ids,  # noqa: E402
                       topk_neighbours)
from grc.signature import (FREQ_MAX_DF, K, MIN_COUNT, MIN_RATIO, frequency_lexicon,  # noqa: E402
                           induce_lexicon, lexicon_signature)
from grc.text import deployed_signature_fa  # noqa: E402

MODELS = {
    "minilm": ("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2", ""),
    "mpnet": ("sentence-transformers/paraphrase-multilingual-mpnet-base-v2", ""),
    "e5": ("intfloat/multilingual-e5-base", "query: "),
    "bgem3": ("BAAI/bge-m3", ""),
}
REVISIONS = {
    "minilm": "e8f8c211226b894fcb81acc59f3b34ba3efd5f42",
    "mpnet": "4328cf26390c98c5e3c738b4460a05b95f4911f5",
    "e5": "d128750597153bb5987e10b1c3493a34e5a4502a",
    "bgem3": "5617a9f61b028005a4858fdac845db406aefb181",
}
# Intents a deterministic rule tier like NexaRoom's would answer before the
# cache: time, date, weather, lights and plugs, timers/alarms, reminders and
# music playback. Removing whole intents is an upper bound on what such a tier
# removes, because the deployed rules hand complex requests to the LLM.
RULE_INTENTS = r"^(iot_.*|datetime_query|weather_query|alarm_.*|calendar_(set|remove|query)|play_music)$"


def embeddings(frame: pd.DataFrame, lang: str, key: str, cache_dir: Path) -> np.ndarray:
    path = cache_dir / f"emb_{lang}_{key}.npy"
    if path.is_file():
        values = np.load(path)
        if values.shape[0] == len(frame):
            return values
    if key not in MODELS:
        raise FileNotFoundError(f"{path} is missing; {key} embeddings are produced by another script")
    from sentence_transformers import SentenceTransformer

    name, prefix = MODELS[key]
    model = SentenceTransformer(name, revision=REVISIONS[key], device="cpu")
    started = time.time()
    values = model.encode([prefix + text for text in frame.utt.tolist()], batch_size=64,
                          normalize_embeddings=True, show_progress_bar=False, convert_to_numpy=True)
    print(f"  encoded {len(frame)} with {key} in {time.time() - started:.0f}s", flush=True)
    np.save(path, values.astype(np.float32))
    return values.astype(np.float32)


def induce(pool: pd.DataFrame, *, k: int = K, min_count: int = MIN_COUNT, min_ratio: float = MIN_RATIO):
    texts = pool.canon.tolist()
    scores = jaccard(texts, texts)
    np.fill_diagonal(scores, -np.inf)
    neighbours = topk_neighbours(scores, k)
    lexicon, stats = induce_lexicon(texts, pool.eqkey.tolist(), neighbours, min_count=min_count, min_ratio=min_ratio)
    return lexicon, stats


def load_pool(frame: pd.DataFrame) -> pd.DataFrame:
    pool = frame[frame.partition == "train"].drop_duplicates("canon", keep="first")
    return pool[pool.canon != ""].reset_index(drop=True)


def entry_thresholds(vectors: np.ndarray, labels: np.ndarray, block: int = 2048) -> np.ndarray:
    """Highest cosine between each pool entry and any pool entry with another label."""

    out = np.empty(len(vectors), dtype=np.float32)
    for start in range(0, len(vectors), block):
        sims = vectors[start:start + block] @ vectors.T
        same = labels[start:start + block, None] == labels[None, :]
        sims[same] = -np.inf
        out[start:start + block] = sims.max(axis=1)
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--lang", required=True, choices=["fa", "en"])
    parser.add_argument("--split", default="test", choices=["dev", "test"])
    parser.add_argument("--models", default="")
    parser.add_argument("--k", type=int, default=K)
    parser.add_argument("--min-count", type=int, default=MIN_COUNT)
    parser.add_argument("--min-ratio", type=float, default=MIN_RATIO)
    parser.add_argument("--exclude-intents", default="", help="'rules' or a regex; matching intents leave pool and queries")
    parser.add_argument("--tag", default="")
    parser.add_argument("--results", default=str(ROOT / "results"))
    args = parser.parse_args()

    results = Path(args.results)
    frame = pd.read_csv(results / f"massive_{args.lang}.csv", keep_default_na=False)
    frame["row"] = np.arange(len(frame))  # embedding files follow the full table
    full = frame
    if args.exclude_intents:
        pattern = re.compile(RULE_INTENTS if args.exclude_intents == "rules" else args.exclude_intents)
        frame = frame[~frame.intent.map(lambda intent: bool(pattern.match(intent)))]
    pool = load_pool(frame)
    queries = frame[frame.partition == args.split].reset_index(drop=True)
    print(f"{args.lang}/{args.split}: pool {len(pool)} entries, {len(queries)} queries", flush=True)

    eq_table: dict[str, int] = {}
    pool_eq = np.asarray([eq_table.setdefault(v, len(eq_table)) for v in pool.eqkey], dtype=np.int64)
    query_eq = np.asarray([eq_table.setdefault(v, len(eq_table)) for v in queries.eqkey], dtype=np.int64)
    equivalent = equal_ids(query_eq, pool_eq)
    has_equivalent = equivalent.any(axis=1)
    action_table: dict[str, int] = {}
    pool_act = np.asarray([action_table.setdefault(v, len(action_table)) for v in pool.action], dtype=np.int64)
    query_act = np.asarray([action_table.setdefault(v, len(action_table)) for v in queries.action], dtype=np.int64)
    same_action = equal_ids(query_act, pool_act)

    norm_codes = pd.factorize(pd.concat([queries.norm, pool.norm]))[0]
    norm_exact = equal_ids(norm_codes[: len(queries)], norm_codes[len(queries):])
    canon_codes = pd.factorize(pd.concat([queries.canon, pool.canon]))[0]
    canon_exact = equal_ids(canon_codes[: len(queries)], canon_codes[len(queries):])

    lexicon, stats = induce(pool, k=args.k, min_count=args.min_count, min_ratio=args.min_ratio)
    signatures = {"ind": lexicon_signature(lexicon),
                  "freq": lexicon_signature(frequency_lexicon(pool.canon.tolist(), FREQ_MAX_DF))}
    if args.lang == "fa":
        signatures["dep"] = deployed_signature_fa
    guards = {}
    for name, signature in signatures.items():
        table: dict[frozenset[str], int] = {}
        guards[name] = equal_ids(signature_ids([signature(t) for t in queries.canon], table),
                                 signature_ids([signature(t) for t in pool.canon], table))

    prediction_files = sorted(results.glob(f"intent_pred_{args.lang}_*.csv"))
    predicted = pd.concat([pd.read_csv(p) for p in prediction_files]) if prediction_files else None
    pool_intent = pool.intent.to_numpy()

    def gate(base: str) -> np.ndarray | None:
        if predicted is None:
            return None
        part = predicted[predicted.base == base].set_index("row").pred
        if part.empty:
            return None
        query_pred = part.reindex(queries.row.to_numpy()).to_numpy()
        return query_pred[:, None] == pool_intent[None, :]

    records: list[dict] = []
    rows = np.arange(len(queries))

    def record(method: str, index: np.ndarray, score: np.ndarray, seconds: float) -> None:
        correct = equivalent[rows, index]
        action_ok = same_action[rows, index]
        exact = canon_exact[rows, index]
        same_norm = norm_exact[rows, index]
        for q in range(len(queries)):
            records.append({"method": method, "q": q, "j": int(index[q]), "score": float(score[q]),
                            "correct": bool(correct[q]), "action_ok": bool(action_ok[q]),
                            "exact": bool(exact[q]), "same_norm": bool(same_norm[q])})
        print(f"  {method:<16} mean best {np.mean(score[np.isfinite(score)]):.3f}  ({seconds:.1f}s)", flush=True)

    def family(base: str, scores: np.ndarray, exact: np.ndarray, constraint: np.ndarray | None, seconds: float) -> None:
        def allowed(mask: np.ndarray | None) -> np.ndarray | None:
            if constraint is None:
                return mask
            return constraint if mask is None else constraint & mask

        index, score = best_match(scores, exact=exact, allowed=constraint)
        record(base, index, score, seconds)
        plain_index, plain_score = index, score
        for name, mask in guards.items():
            index, score = best_match(scores, exact=exact, allowed=allowed(mask))
            record(f"{base}+{name}", index, score, seconds)
        passed = guards["ind"][rows, plain_index] | exact[rows, plain_index]
        record(f"{base}+indv", plain_index, np.where(passed, plain_score, -np.inf), seconds)
        mask = gate(base)
        if mask is not None:
            index, score = best_match(scores, exact=exact, allowed=allowed(mask))
            record(f"{base}+gate", index, score, seconds)
            index, score = best_match(scores, exact=exact, allowed=allowed(mask & guards["ind"]))
            record(f"{base}+gate+ind", index, score, seconds)

    zeros = np.zeros(equivalent.shape, dtype=np.float32)
    for name, exact in (("exact_norm", norm_exact), ("exact_canon", canon_exact)):
        started = time.time()
        index, score = best_match(zeros, exact=exact)
        score = np.where(exact[rows, index], 1.0, 0.0)
        record(name, index, score, time.time() - started)

    started = time.time()
    tri = jaccard(queries.canon.tolist(), pool.canon.tolist())
    length_ok = deployed_constraints(queries.canon.str.split().str.len().to_numpy(),
                                     pool.canon.str.split().str.len().to_numpy())
    family("tri", tri, canon_exact, length_ok, time.time() - started)
    del tri

    for key in [m for m in args.models.split(",") if m]:
        values = embeddings(full, args.lang, key, results)
        q_vec = values[queries.row.to_numpy()]
        p_vec = values[pool.row.to_numpy()]
        started = time.time()
        cosine = q_vec @ p_vec.T
        family(key, cosine, norm_exact, None, time.time() - started)
        index, score = best_match(cosine, exact=norm_exact)
        exact_hit = norm_exact[rows, index]
        for suffix, labels in (("pet_i", pool_act), ("pet_s", pool_eq)):
            threshold = entry_thresholds(p_vec, labels)
            margin = np.where(exact_hit, 1.0, np.minimum(0.5 + score - threshold[index], 0.999))
            record(f"{key}+{suffix}", index, margin, 0.0)
        del cosine

    verifier = results / f"ce_{args.lang}_{args.split}{'_' + args.tag if args.tag else ''}.npz"
    if verifier.is_file():
        data = np.load(verifier)
        if int(data["pool"]) == len(pool) and len(data["cand"]) == len(queries):
            # The verifier's sigmoid saturates near 1, where the threshold grid has few steps.
            # A monotone remap to sigmoid(logit / 4) spreads the scores and keeps 0.5 at logit 0.
            prob = np.clip(data["score"].astype(np.float64), 1e-12, 1.0)
            logit = np.log(prob) - np.log1p(-np.minimum(prob, 1 - 1e-12))
            spread = np.where(prob >= 1.0, 1.0, 1.0 / (1.0 + np.exp(-logit / 4.0)))
            scores = np.full(equivalent.shape, -np.inf, dtype=np.float32)
            np.put_along_axis(scores, data["cand"], spread.astype(np.float32), axis=1)
            index, score = best_match(scores, exact=norm_exact)
            record("ce", index, score, 0.0)
            index, score = best_match(scores, exact=norm_exact, allowed=guards["ind"])
            record("ce+ind", index, score, 0.0)
        else:
            print(f"  {verifier.name} does not match this pool; skipped", flush=True)

    tag = f"_{args.tag}" if args.tag else ""
    out = results / f"runs_{args.lang}_{args.split}{tag}.csv"
    pd.DataFrame(records).to_csv(out, index=False)
    meta = {
        "lang": args.lang, "split": args.split, "pool": len(pool), "queries": len(queries),
        "has_equivalent": float(has_equivalent.mean()), "has_same_intent": float(same_action.any(axis=1).mean()),
        "lexicon_size": len(lexicon), "k": args.k, "min_count": args.min_count, "min_ratio": args.min_ratio,
        "freq_lexicon_size": len(frequency_lexicon(pool.canon.tolist(), FREQ_MAX_DF)), "freq_max_df": FREQ_MAX_DF,
        "exclude_intents": args.exclude_intents,
        "lexicon": sorted(lexicon, key=lambda t: -stats[t][0])[:400],
    }
    (results / f"meta_{args.lang}_{args.split}{tag}.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1))
    np.save(results / f"has_equiv_{args.lang}_{args.split}{tag}.npy", has_equivalent)
    np.save(results / f"has_action_{args.lang}_{args.split}{tag}.npy", same_action.any(axis=1))
    print(f"  reusable queries (an equivalent entry exists): {has_equivalent.mean():.3f}; lexicon {len(lexicon)}")


if __name__ == "__main__":
    main()
