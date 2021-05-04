from pcapi.utils import settings as utils


class ParseEmailAddressesTest:
    def test_returns_an_empty_list(self):
        assert utils.parse_email_addresses("") == []
        assert utils.parse_email_addresses(None) == []

    def test_returns_one_address_when_a_single_one_is_given(self):
        assert utils.parse_email_addresses("recipient@test.com") == ["recipient@test.com"]
        assert utils.parse_email_addresses("recipient@test.com  ;  ") == ["recipient@test.com"]
        assert utils.parse_email_addresses(" , recipient@test.com") == ["recipient@test.com"]

    def test_returns_two_addresses_when_given_addresses_are_separated_by_comma(self):
        assert utils.parse_email_addresses("one@test.com,two@test.com") == ["one@test.com", "two@test.com"]
        assert utils.parse_email_addresses("one@test.com, two@test.com") == ["one@test.com", "two@test.com"]
        assert utils.parse_email_addresses("  one@test.com  , two@test.com   ") == ["one@test.com", "two@test.com"]

    def test_returns_two_addresses_when_given_addresses_are_separated_by_semicolon(self):
        assert utils.parse_email_addresses("one@test.com;two@test.com") == ["one@test.com", "two@test.com"]
        assert utils.parse_email_addresses("one@test.com; two@test.com") == ["one@test.com", "two@test.com"]
        assert utils.parse_email_addresses("  one@test.com  ; two@test.com   ") == ["one@test.com", "two@test.com"]


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
