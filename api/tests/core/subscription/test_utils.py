import pytest

import pcapi.core.subscription.utils as subscription_utils


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
            (None, False),
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
            subscription_utils.validate_name(test_input)
        else:
            with pytest.raises(ValueError):
                subscription_utils.validate_name(test_input)
