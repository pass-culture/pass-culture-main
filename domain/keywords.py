import re

from sqlalchemy import and_, func
from sqlalchemy.sql.expression import or_

AND = '_and_'
LANGUAGE = 'french'
SPACE = ' '


def create_tsvector(*args):
    exp = args[0]
    for e in args[1:]:
        exp += ' ' + e
    return func.to_tsvector(LANGUAGE, exp)


def get_ts_query(token):
    ts_query = re.sub(' +', ' ', token)\
        .strip()\
        .replace(SPACE, ':* & ')
    return ts_query + ':*'


def get_ts_queries(search):
    if AND in search:
        tokens = [token for token in search.split(AND) if token.strip() != '']
        return [get_ts_query(token) for token in tokens]
    return [get_ts_query(search)]


def create_ts_filter_finding_ts_query_in_at_least_one_of_the_models(*models):
    def ts_filter_finding_ts_query_in_at_least_one_of_the_models(ts_query):
        return or_(
            *[
                model.__ts_vector__.match(
                    ts_query,
                    postgresql_regconfig=LANGUAGE
                )
                for model in models
            ]
        )
    return ts_filter_finding_ts_query_in_at_least_one_of_the_models

def create_filter_finding_all_keywords_in_at_least_one_of_the_models(
        ts_filter,
        keywords_chain
):
    ts_queries = get_ts_queries(keywords_chain)
    return and_(*map(ts_filter, ts_queries))
