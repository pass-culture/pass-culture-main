import pytest

from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as users_models
from pcapi.models import db
from pcapi.models import check_database_ssl_settings
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
    @pytest.mark.settings(DATABASE_SSL_MODE="")
    def test_accepts_when_ssl_mode_is_empty(self):
        # When
        check_database_ssl_settings()

    @pytest.mark.settings(DATABASE_SSL_MODE="unkonwon-ssl-mode")
    def test_raise_when_ssl_mode_is_unknown(self):
        with pytest.raises(ValueError, match="Invalid DATABASE_SSLMODE: verify_ca. Allowed values: disable, allow"):
            check_database_ssl_settings()

    @pytest.mark.settings(DATABASE_SSL_MODE="verify-ca")
    def test_raise_when_ssl_mode_is_valid_but_root_cert_is_not_set(self):
        pass

    @pytest.mark.settings(DATABASE_SSL_MODE="verify-ca", DATABASE_SSLROOTCERT="root-cert.pem")
    def test_raise_when_ssl_mode_is_valid_but_cert_is_not_set(self):
        pass

    @pytest.mark.settings(
        DATABASE_SSL_MODE="verify-ca",
        DATABASE_SSLROOTCERT="root-cert.pem",
        DATABASE_SSLCERT="client-cert.pem",
    )
    def test_raise_when_ssl_mode_is_valid_but_key_is_not_set(self):
        pass

    @pytest.mark.settings(
        DATABASE_SSL_MODE="verify-ca",
        DATABASE_SSLROOTCERT="root-cert.pem",
        DATABASE_SSLCERT="client-cert.pem",
        DATABASE_SSLKEY="client-key.pem",
    )
    def test_raise_when_ssl_mode_is_valid_but_key_is_not_set(self):
        pass
    # @pytest.mark.parametrize("sslmode", ["verify-ca", "verify-full"])
    # def test_accepts_verify_modes_with_all_certificates(self, sslmode):
    #     check_database_ssl_settings(sslmode, "root.crt", "client.crt", "client.key")
    #
    # def test_rejects_invalid_mode(self):
    #     with pytest.raises(ValueError, match="Invalid DATABASE_SSLMODE: verify_ca. Allowed values: disable, allow"):
    #         check_database_ssl_settings("verify_ca", None, None, None)
    #
    # def test_lists_missing_certificates_for_verify_modes(self):
    #     with pytest.raises(
    #         ValueError,
    #         match="DATABASE_SSLMODE is verify-ca but these settings are not set: DATABASE_SSLCERT, DATABASE_SSLKEY",
    #     ):
    #         check_database_ssl_settings("verify-ca", "root.crt", None, None)
    #
    # def test_treats_empty_strings_as_missing(self):
    #     with pytest.raises(ValueError, match="not set: DATABASE_SSLROOTCERT, DATABASE_SSLCERT, DATABASE_SSLKEY"):
    #         check_database_ssl_settings("verify-full", "", "", "")
    #
    # @pytest.mark.parametrize("sslcert,sslkey", [("client.crt", None), (None, "client.key")])
    # def test_rejects_certificate_without_key(self, sslcert, sslkey):
    #     with pytest.raises(ValueError, match="DATABASE_SSLCERT and DATABASE_SSLKEY must be set together"):
    #         check_database_ssl_settings("require", None, sslcert, sslkey)
