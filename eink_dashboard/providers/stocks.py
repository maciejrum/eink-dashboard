import csv

from eink_dashboard.config import AppConfig
from eink_dashboard.http import fetch_bytes


def parse_stooq_quote(csv_text: str) -> dict[str, object] | None:
    rows = list(csv.DictReader(csv_text.splitlines()))
    if not rows:
        return None

    row = rows[0]
    try:
        close = float(row["Close"])
    except Exception:
        return None

    return {
        "symbol": row.get("Symbol"),
        "date": row.get("Date"),
        "time": row.get("Time"),
        "close": close,
        "currency": "PLN",
    }


def get_stock_quote(config: AppConfig) -> dict[str, object]:
    last_error = None
    for symbol in config.market.symbols:
        try:
            url = config.market.quote_url.format(sym=symbol)
            payload = fetch_bytes(url, user_agent=config.user_agent).decode("utf-8", errors="replace")
            quote = parse_stooq_quote(payload)
            if quote:
                return quote
        except Exception as exc:
            last_error = exc

    raise RuntimeError(f"stooq fail: {last_error}")

