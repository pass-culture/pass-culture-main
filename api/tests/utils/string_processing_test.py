from pcapi.utils.string_processing import remove_single_letters_for_search
from pcapi.utils.string_processing import tokenize_for_search


def test_tokennize_for_search_removes_special_characters():
    assert tokenize_for_search("Læetitia a mangé's'") == ["læetitia", "a", "mangé", "s", ""]
    assert tokenize_for_search("L'histoire sans fin") == ["l", "histoire", "sans", "fin"]


def test_tokenize_for_search_on_url():
    assert tokenize_for_search("http://www.t_est-toto.fr") == ["http", "www", "t", "est", "toto", "fr"]


def test_remove_single_letters_for_search():
    assert remove_single_letters_for_search(["http", "www", "t", "est", "toto", "fr"]) == [
        "http",
        "www",
        "est",
        "toto",
        "fr",
    ]
