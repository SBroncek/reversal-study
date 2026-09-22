"""Parametric cross-check: Fama-MacBeth regression of forward return on signal.

The bucket test throws magnitudes away and keeps the ordering. This keeps the
magnitudes and fits a straight line. The two fail differently, which is why both
are run. See the README for what the slope means and how it compares.
"""

import numpy as np
import pandas as pd

from download import load_universe
from signal_build import build

MIN_NAMES = 40      # same threshold as buckets.py, so both run on the same weeks


def week_slope(x: pd.Series, y: pd.Series) -> float:
    """OLS slope of y on x for a single week's cross-section.

    Closed form rather than a library call: with one regressor there is nothing a
    solver would add, and this way Sxx is visible in the denominator.
    """
    pair = pd.concat([x, y], axis=1).dropna()      # a name needs both numbers
    if len(pair) < MIN_NAMES:
        return np.nan

    xv = pair.iloc[:, 0].to_numpy()
    yv = pair.iloc[:, 1].to_numpy()

    sxx = ((xv - xv.mean()) ** 2).sum()
    sxy = ((xv - xv.mean()) * (yv - yv.mean())).sum()
    return sxy / sxx


def slope_series(signal: pd.DataFrame, forward: pd.DataFrame) -> pd.Series:
    """Step 1 of Fama-MacBeth: one cross-sectional regression per week."""
    slopes = {d: week_slope(signal.loc[d], forward.loc[d]) for d in signal.index}
    return pd.Series(slopes).dropna()


def fama_macbeth(slopes: pd.Series) -> dict:
    """Step 2: treat the weekly slopes as the data. No second regression.

    The standard error comes from the week-to-week scatter of the slopes, so it
    never assumes the names within a week are independent.
    """
    n = len(slopes)
    mean = slopes.mean()
    sd = slopes.std(ddof=1)
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

    from buckets import bucket_means
    from errorbars import weekly_spread
    means = bucket_means(signal, forward)
    spread = weekly_spread(means)
    t_spread = spread.mean() / (spread.std(ddof=1) / np.sqrt(len(spread)))
    print(f"\n  compare: bucket spread {spread.mean() * 100:+.4f} %/week at "
          f"t = {t_spread:+.2f}, over {len(spread)} weeks")
    print("    slope positive means momentum, bucket spread positive means "
          "reversal, so these two lean opposite ways")
