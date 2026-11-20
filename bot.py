"""Telegram bot that alerts users when a cryptocurrency crosses a price."""

import asyncio
import logging
import os
import sys

from dotenv import load_dotenv
from telegram import Update
from telegram.error import Forbidden, TelegramError
from telegram.ext import Application, CommandHandler, ContextTypes

import db
from alerts import format_price, is_triggered, parse_alert_args
from prices import get_prices

CHECK_INTERVAL_SECONDS = 60

logger = logging.getLogger(__name__)

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
    await update.effective_message.reply_text(HELP_TEXT)


async def alert(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /alert <coin> <above|below> <price>."""
    try:
        coin, direction, price = parse_alert_args(context.args)
    except ValueError as error:
        await update.effective_message.reply_text(str(error))
        return

    alert_id = db.add_alert(update.effective_chat.id, coin, direction, price)
    await update.effective_message.reply_text(
        f"Alert #{alert_id} set: {coin.upper()} {direction} {format_price(price)} EUR"
    )


async def list_alerts(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /list: show all alerts of this chat."""
    rows = db.get_alerts(update.effective_chat.id)
    if not rows:
        await update.effective_message.reply_text(
            "You have no alerts. Create one with /alert btc above 70000"
        )
        return

    lines = [
        f"#{row['id']}: {row['coin'].upper()} {row['direction']} "
        f"{format_price(row['target_price'])} EUR"
        for row in rows
    ]
    await update.effective_message.reply_text("Your alerts:\n" + "\n".join(lines))


async def delete(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /delete <id>."""
    if len(context.args) != 1:
        await update.effective_message.reply_text("Usage: /delete <id>, e.g. /delete 3")
        return

    id_text = context.args[0].lstrip("#")  # accept both "3" and "#3"
    if not id_text.isdigit():
        await update.effective_message.reply_text(f"'{context.args[0]}' is not a valid alert id.")
        return

    alert_id = int(id_text)
    if db.delete_alert(update.effective_chat.id, alert_id):
        await update.effective_message.reply_text(f"Alert #{alert_id} deleted.")
    else:
        await update.effective_message.reply_text(f"You have no alert #{alert_id}. See /list.")


async def check_alerts(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Background job: notify users whose alerts fired, then delete those alerts."""
    alerts = db.get_all_alerts()
    if not alerts:
        return

    symbols = sorted({row["coin"] for row in alerts})  # each coin only once
    # requests is blocking, so run it in a worker thread to keep the bot responsive
    prices = await asyncio.to_thread(get_prices, symbols)

    for row in alerts:
        price = prices.get(row["coin"])
        if price is None or not is_triggered(price, row["direction"], row["target_price"]):
            continue

        text = (
            f"🔔 {row['coin'].upper()} is now {row['direction']} "
            f"{format_price(row['target_price'])} EUR "
            f"(current price: {format_price(price)} EUR).\n"
            f"Alert #{row['id']} has been removed."
        )
        try:
            await context.bot.send_message(chat_id=row["chat_id"], text=text)
        except Forbidden:
            # The user blocked the bot. They can't be notified anymore, so drop the alert.
            logger.info("Chat %s blocked the bot, deleting alert #%s", row["chat_id"], row["id"])
        except TelegramError as error:
            # Probably a temporary problem: keep the alert and try again next round.
            logger.warning("Could not send alert #%s: %s", row["id"], error)
            continue

        db.delete_alert(row["chat_id"], row["id"])


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

    db.init_db()

    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler(["start", "help"], start))
    app.add_handler(CommandHandler("alert", alert))
    app.add_handler(CommandHandler("list", list_alerts))
    app.add_handler(CommandHandler("delete", delete))
    app.job_queue.run_repeating(check_alerts, interval=CHECK_INTERVAL_SECONDS, first=10)

    app.run_polling()  # blocks until Ctrl+C


if __name__ == "__main__":
    main()
