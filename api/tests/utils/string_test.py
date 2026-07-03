import pytest

from pcapi.utils import string as string_utils


class IsNumericTest:
    @pytest.mark.parametrize("value", ["0", "1", "1234567890"])
    def test_is_numeric(self, value):
        assert string_utils.is_numeric(value)

    @pytest.mark.parametrize("value", ["", "-1", "1.5", "²", "½", "\u0660", "1a"])
    def test_is_not_numeric(self, value):
        assert not string_utils.is_numeric(value)


class IsCanonicalIntegerTest:
    @pytest.mark.parametrize("value", ["0", "1", "200"])
    def test_is_canonical_integer(self, value):
        assert string_utils.is_canonical_integer(value)

    @pytest.mark.parametrize("value", ["", "-1", "1.5", "²", "½", "\u0660", "1a", "007", " 1 "])
    def test_is_not_canonical_integer(self, value):
        assert not string_utils.is_canonical_integer(value)
