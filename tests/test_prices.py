"""Tests for get_prices(). requests.get is replaced, so no real API calls are made."""

import requests

import prices


class FakeResponse:
    """Stands in for requests.Response."""

    def __init__(self, data, status_code=200):
        self.data = data
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(f"{self.status_code} Error")

    def json(self):
        return self.data


def test_returns_prices_by_symbol(monkeypatch):
    response = FakeResponse({"bitcoin": {"eur": 56_000}, "dogecoin": {"eur": 0.05}})
    monkeypatch.setattr(requests, "get", lambda *args, **kwargs: response)

    assert prices.get_prices(["btc", "doge"]) == {"btc": 56_000.0, "doge": 0.05}


def test_fetches_all_coins_in_one_request(monkeypatch):
    calls = []

    def fake_get(url, params, timeout):
        calls.append(params)
        return FakeResponse({})

    monkeypatch.setattr(requests, "get", fake_get)
    prices.get_prices(["btc", "eth", "doge"])

    assert len(calls) == 1
    assert calls[0]["ids"] == "bitcoin,ethereum,dogecoin"


def test_coin_missing_from_response_is_left_out(monkeypatch):
    response = FakeResponse({"bitcoin": {"eur": 56_000}})
    monkeypatch.setattr(requests, "get", lambda *args, **kwargs: response)

    assert prices.get_prices(["btc", "doge"]) == {"btc": 56_000.0}


def test_rate_limit_returns_empty_dict(monkeypatch):
    response = FakeResponse({}, status_code=429)
    monkeypatch.setattr(requests, "get", lambda *args, **kwargs: response)

    assert prices.get_prices(["btc"]) == {}


def test_network_error_returns_empty_dict(monkeypatch):
    def fake_get(*args, **kwargs):
        raise requests.ConnectionError("no internet")

    monkeypatch.setattr(requests, "get", fake_get)

    assert prices.get_prices(["btc"]) == {}
