"""search"""
from flask import current_app as app, jsonify, request

from utils.includes import includes
from utils.rest import login_or_api_key_required
from utils.search import AND, search

@app.route('/search', methods=['GET'])
@login_or_api_key_required
def get_founds():
    # MAP SEARCH
    founds = []
    query = request.args.get('q')
    for collection_name in request.args['collectionNames'].split(AND):
        s = search(collection_name, query)
        print('query', query)
        if s:
            entities = s.all()
            founds += [
                dict(
                    entity._asdict(
                        include=includes.get(collection_name),
                        has_model_name=True
                    ),
                    **{'collectionName': collection_name}
                )
                for entity in entities
            ]
    # RETURN
    return jsonify(founds), 200
