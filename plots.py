"""Charts for the README. Reads nothing new: same panel, same functions.

WHY THIS FILE EXISTS (Sam, 15 Sept): the bucket shape was being argued over by
reading rows of numbers, and both of us misread which end the steep part was on.
A shape claim needs a picture, or it is a guess about decimals.

The error bars are +/- 1 standard error of that bucket's mean, computed the same
way as everywhere else in this repo. The weekly bucket means are the data, so the
SE is their standard deviation over weeks divided by sqrt(number of weeks). It is
NOT the spread of individual stocks, because a stock is not an observation here, a
week is.

NO CAPTION ON THE FIGURE (Sam, 19 Sept): "its just the visual for the data and it
just goes where the table is". The chart states nothing the table does not. The
old suptitle asserted that every error bar spans the dotted mean and no bucket is
distinguishable, which was TRUE on the 99-name panel and is FALSE on this one:
at 10 buckets, bucket 1 runs [+0.404, +0.701] against a grand mean of +0.378.
That is one bar of ten clearing, which is about what noise gives, and the study's
actual test is bucket 1 against bucket 5 with its own error bar. A figure that
argues is a figure that can go stale. This one only draws.

TWO FILES, one per table it illustrates. bucket_shape.png is the five-bucket cut,
which is the pre-specified one, and sits with the bucket means table. Sam's rule
is that the visual goes where its table is.
"""

import matplotlib
matplotlib.use("Agg")                 # no display on this machine; write to file
import matplotlib.pyplot as plt
import numpy as np

from download import load_universe
from signal_build import build
from buckets import bucket_means

OUT = "docs"


def bucket_plot(signal, forward, counts=(3, 5, 10), path=f"{OUT}/bucket_shape.png"):
    w = 5.0 if len(counts) == 1 else 13.0
    fig, axes = plt.subplots(1, len(counts), figsize=(w, 4), sharey=True,
                             squeeze=False)
    axes = axes[0]

    for ax, n in zip(axes, counts):
        means = bucket_means(signal, forward, n_buckets=n)
        mu = means.mean() * 100                       # %/week
        se = means.std(ddof=1) / np.sqrt(len(means)) * 100

        x = np.arange(1, n + 1)
        ax.errorbar(x, mu, yerr=se, marker="o", capsize=3, lw=1.5)
        ax.axhline(mu.mean(), ls=":", lw=1, color="grey")
        ax.set_title(f"{n} buckets  ({len(signal.columns)//n} names each)")
        ax.set_xlabel("bucket   (1 = biggest losers)")
        ax.set_xticks(x)
        ax.grid(alpha=.3)

    axes[0].set_ylabel("mean forward return, %/week")
    fig.tight_layout()
    fig.savefig(path, dpi=130)
    print("wrote", path)


if __name__ == "__main__":
    import os
    os.makedirs(OUT, exist_ok=True)
    panel = load_universe()
    signal, forward = build(panel)
    bucket_plot(signal, forward, counts=(5,), path=f"{OUT}/bucket_shape.png")
    bucket_plot(signal, forward, counts=(3, 5, 10),
                path=f"{OUT}/bucket_shape_counts.png")
