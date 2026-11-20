"""Telegram bot that alerts users when a cryptocurrency crosses a price."""

import logging
import os
import sys

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

HELP_TEXT = (
    "Hi! I send you a message when a cryptocurrency crosses a price you set.\n"
    "\n"
    "Commands:\n"
    "/alert <coin> <above|below> <price> - create an alert, e.g. /alert btc above 70000\n"
    "/list - show your alerts\n"
    "/delete <id> - remove an alert\n"
    "/help - show this message\n"
    "\n"
    "Prices are in EUR."
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Reply to /start and /help with the help text."""
    await update.message.reply_text(HELP_TEXT)


def main() -> None:
    load_dotenv()  # copies variables from .env into os.environ, if the file exists
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        sys.exit("TELEGRAM_BOT_TOKEN is not set. Copy .env.example to .env and add your token.")

    logging.basicConfig(
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        level=logging.INFO,
    )
    # httpx logs every request URL, and Telegram URLs contain the bot token.
    logging.getLogger("httpx").setLevel(logging.WARNING)

    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler(["start", "help"], start))

    app.run_polling()  # blocks until Ctrl+C


if __name__ == "__main__":
    main()
