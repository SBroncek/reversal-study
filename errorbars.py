"""Stage 3, part 1: how confident can we actually be in +0.0855 %/week?

THE UNIT OF OBSERVATION IS THE WEEK. Not the stock, not the stock-week. The study
makes one number per week (the bucket 1 minus bucket 5 spread), so the sample size
is 521, not 521 x 99. Getting this wrong is the single easiest way to manufacture
significance out of nothing: treating stock-weeks as independent observations would
divide the standard error by roughly sqrt(99) and turn a non-result into a
"discovery".

Working with the spread rather than the buckets separately is also what makes the
error bar honest. Bucket 1 and bucket 5 both contain most of the market's move that
week, and that shared move does not diversify away. Differencing them cancels it,
so the spread is not merely the cleanest STATEMENT of the answer, it is a
substantially LOWER-VARIANCE estimator than either bucket on its own.

WHY THERE IS A SECOND STANDARD ERROR IN HERE. The textbook s/sqrt(T) assumes the
521 weekly spreads are independent draws. They are not: a factor that pays this
week tends to pay next week, so the series is autocorrelated. Positive
autocorrelation makes s/sqrt(T) TOO SMALL, which makes a study look MORE
significant than it is, not less. So the autocorrelation is measured first and
printed, and then a Newey-West standard error is reported next to the naive one.
Both are shown deliberately. Quoting only the flattering one is the same failure as
reporting bucket 1 minus bucket 4.

NO PER-BUCKET T-STATS. Testing whether bucket 3's mean forward return differs from
zero would be testing whether the stock market went up over ten years. It did. That
is not this study's question and the number would be large and meaningless.
"""

import numpy as np
import pandas as pd

from download import load_universe
from signal_build import build
from buckets import bucket_means

# Weeks per year. Used only to annualise, never inside the test itself.
WEEKS_PER_YEAR = 52


def weekly_spread(means: pd.DataFrame) -> pd.Series:
    """The study's actual sample: one bucket-1-minus-bucket-5 number per week."""
    lo, hi = means.columns[0], means.columns[-1]
    # dropna guards the case where a week produced one bucket but not the other.
    # It does not fire on this panel, but a subtraction against NaN would silently
    # shorten the sample rather than announcing itself.
    return (means[lo] - means[hi]).dropna()


def autocorrelation(d: pd.Series, max_lag: int = 10) -> pd.Series:
    """rho_k for k = 1..max_lag: how much this week's spread predicts week t+k.

    Computed the textbook way, dividing every lag by the SAME variance (gamma_0)
    and the SAME T. pandas' .autocorr() instead correlates two shortened, separately
    demeaned series, which is a slightly different estimator and does not compose
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
    """Standard error of the MEAN, allowing the weeks to be correlated.

    The idea in one sentence: the variance of a sum of correlated terms is the sum
    of the variances PLUS twice all the covariances, so the naive formula is simply
    missing the covariance terms, and this adds them back.

    The Bartlett weight (1 - k/(lag+1)) tapers the covariances toward zero as the
    lag grows. It is not cosmetic: without it the estimated variance can come out
    NEGATIVE, which is nonsense for a variance. Tapering guarantees it cannot.
    """
    x = d.to_numpy()
    T = len(x)
    dev = x - x.mean()

    gamma0 = (dev * dev).sum() / T
    total = gamma0
    for k in range(1, lag + 1):
        gamma_k = (dev[k:] * dev[:-k]).sum() / T
        total += 2.0 * (1.0 - k / (lag + 1.0)) * gamma_k

    # total is the long-run variance of a single week. Divide by T, as usual, to
    # get the variance of the average of T of them.
    return float(np.sqrt(total / T))


def default_lag(T: int) -> int:
    """Newey and West's own rule of thumb: floor(4 * (T/100)^(2/9)).

    Chosen because it is the convention, so it is not a knob that got turned until
    the answer looked good. The sensitivity table printed below is the check that
    the conclusion does not depend on it.
    """
    return int(np.floor(4.0 * (T / 100.0) ** (2.0 / 9.0)))


def report(d: pd.Series) -> None:
    T = len(d)
    mean = d.mean()
    # ddof=1: the sample standard deviation. s_d is MEASURED off the data, not
    # modelled from an assumed single-stock volatility. That is what makes the
    # within-bucket correlation problem vanish rather than needing to be solved:
    # whatever correlation exists between the 20 names is already inside the
    # observed week-to-week variation of the spread.
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
        bar = "#" * int(round(abs(v) * 100))
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
    # mean/sd is the Sharpe per week; sqrt(52) scales it to a year because the
    # mean grows with time while the standard deviation grows with sqrt(time).
    sharpe_weekly = mean / s_d
    print(f"  weekly    : {sharpe_weekly:.4f}")
    print(f"  annualised: {sharpe_weekly * np.sqrt(WEEKS_PER_YEAR):.3f}  "
          f"(fund bar is nearer 1, and this is BEFORE costs)")

    print("\n=== WHAT WOULD IT TAKE ===")
    # Inverted: how many weeks at this mean and this variability before t = 2?
    needed = (2.0 * s_d / mean) ** 2
    print(f"  weeks needed for the naive t to reach 2.0: {needed:,.0f} "
          f"({needed / WEEKS_PER_YEAR:,.0f} years)")
    print("  We have 10 years of data. That is the size of the gap.")


if __name__ == "__main__":
    panel = load_universe()
    signal, forward = build(panel)
    means = bucket_means(signal, forward)

    report(weekly_spread(means))
