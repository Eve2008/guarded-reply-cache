"""Per-lookup latency on one CPU thread: trigram cache versus embedding cache.

The trigram lookup is the deployed algorithm (NexaRoom ``BrainStore.lookup``):
canonicalise the request, compute its signature, try the exact key, then scan
the in-memory index in pure Python, skipping entries whose signature or word
count does not fit and scoring the rest by trigram Jaccard. We time it

* unguarded (no signature test), as a pure-Python scan and, for reference,
  as one vectorised sparse-matrix product over the whole index (the way the
  evaluation computes trigram similarity),
* guarded, scanning every entry as deployed, and
* guarded with the index bucketed by signature, so that only entries with
  the same signature are visited.

Each guarded variant is timed with the induced lexicon and, for Persian,
with the deployed 41-word lexicon. The speed of a guarded lookup depends on
how many entries share the query's signature, which the script records.

The embedding lookup encodes the request with batch size 1 and takes the
best cosine over the pool matrix (one float32 matrix-vector product).
Encoding and search are timed separately.

Cache sizes are 5,000 entries (the deployed index limit, ``MAX_INDEX``) and
the full deduplicated training split. Queries are a fixed random sample of
the test split. Everything runs on one thread; the script sets the thread
variables before numpy and torch are imported.

Each lookup is timed twice: wall-clock time and the CPU time of the calling
thread. On a machine shared with other jobs the wall-clock time includes time
spent waiting for a core; the thread CPU time does not.

Usage: python experiments/latency.py --lang fa --queries 500 --models minilm,mpnet,e5,bgem3
"""

from __future__ import annotations

import os

for _var in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[_var] = "1"
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

import argparse  # noqa: E402
import json  # noqa: E402
import platform  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from collections import defaultdict  # noqa: E402
from pathlib import Path  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments"))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from scipy import sparse  # noqa: E402

from grc.signature import lexicon_signature  # noqa: E402
from grc.text import LANG, deployed_signature_fa, trigrams  # noqa: E402
from run_cache import MODELS, REVISIONS, induce  # noqa: E402

SIZES = (5000, None)  # None = the whole deduplicated train split
THRESHOLD = 0.8


def jaccard(a: frozenset[str], b: frozenset[str]) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


class TrigramCache:
    """The deployed in-memory index and lookup, with a pluggable signature."""

    def __init__(self, keys: list[str], signature, *, guard: bool, bucketed: bool) -> None:
        self.signature = signature
        self.guard = guard
        self.index = {key: (signature(key), trigrams(key), len(key.split())) for key in keys}
        self.buckets: dict[frozenset[str], list[tuple[str, frozenset[str], int]]] = defaultdict(list)
        if bucketed:
            for key, (sig, grams, length) in self.index.items():
                self.buckets[sig].append((key, grams, length))
        self.bucketed = bucketed

    def lookup(self, key: str) -> tuple[float, str] | None:
        if not key:
            return None
        if key in self.index:
            return 1.0, key
        sig = self.signature(key) if self.guard else None
        grams = trigrams(key)
        length = len(key.split())
        best: tuple[float, str] | None = None
        if self.bucketed:
            entries = self.buckets.get(sig, ())
            for other, other_grams, other_length in entries:
                if min(length, other_length) < 2 or not 0.66 <= other_length / max(1, length) <= 1.5:
                    continue
                score = jaccard(grams, other_grams)
                if score >= THRESHOLD and (best is None or score > best[0]):
                    best = (score, other)
            return best
        for other, (other_sig, other_grams, other_length) in self.index.items():
            if (self.guard and other_sig != sig) or min(length, other_length) < 2:
                continue
            if not 0.66 <= other_length / max(1, length) <= 1.5:
                continue
            score = jaccard(grams, other_grams)
            if score >= THRESHOLD and (best is None or score > best[0]):
                best = (score, other)
        return best


class VectorisedTrigramCache:
    """Unguarded trigram lookup as one sparse product over the whole index."""

    def __init__(self, keys: list[str]) -> None:
        self.keys = keys
        self.vocab: dict[str, int] = {}
        rows, cols = [], []
        for row, key in enumerate(keys):
            for gram in trigrams(key):
                rows.append(row)
                cols.append(self.vocab.setdefault(gram, len(self.vocab)))
        matrix = sparse.csr_matrix((np.ones(len(rows), dtype=np.float32), (rows, cols)),
                                   shape=(len(keys), len(self.vocab)))
        matrix.sum_duplicates()
        matrix.data[:] = 1.0
        self.by_gram = matrix.T.tocsr()  # trigram -> entries
        self.sizes = np.asarray(matrix.sum(axis=1), dtype=np.float32).ravel()
        self.lengths = np.asarray([len(key.split()) for key in keys], dtype=np.float32)
        self.exact = {key: i for i, key in enumerate(keys)}

    def lookup(self, key: str) -> tuple[float, str] | None:
        if not key:
            return None
        if key in self.exact:
            return 1.0, key
        grams = trigrams(key)
        ids = [self.vocab[g] for g in grams if g in self.vocab]
        length = len(key.split())
        if not ids or length < 2:
            return None
        inter = np.asarray(self.by_gram[ids].sum(axis=0), dtype=np.float32).ravel()
        score = inter / (len(grams) + self.sizes - inter)
        ratio = self.lengths / length
        score[(self.lengths < 2) | (ratio < 0.66) | (ratio > 1.5)] = 0.0
        best = int(np.argmax(score))
        return (float(score[best]), self.keys[best]) if score[best] >= THRESHOLD else None


def stats(wall_ns: list[int], cpu_ns: list[int]) -> dict[str, float]:
    wall = np.asarray(wall_ns, dtype=np.float64) / 1e6
    cpu = np.asarray(cpu_ns, dtype=np.float64) / 1e6
    return {"median_ms": round(float(np.median(wall)), 4), "mean_ms": round(float(wall.mean()), 4),
            "p95_ms": round(float(np.percentile(wall, 95)), 4),
            "cpu_median_ms": round(float(np.median(cpu)), 4), "cpu_mean_ms": round(float(cpu.mean()), 4),
            "cpu_p95_ms": round(float(np.percentile(cpu, 95)), 4), "n": int(wall.size)}


class Timer:
    """Collects wall-clock and thread CPU time of repeated calls."""

    def __init__(self) -> None:
        self.wall: list[int] = []
        self.cpu: list[int] = []

    def __enter__(self) -> "Timer":
        self._wall = time.perf_counter_ns()
        self._cpu = time.thread_time_ns()
        return self

    def __exit__(self, *exc) -> None:
        self.cpu.append(time.thread_time_ns() - self._cpu)
        self.wall.append(time.perf_counter_ns() - self._wall)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--lang", required=True, choices=["fa", "en"])
    parser.add_argument("--queries", type=int, default=500)
    parser.add_argument("--models", default="minilm,mpnet,e5,bgem3")
    parser.add_argument("--repeats", type=int, default=3, help="passes over the query sample for the trigram cache")
    args = parser.parse_args()

    import torch

    torch.set_num_threads(1)
    torch.set_num_interop_threads(1)
    load_at_start = os.getloadavg()

    results = ROOT / "results"
    frame = pd.read_csv(results / f"massive_{args.lang}.csv", keep_default_na=False)
    frame["row"] = np.arange(len(frame))  # the embedding files follow the full table
    pool = frame[frame.partition == "train"].drop_duplicates("canon", keep="first")
    pool = pool[pool.canon != ""].reset_index(drop=True)
    test = frame[frame.partition == "test"].reset_index(drop=True)
    rng = np.random.default_rng(20261110)
    sample = test.iloc[np.sort(rng.choice(len(test), size=min(args.queries, len(test)), replace=False))]
    utterances = sample.utt.tolist()
    canonical = LANG[args.lang]["canonical"]

    lexicon, _ = induce(pool)  # the hyper-parameters of grc/signature.py, as in run_cache.py
    induced = lexicon_signature(lexicon)
    lexicons = {"induced": induced}
    if args.lang == "fa":
        lexicons["deployed"] = deployed_signature_fa
    rows: list[dict] = []
    buckets: dict[str, dict] = {}

    def add(method: str, size: int, part: str, wall: list[int], cpu: list[int]) -> None:
        entry = {"lang": args.lang, "method": method, "cache_entries": size, "part": part, **stats(wall, cpu)}
        rows.append(entry)
        print(f"  {method:<28} {size:>6}  {part:<7} wall median {entry['median_ms']:.3f} ms "
              f"p95 {entry['p95_ms']:.3f} | cpu median {entry['cpu_median_ms']:.3f} ms "
              f"p95 {entry['cpu_p95_ms']:.3f}", flush=True)

    for size in SIZES:
        keys = pool.canon.tolist()[: size or len(pool)]
        n = len(keys)
        variants = {
            "trigram": TrigramCache(keys, induced, guard=False, bucketed=False),
            "trigram (vectorised)": VectorisedTrigramCache(keys),
        }
        for label, signature in lexicons.items():
            variants[f"trigram + {label} guard (scan)"] = TrigramCache(keys, signature, guard=True, bucketed=False)
            variants[f"trigram + {label} guard (bucketed)"] = TrigramCache(keys, signature, guard=True,
                                                                         bucketed=True)
            # How many index entries share each query's signature (what a guarded lookup visits).
            counts = defaultdict(int)
            for key in keys:
                counts[signature(key)] += 1
            shared = np.asarray([counts.get(signature(canonical(text)), 0) for text in utterances])
            buckets[f"{label}_{n}"] = {"distinct_signatures": len(counts), "median_shared": float(np.median(shared)),
                                       "p95_shared": float(np.percentile(shared, 95)),
                                       "mean_share_of_index": round(float(shared.mean() / n), 4)}
        for name, cache in variants.items():
            for text in utterances[:20]:  # warm-up
                cache.lookup(canonical(text))
            timer = Timer()
            for _ in range(args.repeats):
                for text in utterances:
                    with timer:
                        cache.lookup(canonical(text))
            add(name, n, "total", timer.wall, timer.cpu)

    from sentence_transformers import SentenceTransformer

    versions = {"python": platform.python_version(), "numpy": np.__version__, "torch": torch.__version__}
    try:
        import sentence_transformers

        versions["sentence_transformers"] = sentence_transformers.__version__
    except Exception:  # noqa: BLE001
        pass
    for key in [m for m in args.models.split(",") if m]:
        name, prefix = MODELS[key]
        model = SentenceTransformer(name, revision=REVISIONS[key], device="cpu")
        dim = (model.get_embedding_dimension() if hasattr(model, "get_embedding_dimension")
               else model.get_sentence_embedding_dimension())
        full = np.load(results / f"emb_{args.lang}_{key}.npy")[pool.row.to_numpy()]
        for text in utterances[:10]:  # warm-up
            model.encode([prefix + text], batch_size=1, normalize_embeddings=True, show_progress_bar=False)
        encode, vectors = Timer(), []
        for text in utterances:
            with encode:
                vector = model.encode([prefix + text], batch_size=1, normalize_embeddings=True,
                                      show_progress_bar=False, convert_to_numpy=True)[0]
            vectors.append(vector.astype(np.float32))
        add(f"{key} (dim {dim})", 0, "encode", encode.wall, encode.cpu)
        for size in SIZES:
            matrix = np.ascontiguousarray(full[: size or len(full)])
            search = Timer()
            for vector in vectors[:10]:
                int(np.argmax(matrix @ vector))
            for vector in vectors:
                with search:
                    int(np.argmax(matrix @ vector))
            add(f"{key} (dim {dim})", len(matrix), "search", search.wall, search.cpu)
            add(f"{key} (dim {dim})", len(matrix), "total", [e + s for e, s in zip(encode.wall, search.wall)],
                [e + s for e, s in zip(encode.cpu, search.cpu)])
        del model

    cpu = next((line.split(":", 1)[1].strip() for line in Path("/proc/cpuinfo").read_text().splitlines()
                if line.startswith("model name")), platform.processor())
    table = pd.DataFrame(rows)
    table.to_csv(results / f"latency_{args.lang}.csv", index=False)
    meta = {"lang": args.lang, "queries": len(utterances), "trigram_repeats": args.repeats, "threads": 1,
            "cpu": cpu, "logical_cpus": os.cpu_count(), "load_average_at_start": load_at_start,
            "load_average_at_end": os.getloadavg(), "versions": versions,
            "pool": len(pool), "lexicon_size": len(lexicon), "signature_buckets": buckets}
    (results / f"latency_{args.lang}.json").write_text(json.dumps(meta, indent=1))
    print(json.dumps(meta, indent=1))


if __name__ == "__main__":
    main()
