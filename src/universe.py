"""Static S&P 100-ish liquid universe + coarse sector map."""

# Approximate S&P 100 constituents — liquid names for research.
SP100 = [
    "AAPL", "ABBV", "ABT", "ACN", "ADBE", "AIG", "AMD", "AMGN", "AMT", "AMZN",
    "AVGO", "AXP", "BA", "BAC", "BKNG", "BLK", "BMY", "BRK-B", "C",
    "CAT", "CHTR", "CL", "CMCSA", "COF", "COP", "COST", "CRM", "CSCO", "CVS",
    "CVX", "DE", "DHR", "DIS", "DOW", "DUK", "EMR", "F", "FDX", "GD",
    "GE", "GILD", "GM", "GOOGL", "GS", "HD", "HON", "IBM", "INTC",
    "INTU", "ISRG", "JNJ", "JPM", "KO", "LIN", "LLY", "LMT", "LOW", "MA",
    "MCD", "MDLZ", "MDT", "MET", "META", "MMM", "MO", "MRK", "MS", "MSFT",
    "NEE", "NFLX", "NKE", "NOW", "NVDA", "ORCL", "PEP", "PFE", "PG", "PM",
    "PYPL", "QCOM", "RTX", "SBUX", "SCHW", "SO", "SPG", "T", "TGT", "TMO",
    "TMUS", "TSLA", "TXN", "UNH", "UNP", "UPS", "USB", "V", "VZ", "WFC",
    "WMT", "XOM",
]

BENCHMARK = "SPY"
SAFE_ASSET = "BIL"  # T-bill ETF for risk-off / vol-target residual

# Coarse sectors for concentration control (not official GICS).
SECTOR = {
    "AAPL": "Tech", "MSFT": "Tech", "AVGO": "Tech", "CRM": "Tech", "CSCO": "Tech",
    "IBM": "Tech", "INTC": "Tech", "INTU": "Tech", "NOW": "Tech", "NVDA": "Tech",
    "ORCL": "Tech", "QCOM": "Tech", "TXN": "Tech", "AMD": "Tech", "ADBE": "Tech",
    "ACN": "Tech", "META": "Comm", "GOOGL": "Comm", "NFLX": "Comm", "DIS": "Comm",
    "CMCSA": "Comm", "CHTR": "Comm", "T": "Comm", "VZ": "Comm", "TMUS": "Comm",
    "AMZN": "ConsDisc", "TSLA": "ConsDisc", "HD": "ConsDisc", "LOW": "ConsDisc",
    "NKE": "ConsDisc", "SBUX": "ConsDisc", "TGT": "ConsDisc", "BKNG": "ConsDisc",
    "F": "ConsDisc", "GM": "ConsDisc", "MCD": "ConsStap", "KO": "ConsStap",
    "PEP": "ConsStap", "PG": "ConsStap", "PM": "ConsStap", "MO": "ConsStap",
    "CL": "ConsStap", "MDLZ": "ConsStap", "WMT": "ConsStap", "COST": "ConsStap",
    "JPM": "Fin", "BAC": "Fin", "WFC": "Fin", "C": "Fin", "GS": "Fin", "MS": "Fin",
    "BLK": "Fin", "AXP": "Fin", "COF": "Fin", "SCHW": "Fin", "USB": "Fin",
    "V": "Fin", "MA": "Fin", "MET": "Fin", "AIG": "Fin", "BRK-B": "Fin",
    "SPG": "RE", "AMT": "RE",
    "JNJ": "Health", "UNH": "Health", "LLY": "Health", "MRK": "Health", "ABBV": "Health",
    "ABT": "Health", "PFE": "Health", "BMY": "Health", "AMGN": "Health", "GILD": "Health",
    "MDT": "Health", "ISRG": "Health", "TMO": "Health", "DHR": "Health", "CVS": "Health",
    "XOM": "Energy", "CVX": "Energy", "COP": "Energy",
    "CAT": "Indust", "DE": "Indust", "HON": "Indust", "GE": "Indust", "MMM": "Indust",
    "EMR": "Indust", "GD": "Indust", "LMT": "Indust", "RTX": "Indust", "BA": "Indust",
    "UNP": "Indust", "UPS": "Indust", "FDX": "Indust",
    "LIN": "Materials", "DOW": "Materials",
    "NEE": "Utilities", "SO": "Utilities", "DUK": "Utilities",
    "PYPL": "Fin",
}


def sector_of(ticker: str) -> str:
    return SECTOR.get(ticker, "Other")
