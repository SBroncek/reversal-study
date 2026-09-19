"""Stage 3, part 1: how confident can we actually be in the headline spread?

No number is quoted in this docstring on purpose. The one that used to sit here was
+0.0855, from a 99-name universe, and it was still being read as current after the
universe changed. Every figure in this file is printed by a run.

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
    # dropna: CORRECTED 17 Sept. The old comment said this guard never fires. It
    # was firing, and it was the only thing catching a bad week. A week whose
    # forward returns covered a single name reached the means table with four of
    # five buckets empty, and this dropna silently removed it, which is why
    # buckets.py printed 522 weeks while this file printed 521. Silently removing
    # a broken week is not a fix, because the same week still polluted the column
    # averages in buckets.py. The real guard now lives in bucket_means, which
    # requires MIN_NAMES forward returns before a week is built at all.
    #
    # Kept, for two reasons. It is the reason the discrepancy was visible at all,
    # and it would do real work if buckets were ever cut on raw values (pd.cut,
    # equal-WIDTH bands) instead of ranks, since a calm week can leave such a band
    # empty. A subtraction against NaN would otherwise shorten the sample quietly.
    #
    # The 526 anchors become 521 weeks in bucket_means, not here. Losses are:
    # the first anchor (no prior week, so no signal) and the last four (only one
    # ticker has data past 25 Aug 2026, so no week after 21 Aug clears MIN_NAMES).
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
        # Sign carried into the bar, not just the number. With abs() the largest
        # value in the table (lag 4, -0.13) drew the same bar a +0.13 would, and
        # the picture is what the eye reads first.
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
    # NOT A POWER CALCULATION, and the difference matters. This treats the
    # OBSERVED mean and sd as if they were the true ones, and the observed mean
    # is the quantity we have just shown is indistinguishable from zero. A
    # smaller true mean needs more weeks; a true mean of zero needs infinitely
    # many. Read it as a statement of the size of the gap, never as a plan.
    print("  (Assumes the observed mean IS the truth, so it is a scale for the")
    print("   gap, not a power calculation. If the true mean is smaller, worse.)")


def diversification(means: pd.DataFrame, forward: pd.DataFrame) -> None:
    """Why the measured spread SD is what it is, rather than what independence predicts.

    This block exists because the README states these five numbers, and a number
    quoted in prose with no code behind it is a stale surface waiting to happen.
    Every figure in that paragraph is printed here, so a re-run either reproduces
    the README or contradicts it out loud.

    The substantive point is that averaging 20 names inside a bucket does NOT cut
    their noise by root 20, because all 20 carry the same week's market move. That
    is the single assumption most likely to make a bucket study look significant
    when it is not, and it is worth measuring rather than asserting.
    """
    lo, hi = means.columns[0], means.columns[-1]
    b1, b5 = means[lo], means[hi]
    spread = (b1 - b5).dropna()

    sd_name = forward.stack().std(ddof=1)
    n_per_bucket = 20

    print("\n=== WHY THE SPREAD SD IS NOT THE DIVERSIFIED FIGURE ===")
    print(f"  SD of one name's weekly forward return : {sd_name * 100:.4f} %")
    print(f"  if 20 names were independent, / root 20: "
          f"{sd_name / np.sqrt(n_per_bucket) * 100:.4f} %")
    print(f"  two such buckets differenced, x root 2 : "
          f"{sd_name * np.sqrt(2) / np.sqrt(n_per_bucket) * 100:.4f} %")
    print(f"  MEASURED SD of bucket {lo} weekly mean   : {b1.std(ddof=1) * 100:.4f} %")
    print(f"  MEASURED SD of bucket {hi} weekly mean   : {b5.std(ddof=1) * 100:.4f} %")
    print(f"  corr(bucket {lo}, bucket {hi})               : {b1.corr(b5):.4f}")
    print(f"  SD if those two were independent       : "
          f"{np.sqrt(b1.var(ddof=1) + b5.var(ddof=1)) * 100:.4f} %")
    print(f"  MEASURED SD of the spread              : {spread.std(ddof=1) * 100:.4f} %")
    print("  So differencing does real work, and averaging inside a bucket does far")
    print("  less than root 20 of it.")


if __name__ == "__main__":
    panel = load_universe()
    signal, forward = build(panel)
    means = bucket_means(signal, forward)

    report(weekly_spread(means))
    diversification(means, forward)
