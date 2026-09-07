"""The logging pipeline redacts sensitive keys before rendering."""

from __future__ import annotations

from app.core.logging import REDACTED_KEYS, _redact


def test_sensitive_values_are_redacted_but_context_is_kept() -> None:
    event = {
        "event": "login",
        "password": "hunter2",
        "token": "abc",
        "authorization": "Bearer x",
        "card_number": "4242424242424242",
        "user_id": "u-123",
    }
    redacted = _redact(None, "info", event)
    assert redacted["password"] == "[redacted]"
    assert redacted["token"] == "[redacted]"
    assert redacted["authorization"] == "[redacted]"
    assert redacted["card_number"] == "[redacted]"
    # Non-sensitive correlation context survives so logs stay useful.
    assert redacted["user_id"] == "u-123"
    assert redacted["event"] == "login"


def test_every_declared_sensitive_key_is_redacted() -> None:
    event = dict.fromkeys(REDACTED_KEYS, "secret-value")
    redacted = _redact(None, "info", event)
    assert redacted
    assert all(value == "[redacted]" for value in redacted.values())
