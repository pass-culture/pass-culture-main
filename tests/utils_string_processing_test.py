import pytest

from utils.string_processing import get_matched_string_index, get_price_value, parse_string


@pytest.mark.standalone
def test_get_matched_string_index():
    assert get_matched_string_index(
        'karl marx',
        ['henri guillemin', 'groucho marx', 'kroutchev', 'emmanuel macron']
    ) == 1


@pytest.mark.standalone
def test_get_price_value():
    assert type(get_price_value('')) == int


@pytest.mark.standalone
def test_remove_http_from_url():
    assert parse_string('http://www.test.fr') == 'www.test.fr'
