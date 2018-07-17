from models.occasion import Occasion
from models.pc_object import PcObject
from models.thing import Thing

""" things """
import simplejson as json
from flask import current_app as app, jsonify, request

from utils.includes import THING_INCLUDES
from utils.rest import expect_json_data, \
    load_or_404, \
    login_or_api_key_required, \
    handle_rest_get_list

Occasion = Occasion
Thing = Thing


@app.route('/things/<ofType>:<identifier>', methods=['GET'])
def get_thing(ofType, identifier):
    query = Thing.query.filter(
        (Thing.type == ofType) &
        (Thing.idAtProviders == identifier)
    )
    thing = query.first_or_404()
    return json.dumps(thing)


@app.route('/things', methods=['GET'])
def list_things():
    return handle_rest_get_list(Thing)


@app.route('/things', methods=['POST'])
@login_or_api_key_required
@expect_json_data
def post_thing():
    thing = Thing()
    thing.populateFromDict(request.json)
    ocas = Occasion()
    ocas.venue = request.json['venueId']
    ocas.thing = thing
    PcObject.check_and_save(thing, ocas)
    return jsonify(thing._asdict(
        include=THING_INCLUDES,
        has_dehumanized_id=True,
        has_model_name=True
    )), 201


@app.route('/things/<id>', methods=['PATCH'])
@login_or_api_key_required
@expect_json_data
def patch_thing(id):
    thing = load_or_404(Thing, id)
    thing.populateFromDict(request.json)
    PcObject.check_and_save(thing)
    return jsonify(
        thing._asdict(
            include=THING_INCLUDES,
            has_dehumanized_id=True,
            has_model_name=True
        )
    ), 200
