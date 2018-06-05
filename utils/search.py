""" search """
from flask import current_app as app
from flask_login import current_user
from sqlalchemy import func
from sqlalchemy.sql.expression import and_, or_

from utils.string_processing import inflect_engine

AND = '_and_'
LANGUAGE = 'french'
SPACE = ' '

GENERIC_SEARCH_MODEL_NAMES = [
    'Offerer',
    'Venue'
]

def create_tsvector(*args):
    exp = args[0]
    for e in args[1:]:
        exp += ' ' + e
    return func.to_tsvector(LANGUAGE, exp)

def get_ts_query(token):
    return token.strip().replace(SPACE, ' | ')


def get_ts_queries(search):
    if AND in search:
        tokens = [token for token in search.split(AND) if token.strip() != '']
        return [get_ts_query(token) for token in tokens]
    return [get_ts_query(search)]

def create_get_search_queries(*models):
    def get_search_queries(ts_query):
        return or_(
            *[
                model.__ts_vector__.match(
                    ts_query,
                    postgresql_regconfig=LANGUAGE
                )
                for model in models
            ]
        )
    return get_search_queries

def get_search_filter(models, search):
    ts_queries = get_ts_queries(search)
    return and_(*map(create_get_search_queries(*models), ts_queries))

def search(collection_name, query):
    # MODEL
    model_name = inflect_engine.singular_noun(collection_name.title(), 1)
    model = app.model[model_name]

    # GENERIC METHOD
    if model_name not in GENERIC_SEARCH_MODEL_NAMES:
        return []

    # CREATE GENERIC FILTER
    search_filter = get_search_filter([model], query)

    # SPECIAL FILTER
    if model == app.model.Offerer:
        search_filter = and_(
            search_filter,
            model.id.in_([o.id for o in current_user.offerers])
        )

    # FILTER
    return model.query\
                .filter(search_filter)
