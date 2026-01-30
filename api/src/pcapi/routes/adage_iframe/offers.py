import logging

from sqlalchemy import exc as sa_exc
from sqlalchemy.orm import exc as orm_exc

from pcapi.core.educational import exceptions as educational_exceptions
from pcapi.core.educational import repository as educational_repository
from pcapi.core.educational import utils as educational_utils
from pcapi.core.educational.api import offer as educational_api_offer
from pcapi.core.educational.models import AdageFrontRoles
from pcapi.core.educational.models import EducationalRedactor
from pcapi.models.api_errors import ApiErrors
from pcapi.routes.adage_iframe import blueprint
from pcapi.routes.adage_iframe.security import adage_jwt_required
from pcapi.routes.adage_iframe.serialization import offers as serializers
from pcapi.routes.adage_iframe.serialization.adage_authentication import AuthenticatedInformation
from pcapi.routes.adage_iframe.serialization.adage_authentication import (
    get_redactor_information_from_adage_authentication,
)
from pcapi.serialization.decorator import spectree_serialize
from pcapi.utils.transaction_manager import atomic


logger = logging.getLogger(__name__)


@blueprint.adage_iframe.route("/collective/offers/<int:offer_id>", methods=["GET"])
@atomic()
@spectree_serialize(response_model=serializers.CollectiveOfferResponseModel, api=blueprint.api, on_error_statuses=[404])
@adage_jwt_required
def get_collective_offer(
    authenticated_information: AuthenticatedInformation, offer_id: int
) -> serializers.CollectiveOfferResponseModel:
    try:
        offer = educational_repository.get_collective_offer_by_id_for_adage(offer_id)
    except orm_exc.NoResultFound:
        raise ApiErrors({"code": "COLLECTIVE_OFFER_NOT_FOUND"}, status_code=404)

    _get_redactor(authenticated_information)

    return serializers.CollectiveOfferResponseModel.build(offer=offer)


@blueprint.adage_iframe.route("/collective/offers-template/<int:offer_id>", methods=["GET"])
@atomic()
@spectree_serialize(
    response_model=serializers.CollectiveOfferTemplateResponseModel, api=blueprint.api, on_error_statuses=[404]
)
@adage_jwt_required
def get_collective_offer_template(
    authenticated_information: AuthenticatedInformation, offer_id: int
) -> serializers.CollectiveOfferTemplateResponseModel:
    try:
        offer = educational_repository.get_collective_offer_template_by_id_for_adage(offer_id)
    except orm_exc.NoResultFound:
        raise ApiErrors({"code": "COLLECTIVE_OFFER_TEMPLATE_NOT_FOUND"}, status_code=404)

    redactor = _get_redactor(authenticated_information)
    if redactor:
        is_favorite = offer in redactor.favoriteCollectiveOfferTemplates
    else:
        is_favorite = False

    return serializers.CollectiveOfferTemplateResponseModel.build(offer=offer, is_favorite=is_favorite)


@blueprint.adage_iframe.route("/collective/offers-template/", methods=["GET"])
@atomic()
@spectree_serialize(
    response_model=serializers.ListCollectiveOfferTemplateResponseModel,
    api=blueprint.api,
    on_error_statuses=[404],
    query_params_as_list=["ids"],
)
@adage_jwt_required
def get_collective_offer_templates(
    authenticated_information: AuthenticatedInformation, query: serializers.GetTemplateIdsModel
) -> serializers.ListCollectiveOfferTemplateResponseModel:
    if not query.ids:
        return serializers.ListCollectiveOfferTemplateResponseModel(collectiveOffers=[])

    try:
        offers = educational_repository.get_collective_offer_templates_by_ids_for_adage(query.ids).all()
    except sa_exc.SQLAlchemyError:
        raise ApiErrors({"code": "COLLECTIVE_OFFER_TEMPLATES_NOT_FOUND"}, status_code=400)

    if not offers:
        return serializers.ListCollectiveOfferTemplateResponseModel(collectiveOffers=[])

    redactor = _get_redactor(authenticated_information)
    favorite_offers = set(redactor.favoriteCollectiveOfferTemplates) if redactor else set()

    return serializers.ListCollectiveOfferTemplateResponseModel(
        collectiveOffers=[
            serializers.CollectiveOfferTemplateResponseModel.build(offer=offer, is_favorite=offer in favorite_offers)
            for offer in offers
        ]
    )


@blueprint.adage_iframe.route("/collective/offers-template/<int:offer_id>/request", methods=["POST"])
@atomic()
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
        offer = educational_repository.get_collective_offer_template_by_id_for_adage(offer_id)
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


@blueprint.adage_iframe.route("/collective/offers/my_institution", methods=["GET"])
@atomic()
@spectree_serialize(
    on_success_status=200, response_model=serializers.ListCollectiveOffersResponseModel, api=blueprint.api
)
@adage_jwt_required
def get_collective_offers_for_my_institution(
    authenticated_information: AuthenticatedInformation,
) -> serializers.ListCollectiveOffersResponseModel:
    if authenticated_information.uai is None:
        raise ApiErrors({"institutionId": "institutionId is required"}, status_code=400)

    _get_redactor(authenticated_information)

    offers = [
        offer
        for offer in educational_repository.get_offers_for_my_institution(authenticated_information.uai)
        if offer.isBookable
    ]

    return serializers.ListCollectiveOffersResponseModel(
        collectiveOffers=[serializers.CollectiveOfferResponseModel.build(offer=offer) for offer in offers]
    )
