from sqlalchemy import Index
from sqlalchemy import and_
from sqlalchemy import func
from sqlalchemy.sql.expression import or_

from pcapi.utils import stopwords
from pcapi.utils.string_processing import remove_single_letters_for_search
from pcapi.utils.string_processing import tokenize_for_search


LANGUAGE = "french"
SEARCH_STOPWORDS = stopwords.STOPWORDS | {"où"}


def create_ts_vector_and_table_args(ts_indexes):  # type: ignore [no-untyped-def]
    ts_vectors = []
    table_args = []

    for ts_index in ts_indexes:
        ts_vector = _create_ts_vector(ts_index[1])
        ts_vectors.append(ts_vector)
        table_args.append(_create_fts_index(ts_index[0], ts_vector))

    return ts_vectors, tuple(table_args)


def _create_fts_index(name, ts_vector) -> Index:  # type: ignore [no-untyped-def]
    return Index(name, ts_vector, postgresql_using="gin")


def _create_ts_vector(*args):  # type: ignore [no-untyped-def]
    exp = args[0]
    for e in args[1:]:
        exp += " " + e
    return func.to_tsvector(LANGUAGE + "_unaccent", exp)


def create_get_filter_matching_ts_query_in_any_model(*models):  # type: ignore [no-untyped-def]
    def get_filter_matching_ts_query_in_any_model(ts_query):  # type: ignore [no-untyped-def]
        return or_(
            *[
                ts_vector.match(ts_query, postgresql_regconfig=LANGUAGE + "_unaccent")
                for model in models
                for ts_vector in model.__ts_vectors__
            ]
        )

    return get_filter_matching_ts_query_in_any_model


def create_filter_matching_all_keywords_in_any_model(get_filter_matching_ts_query_in_any_model, keywords_string):  # type: ignore [no-untyped-def]
    ts_queries = _get_ts_queries_from_keywords_string(keywords_string)
    ts_filters = [get_filter_matching_ts_query_in_any_model(ts_query) for ts_query in ts_queries]
    return and_(*ts_filters)


def _get_ts_queries_from_keywords_string(keywords_string) -> list[str]:  # type: ignore [no-untyped-def]
    keywords = tokenize_for_search(keywords_string)
    keywords_without_single_letter = remove_single_letters_for_search(keywords)

    # FIXME (dbaty, 2021-10-01): this is probably useless because
    # PostgreSQL already has a list of stopwords that it ignores.
    keywords_without_stop_words = [
        keyword for keyword in keywords_without_single_letter if keyword.lower() not in SEARCH_STOPWORDS
    ]

    ts_queries = ["{}:*".format(keyword) for keyword in keywords_without_stop_words]

    return ts_queries
