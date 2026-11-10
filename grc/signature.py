"""Signature lexicons: which tokens must agree before two utterances may share a reply.

``induce_lexicon`` learns the lexicon from labelled near neighbours: a token
that often distinguishes two similar utterances with *different* meanings,
and rarely two with the same meaning, is critical. Only the cache-pool
partition is used for induction; hyper-parameters are chosen on dev.
"""

from __future__ import annotations

from collections import Counter
from typing import Callable, Iterable, Sequence

import numpy as np

# Induction hyper-parameters, chosen on the Persian dev split by
# experiments/tune_lexicon.py (results/tuning_fa.csv) and used unchanged for
# English. k = 5, 10 and 20 were tried; k = 5 scored 0.1697 and k = 10 0.1687.
K = 5
MIN_COUNT = 3
MIN_RATIO = 0.9
# Label-free baseline: every word that occurs in at most FREQ_MAX_DF pool
# entries is critical. FREQ_MAX_DF was chosen on the same dev objective
# (results/tuning_freq_fa.csv).
FREQ_MAX_DF = 20


def frequency_lexicon(texts: Sequence[str], max_df: int = FREQ_MAX_DF) -> frozenset[str]:
    """Label-free lexicon: words that occur in at most ``max_df`` of ``texts``."""

    frequency: Counter[str] = Counter(word for text in texts for word in set(text.split()))
    return frozenset(word for word, count in frequency.items() if count <= max_df)


def digits(tokens: Iterable[str]) -> set[str]:
    return {token for token in tokens if token.isdigit()}


def induce_lexicon(
    texts: Sequence[str],
    labels: Sequence[str],
    neighbours: np.ndarray,
    *,
    min_count: int = 3,
    min_ratio: float = 0.9,
) -> tuple[frozenset[str], dict[str, tuple[int, int]]]:
    """Return (critical tokens, {token: (different-meaning count, same-meaning count)}).

    ``neighbours[i]`` holds indices of the nearest pool entries to entry ``i``.
    """

    different: Counter[str] = Counter()
    same: Counter[str] = Counter()
    token_sets = [set(text.split()) for text in texts]
    seen: set[tuple[int, int]] = set()
    for i, row in enumerate(neighbours):
        for j in row:
            j = int(j)
            if j < 0 or j == i:
                continue
            pair = (i, j) if i < j else (j, i)
            if pair in seen:
                continue
            seen.add(pair)
            diff = token_sets[i] ^ token_sets[j]
            if not diff:
                continue
            target = same if labels[i] == labels[j] else different
            target.update(diff)
    critical = frozenset(
        token for token, count in different.items()
        if count >= min_count and count / (count + same[token]) >= min_ratio
    )
    stats = {token: (different[token], same[token]) for token in set(different) | set(same)}
    return critical, stats


def lexicon_signature(lexicon: frozenset[str]) -> Callable[[str], frozenset[str]]:
    def signature(canonical_text: str) -> frozenset[str]:
        tokens = canonical_text.split()
        return frozenset({token for token in tokens if token in lexicon} | digits(tokens))

    return signature
