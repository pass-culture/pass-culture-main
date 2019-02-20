from nltk.corpus import stopwords
from sqlalchemy import and_, func, TEXT
from sqlalchemy.sql.expression import cast, or_
from sqlalchemy.sql.functions import coalesce

from utils.string_processing import remove_single_letters_for_search, tokenize_for_search


LANGUAGE = 'french'
STOP_WORDS = set(stopwords.words(LANGUAGE))


def create_tsvector(*args):
    exp = args[0]
    for e in args[1:]:
        exp += ' ' + e
    return func.to_tsvector(LANGUAGE+'_unaccent', exp)

def get_ts_queries_from_keywords_string(keywords_string):
    keywords = tokenize_for_search(keywords_string)
    keywords_without_single_letter = remove_single_letters_for_search(keywords)

    keywords_without_stop_words = [
        keyword
        for keyword in keywords_without_single_letter
        if keyword.lower() not in STOP_WORDS
    ]

    ts_queries = ['{}:*'.format(keyword) for keyword in keywords_without_stop_words]

    return ts_queries


def get_first_matching_any_ts_queries_at_column(query, ts_queries, column):
    ts_vector = func.to_tsvector(cast(coalesce(column, ''), TEXT))
    ts_queries_filter = or_(
        *[
            ts_vector.match(ts_query, postgresql_regconfig=LANGUAGE)
            for ts_query in ts_queries
        ]
    )
    return query.filter(ts_queries_filter).first()

def get_first_matching_keywords_string_at_column(query, keywords_string, column):
    ts_queries = get_ts_queries_from_keywords_string(keywords_string)
    return get_first_matching_any_ts_queries_at_column(query, ts_queries, column)


def create_get_filter_matching_ts_query_in_any_model(*models):
    def get_filter_matching_ts_query_in_any_model(ts_query):
        return or_(
            *[
                model.__ts_vector__.match(
                    ts_query,
                    postgresql_regconfig=LANGUAGE+'_unaccent'
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
