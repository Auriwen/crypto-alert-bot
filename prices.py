"""Fetch current cryptocurrency prices from the CoinGecko API."""

import logging

import requests

COINGECKO_URL = "https://api.coingecko.com/api/v3/simple/price"
TIMEOUT_SECONDS = 10

# Symbols users type -> CoinGecko coin ids
COIN_IDS = {
    "btc": "bitcoin",
    "eth": "ethereum",
    "sol": "solana",
    "xrp": "ripple",
    "ada": "cardano",
    "doge": "dogecoin",
    "ltc": "litecoin",
    "dot": "polkadot",
}

logger = logging.getLogger(__name__)


def get_prices(symbols: list[str], currency: str = "eur") -> dict[str, float]:
    """Return current prices for several coins with a single API request.

    Example: get_prices(["btc", "doge"]) -> {"btc": 56551.0, "doge": 0.053098}

    Coins without a price are left out, so on any error the result is {}.
    """
    params = {
        "ids": ",".join(COIN_IDS[symbol] for symbol in symbols),
        "vs_currencies": currency,
    }

    try:
        response = requests.get(COINGECKO_URL, params=params, timeout=TIMEOUT_SECONDS)
        response.raise_for_status()  # turns 4xx/5xx (e.g. 429 rate limit) into an exception
        data = response.json()
    except requests.RequestException as error:
        logger.warning("Could not get prices from CoinGecko: %s", error)
        return {}

    prices = {}
    for symbol in symbols:
        try:
            prices[symbol] = float(data[COIN_IDS[symbol]][currency])
        except (KeyError, TypeError, ValueError):
            logger.warning("CoinGecko returned no %s price for %s", currency, symbol)
    return prices


if __name__ == "__main__":
    for symbol, price in get_prices(list(COIN_IDS)).items():
        print(f"{symbol.upper()}: {price} EUR")
