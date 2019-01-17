import re

from sqlalchemy import and_, func
from sqlalchemy.sql.expression import or_

LANGUAGE = 'french'

def create_tsvector(*args):
    exp = args[0]
    for e in args[1:]:
        exp += ' ' + e
    return func.to_tsvector(LANGUAGE, exp)

def get_ts_queries_from_keywords_string(keywords_string):

    ts_queries_string = re.sub(' +', ' ', keywords_string)\
                          .strip()\
                          .replace(' ', ':* ') + ':*'


    ts_queries = [ts_query for ts_query in ts_queries_string.split(' ')]

    return ts_queries

def create_get_filter_matching_ts_query_in_any_model(*models):
    def get_filter_matching_ts_query_in_any_model(ts_query):
        return or_(
            *[
                model.__ts_vector__.match(
                    ts_query,
                    postgresql_regconfig=LANGUAGE
                )
                for model in models
            ]
        )
    return get_filter_matching_ts_query_in_any_model

def create_filter_matching_all_keywords_in_any_model(
        get_filter_matching_ts_query_in_any_model,
        keywords_string
):
    ts_queries = get_ts_queries_from_keywords_string(keywords_string)
    ts_filters = [
        get_filter_matching_ts_query_in_any_model(ts_query)
        for ts_query in ts_queries
    ]
    return and_(*ts_filters)
