"""The ticker universe for the study.

Today's index membership, not point-in-time, so the list already knows which
companies survived. Anything dropped, acquired or bust is missing, and any result
computed on it is made optimistic by that. The README states it as defect 1.
"""

TICKERS = [
    "AAPL", "MSFT", "NVDA", "AMZN", "GOOGL", "META", "TSLA", "BRK-B", "AVGO", "LLY",
    "JPM", "V", "XOM", "UNH", "MA", "COST", "HD", "PG", "JNJ", "WMT",
    "NFLX", "ABBV", "CRM", "BAC", "ORCL", "CVX", "MRK", "KO", "AMD", "PEP",
    "TMO", "LIN", "ADBE", "CSCO", "ACN", "MCD", "ABT", "WFC", "PM", "IBM",
    "GE", "DIS", "CAT", "QCOM", "NOW", "TXN", "VZ", "INTU", "DHR", "AMGN",
    "ISRG", "CMCSA", "NEE", "PFE", "SPGI", "RTX", "UBER", "AXP", "AMAT", "HON",
    "UNP", "LOW", "GS", "BKNG", "ETN", "PGR", "COP", "MS", "T", "BLK",
    "TJX", "SYK", "C", "BSX", "LMT", "VRTX", "MDT", "ADP", "SCHW", "CB",
    "MRSH", "PLD", "ADI", "GILD", "DE", "MU", "REGN", "ELV", "LRCX", "SBUX",
    "BMY", "MDLZ", "KLAC", "SO", "CI", "PANW", "INTC", "DUK", "ZTS", "MO",
]
