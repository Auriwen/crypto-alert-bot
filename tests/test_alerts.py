import pytest

from alerts import format_price, is_triggered, parse_alert_args


@pytest.mark.parametrize(
    ("price", "direction", "target", "expected"),
    [
        (70_001, "above", 70_000, True),
        (70_000, "above", 70_000, True),  # reaching the target exactly counts
        (69_999, "above", 70_000, False),
        (0.04, "below", 0.05, True),
        (0.05, "below", 0.05, True),
        (0.06, "below", 0.05, False),
    ],
)
def test_is_triggered(price, direction, target, expected):
    assert is_triggered(price, direction, target) == expected


def test_is_triggered_rejects_unknown_direction():
    with pytest.raises(ValueError):
        is_triggered(100, "sideways", 50)


def test_parse_alert_args_valid():
    assert parse_alert_args(["btc", "above", "70000"]) == ("btc", "above", 70000.0)


def test_parse_alert_args_is_case_insensitive():
    assert parse_alert_args(["ETH", "Below", "1500.5"]) == ("eth", "below", 1500.5)


@pytest.mark.parametrize(
    ("args", "error_message"),
    [
        ([], "Usage"),
        (["btc", "above"], "Usage"),
        (["btc", "above", "1", "extra"], "Usage"),
        (["xyz", "above", "1"], "Unknown coin"),
        (["btc", "sideways", "1"], "Direction"),
        (["btc", "above", "70k"], "not a number"),
        (["btc", "above", "0"], "positive"),
        (["btc", "above", "-5"], "positive"),
        (["btc", "above", "nan"], "positive"),
        (["btc", "above", "inf"], "positive"),
    ],
)
def test_parse_alert_args_invalid(args, error_message):
    with pytest.raises(ValueError, match=error_message):
        parse_alert_args(args)


@pytest.mark.parametrize(
    ("price", "expected"),
    [
        (70_000, "70,000.00"),
        (1604.17, "1,604.17"),
        (1, "1.00"),
        (0.5, "0.5"),
        (0.053098, "0.053098"),
    ],
)
def test_format_price(price, expected):
    assert format_price(price) == expected
