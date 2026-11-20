"""Alert logic: parse alert commands and decide whether an alert should fire."""

import math

from prices import COIN_IDS

USAGE = "Usage: /alert <coin> <above|below> <price>, e.g. /alert btc above 70000"


def is_triggered(price: float, direction: str, target: float) -> bool:
    """Return True if `price` has reached `target` in the given direction.

    `direction` is "above" or "below".
    """
    if direction == "above":
        return price >= target
    if direction == "below":
        return price <= target
    raise ValueError(f"direction must be 'above' or 'below', got {direction!r}")


def parse_alert_args(args: list[str]) -> tuple[str, str, float]:
    """Turn ["btc", "above", "70000"] into ("btc", "above", 70000.0).

    Raises ValueError with a message meant for the user if the input is invalid.
    """
    if len(args) != 3:
        raise ValueError(USAGE)

    coin, direction, price_text = args
    coin = coin.lower()
    direction = direction.lower()

    if coin not in COIN_IDS:
        supported = ", ".join(COIN_IDS)
        raise ValueError(f"Unknown coin '{coin}'. Supported coins: {supported}")

    if direction not in ("above", "below"):
        raise ValueError(f"Direction must be 'above' or 'below', not '{direction}'.")

    try:
        price = float(price_text)
    except ValueError:
        raise ValueError(f"'{price_text}' is not a number. {USAGE}") from None

    # float() also accepts "nan" and "inf", so check for a real, positive number
    if not math.isfinite(price) or price <= 0:
        raise ValueError("Price must be a positive number.")

    return coin, direction, price


def format_price(price: float) -> str:
    """Format a price for display: 70000 -> "70,000.00", 0.053098 -> "0.053098"."""
    if price >= 1:
        return f"{price:,.2f}"
    return f"{price:.8f}".rstrip("0")  # up to 8 decimals, without trailing zeros
