"""
Parametric cross-check: Fama-MacBeth regression of forward return on signal.

The bucket test (buckets.py) throws the magnitudes away and keeps only the
ordering. This does the opposite: it keeps the magnitudes and fits a straight
line, so the slope answers "how much extra forward return per extra unit of
last week's fall".

The two tests fail differently, which is the whole reason for running both.
A regression assumes linearity. The bucket table is NOT monotonic - both
extremes beat the middle - so a straight line is known in advance to be a poor
description here, and the slope will average that U into something near zero.
Agreement between the two would be evidence; disagreement is the finding.
"""

import numpy as np
import pandas as pd

from download import load_universe
from signal_build import build

# Same threshold buckets.py uses, for the same reason: a week with too few
# names is estimating a slope from almost nothing. Kept identical so the two
# tests run on the same set of weeks and remain comparable.
MIN_NAMES = 40


def week_slope(x: pd.Series, y: pd.Series) -> float:
    """OLS slope of y on x for a single week's cross-section.

    Closed form rather than a library call: slope = Sxy / Sxx, the covariance
    of signal and forward return divided by the variance of the signal. With
    one regressor there is nothing a solver would add, and this way the
    quantity in the denominator is visible.
    """
    pair = pd.concat([x, y], axis=1).dropna()      # [scaffold] a name needs BOTH numbers to be a dot
    if len(pair) < MIN_NAMES:
        return np.nan

    xv = pair.iloc[:, 0].to_numpy()
    yv = pair.iloc[:, 1].to_numpy()

    sxx = ((xv - xv.mean()) ** 2).sum()
    sxy = ((xv - xv.mean()) * (yv - yv.mean())).sum()
    return sxy / sxx


def slope_series(signal: pd.DataFrame, forward: pd.DataFrame) -> pd.Series:
    """Step 1 of Fama-MacBeth: one cross-sectional regression per week.

    Returns one slope per week. This is the object the whole method rests on:
    521 estimates, each computed from a single week's ~99 names, each one
    blind to every other week.
    """
    slopes = {d: week_slope(signal.loc[d], forward.loc[d]) for d in signal.index}
    return pd.Series(slopes).dropna()


def fama_macbeth(slopes: pd.Series) -> dict:
    """Step 2: treat the weekly slopes as the data. No second regression.

    The standard error is MEASURED from the week-to-week scatter of the slopes
    themselves, not modelled from a within-week formula. That is the whole
    point: it never assumes the 99 names in a week are independent, because it
    never looks inside a week again.
    """
    n = len(slopes)
    mean = slopes.mean()
    sd = slopes.std(ddof=1)          # [scaffold] ddof=1: sample SD, divides by n-1
    se = sd / np.sqrt(n)
    return {"n_weeks": n, "mean": mean, "sd": sd, "se": se, "t": mean / se}


if __name__ == "__main__":
    panel = load_universe()
    signal, forward = build(panel)
    slopes = slope_series(signal, forward)
    r = fama_macbeth(slopes)

    print(f"\nweeks with a slope: {r['n_weeks']}")
    print("\nFama-MacBeth, forward return on signal:")
    print(f"  mean slope        : {r['mean']:+.5f}")
    print(f"  weekly SD         : {r['sd']:.5f}")
    print(f"  standard error    : {r['se']:.5f}")
    print(f"  t-stat            : {r['t']:+.3f}")
    print(f"\n  slopes negative in {(slopes < 0).sum()} of {len(slopes)} weeks "
          f"({100 * (slopes < 0).mean():.1f}%)")

    # Computed live, not quoted. This line held a hard-coded +0.0855 at t = +0.79
    # from an earlier 99-name run and was still printing it after the universe
    # changed, which is a stale surface inside the code itself (fixed 17 Sept).
    #
    # The two disagree in ECONOMIC direction, which is not the same as disagreeing
    # in printed sign, and the old comment conflated them. Both numbers print
    # positive. The signal here is the past-week return, so a positive SLOPE means
    # last week's winners did better, which is momentum. A positive bucket SPREAD
    # is bucket 1 minus bucket 5, last week's losers minus last week's winners,
    # which is reversal. Same sign on the page, opposite claim about the world.
    from buckets import bucket_means, summarise
    from errorbars import weekly_spread
    means = bucket_means(signal, forward)
    spread = weekly_spread(means)
    t_spread = spread.mean() / (spread.std(ddof=1) / np.sqrt(len(spread)))
    print(f"\n  compare: bucket spread {spread.mean() * 100:+.4f} %/week at "
          f"t = {t_spread:+.2f}, over {len(spread)} weeks")
    print("    slope positive means momentum, bucket spread positive means "
          "reversal, so these two lean opposite ways")
