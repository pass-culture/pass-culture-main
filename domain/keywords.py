from nltk.corpus import stopwords
from sqlalchemy import and_, func, Index, TEXT
from sqlalchemy.sql.expression import cast, or_
from sqlalchemy.sql.functions import coalesce

from utils.string_processing import remove_single_letters_for_search, tokenize_for_search

LANGUAGE = 'french'
CUSTOM_STOPWORDS = ['où']
STOP_WORDS = set(stopwords.words(LANGUAGE))
STOP_WORDS.update(CUSTOM_STOPWORDS)


def create_fts_index(name, ts_vector):
    return Index(name,
                 ts_vector,
                 postgresql_using='gin')


def create_ts_vector_and_table_args(ts_indexes):
    ts_vectors = []
    table_args = []

    for ts_index in ts_indexes:
        ts_vector = create_tsvector(ts_index[1])
        ts_vectors.append(ts_vector)
        table_args.append(create_fts_index(ts_index[0], ts_vector))

    return ts_vectors, tuple(table_args)


def create_tsvector(*args):
    exp = args[0]
    for e in args[1:]:
        exp += ' ' + e
    return func.to_tsvector(LANGUAGE + '_unaccent', exp)


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
            ts_vector.match(ts_query, postgresql_regconfig=LANGUAGE + '_unaccent')
            for ts_query in ts_queries
        ]
    )
    return query.filter(ts_queries_filter).first()


def create_get_filter_matching_ts_query_in_any_model(*models):
    def get_filter_matching_ts_query_in_any_model(ts_query):
        return or_(
            *[
                ts_vector.match(
                    ts_query,
                    postgresql_regconfig=LANGUAGE + '_unaccent'
                )
                for model in models
                for ts_vector in model.__ts_vectors__
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
