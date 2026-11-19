"""Check the BTC price every 60 seconds against a hard-coded threshold."""

import time

from alerts import is_triggered
from prices import get_price

COIN = "bitcoin"
CURRENCY = "eur"
DIRECTION = "above"
TARGET_PRICE = 60_000
CHECK_INTERVAL_SECONDS = 60


def main() -> None:
    print(f"Watching {COIN}: alert when {DIRECTION} {TARGET_PRICE:,} {CURRENCY.upper()}")

    while True:
        now = time.strftime("%H:%M:%S")
        price = get_price(COIN, CURRENCY)

        if price is None:
            print(f"[{now}] No price this round, trying again later.")
        elif is_triggered(price, DIRECTION, TARGET_PRICE):
            print(f"[{now}] ALERT: {COIN} is {price:,.2f} {CURRENCY.upper()} "
                  f"({DIRECTION} {TARGET_PRICE:,})")
            break
        else:
            print(f"[{now}] {COIN}: {price:,.2f} {CURRENCY.upper()}, no alert yet")

        time.sleep(CHECK_INTERVAL_SECONDS)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:  # raised when you press Ctrl+C
        print("\nStopped.")
