#!/usr/bin/env bash
# Replay the dev and test splits for both locales with every embedding model.
# Embeddings are computed once per locale for all 16,521 utterances and cached under results/.
# The dev runs are needed by compare.py, which picks thresholds on dev and applies them to test.
set -e
cd "$(dirname "$0")/.."
MODELS="${MODELS:-minilm,e5,mpnet,bgem3}"
export OMP_NUM_THREADS="${OMP_NUM_THREADS:-8}" MKL_NUM_THREADS="${MKL_NUM_THREADS:-8}"
for lang in fa en; do
  for split in test dev; do
    python experiments/run_cache.py --lang "$lang" --split "$split" --models "$MODELS"
  done
done
