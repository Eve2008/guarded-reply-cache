"""Turn per-query cache decisions into trade-off curves, tables and error types.

Operating points are chosen by an *unsafe-hit budget*: the largest safe-hit
rate whose unsafe-hit rate (wrong reply served, per query) stays within the
budget. Precision targets are not used: MASSIVE's labels disagree for some
identical sentences, so label noise puts a floor under every policy's error,
and that floor differs between languages.

Criteria: ``intent`` (a hit is correct if the two requests have the same
intent; column ``action_ok``) and ``strict`` (same intent and same slots;
column ``correct``). ``action`` is accepted as an alias of ``intent``.

Usage: python experiments/analyze.py --lang fa --split test --criterion intent
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RNG = np.random.default_rng(20261110)
GRID = np.round(np.arange(0.30, 1.0001, 0.0025), 4)
DEFAULTS = {"tri": [0.8], "emb": [0.7, 0.8, 0.9], "ce": [0.5], "margin": []}
BUDGETS = {"intent": (0.01, 0.02), "action": (0.01, 0.02), "strict": (0.02, 0.05)}

# Intent pairs whose replies do the opposite thing. A hit across such a pair is
# never a labelling nuance: the assistant would undo what the user asked.
OPPOSITES = [
    ("iot_hue_lighton", "iot_hue_lightoff"), ("iot_hue_lightup", "iot_hue_lightdim"),
    ("iot_hue_lighton", "iot_hue_lightdim"), ("iot_hue_lightup", "iot_hue_lightoff"),
    ("iot_wemo_on", "iot_wemo_off"), ("audio_volume_up", "audio_volume_down"),
    ("audio_volume_up", "audio_volume_mute"), ("alarm_set", "alarm_remove"),
    ("calendar_set", "calendar_remove"), ("lists_createoradd", "lists_remove"),
    ("music_likeness", "music_dislikeness"), ("general_affirm", "general_negate"),
]
OPPOSITE = {frozenset(pair) for pair in OPPOSITES}
# Intents whose reply changes the state of a device, a list, a calendar, an
# account or a playback session; the others only inform or converse.
STATE_CHANGING = {
    "iot_hue_lighton", "iot_hue_lightoff", "iot_hue_lightdim", "iot_hue_lightup", "iot_hue_lightchange",
    "iot_wemo_on", "iot_wemo_off", "iot_cleaning", "iot_coffee",
    "alarm_set", "alarm_remove", "audio_volume_up", "audio_volume_down", "audio_volume_mute", "audio_volume_other",
    "calendar_set", "calendar_remove", "lists_createoradd", "lists_remove",
    "play_music", "play_radio", "play_podcasts", "play_audiobook", "play_game",
    "music_likeness", "music_dislikeness", "music_settings",
    "email_sendemail", "email_addcontact", "social_post", "transport_ticket", "transport_taxi", "takeaway_order",
}
OPEN_ENDED = {"general_quirky", "qa_factoid", "qa_maths"}


def curve(score: np.ndarray, correct: np.ndarray) -> pd.DataFrame:
    rows = []
    n = len(score)
    for tau in GRID:
        hit = score >= tau
        safe = int((hit & correct).sum())
        hits = int(hit.sum())
        rows.append({"tau": tau, "hit_rate": hits / n, "safe_hit_rate": safe / n,
                     "unsafe_hit_rate": (hits - safe) / n, "precision": safe / hits if hits else 1.0})
    return pd.DataFrame(rows)


def bootstrap(score: np.ndarray, correct: np.ndarray, tau: float, reps: int = 1000) -> dict[str, list]:
    n = len(score)
    hit = score >= tau
    safe = (hit & correct).astype(np.float32)
    unsafe = (hit & ~correct).astype(np.float32)
    samples = RNG.integers(0, n, size=(reps, n))
    q = lambda v: [round(float(np.percentile(v, 2.5)), 4), round(float(np.percentile(v, 97.5)), 4)]  # noqa: E731
    return {"shr_ci": q(safe[samples].mean(axis=1)), "uhr_ci": q(unsafe[samples].mean(axis=1))}


def budget_point(table: pd.DataFrame, budget: float) -> float | None:
    ok = table[table.unsafe_hit_rate <= budget]
    if ok.empty:
        return None
    return float(ok.sort_values(["safe_hit_rate", "tau"], ascending=[False, False]).iloc[0].tau)


def family(method: str) -> str:
    base = method.split("+")[0]
    if base.startswith("exact"):
        return "exact"
    if "+pet" in method:
        return "margin"
    if base == "ce":
        return "ce"
    return "tri" if base == "tri" else "emb"


def error_type(query: pd.Series, entry: pd.Series) -> str:
    """Kind of a wrong hit. Different intents first, then same intent with other slots."""

    if query.intent != entry.intent:
        if frozenset((query.intent, entry.intent)) in OPPOSITE:
            return "opposite_action"
        changing = (query.intent in STATE_CHANGING) + (entry.intent in STATE_CHANGING)
        return {2: "other_state_change", 1: "state_change_vs_info", 0: "info_vs_info"}[changing]
    if query.intent in OPEN_ENDED:
        return "other_open_question"
    return "argument_state_change" if query.intent in STATE_CHANGING else "argument_info"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--lang", required=True)
    parser.add_argument("--split", default="test")
    parser.add_argument("--tag", default="")
    parser.add_argument("--criterion", default="intent", choices=["strict", "intent", "action"])
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()
    column = "correct" if args.criterion == "strict" else "action_ok"
    args.criterion = "intent" if args.criterion == "action" else args.criterion
    results = ROOT / "results"
    tag = f"_{args.tag}" if args.tag else ""
    out_tag = f"{tag}_{args.criterion}"
    runs = pd.read_csv(results / f"runs_{args.lang}_{args.split}{tag}.csv")
    meta = json.loads((results / f"meta_{args.lang}_{args.split}{tag}.json").read_text())
    frame = pd.read_csv(results / f"massive_{args.lang}.csv", keep_default_na=False)
    if meta.get("exclude_intents"):
        import re
        import sys
        sys.path.insert(0, str(ROOT / "experiments"))
        from run_cache import RULE_INTENTS
        pattern = re.compile(RULE_INTENTS if meta["exclude_intents"] == "rules" else meta["exclude_intents"])
        frame = frame[~frame.intent.map(lambda intent: bool(pattern.match(intent)))]
    pool = frame[frame.partition == "train"].drop_duplicates("canon", keep="first")
    pool = pool[pool.canon != ""].reset_index(drop=True)
    queries = frame[frame.partition == args.split].reset_index(drop=True)
    opposite_pair = np.asarray([
        frozenset((queries.intent.iat[int(q)], pool.intent.iat[int(j)])) in OPPOSITE
        for q, j in zip(runs.q, runs.j)
    ])
    runs = runs.assign(opposite=opposite_pair)

    summary, curves, errors = [], [], []
    for method, group in runs.groupby("method", sort=False):
        group = group.sort_values("q")
        score = group.score.to_numpy()
        score = np.where(np.isfinite(score), score, -1.0)
        correct = group[column].to_numpy().astype(bool)
        opposite = group.opposite.to_numpy().astype(bool)
        same_norm = group.same_norm.to_numpy().astype(bool)
        table = curve(score, correct)
        table.insert(0, "method", method)
        curves.append(table)
        fam = family(method)
        points: list[tuple[str, float]] = []
        if fam == "exact":
            points.append(("exact", 1.0))
        else:
            for budget in BUDGETS[args.criterion]:
                tau = budget_point(table, budget)
                if tau is not None:
                    points.append((f"U<={budget}", tau))
            points += [(f"default {t}", t) for t in DEFAULTS[fam]]
        for label, tau in points:
            hit = score >= tau
            safe = hit & correct
            entry = {"method": method, "point": label, "tau": tau, "hit_rate": hit.mean(),
                     "safe_hit_rate": safe.mean(), "unsafe_hit_rate": (hit & ~correct).mean(),
                     "precision": safe.sum() / hit.sum() if hit.sum() else 1.0,
                     "unsafe_hits": int((hit & ~correct).sum()), "opposite_hits": int((hit & opposite).sum()),
                     "unsafe_identical": int((hit & ~correct & same_norm).sum()),
                     "opposite_identical": int((hit & opposite & same_norm).sum()),
                     "queries": len(score)}
            entry.update(bootstrap(score, correct, tau))
            summary.append(entry)
            bad = group[(score >= tau) & ~correct]
            for _, row in bad.iterrows():
                q, e = queries.iloc[int(row.q)], pool.iloc[int(row.j)]
                errors.append({"method": method, "point": label, "type": error_type(q, e),
                               "query": q.utt, "query_intent": q.intent, "query_slots": q.slots,
                               "cached": e.utt, "cached_intent": e.intent, "cached_slots": e.slots,
                               "score": round(float(row.score), 4), "identical": bool(row.same_norm),
                               "exact_key": bool(row.exact)})

    pd.concat(curves).to_csv(results / f"curves_{args.lang}_{args.split}{out_tag}.csv", index=False)
    summary_frame = pd.DataFrame(summary)
    summary_frame.to_csv(results / f"summary_{args.lang}_{args.split}{out_tag}.csv", index=False)
    error_frame = pd.DataFrame(errors)
    error_frame.to_csv(results / f"unsafe_{args.lang}_{args.split}{out_tag}.csv", index=False)
    if args.quiet:
        return
    print(f"[{args.lang}/{args.split}/{args.criterion}] reusable {meta['has_equivalent']:.3f}  pool {meta['pool']}  "
          f"queries {meta['queries']}  lexicon {meta['lexicon_size']}")
    cols = ["method", "point", "tau", "safe_hit_rate", "unsafe_hit_rate", "precision", "unsafe_hits", "opposite_hits"]
    with pd.option_context("display.width", 220, "display.max_rows", 300):
        print(summary_frame[cols].round(4).to_string(index=False))


if __name__ == "__main__":
    main()
