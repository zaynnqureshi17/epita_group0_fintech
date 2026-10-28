from types import SimpleNamespace

import pytest

from epita_rachid_rahme_fintech import client, config
from epita_rachid_rahme_fintech.cli import main


class DummyResponse:
    def __init__(self, payload, status_code=200):
        self._payload = payload
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError("HTTP error")

    def json(self):
        return self._payload


def test_fetch_live_data_uses_stripe_backend(monkeypatch):
    calls = {}

    def fake_get(url, headers=None, timeout=None):
        calls["url"] = url
        calls["headers"] = headers
        calls["timeout"] = timeout
        return DummyResponse({
            "livemode": False,
            "available": [{"amount": 1234, "currency": "eur"}],
        })

    object.__setattr__(client.config, "api_key", "sk_test_123")
    monkeypatch.setattr(client.requests, "get", fake_get)

    result = client.fetch_live_data()

    assert result == {
        "status": "LIVE_SUCCESS",
        "currency": "EUR",
        "available_balance": 12.34,
        "livemode": False,
    }
    assert calls["url"] == "https://api.stripe.com/v1/balance"
    assert calls["headers"] == {"Authorization": "Bearer sk_test_123"}
    assert calls["timeout"] == 10


def test_missing_api_key_raises_value_error():
    bad = config.Settings(api_key="")
    with pytest.raises(ValueError, match="API key is not configured"):
        bad.validate()


def test_main_renders_dashboard(monkeypatch, capsys):
    monkeypatch.setattr(
        "epita_rachid_rahme_fintech.cli.fetch_live_data",
        lambda: {
            "status": "LIVE_SUCCESS",
            "currency": "EUR",
            "available_balance": 12.34,
            "livemode": False,
        },
    )

    main()

    captured = capsys.readouterr().out
    assert "LIVE_SUCCESS" in captured
    assert "EUR" in captured
