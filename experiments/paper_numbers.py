"""Collect every number quoted in the paper from the result files.

Reads results/ only (run after analyze.py, compare.py, minimal_pairs.py,
lexicon_stats.py, intent_classifier.py and latency.py) and writes
results/paper_numbers.md, one section per table or paragraph of the paper.
Apart from simple counts over the per-query run files (which hit was swapped
by the guard), nothing here is computed from raw data.

Usage: python experiments/paper_numbers.py
"""

from __future__ import annotations

import ast
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
sys.path.insert(0, str(ROOT))
from grc.text import EN_FILLERS, FA_CRITICAL, FA_FILLERS  # noqa: E402

LANGS = {"fa": "Persian", "en": "English"}
BASES = ["tri", "minilm", "mpnet", "e5", "bgem3"]
ENCODERS = BASES[1:]
CRITERIA = ("intent", "strict")
BUDGETS = {"intent": (0.01, 0.02), "strict": (0.02, 0.05)}
LINES: list[str] = []


def out(text: str = "") -> None:
    LINES.append(text)


def pct(value: float, digits: int = 1) -> str:
    return f"{100 * value:.{digits}f}"


def md(frame: pd.DataFrame, index: bool = True) -> str:
    """Markdown table without the optional ``tabulate`` dependency."""

    frame = frame.reset_index() if index else frame
    head = "| " + " | ".join(str(c) for c in frame.columns) + " |"
    rule = "|" + "---|" * len(frame.columns)
    body = ["| " + " | ".join(str(v) for v in row) + " |" for row in frame.itertuples(index=False)]
    return "\n".join([head, rule, *body])


def interval(text) -> list[float]:
    return list(ast.literal_eval(text)) if isinstance(text, str) else [np.nan, np.nan]


def summary(lang: str, criterion: str, tag: str = "") -> pd.DataFrame:
    return pd.read_csv(RESULTS / f"summary_{lang}_test{tag}_{criterion}.csv")


def compare(lang: str, criterion: str, tag: str = "") -> pd.DataFrame:
    return pd.read_csv(RESULTS / f"compare_{lang}_{criterion}{tag}.csv")


def get(table: pd.DataFrame, method: str, point: str) -> pd.Series | None:
    match = table[(table.method == method) & (table.point == point)]
    return None if match.empty else match.iloc[0]


def section_data() -> None:
    out("## Data, setup and tuning (Sections 3-5)\n")
    out(f"- Deployed Persian filler words: {len(FA_FILLERS)}; deployed critical lexicon: {len(FA_CRITICAL)}; "
        f"English filler words: {len(EN_FILLERS)}")
    for lang in LANGS:
        frame = pd.read_csv(RESULTS / f"massive_{lang}.csv", keep_default_na=False)
        meta = json.loads((RESULTS / f"meta_{lang}_test.json").read_text())
        parts = frame.partition.value_counts().to_dict()
        open_share = frame[frame.partition == "test"].intent.isin(["general_quirky", "qa_factoid", "qa_maths"]).mean()
        out(f"- {LANGS[lang]}: {len(frame)} utterances, {frame.scenario.nunique()} scenarios, "
            f"{frame.intent.nunique()} intents, partitions {parts}; pool {meta['pool']}, queries {meta['queries']}; "
            f"reusable (strict) {pct(meta['has_equivalent'])}%, same-intent entry exists {pct(meta['has_same_intent'])}%; "
            f"induced lexicon {meta['lexicon_size']} words (k={meta['k']}, c={meta['min_count']}, r={meta['min_ratio']}); "
            f"frequency lexicon {meta['freq_lexicon_size']} words (df<={meta['freq_max_df']}); "
            f"open-ended test queries {pct(open_share)}%")
    tuning = pd.read_csv(RESULTS / "tuning_fa.csv")
    best = tuning.sort_values("objective", ascending=False).iloc[0]
    out(f"- Lexicon tuning (fa dev, objective = mean safe-hit rate at 1% intent budget over tri+ind and minilm+ind): "
        f"best {best.objective:.4f} at k={best.k}, c={best.min_count}, r={best.min_ratio} (lexicon {best.lexicon})")
    for k in (5, 10, 20):
        cells = ", ".join(f"r={r}: {tuning[(tuning.k == k) & np.isclose(tuning.min_ratio, r)].objective.max():.4f}"
                          for r in (0.7, 0.8, 0.9, 0.95, 1.0))
        out(f"  - k={k} (max over c): {cells}")
    same_c = tuning[(tuning.k == best.k) & np.isclose(tuning.min_ratio, best.min_ratio)]
    out(f"  - at k={best.k}, r={best.min_ratio}: objective per c "
        + ", ".join(f"c={r.min_count}: {r.objective:.4f} (lexicon {r.lexicon})" for r in same_c.itertuples()))
    freq = pd.read_csv(RESULTS / "tuning_freq_fa.csv")
    fbest = freq.sort_values("objective", ascending=False).iloc[0]
    out(f"- Frequency-only lexicon (fa dev): best objective {fbest.objective:.4f} at df<={fbest.max_df} "
        f"(lexicon {fbest.lexicon}); strict objective there {fbest.objective_strict:.4f}; "
        f"induced lexicon strict objective {best.objective_strict:.4f}")
    intent = pd.read_csv(RESULTS / "tuning_intentlabels_fa.csv")
    ibest = intent.sort_values("objective", ascending=False).iloc[0]
    out(f"- Induction from intent labels (fa dev, c=3): best objective {ibest.objective:.4f} at k={ibest.k}, "
        f"r={ibest.min_ratio} (lexicon {ibest.lexicon}); strict objective {ibest.objective_strict:.4f}")
    for lang in LANGS:
        accs = []
        for base in BASES:
            path = RESULTS / f"intent_clf_{lang}_{base}.json"
            if path.is_file():
                meta = json.loads(path.read_text())
                accs.append(f"{base} {meta['test_accuracy']:.3f} (C={meta['C']:g})")
        out(f"- Intent classifier test accuracy, {LANGS[lang]}: " + "; ".join(accs))
    out()


def section_exact() -> None:
    out("## Exact-match references (Section 5.2)\n")
    out("| Language | Reference | hit rate % | intent-wrong hits | share of hits % | strict-wrong hits | share % |")
    out("|---|---|---|---|---|---|---|")
    for lang in LANGS:
        for name in ("exact_norm", "exact_canon"):
            a = get(summary(lang, "intent"), name, "exact")
            s = get(summary(lang, "strict"), name, "exact")
            hits = a.hit_rate * a.queries
            out(f"| {LANGS[lang]} | {name} | {pct(a.hit_rate)} | {a.unsafe_hits} | {pct(a.unsafe_hits / hits)} | "
                f"{s.unsafe_hits} | {pct(s.unsafe_hits / hits)} |")
    out()


def section_defaults() -> None:
    out("## Table 1: default thresholds, test\n")
    out("| Language | Policy | tau | safe intent | unsafe intent | safe strict | unsafe strict | opposite | "
        "opposite identical/exact-key |")
    out("|---|---|---|---|---|---|---|---|---|")
    for lang in LANGS:
        si, ss = summary(lang, "intent"), summary(lang, "strict")
        errors = pd.read_csv(RESULTS / f"unsafe_{lang}_test_intent.csv", keep_default_na=False)
        for base in BASES:
            taus = (0.8,) if base == "tri" else (0.7, 0.8, 0.9)
            for tau in taus:
                a, s = get(si, base, f"default {tau}"), get(ss, base, f"default {tau}")
                opp = errors[(errors.method == base) & (errors.point == f"default {tau}") &
                             (errors.type == "opposite_action")]
                out(f"| {LANGS[lang]} | {base} | {tau} | {pct(a.safe_hit_rate)} | {pct(a.unsafe_hit_rate)} | "
                    f"{pct(s.safe_hit_rate)} | {pct(s.unsafe_hit_rate)} | {a.opposite_hits} | "
                    f"{int(opp.identical.sum())}/{int(opp.exact_key.sum())} |")
    out()
    for tau in (0.7, 0.8, 0.9):
        for lang in LANGS:
            si, ss = summary(lang, "intent"), summary(lang, "strict")
            u = [get(si, e, f"default {tau}").unsafe_hit_rate for e in ENCODERS]
            s = [get(ss, e, f"default {tau}").unsafe_hit_rate for e in ENCODERS]
            p = [get(si, e, f"default {tau}").precision for e in ENCODERS]
            out(f"- tau {tau}, {LANGS[lang]}: unsafe intent {pct(min(u))}-{pct(max(u))}%, unsafe strict "
                f"{pct(min(s))}-{pct(max(s))}%, intent precision {min(p):.3f}-{max(p):.3f}")
    for lang in LANGS:
        si = summary(lang, "intent")
        for e in ENCODERS:
            u8, u9 = get(si, e, "default 0.8").unsafe_hit_rate, get(si, e, "default 0.9").unsafe_hit_rate
            out(f"- {LANGS[lang]} {e}: 0.8 -> 0.9 cuts unsafe intent {u8 / u9:.2f}x")
    out()


def section_error_types() -> None:
    out("## Error types of wrong hits at default 0.8, test (Section 6.1)\n")
    for criterion in CRITERIA:
        for lang in LANGS:
            errors = pd.read_csv(RESULTS / f"unsafe_{lang}_test_{criterion}.csv", keep_default_na=False)
            sub = errors[errors.method.isin(BASES) & (errors.point == "default 0.8")]
            table = sub.pivot_table(index="method", columns="type", values="query", aggfunc="count", fill_value=0)
            table = table.reindex([b for b in BASES if b in table.index])
            table["total"] = table.sum(axis=1)
            table["identical"] = sub.groupby("method").identical.sum().reindex(table.index)
            out(f"### {LANGS[lang]}, {criterion} criterion\n")
            out(md(table))
            shares = (table.drop(columns=["total", "identical"]).sum() / table.total.sum()).round(3)
            out("\nShares over the five policies: " + ", ".join(f"{k} {100 * v:.1f}%" for k, v in shares.items()))
            out()


def section_guard_defaults() -> None:
    out("## Guards and gates at default thresholds (Table 2)\n")
    out("| Language | Candidate | point | intent: unsafe plain->cand (ratio, CI excl 0) | safe plain->cand (ratio) | "
        "strict: unsafe plain->cand (ratio, CI excl 0) | safe plain->cand |")
    out("|---|---|---|---|---|---|---|")
    for lang in LANGS:
        ci_, cs = compare(lang, "intent"), compare(lang, "strict")
        for cand in [c for c in ci_.candidate.unique() if "+" in c and not c.split("+")[1].startswith("pet")]:
            for point in ("default 0.8", "default 0.9"):
                a = ci_[(ci_.candidate == cand) & (ci_.point == point)]
                s = cs[(cs.candidate == cand) & (cs.point == point)]
                if a.empty or s.empty:
                    continue
                a, s = a.iloc[0], s.iloc[0]
                ia, is_ = interval(a.d_unsafe_ci), interval(s.d_unsafe_ci)
                out(f"| {LANGS[lang]} | {cand} | {point} | {pct(a.unsafe_plain)}->{pct(a.unsafe_guard)} "
                    f"({a.unsafe_ratio:.2f}x, {not (ia[0] <= 0 <= ia[1])}) | {pct(a.safe_plain)}->{pct(a.safe_guard)} "
                    f"({a.safe_ratio:.2f}x) | {pct(s.unsafe_plain)}->{pct(s.unsafe_guard)} ({s.unsafe_ratio:.2f}x, "
                    f"{not (is_[0] <= 0 <= is_[1])}) | {pct(s.safe_plain)}->{pct(s.safe_guard)} |")
    out()
    for guard in ("ind", "indv", "gate", "gate+ind", "freq", "dep"):
        for criterion in CRITERIA:
            for lang in LANGS:
                table = compare(lang, criterion)
                rows = table[table.guard.eq(guard) & table.point.isin(["default 0.8", "default 0.9"]) & table.base.isin(ENCODERS)]
                if rows.empty:
                    continue
                removed_u = 1 - rows.unsafe_guard / rows.unsafe_plain
                removed_s = 1 - rows.safe_guard / rows.safe_plain
                prec_p = rows.safe_plain / (rows.safe_plain + rows.unsafe_plain)
                prec_g = rows.safe_guard / (rows.safe_guard + rows.unsafe_guard)
                out(f"- +{guard}, {criterion}, {LANGS[lang]}, encoders at 0.8/0.9: unsafe ratio "
                    f"{rows.unsafe_ratio.min():.2f}-{rows.unsafe_ratio.max():.2f}x (removed {pct(removed_u.min(), 0)}-"
                    f"{pct(removed_u.max(), 0)}%), safe hits removed {pct(removed_s.min(), 0)}-{pct(removed_s.max(), 0)}%, "
                    f"precision {prec_p.min():.3f}-{prec_p.max():.3f} -> {prec_g.min():.3f}-{prec_g.max():.3f}")
    out()


def section_swaps() -> None:
    out("## Pre-filter swaps: wrong hits under the guard whose unguarded hit was correct (Section 6.2)\n")
    for lang in LANGS:
        runs = pd.read_csv(RESULTS / f"runs_{lang}_test.csv")
        for base in BASES:
            for tau in ((0.8,) if base == "tri" else (0.8, 0.9)):
                plain = runs[runs.method == base].sort_values("q")
                for guard in ("+ind", "+gate"):
                    cand = runs[runs.method == base + guard].sort_values("q")
                    if cand.empty:
                        continue
                    hp, hg = plain.score.to_numpy() >= tau, cand.score.to_numpy() >= tau
                    wrong_g = hg & ~cand.action_ok.to_numpy()
                    ok_p = hp & plain.action_ok.to_numpy()
                    swapped = wrong_g & ok_p & (cand.j.to_numpy() != plain.j.to_numpy())
                    out(f"- {LANGS[lang]} {base}{guard} @ {tau}: wrong-intent hits {int(wrong_g.sum())}, of which "
                        f"{int(swapped.sum())} replaced a correct unguarded hit")
    out()


def section_tuned(tag: str = "") -> None:
    out(f"## Dev-chosen thresholds{' (' + tag + ')' if tag else ''}: change in safe hits, test (Tables 3-4)\n")
    out("| Language | Candidate | budget | safe plain->cand | d_safe | CI (test bootstrap) | CI (nested) | "
        "test unsafe plain/cand |")
    out("|---|---|---|---|---|---|---|---|")
    over = []
    for lang in LANGS:
        for criterion in CRITERIA:
            table = compare(lang, criterion, tag)
            for row in table[table.point.str.startswith("dev-chosen")].itertuples():
                budget = float(row.point.split("=")[-1])
                ci1, ci2 = interval(row.d_safe_ci), interval(getattr(row, "d_safe_ci_nested", "[nan, nan]"))
                out(f"| {LANGS[lang]} | {row.candidate} | {criterion} {budget:g} | {pct(row.safe_plain)}->"
                    f"{pct(row.safe_guard)} | {100 * row.d_safe:+.1f} | [{100 * ci1[0]:.1f}, {100 * ci1[1]:.1f}] | "
                    f"[{100 * ci2[0]:.1f}, {100 * ci2[1]:.1f}] | {pct(row.unsafe_plain)}/{pct(row.unsafe_guard)} |")
                over.append({"lang": lang, "criterion": criterion, "candidate": row.candidate, "budget": budget,
                             "plain_excess": row.unsafe_plain - budget, "cand_excess": row.unsafe_guard - budget})
    out()
    frame = pd.DataFrame(over)
    ind = frame[frame.candidate.str.endswith("+ind") & ~frame.candidate.str.contains("gate")]
    ind = ind[ind.candidate.str.split("+").str[0].isin(BASES)]
    if not ind.empty:
        for name, column in (("unguarded", "plain_excess"), ("guarded", "cand_excess")):
            exceeding = ind[ind[column] > 1e-9][column]
            out(f"- Budget excess on test, {name} (+ind comparisons, {len(ind)} cells): {len(exceeding)} exceed; "
                f"median excess among those {100 * exceeding.median():.2f} points; median over all cells "
                f"{100 * ind[column].median():.2f}; max {100 * ind[column].max():.2f}")
    for suffix in ("+ind", "+gate", "+gate+ind"):
        part = frame[frame.candidate.str.endswith(suffix) & frame.candidate.str.split("+").str[0].isin(BASES)]
        if suffix == "+ind":
            part = part[~part.candidate.str.contains("gate")]
        if part.empty:
            continue
        out(f"- Budget excess on test, candidates {suffix} ({len(part)} cells): {(part.cand_excess > 1e-9).sum()} exceed; "
            f"max {100 * part.cand_excess.max():.2f} points; plain max {100 * part.plain_excess.max():.2f}")
    out()


def section_equal_risk(tag: str = "") -> None:
    out(f"## Equal test error: best safe-hit rate on the test curve within each budget{' (' + tag + ')' if tag else ''}\n")
    methods_order = None
    for lang in LANGS:
        for criterion in CRITERIA:
            table = summary(lang, criterion, f"_{tag}" if tag else "")
            points = [f"U<={b}" for b in BUDGETS[criterion]]
            sub = table[table.point.isin(points)].pivot_table(index="method", columns="point", values="safe_hit_rate")
            if methods_order is None:
                methods_order = list(sub.index)
            out(f"### {LANGS[lang]}, {criterion}\n")
            out(md((100 * sub).round(1)))
            out()


def section_minimal_pairs() -> None:
    out("## Minimal pairs (Section 6.3, Table 5)\n")
    for lang in LANGS:
        report = json.loads((RESULTS / f"minimal_pairs_{lang}.json").read_text())
        out(f"### {LANGS[lang]}\n")
        out(f"- pairs {report['pairs']}, counts {report['counts']}, lexicon {report['lexicon_size']}")
        for method, values in report["auc"].items():
            out(f"- AUC {method}: {values}; medians {report['median_similarity_' + method]}")
        for guard, values in report["block_rate"].items():
            out(f"- block rate {guard}: {values}")
        for method, values in report["matched_threshold"].items():
            out(f"- threshold matched to the induced guard's same-meaning block rate, {method}: {values}")
        out()


def section_lexicon() -> None:
    out("## Lexicon evidence (Section 7)\n")
    words = {"en": ["on", "off", "up", "down", "add", "remove", "set", "delete", "cancel", "mute", "silence", "quiet",
                    "reply", "respond", "louder", "lower", "like", "want", "need", "will", "not", "wake"],
             "fa": ["روشن", "خاموش", "حذف", "اضافه", "افزایش", "کاهش", "بیشتر", "کمتر", "دوشاخه", "سوکت", "تقویم",
                    "تقویمم", "زیاد", "کم"]}
    for lang in LANGS:
        table = pd.read_csv(RESULTS / f"lexicon_stats_{lang}.csv", keep_default_na=False)
        meta = json.loads((RESULTS / f"meta_{lang}_test.json").read_text())
        out(f"- {LANGS[lang]}: {len(table)} words ever differed between two neighbours; {int(table.critical.sum())} "
            f"critical (meta lexicon {meta['lexicon_size']})")
        shown = table[table.word.isin(words[lang])]
        for row in shown.itertuples():
            out(f"  - {row.word}: distinguishing {row.distinguishing}, benign {row.benign}, ratio {row.ratio:.3f}, "
                f"critical {row.critical}")
    out()


def section_norules() -> None:
    if not (RESULTS / "compare_fa_intent_norules.csv").is_file():
        return
    out("## Ablation without rule-tier intents (Section 6.4)\n")
    for lang in LANGS:
        meta = json.loads((RESULTS / f"meta_{lang}_test_norules.json").read_text())
        out(f"- {LANGS[lang]}: pool {meta['pool']}, queries {meta['queries']}, reusable {pct(meta['has_equivalent'])}%")
        for criterion in CRITERIA:
            table = summary(lang, criterion, "_norules")
            for base in ("tri", "minilm", "bgem3"):
                for tau in ((0.8,) if base == "tri" else (0.8, 0.9)):
                    a, g = get(table, base, f"default {tau}"), get(table, base + "+ind", f"default {tau}")
                    out(f"  - {criterion} {base} @ {tau}: safe {pct(a.safe_hit_rate)} unsafe {pct(a.unsafe_hit_rate)}; "
                        f"+ind safe {pct(g.safe_hit_rate)} unsafe {pct(g.unsafe_hit_rate)}")
    out()
    section_tuned("_norules")


def section_latency() -> None:
    path = RESULTS / "latency_fa.csv"
    if not path.is_file():
        return
    out("## Latency (Section 6.6, Table 7)\n")
    table = pd.read_csv(path)
    meta = json.loads((RESULTS / "latency_fa.json").read_text())
    out(f"- machine: {meta['cpu']}, {meta['logical_cpus']} logical CPUs, load {meta['load_average_at_start']} -> "
        f"{meta['load_average_at_end']}; versions {meta['versions']}; queries {meta['queries']}")
    out(f"- signature buckets: {json.dumps(meta.get('signature_buckets', {}))}")
    out(md(table[["method", "cache_entries", "part", "cpu_median_ms", "cpu_p95_ms", "median_ms", "p95_ms"]],
       index=False))
    out()


def section_manuscript_tables() -> None:
    """Rows of Tables 5-7 of the manuscript, in the manuscript's own format."""

    out("## Manuscript Table 5 rows (threshold 0.8)\n")
    names = {"": "none", "+ind": "guard", "+indv": "guard as veto", "+gate": "intent gate", "+gate+ind": "gate and guard"}
    labels = {"tri": "trigram", "minilm": "MiniLM", "bgem3": "BGE-M3"}
    for lang in LANGS:
        si, ss = summary(lang, "intent"), summary(lang, "strict")
        for base in ("tri", "minilm", "bgem3"):
            for suffix in (("", "+ind") if base == "tri" else names):
                a, s = get(si, base + suffix, "default 0.8"), get(ss, base + suffix, "default 0.8")
                out(f"| {LANGS[lang]} | {labels[base]} | {names[suffix]} | {pct(a.safe_hit_rate)} | "
                    f"{pct(a.unsafe_hit_rate)} | {pct(s.safe_hit_rate)} | {pct(s.unsafe_hit_rate)} |")
    out()
    out("## Manuscript Table 6 rows (dev-chosen thresholds; d safe [nested 95% CI], points)\n")
    for lang in LANGS:
        tables = {c: compare(lang, c) for c in CRITERIA}
        for base in ("tri", "minilm", "bgem3"):
            for suffix in ("+ind", "+gate", "+gate+ind"):
                cells = []
                for criterion in CRITERIA:
                    for budget in BUDGETS[criterion]:
                        t = tables[criterion]
                        row = t[(t.candidate == base + suffix) & (t.point == f"dev-chosen U<={budget}")]
                        if row.empty:
                            cells.append("–")
                            continue
                        row = row.iloc[0]
                        lo, hi = interval(row.d_safe_ci_nested)
                        bold = "**" if lo > 0 or hi < 0 else ""
                        cells.append(f"{bold}{100 * row.d_safe:+.1f}{bold} [{100 * lo:.1f}, {100 * hi:.1f}]")
                out(f"| {LANGS[lang]} | {labels[base]} | {names[suffix]} | " + " | ".join(cells) + " |")
    out()
    out("## Manuscript Table 7 rows (dev-chosen thresholds; correct hits % (wrong hits % on test))\n")
    # (label, filter label, method for the intent columns, method for the strict columns)
    rows = [("BGE-M3", "none", "bgem3", "bgem3"), ("BGE-M3", "induced guard", "bgem3+ind", "bgem3+ind"),
            ("BGE-M3", "guard as veto", "bgem3+indv", "bgem3+indv"),
            ("BGE-M3", "frequency-only guard", "bgem3+freq", "bgem3+freq"),
            ("BGE-M3", "deployed guard", "bgem3+dep", "bgem3+dep"), ("BGE-M3", "intent gate", "bgem3+gate", "bgem3+gate"),
            ("BGE-M3", "gate and guard", "bgem3+gate+ind", "bgem3+gate+ind"),
            ("BGE-M3", "per-entry thresholds", "bgem3+pet_i", "bgem3+pet_s"),
            ("cross-encoder verifier on BGE-M3's nearest entry", "none", "ce", "ce"),
            ("cross-encoder verifier on BGE-M3's nearest entry", "induced guard", "ce+ind", "ce+ind"),
            ("MiniLM", "none", "minilm", "minilm"), ("fine-tuned MiniLM", "none", "minilmft", "minilmft"),
            ("fine-tuned MiniLM", "induced guard", "minilmft+ind", "minilmft+ind"),
            ("fine-tuned MiniLM", "gate and guard", "minilmft+gate+ind", "minilmft+gate+ind"),
            ("trigram", "none", "tri", "tri"), ("trigram", "induced guard", "tri+ind", "tri+ind"),
            ("trigram", "gate and guard", "tri+gate+ind", "tri+gate+ind")]
    for label, filt, intent_method, strict_method in rows:
        cells = []
        for lang in LANGS:
            for criterion, method in (("intent", intent_method), ("strict", strict_method)):
                t = compare(lang, criterion)
                point = f"dev-chosen U<={BUDGETS[criterion][0]}"
                cand = t[(t.candidate == method) & (t.point == point)]
                ref = t[(t.reference == method) & (t.point == point)]
                if not cand.empty:
                    value = (cand.iloc[0].safe_guard, cand.iloc[0].unsafe_guard)
                elif not ref.empty:
                    value = (ref.iloc[0].safe_plain, ref.iloc[0].unsafe_plain)
                else:
                    cells.append("–")
                    continue
                cells.append(f"{pct(value[0])} ({pct(value[1])})")
        if all(cell == "–" for cell in cells):
            continue
        out(f"| {label} | {filt} | " + " | ".join(cells) + " |")
    out()


def section_equal_risk_deltas() -> None:
    out("## Equal test error: change in safe hits against the unfiltered policy (ranges over the five similarities)\n")
    for lang in LANGS:
        for criterion in CRITERIA:
            table = summary(lang, criterion)
            for budget in BUDGETS[criterion]:
                point = f"U<={budget}"
                for suffix in ("+ind", "+indv", "+gate", "+gate+ind", "+freq"):
                    deltas = []
                    for base in BASES:
                        a, b = get(table, base, point), get(table, base + suffix, point)
                        if a is not None and b is not None:
                            deltas.append((base, 100 * (b.safe_hit_rate - a.safe_hit_rate)))
                    if deltas:
                        values = [d for _, d in deltas]
                        detail = ", ".join(f"{k} {v:+.1f}" for k, v in deltas)
                        out(f"- {LANGS[lang]} {criterion} {budget:g} {suffix}: {min(values):+.1f} to {max(values):+.1f} ({detail})")
    out()


def ms(value: float) -> str:
    return f"{value:.3f}" if value < 0.1 else f"{value:.2f}" if value < 1 else f"{value:.1f}"


def section_latency_table() -> None:
    path = RESULTS / "latency_fa.csv"
    if not path.is_file():
        return
    table = pd.read_csv(path)
    meta = json.loads((RESULTS / "latency_fa.json").read_text())
    if "signature_buckets" not in meta:
        return
    out("## Manuscript Table 9 rows (median CPU ms, p95 in parentheses)\n")
    labels = [("trigram", "Trigram, pure-Python scan, no guard"),
              ("trigram (vectorised)", "Trigram, one sparse-matrix product, no guard"),
              ("trigram + induced guard (scan)", "Trigram, scan, induced guard tested first"),
              ("trigram + induced guard (bucketed)", "Trigram, index grouped by induced signature"),
              ("trigram + deployed guard (scan)", "Trigram, scan, deployed guard tested first (as deployed)"),
              ("trigram + deployed guard (bucketed)", "Trigram, index grouped by deployed signature")]
    sizes = sorted(table.cache_entries[table.cache_entries > 0].unique())
    for method, label in labels:
        cells = []
        for size in sizes:
            row = table[(table.method == method) & (table.cache_entries == size) & (table.part == "total")]
            cells.append("–" if row.empty else f"{ms(row.iloc[0].cpu_median_ms)} ({ms(row.iloc[0].cpu_p95_ms)})")
        out(f"| {label} | " + " | ".join(cells) + " |")
    for key, label in (("minilm", "MiniLM"), ("mpnet", "mpnet"), ("e5", "e5"), ("bgem3", "BGE-M3")):
        cells = []
        for size in sizes:
            row = table[table.method.str.startswith(key + " ") & (table.cache_entries == size) & (table.part == "total")]
            cells.append("–" if row.empty else f"{ms(row.iloc[0].cpu_median_ms)} ({ms(row.iloc[0].cpu_p95_ms)})")
        out(f"| {label}: encode and search | " + " | ".join(cells) + " |")
    out()
    for key in ("minilm", "mpnet", "e5", "bgem3"):
        enc = table[table.method.str.startswith(key + " ") & (table.part == "encode")]
        search = table[table.method.str.startswith(key + " ") & (table.part == "search")]
        if not enc.empty:
            out(f"- {key}: encode median {enc.iloc[0].cpu_median_ms:.1f} ms; search medians "
                + ", ".join(f"{r.cache_entries}: {r.cpu_median_ms:.2f} ms" for r in search.itertuples()))
    for name, info in meta["signature_buckets"].items():
        out(f"- signature buckets {name}: {info}")
    out(f"- load average at start {meta['load_average_at_start']}, at end {meta['load_average_at_end']}")
    out()


def section_ucb() -> None:
    frames = [pd.read_csv(RESULTS / f"ucb_{lang}.csv") for lang in LANGS if (RESULTS / f"ucb_{lang}.csv").is_file()]
    if not frames:
        return
    table = pd.concat(frames)
    out("## Thresholds with a 95% upper confidence bound on the dev error (ucb_thresholds.py)\n")
    table["over"] = table.test_unsafe > table.budget + 1e-12
    table["filter"] = table.method.map(lambda m: m.split("+", 1)[1] if "+" in m else "none")
    for (lang, rule), part in table.groupby(["lang", "rule"]):
        out(f"- {LANGS[lang]}, {rule}: budget exceeded on test in {int(part.over.sum())} of {len(part)} cells; "
            f"max excess {100 * (part.test_unsafe - part.budget).max():.2f} points")
    out()
    pivot = table.pivot_table(index=["lang", "criterion", "budget", "filter"], columns="rule",
                              values="test_safe", aggfunc="mean")
    out(md((100 * pivot).round(1)))
    out()


def main() -> None:
    out("# Numbers quoted in the paper\n")
    out("Criteria: `intent` (a hit is correct when the two requests have the same intent) and `strict` (same intent "
        "and same slots). All rates are per query of the test split unless marked.\n")
    for build in (section_data, section_exact, section_defaults, section_error_types, section_guard_defaults,
                  section_swaps, section_tuned, section_equal_risk, section_minimal_pairs, section_lexicon,
                  section_norules, section_latency, section_manuscript_tables,
                  section_equal_risk_deltas, section_latency_table, section_ucb):
        try:
            build()
        except (FileNotFoundError, KeyError) as error:  # a result file is missing or from an older run
            out(f"(section {build.__name__} skipped: {error!r})\n")
            print(f"section {build.__name__} skipped: {error!r}")
    (RESULTS / "paper_numbers.md").write_text("\n".join(LINES) + "\n")
    print(f"wrote {RESULTS / 'paper_numbers.md'} ({len(LINES)} lines)")


if __name__ == "__main__":
    main()
