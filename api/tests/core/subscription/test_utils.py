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
        "test_input",
        [
            "a",
            "Château-Chinon (Ville)",
            "Trucy-l'Orgueilleux",
        ],
    )
    def test_valid_city(self, test_input):
        subscription_utils.validate_city(test_input)

    @pytest.mark.parametrize(
        "test_input",
        [
            "მარიამ",
            "",
            "  ",
        ],
    )
    def test_invalid_city(self, test_input):
        with pytest.raises(ValueError):
            subscription_utils.validate_city(test_input)

    def test_valid_postal_code(self):
        subscription_utils.validate_postal_code("75000")

    @pytest.mark.parametrize(
        "test_input",
        [
            "750001",
            "7A000",
            "7500",
            "",
            "  ",
            "75 000",
            "75000 ",
            " 75000",
            "(75000)",
            "7500.",
            "750.0",
        ],
    )
    def test_invalid_postal_code(self, test_input):
        with pytest.raises(ValueError):
            subscription_utils.validate_postal_code(test_input)

    @pytest.mark.parametrize(
        "test_input",
        [
            "75000",
            "2A000",
            "2B000",
        ],
    )
    def test_valid_city_cog_code(self, test_input):
        subscription_utils.validate_city_cog_code(test_input)

    @pytest.mark.parametrize(
        "test_input",
        [
            "3A000",
            "750001",
            "7A000",
            "7500",
            "",
            "  ",
            "75 000",
            "75000 ",
            " 75000",
            "(75000)",
            "7500.",
            "750.0",
        ],
    )
    def test_invalid_city_cog_code(self, test_input):
        with pytest.raises(ValueError):
            subscription_utils.validate_city_cog_code(test_input)

    @pytest.mark.parametrize(
        "test_input",
        [country for country, _ in INSEE_COUNTRIES],
    )
    def test_valid_country_cog_code(self, test_input):
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
    def test_invalid_country_cog_code(self, test_input):
        with pytest.raises(ValueError):
            subscription_utils.validate_country_cog_code(test_input)

    @pytest.mark.parametrize(
        "test_input",
        [
            "a",
            "Verona",
            "Charles-Apollon",
            "John O'Wick",
            "John O’Wick",
            "Martin king, Jr.",
            "aé",
        ],
    )
    def test_is_name_valid(self, test_input):
        subscription_utils.validate_name(test_input)

    @pytest.mark.parametrize(
        "test_input",
        [
            "",
            "  ",
            "მარიამ",
            "&",
            "a&",
            "1",
        ],
    )
    def test_invalid_name(self, test_input):
        with pytest.raises(ValueError):
            subscription_utils.validate_name(test_input)
