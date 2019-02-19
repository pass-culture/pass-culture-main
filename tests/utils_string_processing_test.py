import pytest

from utils.string_processing import get_matched_string_index, get_price_value, tokenize_for_search


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
def test_remove_special_character():
    assert tokenize_for_search("Læetitia a mangé's'") == ['læetitia', 'a', 'mangé', 's', '']

@pytest.mark.standalone
def test_remove_special_character():
    assert tokenize_for_search("L'histoire sans fin") == ['l', 'histoire', 'sans', 'fin']

@pytest.mark.standalone
def test_tokenize_url():
    assert tokenize_for_search('http://www.t_est-toto.fr') == ['http', 'www', 't', 'est', 'toto', 'fr' ]
