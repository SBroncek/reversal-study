"""Robustness dial: the number of buckets, 3 vs 5 vs 10.

Narrower buckets make each end a more extreme slice, which should widen the
spread, and hold fewer names, which should grow the standard error. The t-stat is
the race between those two, and which wins is not predictable from the armchair.

The check is not "does it stay significant", since it never was. It is whether the
sign stays put and the magnitude stays the same order.
"""

import numpy as np
import pandas as pd

from download import load_universe
from signal_build import build
from buckets import bucket_means
from errorbars import weekly_spread, newey_west_se, default_lag


def run_one(signal: pd.DataFrame, forward: pd.DataFrame, n: int) -> dict:
    """One full bucket test at n buckets, with both error bars."""
    means = bucket_means(signal, forward, n_buckets=n)
    d = weekly_spread(means)          # the 1-minus-n spread, one number per week

    T = len(d)
    mean = d.mean()
    sd = d.std(ddof=1)
    se = sd / np.sqrt(T)
    nw = newey_west_se(d, default_lag(T))

    return {
        "n_buckets": n,
        "weeks": T,
        "names_per_bucket": len(signal.columns) / n,   # nominal
        "spread": mean,
        "sd": sd,
        "se": se,
        "t": mean / se,
        "se_nw": nw,
        "t_nw": mean / nw,
        "per_bucket": means.mean(),
    }


if __name__ == "__main__":
    panel = load_universe()
    signal, forward = build(panel)

    results = [run_one(signal, forward, n) for n in (3, 5, 10)]

    print("\nSPREAD (bucket 1 minus bucket n), %/week\n")
    print(f"{'buckets':>8} {'weeks':>6} {'names/bkt':>10} "
          f"{'spread':>9} {'SE':>8} {'t':>7} {'SE(NW)':>8} {'t(NW)':>7}")
    for r in results:
        print(f"{r['n_buckets']:>8} {r['weeks']:>6} {r['names_per_bucket']:>10.1f} "
              f"{r['spread']*100:>+9.4f} {r['se']*100:>8.4f} {r['t']:>+7.3f} "
              f"{r['se_nw']*100:>8.4f} {r['t_nw']:>+7.3f}")

    print("\nmean forward return by bucket, %/week (the SHAPE of the sort):")
    for r in results:
        row = "  ".join(f"{v*100:+.3f}" for v in r["per_bucket"])
        print(f"  {r['n_buckets']:>2} buckets: {row}")

    print("\nsign of the spread, by bucket count:",
          [("+" if r["spread"] > 0 else "-") for r in results])
