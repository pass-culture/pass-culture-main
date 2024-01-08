import logging

from sqlalchemy.orm import exc as orm_exc

import pcapi.core.categories.subcategories_v2 as subcategories
from pcapi.core.educational import exceptions as educational_exceptions
from pcapi.core.educational import repository as educational_repository
from pcapi.core.educational.api import favorites as educational_api_favorites
from pcapi.core.educational.api import offer as educational_api_offer
from pcapi.core.educational.api.categories import get_educational_categories
from pcapi.core.educational.models import CollectiveOffer
from pcapi.core.educational.models import CollectiveOfferTemplate
from pcapi.core.educational.models import EducationalRedactor
import pcapi.core.educational.utils as educational_utils
from pcapi.core.offerers.models import Venue
from pcapi.core.offerers.repository import get_venue_by_id
from pcapi.models.api_errors import ApiErrors
from pcapi.routes.adage_iframe import blueprint
from pcapi.routes.adage_iframe.security import adage_jwt_required
from pcapi.routes.adage_iframe.serialization import offers as serializers
from pcapi.routes.adage_iframe.serialization.adage_authentication import (
    get_redactor_information_from_adage_authentication,
)
from pcapi.routes.adage_iframe.serialization.adage_authentication import AdageFrontRoles
from pcapi.routes.adage_iframe.serialization.adage_authentication import AuthenticatedInformation
from pcapi.routes.adage_iframe.serialization.favorites import serialize_collective_offer
from pcapi.serialization.decorator import spectree_serialize


logger = logging.getLogger(__name__)


@blueprint.adage_iframe.route("/offers/categories", methods=["GET"])
@spectree_serialize(response_model=serializers.CategoriesResponseModel, api=blueprint.api)
@adage_jwt_required
def get_educational_offers_categories(
    authenticated_information: AuthenticatedInformation,
) -> serializers.CategoriesResponseModel:
    educational_categories = get_educational_categories()

    return serializers.CategoriesResponseModel(
        categories=[
            serializers.CategoryResponseModel.from_orm(category) for category in educational_categories["categories"]
        ],
        subcategories=[
            serializers.SubcategoryResponseModel.from_orm(subcategory)
            for subcategory in educational_categories["subcategories"]
        ],
    )


@blueprint.adage_iframe.route("/collective/all-offers", methods=["GET"])
@spectree_serialize(response_model=serializers.ListCollectiveOffersResponseModel, api=blueprint.api)
@adage_jwt_required
def get_educational_eligible_offers_by_uai(
    authenticated_information: AuthenticatedInformation,
) -> serializers.ListCollectiveOffersResponseModel:
    # TODO(jeremieb): remove since it should return only indexable
    # collective offers...and we won't index them anymore.
    # Keep the route for now to avoid any breaking change.
    if authenticated_information.uai is None:
        raise ApiErrors({"institutionId": "institutionId is required"}, status_code=400)

    list_offers_by_uai = educational_repository.get_all_collective_offers_by_institutionUAI(
        uai=authenticated_information.uai
    )

    redactor = _get_redactor(authenticated_information)

    current_user_favorite_offers = educational_repository.get_user_favorite_offers_from_uai(
        redactor_id=redactor.id if redactor else None, uai=authenticated_information.uai
    )

    serialized_favorite_offers = [
        serialize_collective_offer(offer=offer, is_favorite=offer.id in current_user_favorite_offers)
        for offer in list_offers_by_uai
        if offer.is_eligible_for_search
    ]

    return serializers.ListCollectiveOffersResponseModel(collectiveOffers=serialized_favorite_offers)


@blueprint.adage_iframe.route("/offers/formats", methods=["GET"])
@spectree_serialize(response_model=serializers.EacFormatsResponseModel, api=blueprint.api)
@adage_jwt_required
def get_educational_offers_formats(
    authenticated_information: AuthenticatedInformation,
) -> serializers.EacFormatsResponseModel:
    return serializers.EacFormatsResponseModel(formats=list(subcategories.EacFormat))


@blueprint.adage_iframe.route("/collective/offers/<int:offer_id>", methods=["GET"])
@spectree_serialize(response_model=serializers.CollectiveOfferResponseModel, api=blueprint.api, on_error_statuses=[404])
@adage_jwt_required
def get_collective_offer(
    authenticated_information: AuthenticatedInformation, offer_id: int
) -> serializers.CollectiveOfferResponseModel:
    try:
        offer = educational_api_offer.get_collective_offer_by_id_for_adage(offer_id)
    except orm_exc.NoResultFound:
        raise ApiErrors({"code": "COLLECTIVE_OFFER_NOT_FOUND"}, status_code=404)

    redactor = _get_redactor(authenticated_information)
    if redactor:
        is_favorite = educational_api_favorites.is_offer_a_redactor_favorite(offer.id, redactor.id)
    else:
        is_favorite = False

    offer_venue = _get_offer_venue(offer)
    return serializers.CollectiveOfferResponseModel.build(
        offer=offer,
        offerVenue=offer_venue,
        is_favorite=is_favorite,
    )


@blueprint.adage_iframe.route("/collective/offers-template/<int:offer_id>", methods=["GET"])
@spectree_serialize(
    response_model=serializers.CollectiveOfferTemplateResponseModel, api=blueprint.api, on_error_statuses=[404]
)
@adage_jwt_required
def get_collective_offer_template(
    authenticated_information: AuthenticatedInformation, offer_id: int
) -> serializers.CollectiveOfferTemplateResponseModel:
    try:
        offer = educational_api_offer.get_collective_offer_template_by_id_for_adage(offer_id)
    except orm_exc.NoResultFound:
        raise ApiErrors({"code": "COLLECTIVE_OFFER_TEMPLATE_NOT_FOUND"}, status_code=404)

    redactor = _get_redactor(authenticated_information)
    if redactor:
        is_favorite = educational_api_favorites.is_offer_template_a_redactor_favorite(offer.id, redactor.id)
    else:
        is_favorite = False

    offer_venue = _get_offer_venue(offer)

    return serializers.CollectiveOfferTemplateResponseModel.build(
        offer=offer, is_favorite=is_favorite, offerVenue=offer_venue
    )


@blueprint.adage_iframe.route("/collective/offers-template/<int:offer_id>/request", methods=["POST"])
@spectree_serialize(
    response_model=serializers.CollectiveRequestResponseModel, api=blueprint.api, on_error_statuses=[404]
)
@adage_jwt_required
def create_collective_request(
    body: serializers.PostCollectiveRequestBodyModel,
    offer_id: int,
    authenticated_information: AuthenticatedInformation,
) -> serializers.CollectiveRequestResponseModel:
    try:
        offer = educational_api_offer.get_collective_offer_template_by_id_for_adage(offer_id)
    except orm_exc.NoResultFound:
        raise ApiErrors({"code": "COLLECTIVE_OFFER_TEMPLATE_NOT_FOUND"}, status_code=404)

    institution = educational_repository.get_educational_institution_public(
        institution_id=None, uai=authenticated_information.uai
    )
    if not institution:
        raise ApiErrors({"code": "INSTITUTION_NOT_FOUND"}, status_code=404)

    redactor_informations = get_redactor_information_from_adage_authentication(authenticated_information)
    redactor = educational_repository.find_or_create_redactor(redactor_informations)

    collective_request = educational_api_offer.create_offer_request(body, offer, institution, redactor)

    educational_utils.log_information_for_data_purpose(
        event_name="CreateCollectiveOfferRequest",
        extra_data={
            "id": collective_request.id,
            "collective_offer_template_id": offer.id,
            "requested_date": body.requested_date,
            "total_students": body.total_students,
            "total_teachers": body.total_teachers,
            "comment": body.comment,
        },
        user_email=authenticated_information.email,
        uai=authenticated_information.uai,
        user_role=AdageFrontRoles.REDACTOR if institution else AdageFrontRoles.READONLY,
    )

    return serializers.CollectiveRequestResponseModel.from_orm(collective_request)


def _get_redactor(authenticated_information: AuthenticatedInformation) -> EducationalRedactor | None:
    try:
        redactor_informations = get_redactor_information_from_adage_authentication(authenticated_information)
    except educational_exceptions.MissingRequiredRedactorInformation:
        return None
    return educational_repository.find_redactor_by_email(redactor_informations.email)


def _get_offer_venue(offer: CollectiveOffer | CollectiveOfferTemplate) -> Venue | None:
    offer_venue_id = offer.offerVenue.get("venueId", None)
    if offer_venue_id:
        return get_venue_by_id(offer_venue_id)
    return None
