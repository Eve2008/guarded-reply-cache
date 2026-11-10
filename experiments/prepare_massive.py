"""Turn MASSIVE 1.1 into cache-evaluation tables (one per locale).

Each row gets an *answer-equivalence key*: the intent plus the multiset of
(slot type, normalised slot value). Two utterances may share a cached reply
only if their keys are equal. For open-ended intents, where the label says
nothing about the answer, only identical canonical forms are equivalent.
The ``action`` column is the intent; the intent-level criterion compares it.

Usage: python experiments/prepare_massive.py <massive-dir> <out-dir>
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd  # noqa: E402

from grc.text import LANG  # noqa: E402

SLOT = re.compile(r"\[\s*([\w-]+)\s*:\s*([^\]]+?)\s*\]")
OPEN_ENDED = {"general_quirky", "qa_factoid", "qa_maths"}
LOCALES = {"fa": "fa-IR", "en": "en-US"}


def load(massive_dir: Path, locale: str) -> list[dict]:
    path = massive_dir / "data" / f"{locale}.jsonl"
    with path.open(encoding="utf8") as handle:
        return [json.loads(line) for line in handle]


def main() -> None:
    massive_dir, out_dir = Path(sys.argv[1]), Path(sys.argv[2])
    out_dir.mkdir(parents=True, exist_ok=True)
    for lang, locale in LOCALES.items():
        normalize = LANG[lang]["normalize"]
        canonical = LANG[lang]["canonical"]
        rows = []
        for item in load(massive_dir, locale):
            slots = sorted((kind, normalize(value)) for kind, value in SLOT.findall(item["annot_utt"]))
            canon = canonical(item["utt"])
            if item["intent"] in OPEN_ENDED:
                key = f"{item['intent']}||{canon}"
            else:
                key = item["intent"] + "||" + ";".join(f"{k}={v}" for k, v in slots)
            # The intent level compares intents only, for open-ended intents too: two
            # different trivia questions share an intent but not an answer, and that
            # error is counted at the strict level (``eqkey``), not as a wrong intent.
            action = item["intent"]
            rows.append({
                "id": item["id"], "partition": item["partition"], "scenario": item["scenario"],
                "intent": item["intent"], "utt": item["utt"], "norm": normalize(item["utt"]),
                "canon": canon, "slots": json.dumps(slots, ensure_ascii=False), "eqkey": key, "action": action,
            })
        frame = pd.DataFrame(rows)
        frame.to_csv(out_dir / f"massive_{lang}.csv", index=False)
        counts = frame.partition.value_counts().to_dict()
        print(lang, len(frame), counts, "intents:", frame.intent.nunique())


if __name__ == "__main__":
    main()
