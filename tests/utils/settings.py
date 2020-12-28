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
