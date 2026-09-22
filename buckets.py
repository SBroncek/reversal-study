"""Sort each week's cross-section into buckets and measure each bucket's forward return.

Headline number: bucket 1 (last week's biggest losers) minus bucket 5 (last
week's biggest winners), averaged over every week. See the README for why ranks,
why five buckets, and why the spread is differenced weekly rather than at the end.
"""

import pandas as pd

from download import load_universe
from signal_build import build

# A week is dropped below this on either side. 40 is the point at which five
# buckets stop being worth cutting: at 20 names a bucket is 4 stocks.
MIN_NAMES = 40


def assign_buckets(week_signal: pd.Series, n_buckets: int = 5) -> pd.Series:
    """Label one week's cross-section 1..n_buckets. 1 = biggest losers.

    Returns an empty Series if the week has too few names to cut.
    """
    s = week_signal.dropna()
    if len(s) < MIN_NAMES:
        return pd.Series(dtype="float64")

    # Labels ascend with the ranks, so bucket 1 is the low end: the biggest
    # losers. Flip this and the sign of the whole study flips, silently.
    return pd.qcut(s.rank(), n_buckets, labels=range(1, n_buckets + 1))


def bucket_means(signal: pd.DataFrame, forward: pd.DataFrame,
                 n_buckets: int = 5) -> pd.DataFrame:
    """Weeks down, buckets across. Cell = that bucket's mean forward return."""
    rows = {}
    for week in signal.index:
        b = assign_buckets(signal.loc[week], n_buckets)
        if b.empty:
            continue
        # reindex so the forward returns line up with the labels positionally
        # as well as by name
        fwd = forward.loc[week].reindex(b.index)
        # Tested on the forward side too, not just the signal side. Checking
        # `fwd.isna().all()` instead lets through a week holding a handful of
        # names, where one stock stands in for a whole bucket.
        if fwd.notna().sum() < MIN_NAMES:
            continue
        rows[week] = fwd.groupby(b, observed=True).mean()

    out = pd.DataFrame.from_dict(rows, orient="index")
    out.index.name = "week"
    out.columns.name = "bucket"
    return out


def summarise(means: pd.DataFrame) -> tuple[pd.Series, float]:
    """Average each bucket down the columns, and report the 1-minus-5 spread."""
    lo, hi = means.columns[0], means.columns[-1]
    per_bucket = means.mean()
    spread = (means[lo] - means[hi]).mean()
    return per_bucket, float(spread)


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
