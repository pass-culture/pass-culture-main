import pytest

from domain.keywords import get_ts_queries_from_keywords_string


@pytest.mark.standalone
def test_get_ts_queries_from_keywords_string_parses_keywords_string_into_list_of_ts_strings():
    # given
    keywords_string = 'PNL chante Marx'

    # when
    keywords_result = get_ts_queries_from_keywords_string(keywords_string)

    # then
    assert keywords_result == ['PNL:*', 'chante:*', 'Marx:*']


@pytest.mark.standalone
def test_get_ts_queries_from_keywords_string_with_double_space_parses_keywords_string_ignoring_consecutive_spaces():
    # given
    keywords_string = 'PNL  chante Marx'

    # when
    keywords_result = get_ts_queries_from_keywords_string(keywords_string)

    # then
    assert keywords_result == ['PNL:*', 'chante:*', 'Marx:*']
