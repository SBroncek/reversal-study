"""Stage 4b: the lookback x holding-period grid.

Each cell ranks stocks on their past `lookback` trading days and measures the next
`hold` trading days. Re-ranking happens only once the hold has finished (Sam's call,
16 Sept), so no two forward returns share a day and no overlap correction is needed.
Cost: a 21-day hold gives ~125 observations instead of ~520.

Counts TRADING days, not calendar Fridays, so the 5x5 cell is close to but not
identical to the headline weekly result. The gap is the price of the Friday grid.
"""

import pandas as pd

from download import load_universe


def grid_build(panel: pd.DataFrame, lookback: int, hold: int):
    """Return (signal, forward) on rank dates spaced `hold` trading days apart."""
    # rank dates: start late enough that a full lookback exists, stop early enough
    # that a full hold exists, step by `hold` so forward windows never overlap
    positions = range(lookback, len(panel) - hold, hold)
    dates = panel.index[positions]

    # past `lookback` days: P_t / P_{t-lookback} - 1   (known at t)
    signal = (panel / panel.shift(lookback) - 1).loc[dates]

    # next `hold` days: P_{t+hold} / P_t - 1   (NOT known at t)
    forward = (panel.shift(-hold) / panel - 1).loc[dates]

    return signal, forward


LENGTHS = [1, 5, 21]     # one day, one week, one month, in trading days


def run_grid(panel: pd.DataFrame, n_buckets: int = 5) -> pd.DataFrame:
    """All nine lookback x hold cells through the same bucket test as stage 3."""
    from robustness import run_one      # the stage-3 test, unchanged

    rows = []
    for lookback in LENGTHS:
        for hold in LENGTHS:
            signal, forward = grid_build(panel, lookback, hold)
            r = run_one(signal, forward, n_buckets)
            rows.append({
                "lookback": lookback,
                "hold": hold,
                "obs": r["weeks"],                    # rank dates, not weeks here
                "spread": r["spread"],                # per HOLD, not per week
                "spread_per_day": r["spread"] / hold, # comparable across holds
                "t": r["t"],
                "t_nw": r["t_nw"],                    # should ~match t: no overlap
            })
    return pd.DataFrame(rows)


if __name__ == "__main__":
    panel = load_universe()
    table = run_grid(panel)
    pd.set_option("display.float_format", "{:+.4f}".format)
    print(table.to_string(index=False))
    print("\nt by cell (rows = lookback, cols = hold):")
    print(table.pivot(index="lookback", columns="hold", values="t"))
