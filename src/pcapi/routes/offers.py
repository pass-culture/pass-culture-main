from flask import request
from flask_login import current_user, login_required

from pcapi.flask_app import private_api
from pcapi.domain.admin_emails import send_offer_creation_notification_to_administration
from pcapi.domain.create_offer import (
    fill_offer_with_new_data,
    initialize_offer_from_product_id,
)
from pcapi.models import OfferSQLEntity, RightsType, VenueSQLEntity
from pcapi.models.api_errors import ResourceNotFoundError
from pcapi.repository import (
    offer_queries,
    repository,
)
from pcapi.routes.serialization.offers_recap_serialize import (
    serialize_offers_recap_paginated,
)
from pcapi.routes.serialization.offers_serialize import (
    PostOfferBodyModel,
    OfferResponseIdModel,
    PatchOfferBodyModel,
    PatchOfferActiveStatusBodyModel,
    ListOffersResponseModel,
    ListOffersQueryModel,
    GetOfferResponseModel,
)
from pcapi.serialization.decorator import spectree_serialize
from pcapi.core.offers.api import list_offers_for_pro_user
from pcapi.use_cases.update_an_offer import update_an_offer
from pcapi.use_cases.update_offers_active_status import (
    update_offers_active_status,
    update_all_offers_active_status,
)
from pcapi.utils.config import PRO_URL
from pcapi.utils.human_ids import dehumanize
from pcapi.utils.mailing import send_raw_email
from pcapi.utils.rest import (
    ensure_current_user_has_rights,
    load_or_404,
    load_or_raise_error,
    login_or_api_key_required,
    expect_json_data,
)
from pcapi.utils.includes import OFFER_INCLUDES
from pcapi.routes.serialization.dictifier import as_dict


@private_api.route("/offers", methods=["GET"])
@login_required
@spectree_serialize(response_model=ListOffersResponseModel)  # type: ignore
def list_offers(query: ListOffersQueryModel) -> ListOffersResponseModel:
    paginated_offers = list_offers_for_pro_user(
        user_id=current_user.id,
        user_is_admin=current_user.isAdmin,
        offerer_id=query.offerer_id,
        venue_id=query.venue_id,
        type_id=query.type_id,
        offers_per_page=query.paginate,
        name_keywords=query.name,
        page=query.page,
        requested_status=query.status,
    )

    return ListOffersResponseModel(**serialize_offers_recap_paginated(paginated_offers))


@private_api.route("/offers/<offer_id>", methods=["GET"])
@login_required
@spectree_serialize(response_model=GetOfferResponseModel)
def get_offer(offer_id: str) -> GetOfferResponseModel:
    offer = load_or_404(OfferSQLEntity, offer_id)
    return GetOfferResponseModel(**as_dict(offer, includes=OFFER_INCLUDES))


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


@private_api.route("/offers/all-active-status", methods=["PATCH"])
@login_or_api_key_required
@expect_json_data
def patch_all_offers_active_status() -> None:
    payload = request.json
    offerer_identifier = dehumanize(payload.get("offererId"))

    venue_identifier = dehumanize(payload.get("venueId"))

    name_keywords = payload.get("name")
    offers_new_active_status = payload.get("isActive")
    type_id = payload.get("typeId")

    update_all_offers_active_status(
        user_id=current_user.id,
        user_is_admin=current_user.isAdmin,
        is_active=offers_new_active_status,
        offerer_id=offerer_identifier,
        requested_status=payload.get("status"),
        venue_id=venue_identifier,
        type_id=type_id,
        name_keywords=name_keywords,
    )

    return "", 204


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
