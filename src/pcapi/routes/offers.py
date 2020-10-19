from flask import jsonify, request
from flask_login import current_user, \
    login_required

from pcapi.flask_app import private_api
from pcapi.domain.admin_emails import send_offer_creation_notification_to_administration
from pcapi.domain.create_offer import fill_offer_with_new_data, \
    initialize_offer_from_product_id
from pcapi.domain.identifier.identifier import Identifier
from pcapi.domain.pro_offers.offers_status_filters import OffersStatusFilters
from pcapi.infrastructure.container import list_offers_for_pro_user
from pcapi.models import OfferSQLEntity, \
    RightsType, \
    VenueSQLEntity
from pcapi.models.api_errors import ResourceNotFoundError
from pcapi.repository import offer_queries, \
    repository, \
    user_offerer_queries, \
    venue_queries
from pcapi.routes.serialization import as_dict
from pcapi.routes.serialization.offers_recap_serialize import serialize_offers_recap_paginated
from pcapi.routes.serialization.offers_serialize import serialize_offer
from pcapi.use_cases.list_offers_for_pro_user import OffersRequestParameters
from pcapi.use_cases.update_an_offer import update_an_offer
from pcapi.use_cases.update_offers_active_status import update_offers_active_status
from pcapi.utils.config import PRO_URL
from pcapi.utils.human_ids import dehumanize
from pcapi.utils.includes import OFFER_INCLUDES
from pcapi.utils.mailing import send_raw_email
from pcapi.utils.rest import ensure_current_user_has_rights, \
    expect_json_data, \
    load_or_404, \
    load_or_raise_error, \
    login_or_api_key_required
from pcapi.validation.routes.offers import check_has_venue_id, \
    check_offer_name_length_is_valid, \
    check_offer_type_is_valid, \
    check_user_has_rights_on_offerer, \
    check_valid_edition, \
    check_venue_exists_when_requested


@private_api.route('/offers', methods=['GET'])
@login_required
def list_offers() -> (str, int):
    offerer_identifier = Identifier.from_scrambled_id(request.args.get('offererId'))
    venue_identifier = Identifier.from_scrambled_id(request.args.get('venueId'))

    if not current_user.isAdmin:
        offerer_id = None
        if venue_identifier:
            venue = venue_queries.find_by_id(venue_identifier.persisted)
            check_venue_exists_when_requested(venue, venue_identifier)
            offerer_id = venue.managingOffererId
        if offerer_identifier:
            offerer_id = offerer_identifier.persisted
        if offerer_id is not None:
            user_offerer = user_offerer_queries.find_one_or_none_by_user_id_and_offerer_id(
                user_id=current_user.id,
                offerer_id=offerer_id
            )
            check_user_has_rights_on_offerer(user_offerer)

    status_filters = OffersStatusFilters(
        exclude_active=request.args.get('active') == 'false',
        exclude_inactive=request.args.get('inactive') == 'false'
    )

    offers_request_parameters = OffersRequestParameters(
        user_id=current_user.id,
        user_is_admin=current_user.isAdmin,
        offerer_id=offerer_identifier,
        venue_id=venue_identifier,
        offers_per_page=int(request.args.get('paginate')) if request.args.get('paginate') else None,
        name_keywords=request.args.get('name'),
        page=int(request.args.get('page')) if request.args.get('page') else None,
        status_filters=status_filters
    )
    paginated_offers = list_offers_for_pro_user.execute(offers_request_parameters)

    return serialize_offers_recap_paginated(paginated_offers), 200


@private_api.route('/offers/<offer_id>', methods=['GET'])
@login_required
def get_offer(offer_id: int) -> (str, int):
    offer = load_or_404(OfferSQLEntity, offer_id)
    return jsonify(serialize_offer(offer, current_user)), 200


@private_api.route('/offers', methods=['POST'])
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


@private_api.route('/offers/active-status', methods=['PATCH'])
@login_or_api_key_required
@expect_json_data
def patch_offers_active_status() -> (str, int):
    payload = request.json
    offers_new_active_status = payload.get('isActive')
    offers_id = [dehumanize(offer_id) for offer_id in payload.get('ids')]
    update_offers_active_status(offers_id, offers_new_active_status)

    return '', 204


@private_api.route('/offers/<offer_id>', methods=['PATCH'])
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
