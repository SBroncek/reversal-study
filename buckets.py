"""Stage 2, final chunk: sort each week's cross-section into buckets and measure
the forward return of each.

THE HEADLINE NUMBER: bucket 1 (last week's biggest losers) minus bucket 5 (last
week's biggest winners), averaged over every week in the sample. Positive means
losers went on to outperform winners, i.e. reversal.

Two conventions fixed here, both surfaced to Sam before they were written:

  RANKS, NOT RAW VALUES. Buckets are cut on the RANK of the signal, so every
  bucket holds the same number of names every week. Cutting on the raw return
  instead gives equal-WIDTH return bands, and the damage is measured, not
  hypothetical. Calmest week in the sample (2016-12-30), 99 names:

      ranks (qcut):  20  19  20  19  20
      raw   (cut):    1   5  43  47   2

  Bucket 1 would hold ONE stock, so its "mean forward return" would be that one
  stock, and the week's headline spread would be one name minus two. Note this
  is not fixed by picking a more volatile week: the wildest week in ten years
  (2026-05-08) gives 1 / 37 / 53 / 5 / 3, because returns are bell-shaped at any
  scale and a single -27% name stretches the bands across the whole range. Equal
  width buckets are hostage to the most extreme name in the cross-section.

  The real argument for ranks is therefore COMPARABILITY: 20-vs-20 every week
  means the 521 weekly spreads are the same kind of object and can be averaged.

  Its cost, which is real: ranks discard magnitude, so "the worst 20 names" in a
  calm week and in March 2020 are treated as the same event. That cost is NOT
  removed by differencing the buckets. Measured, the weekly spread's standard
  deviation is 1.50% in the calmest quartile of weeks and 3.51% in the wildest
  (corr(dispersion, |spread|) = 0.36), so the weekly observations are not
  identically distributed and the error bar in errorbars.py assumes they are.

  THE SPREAD IS DIFFERENCED WEEKLY, THEN AVERAGED. We form the spread inside each
  week and average the 521 results, rather than averaging each bucket over ten
  years and subtracting once.

  On this panel the two routes agree to ten decimal places (+0.0855315612 either
  way), because every bucket exists in every week. The choice therefore changes
  no number today. It changes one as soon as a bucket goes missing in some week:
  average-then-difference would compare bucket 1's average over one set of weeks
  against bucket 5's average over a different set. Difference-then-average cannot,
  since each spread is formed within a single week.

  A bucket will go missing once point-in-time index membership replaces today's
  membership, which is the survivorship fix the README names as defect 1. This
  line is written for that panel, not this one.

NO LOOKAHEAD: bucket membership at week t uses only prices up to t. The forward
return from t to t+1 is measured after the assignment is fixed. The residual
lookahead in this study is not here, it is in the universe (today's large caps,
so zero delistings in ten years) and it is stated in the README.
"""

import pandas as pd

from download import load_universe
from signal_build import build

# Fewer names than this in a week and the ranking is not worth cutting into five
# groups: at 20 names a bucket is 4 stocks and the average is mostly noise.
#
# On the signal side, one week trips it and it is not a data-quality week: the
# FIRST anchor (2016-08-26) has no prior week to compute a signal from, so every
# name is NaN and the count is 0.
#
# bucket_means applies the SAME threshold to the forward side, which is what ends
# the sample. Rewritten 17 Sept. The cache holds anchors out to 18 Sept 2026, but
# only one ticker has data past 25 Aug, so every week after 21 Aug 2026 fails the
# forward test and the sample ends there. Consequence worth having: the sample end
# is now a property of the DATA COVERAGE rather than of whatever the cache last
# happened to hold, so re-downloading cannot quietly move the published numbers.
#
# Every other week carries 98 or 99 names, so the 40-name threshold rejects
# nothing on data-quality grounds today. It starts rejecting weeks once the
# universe becomes point-in-time and names enter and leave mid-sample.
MIN_NAMES = 40


def assign_buckets(week_signal: pd.Series, n_buckets: int = 5) -> pd.Series:
    """Label one week's cross-section 1..n_buckets. 1 = biggest losers.

    Returns an empty Series if the week has too few names to cut.
    """
    s = week_signal.dropna()          # no signal, no rank, no bucket (25 Aug rule)
    if len(s) < MIN_NAMES:
        return pd.Series(dtype="float64")

    # rank(): smallest value -> 1. Ties share the average of their positions.
    # Ranking is what makes this cross-sectional: the question is never "did it
    # fall 3%", it is "did it fall more than the other 98 names this week".
    r = s.rank()

    # qcut = quantile cut = groups of EQUAL SIZE (pd.cut would be equal WIDTH).
    # Labels ascend with the ranks, so bucket 1 is the low end: the biggest
    # losers. If that correspondence ever flips, the sign of the whole study
    # flips with it, silently.
    return pd.qcut(r, n_buckets, labels=range(1, n_buckets + 1))


def bucket_means(signal: pd.DataFrame, forward: pd.DataFrame,
                 n_buckets: int = 5) -> pd.DataFrame:
    """Weeks down, buckets across. Cell = that bucket's mean forward return."""
    rows = {}
    for week in signal.index:
        b = assign_buckets(signal.loc[week], n_buckets)
        if b.empty:
            continue
        # reindex to the names that got a bucket, in that order, so the forward
        # returns line up with the labels positionally as well as by name.
        fwd = forward.loc[week].reindex(b.index)
        # A week needs MIN_NAMES on BOTH sides, not just the signal side. The old
        # test was `fwd.isna().all()`, which only caught a week with nothing at
        # all and let through a week carrying a handful of names. Found 17 Sept:
        # MRSH had been re-downloaded on its own after the MMC ticker change, so
        # its cache ran 3 weeks past the other 99. The week of 28 Aug 2026 then
        # had ONE forward return, that name landed in bucket 3, and the week
        # entered the table with four empty buckets and one stock standing in for
        # the market. A short week is harmless; a week that is one name wearing
        # the market's clothes is not, because it looks like data.
        if fwd.notna().sum() < MIN_NAMES:
            continue
        rows[week] = fwd.groupby(b, observed=True).mean()

    out = pd.DataFrame.from_dict(rows, orient="index")
    out.index.name = "week"
    out.columns.name = "bucket"
    return out


def summarise(means: pd.DataFrame) -> pd.Series:
    """Average each bucket down the columns, and report the 1-minus-5 spread."""
    lo, hi = means.columns[0], means.columns[-1]
    per_bucket = means.mean()
    # The weekly spread, then averaged. See the module docstring for why this
    # order and not the other one.
    spread = (means[lo] - means[hi]).mean()
    return per_bucket, spread


if __name__ == "__main__":
    panel = load_universe()
    signal, forward = build(panel)

    means = bucket_means(signal, forward)
    per_bucket, spread = summarise(means)

    print(f"\nweeks used: {len(means)} of {len(signal)} anchors")
    print("\nmean forward return by bucket, %/week:")
    for b, v in per_bucket.items():
        print(f"  bucket {b}: {v * 100:+.4f}")

    print(f"\nSPREAD (bucket 1 - bucket 5): {spread * 100:+.4f} %/week")
    print(f"  annualised, crudely (x52):   {spread * 52 * 100:+.2f} %")

    print("\nmonotonic 1>2>3>4>5?",
          bool((per_bucket.diff().dropna() < 0).all()))
