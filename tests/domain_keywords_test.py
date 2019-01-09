import pytest

from domain.keywords import get_ts_queries


@pytest.mark.standalone
def test_get_ts_queries_parses_keywords_chain_into_list_of_one_ts_strings():
    # given
    keywords_chain = 'PNL chante Marx'

    # when
    keywords_result = get_ts_queries(keywords_chain)

    # then
    assert keywords_result == ['PNL:* & chante:* & Marx:*']


@pytest.mark.standalone
def test_get_ts_queries_with_and_parses_keywords_chain_into_two_lists_of_ts_strings():
    # given
    keywords_chain = 'PNL chante Marx _and_ Bataclan Paris'

    # when
    keywords_result = get_ts_queries(keywords_chain)

    # then
    assert keywords_result == ['PNL:* & chante:* & Marx:*', 'Bataclan:* & Paris:*']


@pytest.mark.standalone
def test_get_ts_queries_with_double_space_parses_keywords_chain_ignoring_consecutive_spaces():
    # given
    keywords_chain = 'PNL  chante Marx'

    # when
    keywords_result = get_ts_queries(keywords_chain)

    # then
    assert keywords_result == ['PNL:* & chante:* & Marx:*']
