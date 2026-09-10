from pcapi.core.educational import exceptions as educational_exceptions
from pcapi.core.educational import repository as educational_repository
from pcapi.core.educational.repository import find_redactor_by_email
from pcapi.models import db
from pcapi.models.api_errors import ApiErrors
from pcapi.routes.adage_iframe import blueprint
from pcapi.routes.adage_iframe.security import adage_jwt_required
from pcapi.routes.adage_iframe.serialization import offers as serialize_offers
from pcapi.routes.adage_iframe.serialization.adage_authentication import AuthenticatedInformation
from pcapi.routes.adage_iframe.serialization.favorites import FavoritesResponseModel
from pcapi.serialization.decorator import spectree_serialize
from pcapi.utils.transaction_manager import atomic


@blueprint.adage_iframe.route("/collective/templates/<int:offer_id>/favorites", methods=["POST"])
@atomic()
@adage_jwt_required
@spectree_serialize(on_success_status=204, api=blueprint.api)
def post_collective_template_favorites(authenticated_information: AuthenticatedInformation, offer_id: int) -> None:
    try:
        offer_template = educational_repository.get_collective_offer_template_by_id(offer_id=offer_id)
    except educational_exceptions.CollectiveOfferTemplateNotFound:
        raise ApiErrors({"offer": ["Aucune offre trouvée pour cet id."]}, status_code=404)

    redactor = find_redactor_by_email(authenticated_information.email)
    if redactor is None:
        raise ApiErrors({"message": "Redactor not found"}, status_code=403)

    if offer_template not in redactor.favoriteCollectiveOfferTemplates:
        redactor.favoriteCollectiveOfferTemplates.append(offer_template)
        db.session.add(redactor)
        db.session.flush()


@blueprint.adage_iframe.route("/collective/template/<int:offer_template_id>/favorites", methods=["DELETE"])
@atomic()
@adage_jwt_required
@spectree_serialize(on_success_status=204, api=blueprint.api)
def delete_favorite_for_collective_offer_template(
    authenticated_information: AuthenticatedInformation, offer_template_id: int
) -> None:
    redactor = find_redactor_by_email(authenticated_information.email)
    if redactor is None:
        raise ApiErrors({"message": "Redactor not found"}, status_code=403)

    try:
        offer_template = educational_repository.get_collective_offer_template_by_id(offer_id=offer_template_id)
    except educational_exceptions.CollectiveOfferTemplateNotFound:
        raise ApiErrors({"offer_template": ["Aucune offre template trouvée pour cet id"]}, status_code=404)

    if offer_template in redactor.favoriteCollectiveOfferTemplates:
        redactor.favoriteCollectiveOfferTemplates.remove(offer_template)
        db.session.add(redactor)


@blueprint.adage_iframe.route("/collective/favorites", methods=["GET"])
@atomic()
@adage_jwt_required
@spectree_serialize(on_success_status=200, response_model=FavoritesResponseModel, api=blueprint.api)
def get_collective_favorites(authenticated_information: AuthenticatedInformation) -> FavoritesResponseModel:
    redactor = find_redactor_by_email(authenticated_information.email)
    if redactor is None:
        raise ApiErrors({"message": "Redactor not found"}, status_code=403)

    if authenticated_information.uai is None:
        raise ApiErrors({"message": "institutionId is mandatory"}, status_code=403)

    offer_templates = educational_repository.get_all_offer_template_by_redactor_id(redactor_id=redactor.id)

    return FavoritesResponseModel(
        favoritesTemplate=[
            serialize_offers.CollectiveOfferTemplateResponseModel.build(offer=offer, is_favorite=True)
            for offer in offer_templates
            if offer.is_eligible_for_search
        ]
    )
