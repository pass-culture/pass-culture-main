""" things """
import simplejson as json
from flask import current_app as app


from utils.rest import login_or_api_key_required, \
    handle_rest_get_list


@app.route('/things/<ofType>:<identifier>', methods=['GET'])
@login_or_api_key_required
def get_thing(ofType, identifier):
    query = Thing.query.filter(
        (Thing.type == ofType) &
        (Thing.idAtProviders == identifier)
    )
    thing = query.first_or_404()
    return json.dumps(thing)


@app.route('/things', methods=['GET'])
@login_or_api_key_required
def list_things():
    return handle_rest_get_list(Thing)
