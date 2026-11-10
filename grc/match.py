"""Vectorised cache lookup: best pool entry per query under each policy."""

from __future__ import annotations

from typing import Callable, Sequence

import numpy as np
from scipy import sparse

from .text import trigrams


def trigram_matrix(texts: Sequence[str], vocab: dict[str, int] | None = None):
    """Binary query-by-trigram CSR matrix; grows ``vocab`` when given an empty dict."""

    if vocab is None:
        vocab = {}
    rows, cols = [], []
    for row, text in enumerate(texts):
        for gram in trigrams(text):
            index = vocab.get(gram)
            if index is None:
                index = vocab.setdefault(gram, len(vocab))
            rows.append(row)
            cols.append(index)
    data = np.ones(len(rows), dtype=np.float32)
    matrix = sparse.csr_matrix((data, (rows, cols)), shape=(len(texts), max(1, len(vocab))))
    matrix.sum_duplicates()
    matrix.data[:] = 1.0
    return matrix, vocab


def jaccard(queries: Sequence[str], pool: Sequence[str]) -> np.ndarray:
    vocab: dict[str, int] = {}
    pool_m, vocab = trigram_matrix(pool, vocab)
    query_m, vocab = trigram_matrix(queries, vocab)
    width = len(vocab)
    pool_m = sparse.csr_matrix((pool_m.data, pool_m.indices, pool_m.indptr), shape=(pool_m.shape[0], width))
    query_m = sparse.csr_matrix((query_m.data, query_m.indices, query_m.indptr), shape=(query_m.shape[0], width))
    inter = (query_m @ pool_m.T).toarray().astype(np.float32)
    q_size = np.asarray(query_m.sum(axis=1)).ravel().astype(np.float32)
    p_size = np.asarray(pool_m.sum(axis=1)).ravel().astype(np.float32)
    union = q_size[:, None] + p_size[None, :] - inter
    return np.divide(inter, union, out=np.zeros_like(inter), where=union > 0)


def signature_ids(signatures: Sequence[frozenset[str]], table: dict[frozenset[str], int]) -> np.ndarray:
    return np.asarray([table.setdefault(sig, len(table)) for sig in signatures], dtype=np.int64)


def best_match(
    scores: np.ndarray,
    *,
    exact: np.ndarray | None = None,
    allowed: np.ndarray | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    """Return (best pool index, best score) per query.

    ``exact`` marks identical keys: they always win with score 1.0, whatever
    the other constraints say (the deployed cache looked them up first).
    ``allowed`` masks candidates a policy refuses to consider.
    """

    work = scores.copy()
    if allowed is not None:
        work[~allowed] = -np.inf
    if exact is not None:
        work[exact] = np.float32(1.0) + np.float32(1e-3)
    index = np.argmax(work, axis=1)
    best = work[np.arange(work.shape[0]), index]
    best = np.where(best > 1.0, 1.0, best)
    return index, best


def deployed_constraints(query_words: np.ndarray, pool_words: np.ndarray) -> np.ndarray:
    """Length rules of the deployed fuzzy tier: both >= 2 words, length ratio 0.66-1.5."""

    q = query_words[:, None].astype(np.float32)
    p = pool_words[None, :].astype(np.float32)
    ratio = p / np.maximum(q, 1.0)
    return (np.minimum(q, p) >= 2) & (ratio >= 0.66) & (ratio <= 1.5)


def equal_ids(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    return a[:, None] == b[None, :]


def topk_neighbours(scores: np.ndarray, k: int, exclude: np.ndarray | None = None) -> np.ndarray:
    work = scores.copy()
    if exclude is not None:
        work[exclude] = -np.inf
    k = min(k, work.shape[1] - 1)
    part = np.argpartition(-work, kth=k, axis=1)[:, :k]
    return part


def apply(fn: Callable[[str], frozenset[str]], texts: Sequence[str]) -> list[frozenset[str]]:
    return [fn(text) for text in texts]
