import re

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from sqlalchemy import and_, func
from sqlalchemy.sql.expression import or_

LANGUAGE = 'french'
STOP_WORDS = set(stopwords.words(LANGUAGE))

def create_tsvector(*args):
    exp = args[0]
    for e in args[1:]:
        exp += ' ' + e
    return func.to_tsvector(LANGUAGE, exp)

def get_ts_queries_from_keywords_string(keywords_string):

    keywords = word_tokenize(keywords_string)
    keywords_without_stop_words = [
        keyword
        for keyword in keywords
        if keyword not in STOP_WORDS
    ]

    ts_queries = ['{}:*'.format(keyword) for keyword in keywords_without_stop_words]

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
