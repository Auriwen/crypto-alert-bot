"""Fetch current cryptocurrency prices from the CoinGecko API."""

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


def get_price(coin: str, currency: str = "eur") -> float | None:
    """Return the current price of `coin` in `currency`, or None on any error.

    `coin` is a CoinGecko coin id, e.g. "bitcoin" or "ethereum".
    """
    params = {"ids": coin, "vs_currencies": currency}

    try:
        response = requests.get(COINGECKO_URL, params=params, timeout=TIMEOUT_SECONDS)
        response.raise_for_status()  # turns 4xx/5xx (e.g. 429 rate limit) into an exception
        data = response.json()
        return float(data[coin][currency])
    except requests.RequestException as error:
        print(f"Could not reach CoinGecko: {error}")
    except (KeyError, ValueError):
        print(f"Unexpected response from CoinGecko for '{coin}' in '{currency}'")

    return None


if __name__ == "__main__":
    price = get_price("bitcoin", "eur")
    if price is not None:
        print(f"BTC: {price:,.2f} EUR")
