"""Standard errors for the headline spread: naive, autocorrelation, Newey-West.

Every figure is printed by a run. No number is quoted in this file, because one
that was (+0.0855, from a 99-name universe) was still being read as current after
the universe changed. See the README for the unit of observation and what the
numbers mean.
"""

import numpy as np
import pandas as pd

from download import load_universe
from signal_build import build
from buckets import bucket_means

WEEKS_PER_YEAR = 52     # annualisation only, never inside the test


def weekly_spread(means: pd.DataFrame) -> pd.Series:
    """The study's actual sample: one bucket-1-minus-bucket-5 number per week."""
    lo, hi = means.columns[0], means.columns[-1]
    # The real guard is MIN_NAMES in bucket_means; this dropna no longer has a bad
    # week to catch. Kept because it would do real work if buckets were ever cut on
    # raw values (pd.cut, equal-width bands), where a calm week can leave a band
    # empty and a subtraction against NaN would shorten the sample quietly.
    return (means[lo] - means[hi]).dropna()


def autocorrelation(d: pd.Series, max_lag: int = 10) -> pd.Series:
    """rho_k for k = 1..max_lag: how much this week's spread predicts week t+k.

    Every lag divided by the same gamma_0 and the same T. pandas' .autocorr()
    correlates two shortened, separately demeaned series, which does not compose
    into the Newey-West sum below.
    """
    x = d.to_numpy()
    T = len(x)
    dev = x - x.mean()
    gamma0 = (dev * dev).sum() / T
    return pd.Series(
        {k: (dev[k:] * dev[:-k]).sum() / T / gamma0 for k in range(1, max_lag + 1)},
        name="autocorrelation",
    )


def newey_west_se(d: pd.Series, lag: int) -> float:
    """Standard error of the MEAN, allowing the weeks to be correlated."""
    x = d.to_numpy()
    T = len(x)
    dev = x - x.mean()

    gamma0 = (dev * dev).sum() / T
    total = gamma0
    for k in range(1, lag + 1):
        gamma_k = (dev[k:] * dev[:-k]).sum() / T
        # Bartlett weight: tapers the covariances toward zero as the lag grows,
        # which is what guarantees the variance cannot come out negative.
        total += 2.0 * (1.0 - k / (lag + 1.0)) * gamma_k

    # total is the long-run variance of one week; divide by T for the mean of T
    return float(np.sqrt(total / T))


def default_lag(T: int) -> int:
    """Newey and West's rule of thumb: floor(4 * (T/100)^(2/9)).

    The convention, so it is not a knob that got turned until the answer looked
    good. The sensitivity table below is the check on that.
    """
    return int(np.floor(4.0 * (T / 100.0) ** (2.0 / 9.0)))


def report(d: pd.Series) -> None:
    T = len(d)
    mean = d.mean()
    s_d = d.std(ddof=1)

    se_naive = s_d / np.sqrt(T)
    lag = default_lag(T)
    se_nw = newey_west_se(d, lag)

    print("\n=== THE SAMPLE ===")
    print(f"  weeks (the unit of observation): {T}")
    print(f"  mean weekly spread            : {mean * 100:+.4f} %")
    print(f"  weekly std dev of the spread  : {s_d * 100:.4f} %  (measured)")

    print("\n=== AUTOCORRELATION OF THE WEEKLY SPREAD ===")
    print("  (positive values mean the naive standard error below is too small)")
    rho = autocorrelation(d, max_lag=10)
    for k, v in rho.items():
        # sign carried into the bar: with abs() a negative lag drew the same bar
        # as a positive one, and the picture is what the eye reads first
        bar = ("+" if v >= 0 else "-") * int(round(abs(v) * 100))
        print(f"   lag {k:>2}: {v:+.4f}  {bar}")

    print("\n=== STANDARD ERRORS AND T-STATS ===")
    print(f"  naive  s/sqrt(T)      : {se_naive * 100:.4f} %   "
          f"t = {mean / se_naive:+.2f}")
    print(f"  Newey-West (lag {lag:>2})   : {se_nw * 100:.4f} %   "
          f"t = {mean / se_nw:+.2f}")

    print("\n  sensitivity of the Newey-West t-stat to the lag choice:")
    for L in (0, 2, 4, 6, 8, 10, 15, 20):
        se_l = newey_west_se(d, L)
        print(f"    lag {L:>2}: SE {se_l * 100:.4f} %   t = {mean / se_l:+.2f}")

    print("\n=== SHARPE RATIO ===")
    # mean/sd is the weekly Sharpe; sqrt(52) annualises because the mean grows
    # with time while the standard deviation grows with sqrt(time)
    sharpe_weekly = mean / s_d
    print(f"  weekly    : {sharpe_weekly:.4f}")
    print(f"  annualised: {sharpe_weekly * np.sqrt(WEEKS_PER_YEAR):.3f}  "
          f"(fund bar is nearer 1, and this is BEFORE costs)")

    print("\n=== WHAT WOULD IT TAKE ===")
    needed = (2.0 * s_d / mean) ** 2
    print(f"  weeks needed for the naive t to reach 2.0: {needed:,.0f} "
          f"({needed / WEEKS_PER_YEAR:,.0f} years)")
    print("  We have 10 years of data. That is the size of the gap.")
    print("  (Assumes the observed mean IS the truth, so it is a scale for the")
    print("   gap, not a power calculation. If the true mean is smaller, worse.)")


if __name__ == "__main__":
    panel = load_universe()
    signal, forward = build(panel)
    means = bucket_means(signal, forward)

    report(weekly_spread(means))
