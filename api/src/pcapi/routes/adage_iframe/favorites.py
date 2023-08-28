from pcapi.core.educational import exceptions as educational_exceptions
from pcapi.core.educational import repository as educational_repository
from pcapi.core.educational.api import favorites as educational_api
from pcapi.core.educational.repository import find_redactor_by_email
from pcapi.models.api_errors import ApiErrors
from pcapi.routes.adage_iframe import blueprint
from pcapi.routes.adage_iframe.security import adage_jwt_required
from pcapi.routes.adage_iframe.serialization import favorites as serializers
from pcapi.routes.adage_iframe.serialization.adage_authentication import AuthenticatedInformation
from pcapi.routes.adage_iframe.serialization.favorites import CollectiveOfferFavoritesBodyModel
from pcapi.serialization.decorator import spectree_serialize


@blueprint.adage_iframe.route("/collective/offer-favorites", methods=["POST"])
@spectree_serialize(response_model=serializers.FavoritesOfferResponseModel, api=blueprint.api)
@adage_jwt_required
def post_collective_offer_favorites(
    authenticated_information: AuthenticatedInformation,
    body: CollectiveOfferFavoritesBodyModel,
) -> serializers.FavoritesOfferResponseModel:
    try:
        offer = educational_repository.get_collective_offer_by_id(offer_id=body.offerId)
    except educational_exceptions.CollectiveOfferNotFound:
        raise ApiErrors({"offer": "l'offre est introuvable"}, status_code=404)

    redactor = find_redactor_by_email(authenticated_information.email)  # type: ignore [arg-type]
    if not redactor:
        raise ApiErrors({"message": "Redactor not found"}, status_code=403)

    favorite = educational_api.add_offer_to_favorite_adage(
        redactorId=redactor.id,
        offerId=offer.id,
    )

    return serializers.FavoritesOfferResponseModel.from_orm(favorite)


@blueprint.adage_iframe.route("/collective/template-favorites", methods=["POST"])
@spectree_serialize(response_model=serializers.FavoritesTemplateResponseModel, api=blueprint.api)
@adage_jwt_required
def post_collective_template_favorites(
    authenticated_information: AuthenticatedInformation,
    body: CollectiveOfferFavoritesBodyModel,
) -> serializers.FavoritesTemplateResponseModel:
    try:
        offerTemplate = educational_repository.get_collective_offer_template_by_id(offer_id=body.offerId)
    except educational_exceptions.CollectiveOfferTemplateNotFound:
        raise ApiErrors({"offer": ["Aucune offre trouvée pour cet id."]}, status_code=404)

    redactor = find_redactor_by_email(authenticated_information.email)  # type: ignore [arg-type]
    if not redactor:
        raise ApiErrors({"message": "Redactor not found"}, status_code=403)

    favorite = educational_api.add_offer_template_to_favorite_adage(
        redactorId=redactor.id,
        offerId=offerTemplate.id,
    )

    return serializers.FavoritesTemplateResponseModel.from_orm(favorite)
