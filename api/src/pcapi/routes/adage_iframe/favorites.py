from pcapi.core.educational import exceptions as educational_exceptions
from pcapi.core.educational import repository as educational_repository
from pcapi.core.educational.repository import find_redactor_by_email
from pcapi.models import db
from pcapi.models.api_errors import ApiErrors
from pcapi.repository.session_management import atomic
from pcapi.routes.adage_iframe import blueprint
from pcapi.routes.adage_iframe.security import adage_jwt_required
from pcapi.routes.adage_iframe.serialization import favorites as serialize_favorites
from pcapi.routes.adage_iframe.serialization.adage_authentication import AuthenticatedInformation
from pcapi.routes.adage_iframe.serialization.favorites import FavoritesResponseModel
from pcapi.serialization.decorator import spectree_serialize


@blueprint.adage_iframe.route("/collective/templates/<int:offer_id>/favorites", methods=["POST"])
@atomic()
@spectree_serialize(on_success_status=204, api=blueprint.api)
@adage_jwt_required
def post_collective_template_favorites(authenticated_information: AuthenticatedInformation, offer_id: int) -> None:
    try:
        offer_template = educational_repository.get_collective_offer_template_by_id(offer_id=offer_id)
    except educational_exceptions.CollectiveOfferTemplateNotFound:
        raise ApiErrors({"offer": ["Aucune offre trouvée pour cet id."]}, status_code=404)

    redactor = find_redactor_by_email(authenticated_information.email)
    if redactor is None:
        raise ApiErrors({"message": "Redactor not found"}, status_code=403)

    redactor.favoriteCollectiveOfferTemplates.append(offer_template)
    db.session.add(redactor)


@blueprint.adage_iframe.route("/collective/template/<int:offer_template_id>/favorites", methods=["DELETE"])
@atomic()
@spectree_serialize(on_success_status=204, api=blueprint.api)
@adage_jwt_required
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
@spectree_serialize(on_success_status=200, response_model=FavoritesResponseModel, api=blueprint.api)
@adage_jwt_required
def get_collective_favorites(authenticated_information: AuthenticatedInformation) -> FavoritesResponseModel:
    redactor = find_redactor_by_email(authenticated_information.email)
    if redactor is None:
        raise ApiErrors({"message": "Redactor not found"}, status_code=403)

    offer_templates = educational_repository.get_all_offer_template_by_redactor_id(redactor_id=redactor.id)

    if authenticated_information.uai is None:
        raise ApiErrors({"message": "institutionId is mandatory"}, status_code=403)

    serialized_favorite_templates = [
        serialize_favorites.serialize_collective_offer_template(offer_template=offer_template, is_favorite=True)
        for offer_template in offer_templates
    ]

    return FavoritesResponseModel(favoritesTemplate=serialized_favorite_templates)
