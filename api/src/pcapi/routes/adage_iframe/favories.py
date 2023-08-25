from pcapi.core.educational import exceptions as educational_exceptions
from pcapi.core.educational import repository as educational_repository
from pcapi.core.educational.api import favories as educational_api
from pcapi.routes.adage_iframe import blueprint
from pcapi.routes.adage_iframe.security import adage_jwt_required
from pcapi.routes.adage_iframe.serialization import favories as serializers
from pcapi.routes.adage_iframe.serialization.adage_authentication import AuthenticatedInformation
from pcapi.routes.adage_iframe.serialization.favories import CollectiveOfferFavoriesBodyModel
from pcapi.serialization.decorator import spectree_serialize


@blueprint.adage_iframe.route("/collective/favories", methods=["POST"])
@spectree_serialize(response_model=serializers.FavoriesResponseModel, api=blueprint.api)
@adage_jwt_required
def post_collective_favories(
    authenticated_information: AuthenticatedInformation,
    body: CollectiveOfferFavoriesBodyModel,
) -> serializers.FavoriesResponseModel:
    try:
        offerTemplate = educational_repository.get_collective_offer_template_by_id(offer_id=body.offerId)
    except educational_exceptions.CollectiveOfferTemplateNotFound:
        offerTemplate = None
    if not offerTemplate:
        offer = educational_repository.get_collective_offer_by_id(offer_id=body.offerId)

    if offerTemplate:
        favories = educational_api.add_offer_template_to_favories_adage(
            uai=authenticated_information.uai,  # type: ignore [arg-type]
            offerId=offerTemplate.id,
        )
        result = serializers.FavoriesResponseModel(
            educationalRedactor=favories.educationalRedactor, offerId=favories.offerTemplateId
        )
    else:
        favories = educational_api.add_offer_to_favories_adage(
            uai=authenticated_information.uai,  # type: ignore [arg-type]
            offerId=offer.id,
        )
        result = serializers.FavoriesResponseModel.from_orm(favories)
    return result
