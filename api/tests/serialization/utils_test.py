import pytest

from pcapi.serialization.utils import is_latin


class UtilsUnitTest:
    @pytest.mark.parametrize(
        "test_input,expected",
        [
            ("", True),
            ("a", True),
            ("Verona", True),
            ("Charles-Apollon", True),
            ("John O'Wick", True),
            ("Martin king, Jr.", True),
            ("მარიამ", False),
            ("aé", True),
            ("&", False),
            ("a&", False),
            ("1", False),
        ],
    )
    def test_is_latin(self, test_input, expected):
        assert is_latin(test_input) == expected
