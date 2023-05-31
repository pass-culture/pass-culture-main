import logging

from sqlalchemy.orm import exc as orm_exc

from pcapi.core.educational import repository as educational_repository
from pcapi.core.educational.api import offer as educational_api_offer
from pcapi.core.educational.api.categories import get_educational_categories
import pcapi.core.educational.utils as educational_utils
from pcapi.core.offerers.repository import get_venue_by_id
from pcapi.models.api_errors import ApiErrors
from pcapi.routes.adage_iframe import blueprint
from pcapi.routes.adage_iframe.security import adage_jwt_required
from pcapi.routes.adage_iframe.serialization import offers as serializers
from pcapi.routes.adage_iframe.serialization.adage_authentication import AuthenticatedInformation
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

    offer_venue_id = offer.offerVenue.get("venueId", None)
    if offer_venue_id:
        offer_venue = get_venue_by_id(offer_venue_id)
    else:
        offer_venue = None

    return serializers.CollectiveOfferResponseModel.from_orm(
        offer=offer,
        offerVenue=offer_venue,
        uai=authenticated_information.uai,
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

    offer_venue_id = offer.offerVenue.get("venueId", None)
    if offer_venue_id:
        offer_venue = get_venue_by_id(offer_venue_id)
    else:
        offer_venue = None

    return serializers.CollectiveOfferTemplateResponseModel.from_orm(offer, offer_venue)


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
    redactor = educational_repository.find_redactor_by_email(authenticated_information.email)  # type: ignore [arg-type]
    assert redactor
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
    )

    return serializers.CollectiveRequestResponseModel.from_orm(collective_request)
