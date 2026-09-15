"""Charts for the README. Reads nothing new: same panel, same functions.

WHY THIS FILE EXISTS (Sam, 15 Sept): the bucket shape was being argued over by
reading rows of numbers, and both of us misread which end the steep part was on.
A shape claim needs a picture, or it is a guess about decimals.

The error bars are +/- 1 standard error of that bucket's mean, computed the same
way as everywhere else in this repo: the weekly bucket means are the data, so the
SE is their standard deviation over weeks divided by sqrt(number of weeks). It is
NOT the spread of individual stocks - a stock is not an observation here, a week
is.
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
    fig, axes = plt.subplots(1, len(counts), figsize=(13, 4), sharey=True)

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
    fig.suptitle("Forward return by past-return bucket, with +/-1 SE. "
                 "Every error bar spans the dotted mean: no bucket is distinguishable.",
                 fontsize=9)
    fig.tight_layout()
    fig.savefig(path, dpi=130)
    print("wrote", path)


if __name__ == "__main__":
    import os
    os.makedirs(OUT, exist_ok=True)
    panel = load_universe()
    signal, forward = build(panel)
    bucket_plot(signal, forward)
