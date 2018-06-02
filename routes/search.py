"""search"""
from flask import current_app as app, jsonify, request
from flask_login import current_user
from sqlalchemy.sql.expression import and_

from utils.includes import includes
from utils.rest import login_or_api_key_required
from utils.search import get_search_filter
from utils.string_processing import inflect_engine

GENERIC_SEARCH_MODEL_NAMES = [
    'Offerer',
    'Venue'
]

@app.route('/search', methods=['GET'])
@login_or_api_key_required
def get_founds():

    # UNPACK
    collection_name = request.args['collectionName']
    include = includes.get(collection_name)
    model_name = inflect_engine.singular_noun(collection_name.title(), 1)
    model = app.model[model_name]

    # GENERIC METHOD
    if model_name in GENERIC_SEARCH_MODEL_NAMES:
        # CREATE GENERIC FILTER
        search = request.args.get('q')
        search_filter = get_search_filter([model], search)

        # SPECIAL FILTER
        if model_name == 'Offerer':
            search_filter = and_(
                search_filter,
                model.id.in_([o.id for o in current_user.offerers])
            )

        # FILTER
        founds = model.query\
                      .filter(search_filter)\
                      .all()

    # RETURN
    return jsonify([f._asdict(include=include) for f in  founds]), 200
