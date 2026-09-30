from pcapi import settings
from pcapi.models import get_db_connection_args


def test_no_options_and_no_sslmode(monkeypatch):
    monkeypatch.setattr(settings, "DATABASE_SSLMODE", None)

    assert get_db_connection_args([]) == {}


def test_options_only(monkeypatch):
    monkeypatch.setattr(settings, "DATABASE_SSLMODE", None)

    assert get_db_connection_args(["-c lock_timeout=5000", "-c statement_timeout=60000"]) == {
        "options": "-c lock_timeout=5000 -c statement_timeout=60000"
    }


def test_sslmode_only(monkeypatch):
    monkeypatch.setattr(settings, "DATABASE_SSLMODE", "verify-ca")

    assert get_db_connection_args([]) == {"sslmode": "verify-ca"}


def test_options_and_sslmode(monkeypatch):
    monkeypatch.setattr(settings, "DATABASE_SSLMODE", "require")

    assert get_db_connection_args(["-c lock_timeout=5000"]) == {
        "options": "-c lock_timeout=5000",
        "sslmode": "require",
    }
