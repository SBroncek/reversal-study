"""Robustness: does the bucket result survive changing the arbitrary dials?

A "robustness check" is the same test rerun with one setting changed. It is not
a new question. The point is that nothing in the market says "five buckets", so
if the finding lives or dies on that number then the finding was about the
setting, not about stocks.

THE DIAL TESTED HERE: the number of buckets, 3 vs 5 vs 10.

What moves when it changes, and the two effects pull opposite ways:

  MORE buckets -> each end bucket is a more EXTREME slice of the cross-section
  (top 10% rather than top 20%), so the spread between the ends should WIDEN.

  MORE buckets -> each end bucket holds FEWER names (99/10 is about 10 stocks,
  against 20 at quintiles), so each week's bucket mean is noisier, so the
  standard error should GROW.

  The t-statistic is spread divided by its standard error, so it is a race
  between those two. Which one wins is not predictable from the armchair, which
  is the entire reason this file exists rather than an argument.

A NOTE ON WHAT WOULD COUNT AS A FAILURE. This study's headline is a NULL: the
quintile spread is +0.0855 %/week at t = +0.79, which is not distinguishable
from zero. So the check here is not "does it stay significant" - it never was.
It is "does the SIGN stay put and does the magnitude stay the same order".
A null that becomes a strong positive at 10 buckets and a strong negative at 3
would mean the panel is being fitted, not measured.
"""

import numpy as np
import pandas as pd

from download import load_universe
from signal_build import build
from buckets import bucket_means
from errorbars import weekly_spread, newey_west_se, default_lag

WEEKS_PER_YEAR = 52


def run_one(signal: pd.DataFrame, forward: pd.DataFrame, n: int) -> dict:
    """One full bucket test at n buckets, with both error bars."""
    means = bucket_means(signal, forward, n_buckets=n)
    d = weekly_spread(means)          # the 1-minus-n spread, one number per week

    T = len(d)
    mean = d.mean()
    sd = d.std(ddof=1)                # ddof=1: sample SD, divides by T-1
    se = sd / np.sqrt(T)
    nw = newey_west_se(d, default_lag(T))

    return {
        "n_buckets": n,
        "weeks": T,
        "names_per_bucket": len(signal.columns) / n,   # nominal, ~99 names
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
