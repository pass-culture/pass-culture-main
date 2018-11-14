from sqlalchemy import and_

from domain.search import get_ts_queries, create_get_search_queries


def get_keywords_filter(models, keywords):
    ts_queries = get_ts_queries(keywords)
    return and_(*map(create_get_search_queries(*models), ts_queries))
