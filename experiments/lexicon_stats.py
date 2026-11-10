"""Dump the evidence behind the induced lexicon: for every word, how often it
distinguished two near neighbours with different meanings and how often it
differed between two with the same meaning.

Writes results/lexicon_stats_{lang}.csv (all words, sorted by distinguishing
count) and prints a few action words that decide between opposite intents.

Usage: python experiments/lexicon_stats.py --lang en
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments"))

import pandas as pd  # noqa: E402

from grc.signature import K, MIN_COUNT, MIN_RATIO  # noqa: E402
from grc.text import LANG  # noqa: E402
from run_cache import induce  # noqa: E402

ACTION_WORDS = {
    "en": ["on", "off", "up", "down", "dim", "brighter", "louder", "lower", "increase", "decrease", "mute",
           "set", "add", "remove", "delete", "cancel", "alarm"],
    "fa": ["روشن", "خاموش", "بالا", "پایین", "کم", "زیاد", "بیشتر", "کمتر", "کاهش", "افزایش",
           "تنظیم", "اضافه", "حذف", "پاک", "لغو"],
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--lang", required=True, choices=["fa", "en"])
    parser.add_argument("--k", type=int, default=K)
    parser.add_argument("--min-count", type=int, default=MIN_COUNT)
    parser.add_argument("--min-ratio", type=float, default=MIN_RATIO)
    args = parser.parse_args()
    frame = pd.read_csv(ROOT / "results" / f"massive_{args.lang}.csv", keep_default_na=False)
    pool = frame[frame.partition == "train"].drop_duplicates("canon", keep="first")
    pool = pool[pool.canon != ""].reset_index(drop=True)
    lexicon, stats = induce(pool, k=args.k, min_count=args.min_count, min_ratio=args.min_ratio)
    table = pd.DataFrame([
        {"word": word, "distinguishing": d, "benign": s, "ratio": d / (d + s) if d + s else 0.0,
         "critical": word in lexicon}
        for word, (d, s) in stats.items()
    ]).sort_values(["distinguishing", "word"], ascending=[False, True])
    table.to_csv(ROOT / "results" / f"lexicon_stats_{args.lang}.csv", index=False)
    # How many critical words occur inside a slot value (a name, place, title, time...) of the pool.
    canonical = LANG[args.lang]["canonical"]
    slot_words = {word for slots in pool.slots for _kind, value in json.loads(slots) for word in canonical(value).split()}
    in_slots = sum(1 for word in lexicon if word in slot_words)
    summary = {"lang": args.lang, "words_seen": len(table), "critical": len(lexicon), "critical_in_slot_values": in_slots,
               "share_in_slot_values": round(in_slots / len(lexicon), 4), "k": args.k, "min_count": args.min_count,
               "min_ratio": args.min_ratio}
    (ROOT / "results" / f"lexicon_summary_{args.lang}.json").write_text(json.dumps(summary, indent=1))
    print(json.dumps(summary))
    print(f"{args.lang}: {len(table)} words seen, {len(lexicon)} critical "
          f"(k={args.k}, c={args.min_count}, r={args.min_ratio})")
    shown = table[table.word.isin(ACTION_WORDS[args.lang])].copy()
    shown["ratio"] = shown.ratio.round(3)
    print(shown.to_string(index=False))


if __name__ == "__main__":
    main()
