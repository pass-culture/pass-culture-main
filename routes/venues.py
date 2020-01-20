import copy
from flask import current_app as app, jsonify, request
from flask_login import login_required, current_user

from connectors import redis
from domain.admin_emails import send_venue_validation_email
from domain.offers import update_is_active_status
from domain.venues import is_algolia_indexing
from models import PcObject
from models.user_offerer import RightsType
from models.venue import Venue
from repository.venue_queries import save_venue, find_by_managing_user
from routes.serialization import as_dict
from utils.human_ids import dehumanize
from utils.includes import OFFER_INCLUDES, VENUE_INCLUDES
from utils.mailing import MailServiceException, send_raw_email
from utils.rest import ensure_current_user_has_rights, \
    expect_json_data, \
    load_or_404
from validation.venues import validate_coordinates, check_valid_edition


@app.route('/venues/<venueId>', methods=['GET'])
@login_required
def get_venue(venueId):
    venue = load_or_404(Venue, venueId)
    ensure_current_user_has_rights(RightsType.editor, venue.managingOffererId)
    return jsonify(as_dict(venue, includes=VENUE_INCLUDES)), 200


@app.route('/venues', methods=['GET'])
@login_required
def get_venues():
    venues = find_by_managing_user(current_user)
    return jsonify([as_dict(venue, includes=VENUE_INCLUDES) for venue in venues]), 200


@app.route('/venues', methods=['POST'])
@login_required
@expect_json_data
def create_venue():
    validate_coordinates(request.json.get('latitude', None), request.json.get('longitude', None))
    venue = Venue(from_dict=request.json)
    venue.departementCode = 'XX'  # avoid triggerring check on this
    siret = request.json.get('siret')
    if not siret:
        venue.generate_validation_token()
    save_venue(venue)

    if not venue.isValidated:
        try:
            send_venue_validation_email(venue, send_raw_email)
        except MailServiceException as e:
            app.logger.error('Mail service failure', e)

    return jsonify(as_dict(venue, includes=VENUE_INCLUDES)), 201

@app.route('/venues/<venueId>', methods=['PATCH'])
@login_required
@expect_json_data
def edit_venue(venueId):
    venue = load_or_404(Venue, venueId)
    previous_venue = copy.deepcopy(venue)
    check_valid_edition(request, venue)
    validate_coordinates(request.json.get('latitude', None), request.json.get('longitude', None))
    ensure_current_user_has_rights(RightsType.editor, venue.managingOffererId)
    venue.populate_from_dict(request.json)
    save_venue(venue)

    if is_algolia_indexing(previous_venue, request.json):
        redis.add_venue_id(client=app.redis_client, venue_id=dehumanize(venueId))

    return jsonify(as_dict(venue, includes=VENUE_INCLUDES)), 200


@app.route('/venues/<venueId>/offers/activate', methods=['PUT'])
@login_required
def activate_venue_offers(venueId):
    venue = load_or_404(Venue, venueId)
    ensure_current_user_has_rights(RightsType.editor, venue.managingOffererId)
    offers = venue.offers
    activated_offers = update_is_active_status(offers, True)
    PcObject.save(*activated_offers)
    return jsonify([as_dict(offer, includes=OFFER_INCLUDES) for offer in activated_offers]), 200


@app.route('/venues/<venueId>/offers/deactivate', methods=['PUT'])
@login_required
def deactivate_venue_offers(venueId):
    venue = load_or_404(Venue, venueId)
    ensure_current_user_has_rights(RightsType.editor, venue.managingOffererId)
    offers = venue.offers
    deactivated_offers = update_is_active_status(offers, False)
    PcObject.save(*deactivated_offers)
    return jsonify([as_dict(offer, includes=OFFER_INCLUDES) for offer in deactivated_offers]), 200
