""" things """
import simplejson as json
from flask import current_app as app, jsonify, request
from flask_login import current_user

from domain.admin_emails import send_offer_creation_notification_to_support
from models.offer import Offer
from models.pc_object import PcObject
from models.thing import Thing
from models.venue import Venue
from models.user_offerer import RightsType
from repository import offer_queries
from utils.config import PRO_URL
from utils.human_ids import dehumanize
from utils.includes import THING_INCLUDES
from utils.rest import expect_json_data, \
    ensure_current_user_has_rights, \
    load_or_404, \
    login_or_api_key_required, \
    handle_rest_get_list
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
    venue_id = request.json['venueId']
    venue = load_or_404(Venue, venue_id)
    ensure_current_user_has_rights(RightsType.editor, venue.managingOffererId)
    thing = Thing()
    thing.populateFromDict(request.json)
    offer = Offer()
    offer.venueId = dehumanize(venue_id)
    offer.thing = thing
    if thing.url:
        is_url_safe(thing.url)
        thing.isNational = True
    offer.bookingEmail = request.json.get('bookingEmail', None)
    PcObject.check_and_save(thing, offer)
    send_offer_creation_notification_to_support(offer, current_user, PRO_URL, app.mailjet_client.send.create)

    return jsonify(thing._asdict(
        include=THING_INCLUDES,
        has_dehumanized_id=True,
        has_model_name=True
    )), 201


@app.route('/things/<id>', methods=['PATCH'])
@login_or_api_key_required
@expect_json_data
def patch_thing(id):
    venue_id = request.json['venueId']
    venue = load_or_404(Venue, venue_id)
    ensure_current_user_has_rights(RightsType.editor, venue.managingOffererId)
    thing = load_or_404(Thing, id)
    thing.populateFromDict(request.json)
    is_url_safe(thing.url)
    offer_booking_email = request.json.get('bookingEmail', None)
    objects_to_save = [thing]
    if offer_booking_email:
        offer = offer_queries.find_first_offer_linked_to_thing(thing)
        offer.bookingEmail = offer_booking_email
        objects_to_save.append(offer)
    PcObject.check_and_save(*objects_to_save)
    return jsonify(
        thing._asdict(
            include=THING_INCLUDES,
            has_dehumanized_id=True,
            has_model_name=True
        )
    ), 200
