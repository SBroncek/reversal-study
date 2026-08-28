"""Build the signal and the forward return.

Spec (fixed 25 Aug):
  signal        = a stock's return over the PAST 5 trading days
  forward return = the same stock's return over the NEXT 5 trading days
  the two windows SHARE NO DAYS

Implementation note: "week" here means a block of 5 trading days, not a calendar
week. We anchor on every 5th row of the trading-day index, so a holiday-shortened
calendar week never silently becomes a 4-day signal window.

THE FAILURE MODE THIS FILE IS WRITTEN AGAINST: shift(1) where shift(-1) was meant.
It raises no error, and the "forward" return becomes the signal itself, so the
study reports a perfect relationship. Hence `alignment_check()` at the bottom,
which prints the four raw prices so a human can verify with a calculator.
"""

import pandas as pd

from download import load_universe

STEP = 5   # trading days in a "week"


def build(panel: pd.DataFrame, step: int = STEP):
    """Return (signal, forward) frames: anchor dates down, tickers across."""
    # anchor rows: every `step`-th trading day, so windows tile without overlap
    anchors = panel.iloc[::step]

    # past `step` days: (P_t / P_{t-step}) - 1, using only info available at t
    signal = anchors.pct_change()

    # next `step` days: (P_{t+step} / P_t) - 1.
    # shift(-1) on the ANCHOR grid pulls the NEXT anchor's price back to row t.
    forward = anchors.shift(-1) / anchors - 1

    return signal, forward


def alignment_check(panel: pd.DataFrame, ticker: str, anchor_date, step: int = STEP):
    """Print the raw prices behind one signal/forward pair, for hand-checking."""
    anchors = panel.iloc[::step]
    signal, forward = build(panel, step)

    i = anchors.index.get_loc(pd.Timestamp(anchor_date))
    p_prev = anchors[ticker].iloc[i - 1]
    p_now  = anchors[ticker].iloc[i]
    p_next = anchors[ticker].iloc[i + 1]

    print(f"\n=== ALIGNMENT CHECK: {ticker} ===")
    print(f"  t-{step} ({anchors.index[i-1].date()}):  {p_prev:.4f}")
    print(f"  t    ({anchors.index[i].date()}):  {p_now:.4f}   <- anchor")
    print(f"  t+{step} ({anchors.index[i+1].date()}):  {p_next:.4f}")
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
    print("anchors:", signal.shape, "(rows = 5-day blocks, cols = tickers)")
    print("first anchor:", signal.index[0].date(), " last:", signal.index[-1].date())
    print("\nsignal is NaN on the first anchor (no prior block):",
          bool(signal.iloc[0].isna().all()))
    print("forward is NaN on the last anchor (no next block):",
          bool(forward.iloc[-1].isna().all()))

    alignment_check(panel, "AAPL", signal.index[500])
