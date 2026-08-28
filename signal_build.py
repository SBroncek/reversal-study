"""Build the signal and the forward return.

Spec (fixed 25 Aug):
  signal        = a stock's return over the PAST 5 trading days
  forward return = the same stock's return over the NEXT 5 trading days
  the two windows SHARE NO DAYS

Implementation note (Sam's call, 28 Aug): a "week" is a CALENDAR week, anchored on
the Friday close. Chosen over fixed 5-trading-day blocks because it is the grid a
strategy would actually be rebalanced on. Cost: 18.5% of weeks in the sample are
holiday-shortened, so the weekly observations are not identically scaled. The
within-week ranking is unaffected (every name shares the same window), but the
error bar in stage 3 rests on a slightly false assumption. README says so.

THE FAILURE MODE THIS FILE IS WRITTEN AGAINST: shift(1) where shift(-1) was meant.
It raises no error, and the "forward" return becomes the signal itself, so the
study reports a perfect relationship. Hence `alignment_check()` at the bottom,
which prints the four raw prices so a human can verify with a calculator.
"""

import pandas as pd

from download import load_universe

def anchor_grid(panel: pd.DataFrame) -> pd.DataFrame:
    """One row per week, holding that week's closing price for every ticker.

    The only definition of a "week" in the study; build() and alignment_check()
    both call it, so the check cannot verify a grid the study does not use.

    .last() takes each column's last non-NaN value in the bucket, so a week whose
    Friday was a holiday resolves to Thursday's close, still labelled Friday.
    Selecting Fridays directly would instead drop those 96 weeks outright.

    how="all" only removes weeks with no data for any name. The default, "any",
    would cut the sample from 523 weeks to 381 by deleting every week in which a
    single one of the 99 tickers was missing.
    """
    return panel.resample("W-FRI").last().dropna(how="all")


def build(panel: pd.DataFrame):
    """Return (signal, forward) frames: week-ending dates down, tickers across."""
    anchors = anchor_grid(panel)

    # past week: (P_t / P_{t-1}) - 1 on the WEEKLY grid, info available at t
    signal = anchors.pct_change()

    # next week: (P_{t+1} / P_t) - 1.
    # shift(-1) on the ANCHOR grid pulls the NEXT week's price back to row t.
    forward = anchors.shift(-1) / anchors - 1

    return signal, forward


def alignment_check(panel: pd.DataFrame, ticker: str, anchor_date):
    """Print the raw prices behind one signal/forward pair, for hand-checking."""
    anchors = anchor_grid(panel)
    signal, forward = build(panel)

    # get_indexer, not get_loc: get_loc's return type is int | slice | bool-array,
    # since a non-unique index makes "the position of this label" ambiguous. On a
    # duplicated week label the arithmetic below would then silently do something
    # other than what it reads as. get_indexer always gives positions, -1 if absent.
    i = int(anchors.index.get_indexer(pd.DatetimeIndex([anchor_date]))[0])
    if i < 1 or i > len(anchors) - 2:
        raise KeyError(f"{anchor_date} is not an anchor with a week either side")
    p_prev = anchors[ticker].iloc[i - 1]
    p_now  = anchors[ticker].iloc[i]
    p_next = anchors[ticker].iloc[i + 1]

    print(f"\n=== ALIGNMENT CHECK: {ticker} ===")
    print(f"  week -1 ({anchors.index[i-1].date()}):  {p_prev:.4f}")
    print(f"  week  0 ({anchors.index[i].date()}):  {p_now:.4f}   <- anchor")
    print(f"  week +1 ({anchors.index[i+1].date()}):  {p_next:.4f}")
    print()
    print(f"  by hand   signal  = {p_now}/{p_prev} - 1")
    print(f"  code says signal  = {signal[ticker].iloc[i]:+.6f}")
    print(f"  by hand   forward = {p_next}/{p_now} - 1")
    print(f"  code says forward = {forward[ticker].iloc[i]:+.6f}")
    print()
    print("  no shared days: signal window ends at t, forward window starts at t.")
    print(f"  sanity: signal at t+1 should equal forward at t -> "
          f"{signal[ticker].iloc[i+1]:+.6f}")


if __name__ == "__main__":
    panel = load_universe()
    signal, forward = build(panel)

    print("panel :", panel.shape)
    print("anchors:", signal.shape, "(rows = calendar weeks, cols = tickers)")
    print("first anchor:", signal.index[0].date(), " last:", signal.index[-1].date())
    print("\nsignal is NaN on the first anchor (no prior block):",
          bool(signal.iloc[0].isna().all()))
    print("forward is NaN on the last anchor (no next week):",
          bool(forward.iloc[-1].isna().all()))

    alignment_check(panel, "AAPL", signal.index[500])
