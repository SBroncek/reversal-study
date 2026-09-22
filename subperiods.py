"""Sub-period stability of the headline bucket spread.

Five consecutive two-year blocks, length fixed before looking. Pre-committed: if
any block reaches |t| >= 2, re-run with the blocks shifted one year and only call
it real if it survives the shift.

Out-of-sample selection is deliberately not run: nothing was significant
in-sample, so there is no finding to carry out.
"""

import numpy as np
import pandas as pd

from download import load_universe
from signal_build import build
from buckets import bucket_means
from errorbars import weekly_spread

N_BLOCKS = 5


def block_stats(d: pd.Series, n_blocks: int = N_BLOCKS) -> pd.DataFrame:
    """Cut the weekly spread into consecutive blocks; spread, SE and t for each."""
    rows = []
    # array_split keeps time order and gives the remainder to the first block
    for idx in np.array_split(np.arange(len(d)), n_blocks):
        block = d.iloc[idx]
        T = len(block)
        se = block.std(ddof=1) / np.sqrt(T)
        rows.append({
            "start": block.index[0].date(),
            "end": block.index[-1].date(),
            "weeks": T,
            "spread_pct": block.mean() * 100,
            "t": block.mean() / se,
        })
    return pd.DataFrame(rows)


if __name__ == "__main__":
    from errorbars import newey_west_se, default_lag

    panel = load_universe()
    d = weekly_spread(bucket_means(*build(panel), n_buckets=5))
    table = block_stats(d)

    table["t_nw"] = [b.mean() / newey_west_se(b, default_lag(len(b)))
                     for b in (d.iloc[i] for i in np.array_split(np.arange(len(d)), N_BLOCKS))]

    print(f"full sample: {len(d)} weeks, spread {d.mean()*100:+.4f} %/wk, "
          f"t {d.mean() / (d.std(ddof=1) / np.sqrt(len(d))):+.3f}\n")
    pd.set_option("display.float_format", "{:+.4f}".format)
    print(table.to_string(index=False))
    print("\nany |t| >= 2 (triggers the one-year shift):", bool((table["t"].abs() >= 2).any()))
