""" things """
import simplejson as json
from flask import current_app as app, jsonify, request
from flask_login import current_user

from models import ThingType
from models.api_errors import ForbiddenError
from models.offer import Offer
from models.pc_object import PcObject
from models.thing import Thing
from utils.human_ids import dehumanize
from utils.includes import THING_INCLUDES
from utils.rest import expect_json_data, \
    load_or_404, \
    login_or_api_key_required, \
    handle_rest_get_list
from validation.things import check_user_can_create_activation_thing
from validation.url import is_url_safe


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


@app.route('/things', methods=['POST'])
@login_or_api_key_required
@expect_json_data
def post_thing():
    thing = Thing()
    thing.populateFromDict(request.json)
    check_user_can_create_activation_thing(current_user, thing)
    offer = Offer()
    offer.venueId = dehumanize(request.json['venueId'])
    offer.thing = thing
    if thing.url:
        is_url_safe(thing.url)
        thing.isNational = True
    PcObject.check_and_save(thing, offer)
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
    is_url_safe(thing.url)
    PcObject.check_and_save(thing)
    return jsonify(
        thing._asdict(
            include=THING_INCLUDES,
            has_dehumanized_id=True,
            has_model_name=True
        )
    ), 200
