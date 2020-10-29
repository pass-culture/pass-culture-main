from flask import jsonify, request
from flask_login import current_user, login_required

from pcapi.flask_app import private_api
from pcapi.domain.admin_emails import send_offer_creation_notification_to_administration
from pcapi.domain.create_offer import (
    fill_offer_with_new_data,
    initialize_offer_from_product_id,
)
from pcapi.domain.pro_offers.offers_status_filters import OffersStatusFilters
from pcapi.infrastructure.container import list_offers_for_pro_user
from pcapi.models import OfferSQLEntity, RightsType, VenueSQLEntity
from pcapi.models.api_errors import ResourceNotFoundError
from pcapi.repository import (
    offer_queries,
    repository,
    user_offerer_queries,
    venue_queries,
)
from pcapi.routes.serialization.offers_recap_serialize import (
    serialize_offers_recap_paginated,
)
from pcapi.routes.serialization.offers_serialize import (
    serialize_offer,
    PostOfferBodyModel,
    OfferResponseIdModel,
    PatchOfferBodyModel,
    PatchOfferActiveStatusBodyModel,
    ListOffersResponseModel,
    ListOffersQueryModel,
    GetOfferResponseModel,
)
from pcapi.serialization.decorator import spectree_serialize
from pcapi.use_cases.list_offers_for_pro_user import OffersRequestParameters
from pcapi.use_cases.update_an_offer import update_an_offer
from pcapi.use_cases.update_offers_active_status import update_offers_active_status
from pcapi.utils.config import PRO_URL
from pcapi.utils.human_ids import dehumanize
from pcapi.utils.mailing import send_raw_email
from pcapi.utils.rest import (
    ensure_current_user_has_rights,
    load_or_404,
    load_or_raise_error,
    login_or_api_key_required,
)
from pcapi.validation.routes.offers import (
    check_user_has_rights_on_offerer,
    check_venue_exists_when_requested,
)


@private_api.route("/offers", methods=["GET"])
@login_required
@spectree_serialize(response_model=ListOffersResponseModel)  # type: ignore
def list_offers(query: ListOffersQueryModel) -> ListOffersResponseModel:
    if not current_user.isAdmin:
        offerer_id = None
        if query.venue_id:
            venue = venue_queries.find_by_id(query.venue_id)
            check_venue_exists_when_requested(venue, query.venue_id)
            offerer_id = venue.managingOffererId
        if query.offerer_id:
            offerer_id = query.offerer_id
        if offerer_id is not None:
            user_offerer = (
                user_offerer_queries.find_one_or_none_by_user_id_and_offerer_id(
                    user_id=current_user.id, offerer_id=offerer_id
                )
            )
            check_user_has_rights_on_offerer(user_offerer)

    status_filters = OffersStatusFilters(
        exclude_active=query.active == "false",
        exclude_inactive=query.inactive == "false",
    )

    offers_request_parameters = OffersRequestParameters(
        user_id=current_user.id,
        user_is_admin=current_user.isAdmin,
        offerer_id=query.offerer_id,
        venue_id=query.venue_id,
        offers_per_page=query.paginate,
        name_keywords=query.name,
        page=query.page,
        status_filters=status_filters,
    )
    paginated_offers = list_offers_for_pro_user.execute(offers_request_parameters)

    return ListOffersResponseModel(**serialize_offers_recap_paginated(paginated_offers))


@private_api.route("/offers/<offer_id>", methods=["GET"])
@login_required
@spectree_serialize(response_model=GetOfferResponseModel)
def get_offer(offer_id: str) -> GetOfferResponseModel:
    offer = load_or_404(OfferSQLEntity, offer_id)
    return GetOfferResponseModel(**serialize_offer(offer, current_user))


@private_api.route("/offers", methods=["POST"])
@login_or_api_key_required
@spectree_serialize(response_model=OfferResponseIdModel, on_success_status=201)  # type: ignore
def post_offer(body: PostOfferBodyModel) -> OfferResponseIdModel:
    venue = load_or_raise_error(VenueSQLEntity, body.venue_id)
    ensure_current_user_has_rights(RightsType.editor, venue.managingOffererId)

    if body.product_id:
        offer = initialize_offer_from_product_id(body.product_id)
    else:
        offer = fill_offer_with_new_data(request.json, current_user)
        offer.product.owningOfferer = venue.managingOfferer

    offer.venue = venue
    offer.bookingEmail = body.booking_email
    repository.save(offer)
    send_offer_creation_notification_to_administration(
        offer, current_user, PRO_URL, send_raw_email
    )

    return OfferResponseIdModel.from_orm(offer)


@private_api.route("/offers/active-status", methods=["PATCH"])
@login_or_api_key_required
@spectree_serialize(response_model=None, on_success_status=204)  # type: ignore
def patch_offers_active_status(body: PatchOfferActiveStatusBodyModel) -> None:
    update_offers_active_status(body.ids, body.is_active)


@private_api.route("/offers/<offer_id>", methods=["PATCH"])
@login_or_api_key_required
@spectree_serialize(response_model=OfferResponseIdModel)  # type: ignore
def patch_offer(offer_id: str, body: PatchOfferBodyModel) -> OfferResponseIdModel:
    offer = offer_queries.get_offer_by_id(dehumanize(offer_id))

    if not offer:
        raise ResourceNotFoundError

    ensure_current_user_has_rights(RightsType.editor, offer.venue.managingOffererId)
    offer = update_an_offer(offer, modifications=body.dict(exclude_unset=True))

    return OfferResponseIdModel.from_orm(offer)
