import copy

from flask import current_app as app
from flask import jsonify, request
from flask_login import current_user, login_required

from connectors import redis
from domain.iris import link_valid_venue_to_irises
from domain.offers import update_is_active_status
from domain.venues import is_algolia_indexing
from models.feature import FeatureToggle
from models.user_offerer import RightsType
from models import VenueSQLEntity
from repository import feature_queries, repository
from repository.iris_venues_queries import delete_venue_from_iris_venues
from repository.venue_queries import find_by_managing_user
from routes.serialization import as_dict
from use_cases.create_venue import create_venue
from utils.human_ids import dehumanize
from utils.includes import OFFER_INCLUDES, VENUE_INCLUDES
from utils.rest import ensure_current_user_has_rights, expect_json_data, \
    load_or_404
from validation.routes.venues import check_valid_edition, validate_coordinates


@app.route('/venues/<venue_id>', methods=['GET'])
@login_required
def get_venue(venue_id):
    venue = load_or_404(VenueSQLEntity, venue_id)
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
def post_create_venue():
    validate_coordinates(request.json.get('latitude', None), request.json.get('longitude', None))

    venue = create_venue(venue_properties=request.json, save=repository.save)

    return jsonify(as_dict(venue, includes=VENUE_INCLUDES)), 201


@app.route('/venues/<venue_id>', methods=['PATCH'])
@login_required
@expect_json_data
def edit_venue(venue_id):
    venue = load_or_404(VenueSQLEntity, venue_id)
    previous_venue = copy.deepcopy(venue)
    check_valid_edition(request, venue)
    validate_coordinates(request.json.get('latitude', None), request.json.get('longitude', None))
    ensure_current_user_has_rights(RightsType.editor, venue.managingOffererId)
    venue.populate_from_dict(request.json)

    if not venue.isVirtual:
        delete_venue_from_iris_venues(venue.id)

    repository.save(venue)
    link_valid_venue_to_irises(venue)

    if is_algolia_indexing(previous_venue, request.json):
        if feature_queries.is_active(FeatureToggle.SYNCHRONIZE_ALGOLIA):
            redis.add_venue_id(client=app.redis_client, venue_id=dehumanize(venue_id))

    return jsonify(as_dict(venue, includes=VENUE_INCLUDES)), 200


@app.route('/venues/<venue_id>/offers/activate', methods=['PUT'])
@login_required
def activate_venue_offers(venue_id):
    venue = load_or_404(VenueSQLEntity, venue_id)
    ensure_current_user_has_rights(RightsType.editor, venue.managingOffererId)
    offers = venue.offers
    activated_offers = update_is_active_status(offers, True)
    repository.save(*activated_offers)
    if feature_queries.is_active(FeatureToggle.SYNCHRONIZE_ALGOLIA):
        redis.add_venue_id(client=app.redis_client, venue_id=venue.id)
    return jsonify([as_dict(offer, includes=OFFER_INCLUDES) for offer in activated_offers]), 200


@app.route('/venues/<venue_id>/offers/deactivate', methods=['PUT'])
@login_required
def deactivate_venue_offers(venue_id):
    venue = load_or_404(VenueSQLEntity, venue_id)
    ensure_current_user_has_rights(RightsType.editor, venue.managingOffererId)
    offers = venue.offers
    deactivated_offers = update_is_active_status(offers, False)
    repository.save(*deactivated_offers)
    if feature_queries.is_active(FeatureToggle.SYNCHRONIZE_ALGOLIA):
        redis.add_venue_id(client=app.redis_client, venue_id=venue.id)
    return jsonify([as_dict(offer, includes=OFFER_INCLUDES) for offer in deactivated_offers]), 200
