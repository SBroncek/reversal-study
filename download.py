"""Download and cache daily prices for a single ticker.

Step 1 of the reversal study: just get data on disk and look at it.
Run again and it loads from the cache instead of re-hitting the network.
"""

from pathlib import Path

import pandas as pd
import yfinance as yf

TICKER = "AAPL"
YEARS = 10
DATA_DIR = Path(__file__).parent / "data"


def load_prices(ticker: str = TICKER, years: int = YEARS) -> pd.DataFrame:
    """Return daily OHLCV for `ticker`, cached as a CSV under data/."""
    DATA_DIR.mkdir(exist_ok=True)
    cache = DATA_DIR / f"{ticker}.csv"

    if cache.exists():
        print(f"loading cached {cache}")
        return pd.read_csv(cache, index_col=0, parse_dates=True)

    print(f"downloading {ticker} from yfinance...")
    df = yf.download(
        ticker,
        period=f"{years}y",
        interval="1d",
        auto_adjust=True,   # Close is split- and dividend-adjusted
        progress=False,
    )
    if isinstance(df.columns, pd.MultiIndex):
        # yfinance returns (field, ticker) columns; flatten for a single name
        df.columns = df.columns.droplevel(1)
    df.index.name = "Date"
    df.to_csv(cache)
    print(f"cached to {cache}")
    return df


if __name__ == "__main__":
    prices = load_prices()

    print("\ncolumns:", list(prices.columns))
    print("dtypes:\n", prices.dtypes)
    print("\nrows:", len(prices))
    print("date range:", prices.index.min().date(), "->", prices.index.max().date())
    print("missing values per column:\n", prices.isna().sum())
    print("\nfirst 5 rows:\n", prices.head())
    print("\nlast 5 rows:\n", prices.tail())
