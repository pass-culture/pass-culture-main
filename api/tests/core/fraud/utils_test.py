import pytest

import pcapi.core.fraud.utils as fraud_utils


class UtilsUnitTest:
    @pytest.mark.parametrize(
        "test_input,expected",
        [
            ("", False),
            ("a", True),
            ("Verona", True),
            ("მარიამ", False),
            ("aé", True),
            ("&", False),
            ("a&", False),
            ("1", False),
        ],
    )
    def test_is_latin(self, test_input, expected):
        assert fraud_utils.is_latin(test_input, accepted_chars=[]) == expected

    @pytest.mark.parametrize(
        "test_input,expected",
        [
            ("a", True),
            ("მარიამ", False),
            ("1 allée des séqoïas", True),
            ("&", False),
            ("25 & 26 rue Duhesme", False),
            ("1", True),
            ("La rue d'en face de chose-les-bains", True),
        ],
    )
    def test_is_address_valid(self, test_input, expected):
        if expected:
            fraud_utils.validate_address(test_input)
        else:
            with pytest.raises(ValueError):
                fraud_utils.validate_address(test_input)

    @pytest.mark.parametrize(
        "test_input,expected",
        [
            ("a", True),
            ("მარიამ", False),
            ("Château-Chinon (Ville)", True),
            ("Trucy-l'Orgueilleux", True),
            ("", False),
            (None, False),
        ],
    )
    def test_is_city_valid(self, test_input, expected):
        if expected:
            fraud_utils.validate_city(test_input)
        else:
            with pytest.raises(ValueError):
                fraud_utils.validate_city(test_input)

    @pytest.mark.parametrize(
        "test_input,expected",
        [
            ("", False),
            ("a", True),
            ("Verona", True),
            ("Charles-Apollon", True),
            ("John O'Wick", True),
            ("John O’Wick", True),
            ("Martin king, Jr.", True),
            ("მარიამ", False),
            ("aé", True),
            ("&", False),
            ("a&", False),
            ("1", False),
        ],
    )
    def test_is_name_valid(self, test_input, expected):
        if expected:
            fraud_utils.validate_name(test_input)
        else:
            with pytest.raises(ValueError):
                fraud_utils.validate_name(test_input)
