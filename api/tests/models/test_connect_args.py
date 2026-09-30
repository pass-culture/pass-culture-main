import pytest

from pcapi import settings
from pcapi.models import get_db_connection_args


@pytest.fixture(autouse=True)
def clear_ssl_cert_settings(monkeypatch):
    monkeypatch.setattr(settings, "DATABASE_SSLROOTCERT", None)
    monkeypatch.setattr(settings, "DATABASE_SSLCERT", None)
    monkeypatch.setattr(settings, "DATABASE_SSLKEY", None)


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


def test_sslmode_and_certificates(monkeypatch):
    monkeypatch.setattr(settings, "DATABASE_SSLMODE", "verify-ca")
    monkeypatch.setattr(settings, "DATABASE_SSLROOTCERT", "/etc/pcapi/pg-tls/root.crt")
    monkeypatch.setattr(settings, "DATABASE_SSLCERT", "/etc/pcapi/pg-tls/client.crt")
    monkeypatch.setattr(settings, "DATABASE_SSLKEY", "/etc/pcapi/pg-tls/client.key")

    assert get_db_connection_args([]) == {
        "sslmode": "verify-ca",
        "sslrootcert": "/etc/pcapi/pg-tls/root.crt",
        "sslcert": "/etc/pcapi/pg-tls/client.crt",
        "sslkey": "/etc/pcapi/pg-tls/client.key",
    }
