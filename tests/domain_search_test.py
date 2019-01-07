import pytest

from domain.search import get_ts_queries


@pytest.mark.standalone
def test_get_ts_queries_parses_search_string_into_list_of_one_ts_strings():
    # given
    search = 'PNL chante Marx'

    # when
    search_result = get_ts_queries(search)

    # then
    assert search_result == ['PNL:* | chante:* | Marx:*']


@pytest.mark.standalone
def test_get_ts_queries_with_and_parses_search_string_into_two_lists_of_ts_strings():
    # given
    search = 'PNL chante Marx _and_ Bataclan Paris'

    # when
    search_result = get_ts_queries(search)

    # then
    assert search_result == ['PNL:* | chante:* | Marx:*', 'Bataclan:* | Paris:*']


@pytest.mark.standalone
def test_get_ts_queries_with_double_space_parses_search_string_ignoring_consecutive_spaces():
    # given
    search = 'PNL  chante Marx'

    # when
    search_result = get_ts_queries(search)

    # then
    assert search_result == ['PNL:* | chante:* | Marx:*']
