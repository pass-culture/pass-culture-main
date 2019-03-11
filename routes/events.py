"""events"""
from flask import current_app as app, jsonify, request
from flask_login import current_user

from domain.admin_emails import send_offer_creation_notification_to_support
from models import Event, Offer, PcObject, Venue
from models.user_offerer import RightsType
from repository import offer_queries
from utils.config import PRO_URL
from utils.human_ids import dehumanize
from utils.includes import EVENT_INCLUDES
from utils.mailing import send_raw_email
from utils.rest import expect_json_data, \
    ensure_current_user_has_rights, \
    load_or_404, \
    load_or_raise_error, \
    login_or_api_key_required
from validation.events import check_has_venue_id, \
    check_user_can_create_activation_event


@app.route('/events/<id>', methods=['GET'])
@login_or_api_key_required
def get_event(id):
    event = load_or_404(Event, id)
    return jsonify(
        event._asdict(include=EVENT_INCLUDES)
    ), 200


@app.route('/events', methods=['POST'])
@login_or_api_key_required
@expect_json_data
def post_event():
    offer = Offer()
    event = Event()
    event.populateFromDict(request.json)
    check_user_can_create_activation_event(current_user, event)
    venue_id = request.json.get('venueId')
    check_has_venue_id(venue_id)
    venue = load_or_raise_error(Venue, venue_id)

    ensure_current_user_has_rights(RightsType.editor, venue.managingOffererId)

    offer.venueId = dehumanize(venue_id)
    offer.event = event
    offer.bookingEmail = request.json.get('bookingEmail', None)

    PcObject.check_and_save(event, offer)

    send_offer_creation_notification_to_support(offer, current_user, PRO_URL, send_raw_email)

    return jsonify(
        event._asdict(include=EVENT_INCLUDES)
    ), 201


@app.route('/events/<id>', methods=['PATCH'])
@login_or_api_key_required
@expect_json_data
def patch_event(id):
    venue_id = request.json['venueId']
    venue = load_or_raise_error(Venue, venue_id)
    ensure_current_user_has_rights(RightsType.editor, venue.managingOffererId)
    event = load_or_404(Event, id)
    event.populateFromDict(request.json)
    offer_booking_email = request.json.get('bookingEmail', None)
    objects_to_save = [event]
    if offer_booking_email:
        offer = offer_queries.find_first_offer_linked_to_event(event)
        offer.bookingEmail = offer_booking_email
        objects_to_save.append(offer)
    PcObject.check_and_save(*objects_to_save)
    return jsonify(
        event._asdict(include=EVENT_INCLUDES)
    ), 200
