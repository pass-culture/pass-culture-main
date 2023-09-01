from pcapi.core.educational import exceptions as educational_exceptions
from pcapi.core.educational import repository as educational_repository
from pcapi.core.educational.api import favorites as educational_api
from pcapi.core.educational.models import CollectiveOfferEducationalRedactor
from pcapi.core.educational.models import CollectiveOfferTemplateEducationalRedactor
from pcapi.core.educational.repository import find_redactor_by_email
from pcapi.models import db
from pcapi.models.api_errors import ApiErrors
from pcapi.routes.adage_iframe import blueprint
from pcapi.routes.adage_iframe.security import adage_jwt_required
from pcapi.routes.adage_iframe.serialization.adage_authentication import AuthenticatedInformation
from pcapi.serialization.decorator import spectree_serialize


@blueprint.adage_iframe.route("/collective/offers/<int:offer_id>/favorites", methods=["POST"])
@spectree_serialize(on_success_status=204, api=blueprint.api)
@adage_jwt_required
def post_collective_offer_favorites(
    authenticated_information: AuthenticatedInformation,
    offer_id: int,
) -> None:
    try:
        offer = educational_repository.get_collective_offer_by_id(offer_id=offer_id)
    except educational_exceptions.CollectiveOfferNotFound:
        raise ApiErrors({"offer": "l'offre est introuvable"}, status_code=404)

    if authenticated_information.email is None:
        raise ApiErrors({"message": "email is mandatory"}, status_code=400)

    redactor = find_redactor_by_email(authenticated_information.email)
    if redactor is None:
        raise ApiErrors({"message": "Redactor not found"}, status_code=403)

    educational_api.add_offer_to_favorite_adage(
        redactorId=redactor.id,
        offerId=offer.id,
    )

    return


@blueprint.adage_iframe.route("/collective/templates/<int:offer_id>/favorites", methods=["POST"])
@spectree_serialize(on_success_status=204, api=blueprint.api)
@adage_jwt_required
def post_collective_template_favorites(
    authenticated_information: AuthenticatedInformation,
    offer_id: int,
) -> None:
    try:
        offerTemplate = educational_repository.get_collective_offer_template_by_id(offer_id=offer_id)
    except educational_exceptions.CollectiveOfferTemplateNotFound:
        raise ApiErrors({"offer": ["Aucune offre trouvée pour cet id."]}, status_code=404)

    if authenticated_information.email is None:
        raise ApiErrors({"message": "email is mandatory"}, status_code=400)

    redactor = find_redactor_by_email(authenticated_information.email)
    if redactor is None:
        raise ApiErrors({"message": "Redactor not found"}, status_code=403)

    educational_api.add_offer_template_to_favorite_adage(
        redactorId=redactor.id,
        offerId=offerTemplate.id,
    )

    return


@blueprint.adage_iframe.route("/collective/offer/<int:offer_id>/favorites", methods=["DELETE"])
@spectree_serialize(on_success_status=204, api=blueprint.api)
@adage_jwt_required
def delete_favorite_for_collective_offer(authenticated_information: AuthenticatedInformation, offer_id: int) -> None:
    if authenticated_information.email is None:
        raise ApiErrors({"message": "email is mandatory"}, status_code=400)

    redactor = find_redactor_by_email(authenticated_information.email)
    if redactor is None:
        raise ApiErrors({"message": "Redactor not found"}, status_code=403)

    try:
        educational_repository.get_collective_offer_by_id(offer_id=offer_id)
    except educational_exceptions.CollectiveOfferNotFound:
        raise ApiErrors({"offer": ["Aucune offre trouvée pour cet id"]}, status_code=404)

    CollectiveOfferEducationalRedactor.query.filter_by(
        educationalRedactorId=redactor.id, collectiveOfferId=offer_id
    ).delete(synchronize_session=False)

    db.session.commit()

    return


@blueprint.adage_iframe.route("/collective/template/<int:offer_template_id>/favorites", methods=["DELETE"])
@spectree_serialize(on_success_status=204, api=blueprint.api)
@adage_jwt_required
def delete_favorite_for_collective_offer_template(
    authenticated_information: AuthenticatedInformation, offer_template_id: int
) -> None:
    if authenticated_information.email is None:
        raise ApiErrors({"message": "email is mandatory"}, status_code=400)

    redactor = find_redactor_by_email(authenticated_information.email)
    if redactor is None:
        raise ApiErrors({"message": "Redactor not found"}, status_code=403)

    try:
        educational_repository.get_collective_offer_template_by_id(offer_id=offer_template_id)
    except educational_exceptions.CollectiveOfferTemplateNotFound:
        raise ApiErrors({"offer_template": ["Aucune offre template trouvée pour cet id"]}, status_code=404)

    CollectiveOfferTemplateEducationalRedactor.query.filter_by(
        educationalRedactorId=redactor.id, collectiveOfferTemplateId=offer_template_id
    ).delete(synchronize_session=False)

    db.session.commit()

    return
