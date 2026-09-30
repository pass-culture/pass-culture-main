import pytest

from pcapi.utils import settings as utils


class ParseEmailAddressesTest:
    def test_returns_an_empty_list(self):
        assert utils.parse_str_to_list("") == []
        assert utils.parse_str_to_list(None) == []

    def test_returns_one_address_when_a_single_one_is_given(self):
        assert utils.parse_str_to_list("recipient@test.com") == ["recipient@test.com"]
        assert utils.parse_str_to_list("recipient@test.com  ;  ") == ["recipient@test.com"]
        assert utils.parse_str_to_list(" , recipient@test.com") == ["recipient@test.com"]

    def test_returns_two_addresses_when_given_addresses_are_separated_by_comma(self):
        assert utils.parse_str_to_list("one@test.com,two@test.com") == ["one@test.com", "two@test.com"]
        assert utils.parse_str_to_list("one@test.com, two@test.com") == ["one@test.com", "two@test.com"]
        assert utils.parse_str_to_list("  one@test.com  , two@test.com   ") == ["one@test.com", "two@test.com"]

    def test_returns_two_addresses_when_given_addresses_are_separated_by_semicolon(self):
        assert utils.parse_str_to_list("one@test.com;two@test.com") == ["one@test.com", "two@test.com"]
        assert utils.parse_str_to_list("one@test.com; two@test.com") == ["one@test.com", "two@test.com"]
        assert utils.parse_str_to_list("  one@test.com  ; two@test.com   ") == ["one@test.com", "two@test.com"]


class ParsePhoneNumbersTest:
    def test_returns_phones(self):
        assert utils.parse_phone_numbers("prenom.nom:33601020304; prenom.nom:33602030405") == [
            "33601020304",
            "33602030405",
        ]

    def test_does_not_fail(self):
        assert not utils.parse_phone_numbers("33601020304; prenom.nom:33602030405")

    def test_void_phone_numbers(self):
        assert not utils.parse_phone_numbers(None)


class CheckDatabaseSslSettingsTest:
    @pytest.mark.parametrize("sslmode", [None, "disable", "allow", "prefer", "require"])
    def test_accepts_modes_without_certificates(self, sslmode):
        utils.check_database_ssl_settings(sslmode, None, None, None)

    @pytest.mark.parametrize("sslmode", ["verify-ca", "verify-full"])
    def test_accepts_verify_modes_with_all_certificates(self, sslmode):
        utils.check_database_ssl_settings(sslmode, "root.crt", "client.crt", "client.key")

    def test_rejects_invalid_mode(self):
        with pytest.raises(ValueError, match="Invalid DATABASE_SSLMODE: verify_ca. Allowed values: disable, allow"):
            utils.check_database_ssl_settings("verify_ca", None, None, None)

    def test_lists_missing_certificates_for_verify_modes(self):
        with pytest.raises(
            ValueError,
            match="DATABASE_SSLMODE is verify-ca but these settings are not set: DATABASE_SSLCERT, DATABASE_SSLKEY",
        ):
            utils.check_database_ssl_settings("verify-ca", "root.crt", None, None)

    def test_treats_empty_strings_as_missing(self):
        with pytest.raises(ValueError, match="not set: DATABASE_SSLROOTCERT, DATABASE_SSLCERT, DATABASE_SSLKEY"):
            utils.check_database_ssl_settings("verify-full", "", "", "")

    @pytest.mark.parametrize("sslcert,sslkey", [("client.crt", None), (None, "client.key")])
    def test_rejects_certificate_without_key(self, sslcert, sslkey):
        with pytest.raises(ValueError, match="DATABASE_SSLCERT and DATABASE_SSLKEY must be set together"):
            utils.check_database_ssl_settings("require", None, sslcert, sslkey)
