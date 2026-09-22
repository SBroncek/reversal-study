"""Build the signal and the forward return on a weekly grid.

signal  = a stock's return over the past week
forward = the same stock's return over the next week, sharing no days with it

See the README for the week definition and the short-week caveat.
"""

import pandas as pd

from download import load_universe


def anchor_grid(panel: pd.DataFrame) -> pd.DataFrame:
    """One row per week, holding that week's closing price for every ticker.

    The only definition of a week in the study. build() and alignment_check()
    both call it, so the check cannot verify a grid the study does not use.
    """
    # .last() takes each column's last non-NaN value in the week, so a week whose
    # Friday was a holiday resolves to Thursday's close, still labelled Friday.
    # Selecting Fridays directly would drop those weeks: 18 of 526 anchors (3.4%)
    # have no Friday trading day.
    #
    # how="all" drops only weeks with no data for any name, which on this panel is
    # none. "any" would cut the sample to 381, since one 2019 IPO would erase the
    # first three years for the other 99 names.
    return panel.resample("W-FRI").last().dropna(how="all")


def build(panel: pd.DataFrame):
    """Return (signal, forward) frames: week-ending dates down, tickers across."""
    anchors = anchor_grid(panel)

    # past week, known at t
    signal = anchors.pct_change()

    # next week: shift(-1) pulls the NEXT week's price back to row t
    forward = anchors.shift(-1) / anchors - 1

    return signal, forward


def alignment_check(panel: pd.DataFrame, ticker: str, anchor_date):
    """Print the raw prices behind one signal/forward pair, for hand-checking."""
    anchors = anchor_grid(panel)
    signal, forward = build(panel)

    # get_indexer, not get_loc: get_loc returns int | slice | bool-array, so on a
    # duplicated week label the arithmetic below would silently do something other
    # than what it reads as. get_indexer always gives positions, -1 if absent.
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
