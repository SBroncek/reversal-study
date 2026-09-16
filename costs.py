"""Robustness: transaction costs on the long-short spread (long bucket 1, short bucket 5).

Cost is charged on MONEY TRADED, not per order, so grouping orders changes nothing.
Per 100 of one leg, fully replacing a leg trades 200 (100 out, 100 in); two legs trade
400. So weekly cost on the spread = (turnover_long + turnover_short) * 2 * cost.

Pre-committed (16 Sept): if the net spread at 5bp is <= 0, the README says "does not
survive realistic costs" and we stop. No search for a cost level that rescues it.
"""

import numpy as np
import pandas as pd

from download import load_universe
from signal_build import build
from buckets import assign_buckets, bucket_means
from errorbars import weekly_spread


def members(signal: pd.DataFrame, bucket: int, n_buckets: int = 5) -> pd.Series:
    """Week -> the set of names in `bucket` that week."""
    out = {}
    for week in signal.index:
        b = assign_buckets(signal.loc[week], n_buckets)
        if not b.empty:
            out[week] = set(b.index[b == bucket])
    return pd.Series(out)


def turnover(m: pd.Series) -> pd.Series:
    """Share of this week's bucket that was NOT in last week's (equal weights)."""
    vals = [len(now - prev) / len(now) for prev, now in zip(m.iloc[:-1], m.iloc[1:])]
    return pd.Series(vals, index=m.index[1:])


def net_spread(d: pd.Series, to_long: pd.Series, to_short: pd.Series,
               bp: float) -> pd.Series:
    """Weekly spread minus that week's cost. Cost = (TO_long + TO_short) * 2 * bp."""
    cost = (to_long + to_short) * 2 * bp / 10_000
    return (d - cost.reindex(d.index)).dropna()   # week 1 has no prior bucket: dropped


def t_stat(x: pd.Series) -> float:
    return x.mean() / (x.std(ddof=1) / np.sqrt(len(x)))


if __name__ == "__main__":
    signal, forward = build(load_universe())
    to = {}
    for bucket in (1, 5):
        to[bucket] = turnover(members(signal, bucket))
        print(f"bucket {bucket}: weeks {len(to[bucket])}  mean turnover "
              f"{to[bucket].mean():.3f}  min {to[bucket].min():.2f}  "
              f"max {to[bucket].max():.2f}")
    print("random-pick benchmark: 0.800")
    print()

    d = weekly_spread(bucket_means(signal, forward, n_buckets=5))
    print(f"{'cost':>6} {'weeks':>6} {'spread %/wk':>12} {'t':>7}")
    for bp in (0, 5, 10):
        n = net_spread(d, to[1], to[5], bp)
        print(f"{bp:>4}bp {len(n):>6} {n.mean() * 100:>12.4f} {t_stat(n):>7.2f}")
