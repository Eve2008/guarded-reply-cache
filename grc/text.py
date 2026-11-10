"""Text normalisation, canonical keys and signatures.

The Persian rules reproduce the reply cache of the NexaRoom assistant as it
was deployed (October 2026). The English rules mirror the same categories so
that both languages are treated alike. Nothing here is fitted to the
evaluation data; the induced signature lexicon lives in ``signature.py``.
"""

from __future__ import annotations

import re
import unicodedata

_FA_CHARACTER_MAP = str.maketrans({
    "ي": "ی", "ى": "ی", "ئ": "ی", "ك": "ک", "ة": "ه", "ۀ": "ه",
    "ؤ": "و", "إ": "ا", "أ": "ا", "ٱ": "ا", "ـ": " ",
    "۰": "0", "۱": "1", "۲": "2", "۳": "3", "۴": "4",
    "۵": "5", "۶": "6", "۷": "7", "۸": "8", "۹": "9",
    "٠": "0", "١": "1", "٢": "2", "٣": "3", "٤": "4",
    "٥": "5", "٦": "6", "٧": "7", "٨": "8", "٩": "9",
    "\u200c": " ",  # ZWNJ becomes a space, as the deployed punctuation rule already did
})
_DIACRITICS = re.compile(r"[ً-ٰٟۖ-ۭ]")
_PUNCTUATION = re.compile(r"[^\w\s]", flags=re.UNICODE)
_SPACES = re.compile(r"\s+")
_MI = re.compile(r"\b(ن?می) (\S)")
_HA = re.compile(r"(\S) (ها|های|هایی)\b")

# Deployed filler list (wake name, politeness, framing words).
FA_FILLERS = frozenset({
    "نکسا", "نکسای", "نیکسا", "لطفا", "لطفن", "خواهشا", "هی", "آهای", "خب", "ببین", "ببینم",
    "بیزحمت", "زحمت", "یه", "رو", "را", "دیگه", "اصلا", "حالا", "جان", "جون", "عزیزم",
    "میشه", "میشود", "میتونی", "میتونید", "میشد", "بگو", "بگی", "بگین", "بهم", "برام", "واسم",
    "ممنون", "مرسی", "لحظه", "عزیز", "جونم", "جانم", "اوه", "اوم", "هوم",
})

# Deployed critical lexicon (device names, polarity, negation, numbers, day words).
FA_CRITICAL = frozenset({
    "روشن", "خاموش", "اتاق", "هالوژن", "پذیرایی", "نشیمن", "آینه", "مانیتور", "کولر", "پایین", "بالا",
    "امروز", "فردا", "دیروز", "امشب", "پسفردا", "هفته", "ماه", "سال", "صبح", "شب",
    "نه", "نکن", "نزن", "نباید", "نیست", "نکنی", "هیچ", "همه", "هردو", "یک", "دو", "سه", "چهار",
    "اول", "دوم", "سوم", "کم", "زیاد", "بیشتر", "کمتر",
})
FA_CRITICAL_PREFIXES = ("روشن", "خاموش", "هالوژن", "آینه", "مانیتور", "کولر")

# English counterpart of the deployed Persian filler categories: the wake name
# («نکسا» -> "olly", MASSIVE's wake word), politeness («لطفا», «ممنون»), discourse
# fillers («خب», «حالا»), request framing («میشه», «میتونی», «بگو», «بهم» -> "can",
# "could", "would", "you", "tell", "me") and articles (the counterpart of «یه» and
# the object markers «را»/«رو»). Version 1 of this list also dropped "i", "to",
# "will", "want", "wanna", "need" and "like"; those carry meaning ("i like this
# song" is music_likeness) and were removed after review.
EN_FILLERS = frozenset({
    "olly", "alexa", "hey", "please", "pls", "plz", "kindly", "thanks", "thank",
    "ok", "okay", "so", "well", "um", "uh", "hmm", "just",
    "can", "could", "would", "you", "u", "tell", "me",
    "the", "a", "an",
})


def normalize_fa(text: str) -> str:
    value = unicodedata.normalize("NFKC", text).translate(_FA_CHARACTER_MAP)
    value = _DIACRITICS.sub("", value)
    value = _PUNCTUATION.sub(" ", value.lower())
    return _SPACES.sub(" ", value).strip()


def normalize_en(text: str) -> str:
    value = unicodedata.normalize("NFKC", text).lower().replace("'", "")
    value = _PUNCTUATION.sub(" ", value)
    return _SPACES.sub(" ", value).strip()


def canonical_fa(text: str) -> str:
    value = normalize_fa(text)
    value = _MI.sub(r"\1\2", value)
    value = _HA.sub(r"\1\2", value)
    return " ".join(word for word in value.split() if word not in FA_FILLERS)


def canonical_en(text: str) -> str:
    return " ".join(word for word in normalize_en(text).split() if word not in EN_FILLERS)


def deployed_signature_fa(canonical_text: str) -> frozenset[str]:
    """The signature exactly as NexaRoom computed it."""

    marks: set[str] = set()
    for word in canonical_text.split():
        if word in FA_CRITICAL:
            marks.add(word)
        elif word.isdigit():
            marks.add(word)
        elif word.startswith("نمی") or word.startswith("نکن"):
            marks.add("neg")
        for critical in FA_CRITICAL_PREFIXES:
            if word.startswith(critical):
                marks.add(critical)
    return frozenset(marks)


LANG = {
    "fa": {"normalize": normalize_fa, "canonical": canonical_fa},
    "en": {"normalize": normalize_en, "canonical": canonical_en},
}


def trigrams(text: str) -> frozenset[str]:
    padded = f"  {text} "
    return frozenset(padded[i:i + 3] for i in range(len(padded) - 2))
