"""events"""
import binascii
from flask import current_app as app, jsonify, request
from flask_login import current_user

from domain.admin_emails import send_offer_creation_notification_to_support
from models import ApiErrors, Event, Offer, PcObject, Venue, EventType
from models.api_errors import ForbiddenError
from models.user_offerer import RightsType
from repository import offer_queries
from utils.config import PRO_URL
from utils.human_ids import dehumanize
from utils.includes import EVENT_INCLUDES
from utils.rest import expect_json_data, \
    ensure_current_user_has_rights, \
    load_or_404, \
    login_or_api_key_required
from validation.events import check_has_venue_id, check_user_can_create_activation_event


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
    event = Event()
    event.populateFromDict(request.json)
    check_user_can_create_activation_event(current_user, event)
    offer = Offer()
    venue_id = request.json.get('venueId')
    check_has_venue_id(venue_id)
    venue = Venue.query.filter_by(id=dehumanize(venue_id)).first()

    if venue:
        ensure_current_user_has_rights(RightsType.editor, venue.managingOffererId)
    api_errors = ApiErrors()
    try:
        offer.venueId = dehumanize(venue_id)
    except binascii.Error:
        api_errors.addError('venueId', 'le lieu est invalide')
        raise api_errors

    offer.event = event
    offer.bookingEmail = request.json.get('bookingEmail', None)

    PcObject.check_and_save(event, offer)

    send_offer_creation_notification_to_support(offer, current_user, PRO_URL, app.mailjet_client.send.create)

    return jsonify(
        event._asdict(include=EVENT_INCLUDES)
    ), 201


@app.route('/events/<id>', methods=['PATCH'])
@login_or_api_key_required
@expect_json_data
def patch_event(id):
    venue_id = request.json['venueId']
    venue = load_or_404(Venue, venue_id)
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
