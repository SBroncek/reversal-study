"""Download and cache daily prices for the study universe.

One CSV per ticker under data/. Tickers already cached are skipped, so re-running
this is cheap and offline. `load_universe()` stitches the cached files into a
single adjusted-close panel: dates down the index, tickers across the columns.
"""

from pathlib import Path

import pandas as pd
import yfinance as yf

from universe import TICKERS

YEARS = 10
DATA_DIR = Path(__file__).parent / "data"


def load_prices(ticker: str, years: int = YEARS) -> pd.DataFrame:
    """Return daily OHLCV for `ticker`, cached as a CSV under data/."""
    DATA_DIR.mkdir(exist_ok=True)
    cache = DATA_DIR / f"{ticker}.csv"

    if cache.exists():
        return pd.read_csv(cache, index_col=0, parse_dates=True)

    print(f"downloading {ticker}...")
    df = yf.download(
        ticker,
        period=f"{years}y",
        interval="1d",
        auto_adjust=True,   # Close is split- and dividend-adjusted
        progress=False,
    )
    if df.empty:
        raise ValueError(f"yfinance returned no rows for {ticker}")
    if isinstance(df.columns, pd.MultiIndex):
        # yfinance returns (field, ticker) columns; flatten for a single name
        df.columns = df.columns.droplevel(1)
    df.index.name = "Date"
    df.to_csv(cache)
    return df


def download_universe(tickers: list[str] = TICKERS, years: int = YEARS) -> list[str]:
    """Cache every ticker. Returns the ones that failed, having warned about each."""
    failed = []
    for ticker in tickers:
        try:
            load_prices(ticker, years)
        except Exception as exc:                      # network, delisting, bad symbol
            print(f"WARNING: skipping {ticker}: {exc}")
            failed.append(ticker)
    return failed


def load_universe(tickers: list[str] = TICKERS, years: int = YEARS) -> pd.DataFrame:
    """Adjusted closes for the whole universe: dates as index, tickers as columns.

    Tickers that fail to download are warned about and left out entirely.
    """
    closes = {}
    for ticker in tickers:
        try:
            closes[ticker] = load_prices(ticker, years)["Close"]
        except Exception as exc:
            print(f"WARNING: skipping {ticker}: {exc}")

    # outer join on dates, so a name with a shorter history gets NaN, not a silent
    # truncation of everyone else
    panel = pd.DataFrame(closes)
    panel.index.name = "Date"
    return panel.sort_index()


if __name__ == "__main__":
    failed = download_universe()
    if failed:
        print(f"\n{len(failed)} ticker(s) failed: {failed}")

    prices = load_universe()

    print("\nshape:", prices.shape, "(rows = days, cols = tickers)")
    print("date range:", prices.index.min().date(), "->", prices.index.max().date())
    print("\ntickers with missing days:")
    gaps = prices.isna().sum()
    print(gaps[gaps > 0].sort_values(ascending=False).head(20))
    print("\nlast 5 rows, first 5 tickers:\n", prices.iloc[-5:, :5])
