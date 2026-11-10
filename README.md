# guarded-reply-cache

Code and results for the paper *When is a cached reply safe to reuse? Wrong-intent and wrong-argument hits of semantic caches for LLM assistants*.

A reply cache for an assistant may reuse an answer only when the new request means the same thing as the old one. A cosine threshold on sentence embeddings does not guarantee this: "turn on the light" and "turn off the light" are close in every encoder we tried. This repository measures how often caches serve a reply written for another intent, or for the same intent with another argument, on the Persian and English parts of [MASSIVE](https://github.com/alexa/massive). It evaluates a *signature guard* reproduced from a deployed Persian assistant (a fuzzy hit is allowed only between requests that contain the same distinguishing words), with its lexicon induced from data, against an intent gate, per-entry thresholds, a cross-encoder verifier and a fine-tuned encoder, with thresholds chosen on development data. `results/paper_numbers.md` collects every number quoted in the paper.

## Layout

| Path | What it is |
|---|---|
| `grc/text.py` | Normalisation, canonical keys, the deployed Persian filler list and critical lexicon, and the English counterpart |
| `grc/signature.py` | Lexicon induction from labelled near neighbours |
| `grc/match.py` | Vectorised lookup: trigram Jaccard, the deployed length rules, guards |
| `experiments/prepare_massive.py` | Builds `results/massive_{fa,en}.csv` with answer-equivalence keys |
| `experiments/run_cache.py` | Replays a split against a cache filled with the train split, for every policy (guards, veto, intent gate, per-entry thresholds, verifier) |
| `experiments/intent_classifier.py` | Logistic-regression intent classifiers on each similarity's features, for the intent-gate baseline |
| `experiments/verifier.py` | Cross-encoder verifier (BAAI/bge-reranker-v2-m3) on BGE-M3's nearest candidate |
| `experiments/finetune_minilm.py` | Contrastive fine-tune of MiniLM on cache pairs from the train split |
| `experiments/audit_sample.py` | Draws the stratified sample of wrong hits released for human adjudication |
| `experiments/encode_all.sh` | Runs `run_cache.py` for both locales, both evaluation splits and all encoders |
| `experiments/analyze.py` | Trade-off curves, unsafe-hit budgets, bootstrap intervals and error types |
| `experiments/compare.py` | Guard versus no guard; thresholds chosen on dev, applied to test; paired bootstrap |
| `experiments/ucb_thresholds.py` | Thresholds chosen with a 95% upper confidence bound on the dev error |
| `experiments/minimal_pairs.py` | Probe of one-word minimal pairs |
| `experiments/tune_lexicon.py` | Hyper-parameter choice on dev only (also the frequency-only and intent-label lexicons) |
| `experiments/lexicon_stats.py` | Per-word evidence behind the induced lexicon |
| `experiments/latency.py` | Per-lookup time on one CPU thread, trigram and embedding caches |
| `experiments/figures.py` | Figures |
| `experiments/paper_numbers.py` | Collects every number quoted in the paper into `results/paper_numbers.md` |
| `results/` | Every number in the paper (CSV/JSON/MD/NPZ), including the tuning tables. Embedding caches (`emb_*.npy`) are not committed; `run_cache.py` recomputes them, and `finetune_minilm.py` writes `emb_*_minilmft.npy`. |

## Encoders

| Key | Hugging Face model | Revision used | Prefix |
|---|---|---|---|
| `minilm` | `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` | `e8f8c211226b894fcb81acc59f3b34ba3efd5f42` | – |
| `mpnet` | `sentence-transformers/paraphrase-multilingual-mpnet-base-v2` | `4328cf26390c98c5e3c738b4460a05b95f4911f5` | – |
| `e5` | `intfloat/multilingual-e5-base` | `d128750597153bb5987e10b1c3493a34e5a4502a` | `query: ` |
| `bgem3` | `BAAI/bge-m3` (dense CLS embedding, 1,024 dimensions) | `5617a9f61b028005a4858fdac845db406aefb181` | – |
| verifier | `BAAI/bge-reranker-v2-m3` (cross-encoder, used by `verifier.py`) | `953dc6f6f85a1b2dbfca4c34a2796e7dde08d41e` | – |

## Reproduce

Requires Python 3.12 and about 6 GB of disk for the embedding models. A GPU is not needed.

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
curl -LO https://amazon-massive-nlu-dataset.s3.amazonaws.com/amazon-massive-dataset-1.1.tar.gz
tar -xzf amazon-massive-dataset-1.1.tar.gz
python experiments/prepare_massive.py 1.1 results
python experiments/tune_lexicon.py --lang fa                      # dev split only
MODELS=minilm,e5,mpnet,bgem3 ./experiments/encode_all.sh          # embeddings; dev and test, fa and en
for lang in fa en; do
  python experiments/intent_classifier.py --lang $lang            # intent-gate baseline
  for split in dev test; do python experiments/verifier.py --lang $lang --split $split --top 1; done
  python experiments/finetune_minilm.py --lang $lang              # writes results/emb_${lang}_minilmft.npy
done
MODELS=minilm,mpnet,e5,bgem3,minilmft ./experiments/encode_all.sh # again, with gate, verifier and fine-tuned MiniLM
for lang in fa en; do
  for split in dev test; do for c in intent strict; do
    python experiments/analyze.py --lang $lang --split $split --criterion $c --quiet; done; done
  for c in intent strict; do python experiments/compare.py --lang $lang --criterion $c; done
  for split in dev test; do
    python experiments/run_cache.py --lang $lang --split $split --models minilm,bgem3 --exclude-intents rules --tag norules
  done
  for c in intent strict; do
    python experiments/analyze.py --lang $lang --split test --tag norules --criterion $c --quiet
    python experiments/compare.py --lang $lang --criterion $c --tag norules; done
  python experiments/minimal_pairs.py --lang $lang
  python experiments/lexicon_stats.py --lang $lang
  python experiments/audit_sample.py --lang $lang
  python experiments/ucb_thresholds.py --lang $lang
done
python experiments/latency.py --lang fa --queries 500             # one thread; slow on purpose
python experiments/figures.py --out ../../papers/02-guarded-reply-cache/figures
python experiments/paper_numbers.py
```

The analysis is deterministic: lexicon induction and lookups involve no randomness, and the bootstrap uses fixed seeds. Encoding is the slow part. With 8 CPU threads, BGE-M3 took 702 s for the 16,521 Persian utterances, and 2,021 s for the English ones while other jobs shared the machine; the three smaller encoders take a few minutes each. Latency numbers depend on the machine and on its load, and will differ from the paper's.

## Licence

Code: MIT (see `LICENSE`). MASSIVE is © Amazon.com, Inc. and is licensed under CC BY 4.0. `results/massive_*.csv`, `results/unsafe_*.csv`, `results/minimal_pairs_*.csv` and `results/audit_*_sample.csv` contain MASSIVE utterances and annotations (adapted: normalised text and derived keys). They are redistributed under CC BY 4.0 with attribution to FitzGerald et al. (2023), *MASSIVE: A 1M-example multilingual natural language understanding dataset with 51 typologically-diverse languages*, ACL 2023, https://github.com/alexa/massive.
