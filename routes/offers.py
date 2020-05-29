from flask import current_app as app
from flask import jsonify, request
from flask_login import current_user, login_required

from domain.admin_emails import \
    send_offer_creation_notification_to_administration
from domain.create_offer import fill_offer_with_new_data, initialize_offer_from_product_id
from models import Offer, RightsType, VenueSQLEntity
from models.api_errors import ResourceNotFoundError
from repository import offer_queries, repository, venue_queries
from repository.offer_queries import find_activation_offers, find_offers_with_filter_parameters
from routes.serialization import as_dict
from routes.serialization.offers_serialize import serialize_offer
from use_cases.update_an_offer import update_an_offer
from utils.config import PRO_URL
from utils.human_ids import dehumanize
from utils.includes import OFFER_INCLUDES
from utils.mailing import send_raw_email
from utils.rest import ensure_current_user_has_rights, expect_json_data, \
    handle_rest_get_list, load_or_404, load_or_raise_error, \
    login_or_api_key_required
from validation.routes.offers import check_has_venue_id, \
    check_offer_name_length_is_valid, check_offer_type_is_valid, \
    check_user_has_rights_for_query, check_valid_edition, \
    check_venue_exists_when_requested


@app.route('/offers', methods=['GET'])
@login_required
def list_offers() -> (str, int):
    offerer_id = dehumanize(request.args.get('offererId'))
    venue_id = dehumanize(request.args.get('venueId'))
    pagination_limit = request.args.get('paginate', '10')
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
                                includes=OFFER_INCLUDES,
                                order_by=None,
                                page=request.args.get('page'),
                                paginate=int(pagination_limit),
                                query=query,
                                with_total_data_count=True)


@app.route('/offers/<offer_id>', methods=['GET'])
@login_required
def get_offer(offer_id: int) -> (str, int):
    offer = load_or_404(Offer, offer_id)
    return jsonify(serialize_offer(offer, current_user)), 200


@app.route('/offers/activation', methods=['GET'])
@login_required
def list_activation_offers() -> (str, int):
    query = find_activation_offers(current_user.departementCode)
    return handle_rest_get_list(Offer, query=query, includes=OFFER_INCLUDES)


@app.route('/offers', methods=['POST'])
@login_or_api_key_required
@expect_json_data
def post_offer() -> (str, int):
    venue_id = request.json.get('venueId')
    check_has_venue_id(venue_id)
    venue = load_or_raise_error(VenueSQLEntity, venue_id)
    ensure_current_user_has_rights(RightsType.editor, venue.managingOffererId)
    product_id = dehumanize(request.json.get('productId'))

    if product_id:
        offer = initialize_offer_from_product_id(product_id)
    else:
        offer_type_name = request.json.get('type')
        check_offer_type_is_valid(offer_type_name)
        offer_name = request.json.get('name')
        check_offer_name_length_is_valid(offer_name)
        offer = fill_offer_with_new_data(request.json, current_user)
        offer.product.owningOfferer = venue.managingOfferer

    offer.venue = venue
    offer.bookingEmail = request.json.get('bookingEmail', None)
    repository.save(offer)
    send_offer_creation_notification_to_administration(offer, current_user, PRO_URL, send_raw_email)

    return jsonify(as_dict(offer, includes=OFFER_INCLUDES)), 201


@app.route('/offers/<offer_id>', methods=['PATCH'])
@login_or_api_key_required
@expect_json_data
def patch_offer(offer_id: str) -> (str, int):
    payload = request.json
    check_valid_edition(payload)
    offer = offer_queries.get_offer_by_id(dehumanize(offer_id))

    if not offer:
        raise ResourceNotFoundError

    ensure_current_user_has_rights(RightsType.editor, offer.venue.managingOffererId)

    offer_name = request.json.get('name')
    if offer_name:
        check_offer_name_length_is_valid(offer_name)

    offer = update_an_offer(offer, modifications=payload)

    return jsonify(as_dict(offer, includes=OFFER_INCLUDES)), 200
