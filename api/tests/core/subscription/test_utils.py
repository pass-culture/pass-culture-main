import pytest

import pcapi.core.subscription.utils as subscription_utils
from pcapi.utils.countries import INSEE_COUNTRIES


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
        assert subscription_utils.is_latin(test_input, accepted_chars=[]) == expected

    @pytest.mark.parametrize(
        "test_input",
        [
            "a",
            "1 allée des séqoïas",
            "1",
            "La rue d'en face de chose-les-bains",
            "14 Chemin n°15 dit la Terre basse",
            "Pas ici mais là-bas (plus loin)",
        ],
    )
    def test_valid_address(self, test_input):
        subscription_utils.validate_address(test_input)

    @pytest.mark.parametrize(
        "test_input",
        [
            "",
            "  ",
            "მარიამ",
            "&",
            "25 & 26 rue Duhesme",
        ],
    )
    def test_invalid_address(self, test_input):
        with pytest.raises(ValueError):
            subscription_utils.validate_address(test_input)

    @pytest.mark.parametrize(
        "test_input,expected",
        [
            ("a", True),
            ("მარიამ", False),
            ("Château-Chinon (Ville)", True),
            ("Trucy-l'Orgueilleux", True),
            ("", False),
            ("  ", False),
        ],
    )
    def test_is_city_valid(self, test_input, expected):
        if expected:
            subscription_utils.validate_city(test_input)
        else:
            with pytest.raises(ValueError):
                subscription_utils.validate_city(test_input)

    @pytest.mark.parametrize(
        "test_input,expected",
        [
            ("75000", True),
            ("750001", False),
            ("7A000", False),
            ("7500", False),
            ("", False),
            ("  ", False),
            ("75 000", False),
            ("75000 ", False),
            (" 75000", False),
            ("(75000)", False),
            ("7500.", False),
            ("750.0", False),
        ],
    )
    def test_is_postal_code_valid(self, test_input, expected):
        if expected:
            subscription_utils.validate_postal_code(test_input)
        else:
            with pytest.raises(ValueError):
                subscription_utils.validate_postal_code(test_input)

    @pytest.mark.parametrize(
        "test_input,expected",
        [
            ("75000", True),
            ("2A000", True),
            ("2B000", True),
            ("3A000", False),
            ("750001", False),
            ("7A000", False),
            ("7500", False),
            ("", False),
            ("  ", False),
            ("75 000", False),
            ("75000 ", False),
            (" 75000", False),
            ("(75000)", False),
            ("7500.", False),
            ("750.0", False),
        ],
    )
    def test_is_city_cog_code_valid(self, test_input, expected):
        if expected:
            subscription_utils.validate_city_cog_code(test_input)
        else:
            with pytest.raises(ValueError):
                subscription_utils.validate_city_cog_code(test_input)

    @pytest.mark.parametrize(
        "test_input",
        [country for country, _ in INSEE_COUNTRIES],
    )
    def test_valid_country_cog_code_valid(self, test_input):
        subscription_utils.validate_country_cog_code(test_input)

    @pytest.mark.parametrize(
        "test_input",
        [
            "",
            " ",
            "99100 ",
            " 99100",
            "99 100",
            "991000",
        ],
    )
    def test_invalid_country_cog_code_valid(self, test_input):
        with pytest.raises(ValueError):
            subscription_utils.validate_country_cog_code(test_input)

    @pytest.mark.parametrize(
        "test_input,expected",
        [
            ("", False),
            ("  ", False),
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
            subscription_utils.validate_name(test_input)
        else:
            with pytest.raises(ValueError):
                subscription_utils.validate_name(test_input)
