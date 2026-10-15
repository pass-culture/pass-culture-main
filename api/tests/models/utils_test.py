import pytest

from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as users_models
from pcapi.models import check_database_ssl_settings
from pcapi.models import db
from pcapi.models import get_db_connection_args
from pcapi.models import get_db_options
from pcapi.models.api_errors import ApiErrors
from pcapi.models.utils import first_or_404


class FirstOr404Test:
    def test_first_or_404_should_return_first_object_when_found(self, db_session):
        obj_1 = users_factories.UserFactory(firstName="Alice")
        obj_2 = users_factories.UserFactory(firstName="Alice")
        obj_3 = users_factories.UserFactory(firstName="Bob")
        db.session.add_all([obj_1, obj_2, obj_3])

        first_object = first_or_404(db.session.query(users_models.User).filter(users_models.User.firstName == "Alice"))

        assert first_object in (obj_1, obj_2)

    def test_first_or_404_should_raise_exception_when_not_found(self, db_session):
        obj = users_factories.UserFactory(firstName="Alice")
        db.session.add(obj)

        with pytest.raises(ApiErrors):
            first_or_404(db.session.query(users_models.User).filter(users_models.User.firstName == "Bob"))


class CheckDatabaseSslSettingsTest:
    @pytest.mark.settings(DATABASE_SSLMODE="")
    def test_accepts_when_ssl_mode_is_empty(self):
        check_database_ssl_settings()

    @pytest.mark.settings(DATABASE_SSLMODE=None)
    def test_accepts_when_ssl_mode_is_none(self):
        check_database_ssl_settings()

    @pytest.mark.parametrize("ssl_mode", ["disable", "allow", "prefer", "require"])
    def test_accepts_non_verify_modes_without_certificates(self, settings, ssl_mode):
        settings.DATABASE_SSLMODE = ssl_mode
        check_database_ssl_settings()

    @pytest.mark.parametrize("ssl_mode", ["verify-ca", "verify-full"])
    def test_accepts_verify_modes_with_all_certificates(self, settings, ssl_mode):
        settings.DATABASE_SSLMODE = ssl_mode
        settings.DATABASE_SSLROOTCERT = "root-cert.pem"
        settings.DATABASE_SSLCERT = "client-cert.pem"
        settings.DATABASE_SSLKEY = "client-key.pem"
        check_database_ssl_settings()

    @pytest.mark.settings(DATABASE_SSLMODE="unknown-ssl-mode")
    def test_raise_when_ssl_mode_is_unknown(self):
        with pytest.raises(
            ValueError,
            match=(
                "Invalid DATABASE_SSLMODE: unknown-ssl-mode. "
                "Allowed values are: disable, allow, prefer, require, verify-ca, verify-full"
            ),
        ):
            check_database_ssl_settings()

    @pytest.mark.parametrize("ssl_mode", ["verify-ca", "verify-full"])
    def test_raise_when_root_cert_is_not_set(self, settings, ssl_mode):
        settings.DATABASE_SSLMODE = ssl_mode
        settings.DATABASE_SSLROOTCERT = None
        with pytest.raises(
            ValueError,
            match=f"DATABASE_SSLROOTCERT, DATABASE_SSLCERT and DATABASE_SSLKEY are required when DATABASE_SSLMODE is {ssl_mode}.",
        ):
            check_database_ssl_settings()

    def test_raise_when_cert_is_not_set(self, settings):
        settings.DATABASE_SSLMODE = "verify-ca"
        settings.DATABASE_SSLROOTCERT = "root-cert.pem"
        settings.DATABASE_SSLCERT = None
        with pytest.raises(
            ValueError,
            match="DATABASE_SSLROOTCERT, DATABASE_SSLCERT and DATABASE_SSLKEY are required when DATABASE_SSLMODE is verify-ca.",
        ):
            check_database_ssl_settings()

    def test_raise_when_key_is_not_set(self, settings):
        settings.DATABASE_SSLMODE = "verify-ca"
        settings.DATABASE_SSLROOTCERT = "root-cert.pem"
        settings.DATABASE_SSLCERT = "client-cert.pem"
        settings.DATABASE_SSLKEY = None
        with pytest.raises(
            ValueError,
            match="DATABASE_SSLROOTCERT, DATABASE_SSLCERT and DATABASE_SSLKEY are required when DATABASE_SSLMODE is verify-ca.",
        ):
            check_database_ssl_settings()


class GetDbConnectionArgsTest:
    @pytest.fixture(autouse=True)
    def _clear_settings(self, settings):
        settings.DATABASE_LOCK_TIMEOUT = 0
        settings.DATABASE_STATEMENT_TIMEOUT = 0
        settings.DATABASE_IDLE_IN_TRANSACTION_SESSION_TIMEOUT = 0
        settings.DATABASE_SSLMODE = None
        settings.DATABASE_SSLROOTCERT = None
        settings.DATABASE_SSLCERT = None
        settings.DATABASE_SSLKEY = None

    def test_returns_empty_dict_when_no_timeout_and_no_ssl(self):
        assert get_db_connection_args() == {}

    def test_joins_options_with_spaces(self, settings):
        settings.DATABASE_LOCK_TIMEOUT = 5000
        settings.DATABASE_STATEMENT_TIMEOUT = 10000

        connect_args = get_db_connection_args()

        assert connect_args == {"options": "-c lock_timeout=5000 -c statement_timeout=10000"}

    def test_includes_single_option(self, settings):
        settings.DATABASE_LOCK_TIMEOUT = 5000

        connect_args = get_db_connection_args()

        assert connect_args == {"options": "-c lock_timeout=5000"}

    def test_includes_ssl_mode(self, settings):
        settings.DATABASE_SSLMODE = "require"

        assert get_db_connection_args() == {"sslmode": "require"}

    def test_includes_all_ssl_settings(self, settings):
        settings.DATABASE_SSLMODE = "verify-full"
        settings.DATABASE_SSLROOTCERT = "root-cert.pem"
        settings.DATABASE_SSLCERT = "client-cert.pem"
        settings.DATABASE_SSLKEY = "client-key.pem"

        assert get_db_connection_args() == {
            "sslmode": "verify-full",
            "sslrootcert": "root-cert.pem",
            "sslcert": "client-cert.pem",
            "sslkey": "client-key.pem",
        }

    def test_combines_options_and_ssl_settings(self, settings):
        settings.DATABASE_SSLMODE = "require"
        settings.DATABASE_SSLROOTCERT = "root-cert.pem"
        settings.DATABASE_LOCK_TIMEOUT = 5000

        assert get_db_connection_args() == {
            "options": "-c lock_timeout=5000",
            "sslmode": "require",
            "sslrootcert": "root-cert.pem",
        }

    def test_omits_ssl_keys_that_are_not_set(self, settings):
        settings.DATABASE_SSLMODE = "verify-ca"
        settings.DATABASE_SSLROOTCERT = "root-cert.pem"

        connect_args = get_db_connection_args()

        assert connect_args == {"sslmode": "verify-ca", "sslrootcert": "root-cert.pem"}
        assert "sslcert" not in connect_args
        assert "sslkey" not in connect_args


class GetDbOptionsTest:
    @pytest.fixture(autouse=True)
    def _clear_timeout_settings(self, settings):
        # Isolate from the ambient test environment: every timeout defaults to
        # unset (0) unless a test sets it explicitly.
        settings.DATABASE_LOCK_TIMEOUT = 0
        settings.DATABASE_STATEMENT_TIMEOUT = 0
        settings.DATABASE_IDLE_IN_TRANSACTION_SESSION_TIMEOUT = 0

    def test_returns_empty_list_when_no_timeout_is_set(self):
        assert get_db_options() == []

    def test_includes_lock_timeout(self, settings):
        settings.DATABASE_LOCK_TIMEOUT = 5000

        assert get_db_options() == ["-c lock_timeout=5000"]

    def test_includes_statement_timeout(self, settings):
        settings.DATABASE_STATEMENT_TIMEOUT = 10000

        assert get_db_options() == ["-c statement_timeout=10000"]

    def test_includes_idle_in_transaction_session_timeout(self, settings):
        settings.DATABASE_IDLE_IN_TRANSACTION_SESSION_TIMEOUT = 15000

        assert get_db_options() == ["-c idle_in_transaction_session_timeout=15000"]

    def test_includes_all_timeouts_in_order(self, settings):
        settings.DATABASE_LOCK_TIMEOUT = 5000
        settings.DATABASE_STATEMENT_TIMEOUT = 10000
        settings.DATABASE_IDLE_IN_TRANSACTION_SESSION_TIMEOUT = 15000

        assert get_db_options() == [
            "-c lock_timeout=5000",
            "-c statement_timeout=10000",
            "-c idle_in_transaction_session_timeout=15000",
        ]

    def test_omits_timeouts_that_are_zero(self, settings):
        settings.DATABASE_LOCK_TIMEOUT = 5000
        settings.DATABASE_STATEMENT_TIMEOUT = 0
        settings.DATABASE_IDLE_IN_TRANSACTION_SESSION_TIMEOUT = 15000

        assert get_db_options() == [
            "-c lock_timeout=5000",
            "-c idle_in_transaction_session_timeout=15000",
        ]
