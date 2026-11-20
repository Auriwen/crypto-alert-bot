"""Tests for the background job bot.check_alerts(), with fake prices and a fake Telegram bot."""

import asyncio
from types import SimpleNamespace

import pytest
from telegram.error import Forbidden, TimedOut

import bot
import db

pytestmark = pytest.mark.usefixtures("temp_db")


class FakeBot:
    """Stands in for telegram.Bot: records messages instead of sending them."""

    def __init__(self, error=None):
        self.error = error
        self.sent = []

    async def send_message(self, chat_id, text):
        if self.error:
            raise self.error
        self.sent.append((chat_id, text))


def run_check(monkeypatch, current_prices, fake_bot):
    """Run one round of check_alerts with the given prices."""
    monkeypatch.setattr(bot, "get_prices", lambda symbols: current_prices)
    context = SimpleNamespace(bot=fake_bot)  # the job only uses context.bot
    asyncio.run(bot.check_alerts(context))


def test_fired_alert_is_sent_and_deleted(monkeypatch):
    db.add_alert(42, "btc", "above", 70_000)
    fake_bot = FakeBot()

    run_check(monkeypatch, {"btc": 71_000}, fake_bot)

    assert len(fake_bot.sent) == 1
    chat_id, text = fake_bot.sent[0]
    assert chat_id == 42
    assert "BTC is now above 70,000.00 EUR" in text
    assert db.get_all_alerts() == []


def test_alert_not_reached_is_kept(monkeypatch):
    db.add_alert(42, "btc", "above", 70_000)
    fake_bot = FakeBot()

    run_check(monkeypatch, {"btc": 69_000}, fake_bot)

    assert fake_bot.sent == []
    assert len(db.get_all_alerts()) == 1


def test_alert_is_kept_when_price_is_unavailable(monkeypatch):
    db.add_alert(42, "btc", "above", 70_000)
    fake_bot = FakeBot()

    run_check(monkeypatch, {}, fake_bot)  # e.g. CoinGecko was down

    assert fake_bot.sent == []
    assert len(db.get_all_alerts()) == 1


def test_alert_is_kept_on_temporary_telegram_error(monkeypatch):
    db.add_alert(42, "btc", "above", 70_000)

    run_check(monkeypatch, {"btc": 71_000}, FakeBot(error=TimedOut()))

    assert len(db.get_all_alerts()) == 1  # will be retried next round


def test_alert_is_deleted_when_user_blocked_the_bot(monkeypatch):
    db.add_alert(42, "btc", "above", 70_000)

    run_check(monkeypatch, {"btc": 71_000}, FakeBot(error=Forbidden("bot was blocked")))

    assert db.get_all_alerts() == []
