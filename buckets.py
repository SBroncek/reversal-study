"""Stage 2, final chunk: sort each week's cross-section into buckets and measure
the forward return of each.

THE HEADLINE NUMBER: bucket 1 (last week's biggest losers) minus bucket 5 (last
week's biggest winners), averaged over every week in the sample. Positive means
losers went on to outperform winners, i.e. reversal.

Two conventions fixed here, both surfaced to Sam before they were written:

  RANKS, NOT RAW VALUES. Buckets are cut on the RANK of the signal, so every
  bucket holds the same number of names every week. Cutting on the raw return
  instead would give equal-WIDTH return bands, and in a calm week bucket 1 might
  hold two names while bucket 3 held sixty. Equal-sized buckets are what the spec
  says and what a fund would actually trade.

  THE SPREAD IS AVERAGED, NOT DIFFERENCED AT THE END. We compute the spread each
  week and then average those, rather than averaging each bucket over ten years
  and subtracting once. The two agree exactly when both buckets exist in every
  week, and when they do not, the weekly version is the honest one: it never
  compares bucket 1's average over one set of weeks against bucket 5's over a
  different set.

NO LOOKAHEAD: bucket membership at week t uses only prices up to t. The forward
return from t to t+1 is measured after the assignment is fixed. The residual
lookahead in this study is not here, it is in the universe (today's large caps,
so zero delistings in ten years) and it is stated in the README.
"""

import pandas as pd

from download import load_universe
from signal_build import build

# Fewer names than this in a week and the ranking is not worth cutting into five
# groups: at 20 names a bucket is 4 stocks and the average is mostly noise. In
# this panel no week trips it (the minimum is 96), so it is a guard against a
# future universe change, not a filter doing work today.
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
        if fwd.isna().all():          # the final week has no forward return
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
