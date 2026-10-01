import pytest

from pcapi.models import get_db_connection_args


NO_SSL = dict(DATABASE_SSLMODE=None, DATABASE_SSLROOTCERT=None, DATABASE_SSLCERT=None, DATABASE_SSLKEY=None)


class GetDbConnectionArgsTest:
    @pytest.mark.settings(**NO_SSL)
    def test_no_options_and_no_sslmode(self):
        assert get_db_connection_args([]) == {}

    @pytest.mark.settings(**NO_SSL)
    def test_options_only(self):
        args = get_db_connection_args(["-c lock_timeout=5000", "-c statement_timeout=60000"])
        assert args == {"options": "-c lock_timeout=5000 -c statement_timeout=60000"}

    @pytest.mark.settings(**NO_SSL, DATABASE_SSLMODE="verify-ca")
    def test_sslmode_only(self):
        args = get_db_connection_args([])

        assert args == {"sslmode": "verify-ca"}

    @pytest.mark.settings(**NO_SSL, DATABASE_SSLMODE="require")
    def test_options_and_sslmode(self):
        assert get_db_connection_args(["-c lock_timeout=5000"]) == {
            "options": "-c lock_timeout=5000",
            "sslmode": "require",
        }

    @pytest.mark.settings(
        DATABASE_SSLMODE="verify-ca",
        DATABASE_SSLROOTCERT="/etc/pcapi/pg-tls/root.crt",
        DATABASE_SSLCERT="/etc/pcapi/pg-tls/client.crt",
        DATABASE_SSLKEY="/etc/pcapi/pg-tls/client.key",
    )
    def test_sslmode_and_certificates(self):
        assert get_db_connection_args([]) == {
            "sslmode": "verify-ca",
            "sslrootcert": "/etc/pcapi/pg-tls/root.crt",
            "sslcert": "/etc/pcapi/pg-tls/client.crt",
            "sslkey": "/etc/pcapi/pg-tls/client.key",
        }
