"""Figures for the paper.

Figure 1 (tradeoff): safe-hit against unsafe-hit rate as the threshold varies,
test split, for BGE-M3 without guard, with the induced guard, with the intent
gate and with both, and for character trigrams without and with the guard.
Squares mark BGE-M3 at threshold 0.8, diamonds at the threshold chosen on dev
for the tighter budget of each criterion. The other encoders and policies are
in results/curves_*.csv.
Figure 2 (minimal_pairs): similarity of one-word minimal pairs by pair type.
Figure 3 (minimal_pairs_roc): ROC curves of each similarity for separating
same-meaning pairs from different-intent and from different-argument pairs,
with the operating points of the induced and the frequency-only guards.

All are written as PDF and as 200-dpi PNG to figures/ and to every extra
directory given with --out.

Usage: python experiments/figures.py [--out ../../papers/02-guarded-reply-cache/figures]
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from sklearn.metrics import roc_curve  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "experiments"))
from compare import dev_threshold  # noqa: E402

RESULTS = ROOT / "results"
FIGURES = ROOT / "figures"
LABELS = {"tri": "char. trigrams", "minilm": "MiniLM-L12", "mpnet": "mpnet-base", "e5": "mE5-base",
          "bgem3": "BGE-M3"}
# Categorical slots of the validated reference palette, in fixed order; markers add a second cue.
COLORS = {"tri": "#2a78d6", "minilm": "#eb6834", "mpnet": "#1baf7a", "e5": "#eda100", "bgem3": "#e87ba4"}
MARKERS = {"tri": "o", "minilm": "s", "mpnet": "^", "e5": "D", "bgem3": "v"}
KINDS = {"same_meaning": ("same meaning", "#2a78d6"), "different_intent": ("different intent", "#eb6834"),
         "different_argument": ("different argument", "#1baf7a")}
INK, MUTED = "#0b0b0b", "#52514e"
TIGHT = {"intent": 0.01, "strict": 0.02}

plt.rcParams.update({"font.size": 9, "axes.edgecolor": MUTED, "axes.labelcolor": INK, "xtick.color": MUTED,
                     "ytick.color": MUTED, "axes.spines.top": False, "axes.spines.right": False})


def runs_arrays(runs: pd.DataFrame, method: str, column: str) -> tuple[np.ndarray, np.ndarray]:
    group = runs[runs.method == method].sort_values("q")
    score = np.where(np.isfinite(group.score.to_numpy()), group.score.to_numpy(), -1.0)
    return score, group[column].to_numpy().astype(bool)


def point(score: np.ndarray, correct: np.ndarray, tau: float) -> tuple[float, float]:
    hit = score >= tau
    return 100 * float((hit & ~correct).mean()), 100 * float((hit & correct).mean())


VARIANTS = {"": ("no guard", "#52514e", "--"), "+ind": ("induced guard", "#2a78d6", "-"),
            "+gate": ("intent gate", "#eb6834", "-."), "+gate+ind": ("gate and guard", "#1baf7a", "-")}


def panel(ax, lang: str, criterion: str, x_max: float) -> None:
    column = "action_ok" if criterion == "intent" else "correct"
    test = pd.read_csv(RESULTS / f"runs_{lang}_test.csv")
    dev = pd.read_csv(RESULTS / f"runs_{lang}_dev.csv")
    curves = pd.read_csv(RESULTS / f"curves_{lang}_test_{criterion}.csv")
    top = 0.0
    for base, width, alpha in (("tri", 1.0, 0.75), ("bgem3", 1.7, 1.0)):
        for suffix, (name, color, style) in VARIANTS.items():
            method = base + suffix
            if base == "tri" and suffix not in ("", "+ind"):
                continue
            data = curves[curves.method == method].sort_values("unsafe_hit_rate")
            if data.empty:
                continue
            data = data[data.unsafe_hit_rate * 100 <= x_max * 1.02]
            top = max(top, data.safe_hit_rate.max())
            line_style = ":" if base == "tri" else style
            ax.plot(100 * data.unsafe_hit_rate, 100 * data.safe_hit_rate, line_style, color=color, lw=width,
                    alpha=alpha, label=f"{LABELS[base]}, {name}")
            if base != "bgem3":
                continue
            score, correct = runs_arrays(test, method, column)
            x, y = point(score, correct, 0.8)
            if x <= x_max:
                ax.plot(x, y, "s", color=color, mfc="white", mew=1.4, ms=6, zorder=4)
            tau = dev_threshold(*runs_arrays(dev, method, column), TIGHT[criterion])
            if tau is not None:
                x, y = point(score, correct, tau)
                ax.plot(x, y, "D", color=color, ms=5.5, zorder=4)
    for name, marker in (("exact_norm", "o"), ("exact_canon", "P")):
        exact = curves[(curves.method == name) & (curves.tau == 1.0)]
        if not exact.empty:
            ax.plot(100 * exact.unsafe_hit_rate, 100 * exact.safe_hit_rate, marker, color=INK, ms=5, zorder=5)
    ax.axvline(100 * TIGHT[criterion], color=MUTED, lw=0.7, ls=":")
    ax.set_xlim(0, x_max)
    ax.set_ylim(0, 5 * np.ceil(110 * top / 5))
    ax.set_xlabel("unsafe hits (% of queries)")
    ax.set_ylabel("safe hits (% of queries)")
    what = {"intent": "wrong intent", "strict": "wrong intent or argument"}[criterion]
    ax.set_title(f"{ {'fa': 'Persian', 'en': 'English'}[lang]}: unsafe = {what}", fontsize=9.5, color=INK)
    ax.grid(alpha=0.25, lw=0.6)


def tradeoff() -> plt.Figure:
    fig, axes = plt.subplots(2, 2, figsize=(9, 8.0))
    for row, criterion in enumerate(("intent", "strict")):
        for col, lang in enumerate(("fa", "en")):
            panel(axes[row, col], lang, criterion, 5 if criterion == "intent" else 10)
    handles, labels = axes[0, 0].get_legend_handles_labels()
    extra = [plt.Line2D([], [], ls="", marker="s", color=MUTED, mfc="white", mew=1.4, ms=6),
             plt.Line2D([], [], ls="", marker="D", color=MUTED, ms=5.5),
             plt.Line2D([], [], ls="", marker="o", color=INK, ms=5),
             plt.Line2D([], [], ls="", marker="P", color=INK, ms=5)]
    labels += ["BGE-M3 at threshold 0.8", "BGE-M3 at the threshold chosen on dev (1% / 2% budget)",
               "exact: identical normalised request", "exact: identical canonical key"]
    fig.legend(handles + extra, labels, loc="lower center", ncol=2, fontsize=8, frameon=False)
    fig.tight_layout(rect=(0, 0.14, 1, 1))
    return fig


def minimal_pairs() -> plt.Figure:
    fig, axes = plt.subplots(1, 2, figsize=(9, 3.6), sharey=True)
    for ax, lang in zip(axes, ("fa", "en")):
        table = pd.read_csv(RESULTS / f"minimal_pairs_{lang}.csv")
        methods = [m for m in COLORS if m in table.columns]
        width = 0.24
        for offset, (kind, (label, color)) in zip((-width, 0.0, width), KINDS.items()):
            data = [table.loc[table.kind == kind, m].to_numpy() for m in methods]
            positions = np.arange(len(methods)) + offset
            parts = ax.boxplot(data, positions=positions, widths=width * 0.85, patch_artist=True, showfliers=False,
                               medianprops={"color": INK, "lw": 1.2}, whiskerprops={"color": MUTED},
                               capprops={"color": MUTED})
            for box in parts["boxes"]:
                box.set_facecolor(color)
                box.set_edgecolor("white")
                box.set_alpha(0.9)
            ax.plot([], [], "s", color=color, label=label)
        ax.set_xticks(np.arange(len(methods)), [LABELS[m] for m in methods], fontsize=8)
        ax.set_title({"fa": "Persian", "en": "English"}[lang] + f" ({len(table)} pairs)", fontsize=9.5, color=INK)
        ax.grid(axis="y", alpha=0.25, lw=0.6)
    axes[0].set_ylabel("similarity of the two requests")
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=3, fontsize=8, frameon=False)
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    return fig


def minimal_pairs_roc() -> plt.Figure:
    fig, axes = plt.subplots(2, 2, figsize=(9, 7.6))
    for col, lang in enumerate(("fa", "en")):
        table = pd.read_csv(RESULTS / f"minimal_pairs_{lang}.csv")
        same = table.kind == "same_meaning"
        for row, kind in enumerate(("different_intent", "different_argument")):
            ax = axes[row, col]
            other = table.kind == kind
            for method in [m for m in COLORS if m in table.columns]:
                y = np.r_[np.ones(same.sum()), np.zeros(other.sum())]
                s = np.r_[table[method][same], table[method][other]]
                fpr, tpr, _ = roc_curve(y, s)
                ax.plot(100 * fpr, 100 * tpr, color=COLORS[method], lw=1.3, label=LABELS[method])
            for guard, marker, label in (("blocked_ind", "*", "induced guard"),
                                         ("blocked_freq", "X", "frequency-only guard"),
                                         ("blocked_dep", "P", "deployed guard")):
                if guard not in table:
                    continue
                ax.plot(100 * (1 - table[guard][other].mean()), 100 * (1 - table[guard][same].mean()), marker,
                        color=INK, ms=9 if marker == "*" else 7, zorder=5, label=label)
            ax.plot([0, 100], [0, 100], color=MUTED, lw=0.6, ls=":")
            ax.set_xlim(0, 100)
            ax.set_ylim(0, 100)
            ax.set_xlabel(f"{KINDS[kind][0]} pairs let through (%)")
            ax.set_ylabel("same-meaning pairs let through (%)")
            ax.set_title(f"{ {'fa': 'Persian', 'en': 'English'}[lang]}: same meaning vs {KINDS[kind][0]}",
                         fontsize=9.5, color=INK)
            ax.grid(alpha=0.25, lw=0.6)
    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=4, fontsize=8, frameon=False)
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    return fig


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", action="append", default=[], help="extra directory to copy the figures to")
    args = parser.parse_args()
    FIGURES.mkdir(exist_ok=True)
    for name, build in (("tradeoff", tradeoff), ("minimal_pairs", minimal_pairs),
                        ("minimal_pairs_roc", minimal_pairs_roc)):
        fig = build()
        fig.savefig(FIGURES / f"{name}.pdf")
        fig.savefig(FIGURES / f"{name}.png", dpi=200)
        plt.close(fig)
        for extra in args.out:
            target = Path(extra)
            target.mkdir(parents=True, exist_ok=True)
            for suffix in (".pdf", ".png"):
                shutil.copy2(FIGURES / f"{name}{suffix}", target / f"{name}{suffix}")
        print("wrote", FIGURES / f"{name}.pdf", "and .png")


if __name__ == "__main__":
    main()
