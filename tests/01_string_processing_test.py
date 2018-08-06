from hypothesis import given
from hypothesis.strategies import text

from utils.string_processing import get_matched_string_index, get_price_value


def test_get_matched_string_index():
    assert get_matched_string_index(
        'karl marx',
        ['henri guillemin', 'groucho marx', 'kroutchev', 'emmanuel macron']
    ) == 1


@given(string_value=text())
def test_get_price_value(string_value, capsys):
    assert type(get_price_value(string_value)) == int
