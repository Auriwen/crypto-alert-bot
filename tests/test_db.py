import sqlite3

import pytest

import db

# Every test in this file gets its own empty database (see conftest.py)
pytestmark = pytest.mark.usefixtures("temp_db")


def test_added_alert_can_be_read_back():
    alert_id = db.add_alert(1, "btc", "above", 70_000)

    alerts = db.get_alerts(1)
    assert len(alerts) == 1
    assert alerts[0]["id"] == alert_id
    assert alerts[0]["coin"] == "btc"
    assert alerts[0]["direction"] == "above"
    assert alerts[0]["target_price"] == 70_000


def test_get_alerts_returns_only_own_chat():
    db.add_alert(1, "btc", "above", 70_000)
    db.add_alert(2, "eth", "below", 1_500)

    assert [row["coin"] for row in db.get_alerts(1)] == ["btc"]
    assert db.get_alerts(3) == []


def test_get_all_alerts_returns_every_chat():
    db.add_alert(1, "btc", "above", 70_000)
    db.add_alert(2, "eth", "below", 1_500)

    assert [row["chat_id"] for row in db.get_all_alerts()] == [1, 2]


def test_delete_own_alert():
    alert_id = db.add_alert(1, "btc", "above", 70_000)

    assert db.delete_alert(1, alert_id) is True
    assert db.get_alerts(1) == []


def test_cannot_delete_alert_of_another_chat():
    alert_id = db.add_alert(1, "btc", "above", 70_000)

    assert db.delete_alert(2, alert_id) is False
    assert len(db.get_alerts(1)) == 1


def test_delete_missing_alert_returns_false():
    assert db.delete_alert(1, 999) is False


def test_init_db_can_run_twice():
    db.init_db()  # the fixture already ran it once; this must not fail


def test_database_rejects_invalid_direction():
    with pytest.raises(sqlite3.IntegrityError):
        db.add_alert(1, "btc", "sideways", 70_000)
