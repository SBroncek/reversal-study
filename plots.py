"""Charts for the README. Reads nothing new: same panel, same functions.

Error bars are +/- 1 standard error of that bucket's weekly mean: the standard
deviation of the weekly means over sqrt(weeks). Not the spread of individual
stocks, since a week is the observation and a stock is not.

No caption on the figure. A figure that argues can go stale; this one only draws.
Two files, one per table it illustrates.
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
