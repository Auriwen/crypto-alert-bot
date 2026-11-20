# Crypto Alert Bot

A Telegram bot that messages you when a cryptocurrency crosses a price you set.

```
You:  /alert btc above 70000
Bot:  Alert #1 set: BTC above 70,000.00 EUR

      ... later ...

Bot:  🔔 BTC is now above 70,000.00 EUR (current price: 70,112.00 EUR).
      Alert #1 has been removed.
```

<!-- Screenshot: save it as docs/demo.png (or .gif) and remove these comment markers:
![Chat with the bot](docs/demo.png)
-->

## Features

- **Price alerts** for BTC, ETH, SOL, XRP, ADA, DOGE, LTC and DOT, in EUR
- **`/list` and `/delete`** to manage your alerts. Each user only sees and deletes their own.
- **Background check every 60 seconds.** Fired alerts are sent and then removed.
- **Fault tolerant:** if the price API is down, slow or rate-limited, the bot logs it and retries next round instead of crashing.
- **Persistent:** alerts are stored in SQLite and survive restarts.

## Commands

| Command | Example | Description |
|---|---|---|
| `/alert <coin> <above\|below> <price>` | `/alert eth below 1500` | Create an alert |
| `/list` | `/list` | Show your alerts |
| `/delete <id>` | `/delete 3` | Remove one of your alerts |
| `/start`, `/help` | | Show the help text |

## Getting started

Requirements: Python 3.10+ and a Telegram account.

1. **Create a bot.** In Telegram, message [@BotFather](https://t.me/BotFather), send `/newbot` and copy the token it gives you.

2. **Install.**
   ```bash
   git clone https://github.com/Auriwen/crypto-alert-bot.git
   cd crypto-alert-bot
   python3 -m venv .venv
   source .venv/bin/activate        # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure.**
   ```bash
   cp .env.example .env
   ```
   Open `.env` and paste your token after `TELEGRAM_BOT_TOKEN=`. The `.env` file is ignored by git, so the token never gets committed.

4. **Run.**
   ```bash
   python bot.py
   ```
   Open your bot in Telegram and send `/start`.

## Running the tests

```bash
pip install -r requirements-dev.txt
pytest
```

The tests replace the CoinGecko API and Telegram with fakes, so they run offline in well under a second.

## Tech stack

- **Python 3**
- **[python-telegram-bot](https://python-telegram-bot.org/)** for the Telegram API and the built-in job scheduler
- **[CoinGecko API](https://www.coingecko.com/en/api)** for prices (free, no API key)
- **requests** for HTTP calls
- **SQLite** (Python's built-in `sqlite3` module) for storage
- **pytest** for tests

## Project structure

```
bot.py       Telegram command handlers and the 60-second background job
alerts.py    Parsing /alert input and deciding when an alert fires (pure functions)
prices.py    Fetching prices from CoinGecko
db.py        SQLite storage for alerts
tests/       pytest tests for all of the above
```

## Design decisions

- **One API request per check, however many alerts there are.** The background job collects every coin that has an alert and fetches all prices in a single CoinGecko call. With 2 or 2,000 alerts, the bot makes one request per minute and stays far below the free API's rate limit.
- **Blocking HTTP call in a worker thread.** The bot runs on a single asyncio event loop. `requests` is blocking, so the price fetch runs via `asyncio.to_thread()` and the bot keeps answering commands while it waits for CoinGecko.
- **Errors never stop the bot.** A failed price request skips one round. A temporary Telegram error keeps the alert so it's retried next round. If the user has blocked the bot, the alert is dropped because it can never be delivered.
- **Send first, then delete.** If the bot stops between the two steps, the user gets a duplicate notification rather than none (at-least-once delivery).
- **Users can only touch their own alerts.** Every query filters by `chat_id`, including `DELETE`, so guessing another user's alert id does nothing. Covered by a test.
- **Logic kept separate from I/O.** Input parsing and the trigger check in `alerts.py` know nothing about Telegram, the network or the database, which makes them easy to unit-test.
- **No secrets in the code.** The bot token is read from an environment variable. HTTP request logging is turned down because Telegram API URLs contain the token.

## Possible improvements

- Support any coin CoinGecko lists, not just a fixed set
- Let users choose their currency (USD, CHF, ...)
- Repeating alerts that don't delete themselves after firing
