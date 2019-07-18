from flask import current_app as app, jsonify, request
from flask_login import current_user, login_required

from domain.admin_emails import send_offer_creation_notification_to_administration
from domain.favorites import create_favorite
from domain.offers import add_stock_alert_message_to_offer, update_is_active_status
from domain.create_offer import fill_offer_with_new_data, initialize_offer_from_product_id
from models import Offer, PcObject, Venue, RightsType, Mediation
from models.api_errors import ResourceNotFound
from models.feature import FeatureToggle
from repository import venue_queries, offer_queries
from repository.favorite_queries import find_favorite_for_offer_mediation_and_user
from repository.offer_queries import find_activation_offers, \
    find_offers_with_filter_parameters, get_active_offers
from repository.recommendation_queries import invalidate_recommendations
from utils.config import PRO_URL
from utils.feature import feature_required
from utils.human_ids import dehumanize
from utils.includes import OFFER_INCLUDES
from utils.mailing import send_raw_email
from utils.rest import expect_json_data, \
    handle_rest_get_list, \
    load_or_404, login_or_api_key_required, load_or_raise_error, ensure_current_user_has_rights
from validation.offers import check_venue_exists_when_requested, check_user_has_rights_for_query, check_valid_edition, \
    check_has_venue_id, check_offer_type_is_valid, check_offer_id_and_mediation_id_are_present_in_request


@app.route('/offers', methods=['GET'])
@login_required
def list_offers():
    offerer_id = dehumanize(request.args.get('offererId'))
    venue_id = dehumanize(request.args.get('venueId'))
    venue = venue_queries.find_by_id(venue_id)

    check_venue_exists_when_requested(venue, venue_id)
    check_user_has_rights_for_query(offerer_id, venue, venue_id)

    query = find_offers_with_filter_parameters(
        current_user,
        offerer_id=offerer_id,
        venue_id=venue_id,
        keywords_string=request.args.get('keywords')
    )

    return handle_rest_get_list(Offer,
                                include=OFFER_INCLUDES,
                                populate=add_stock_alert_message_to_offer,
                                page=request.args.get('page'),
                                paginate=10,
                                order_by='offer.id desc',
                                query=query
                                )


@app.route('/offers/<id>', methods=['GET'])
@login_required
def get_offer(id):
    offer = load_or_404(Offer, id)
    return jsonify(offer.as_dict(include=OFFER_INCLUDES))


@app.route('/offers/activation', methods=['GET'])
@login_required
def list_activation_offers():
    departement_code = current_user.departementCode
    query = find_activation_offers(departement_code)

    return handle_rest_get_list(
        Offer,
        include=OFFER_INCLUDES,
        query=query
    )

@app.route("/offers/deactivate", methods=["PUT"])
@login_required
def list_all_deactivated_offers():
    offers = get_active_offers(user=current_user)
    deactivaded_offers = update_is_active_status(offers, False)
    return jsonify([b.as_dict(include=OFFER_INCLUDES) for b in deactivaded_offers]), 200


@app.route("/offers/activate", methods=["PUT"])
@login_required
def list_all_activated_offers():
    offers = get_active_offers(user=current_user)
    activated_offers = update_is_active_status(offers, True)
    return jsonify([b.as_dict(include=OFFER_INCLUDES) for b in activated_offers]), 200


@app.route('/offers', methods=['POST'])
@login_or_api_key_required
@expect_json_data
def post_offer():
    venue_id = request.json.get('venueId')
    check_has_venue_id(venue_id)
    venue = load_or_raise_error(Venue, venue_id)
    ensure_current_user_has_rights(RightsType.editor, venue.managingOffererId)
    product_id = dehumanize(request.json.get('productId'))
    if product_id:
        offer = initialize_offer_from_product_id(product_id)

    else:
        offer_type_name = request.json.get('type')
        check_offer_type_is_valid(offer_type_name)
        offer = fill_offer_with_new_data(request.json, current_user)
        offer.product.owningOfferer = venue.managingOfferer

    offer.venue = venue
    offer.bookingEmail = request.json.get('bookingEmail', None)
    PcObject.save(offer)
    send_offer_creation_notification_to_administration(offer, current_user, PRO_URL, send_raw_email)

    return jsonify(
        offer.as_dict(include=OFFER_INCLUDES)
    ), 201


@app.route('/offers/<id>', methods=['PATCH'])
@login_or_api_key_required
@expect_json_data
def patch_offer(id):
    thing_or_event_dict = request.json
    check_valid_edition(request.json)
    offer = offer_queries.find_offer_by_id(dehumanize(id))
    if not offer:
        raise ResourceNotFound
    ensure_current_user_has_rights(RightsType.editor, offer.venue.managingOffererId)
    offer.populate_from_dict(request.json)
    offer.update_with_product_data(thing_or_event_dict)
    PcObject.save(offer)
    if 'isActive' in request.json and not request.json['isActive']:
        invalidate_recommendations(offer)

    return jsonify(
        offer.as_dict(include=OFFER_INCLUDES)
    ), 200


@app.route('/offers/favorites', methods=['POST'])
@feature_required(FeatureToggle.FAVORITE_OFFER)
@login_required
def add_to_favorite():
    offer_id = request.json.get('offerId')
    mediation_id = request.json.get('mediationId')
    check_offer_id_and_mediation_id_are_present_in_request(offer_id, mediation_id)

    offer = load_or_404(Offer, offer_id)
    mediation = load_or_404(Mediation, mediation_id)

    favorite = create_favorite(mediation, offer, current_user)
    PcObject.save(favorite)

    return jsonify(favorite.as_dict()), 201


@app.route('/offers/favorites/<offer_id>/<mediation_id>', methods=['DELETE'])
@feature_required(FeatureToggle.FAVORITE_OFFER)
@login_required
def delete_favorite(offer_id, mediation_id):
    dehumanized_offer_id = dehumanize(offer_id)
    dehumanized_mediation_id = dehumanize(mediation_id)

    favorite = find_favorite_for_offer_mediation_and_user(dehumanized_mediation_id,
                                                          dehumanized_offer_id,
                                                          current_user.id) \
        .first_or_404()

    PcObject.delete(favorite)

    return jsonify({}), 204
