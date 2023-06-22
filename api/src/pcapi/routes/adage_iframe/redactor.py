from pcapi.core.educational import repository as educational_repository
import pcapi.core.educational.api.redactor as educational_redactor_api
from pcapi.core.educational.exceptions import MissingRequiredRedactorInformation
from pcapi.models.api_errors import ApiErrors
from pcapi.routes.adage_iframe import blueprint
from pcapi.routes.adage_iframe import serialization
from pcapi.routes.adage_iframe.security import adage_jwt_required
from pcapi.routes.adage_iframe.serialization.adage_authentication import (
    get_redactor_information_from_adage_authentication,
)
from pcapi.routes.adage_iframe.serialization.adage_authentication import AuthenticatedInformation
from pcapi.serialization.decorator import spectree_serialize


@blueprint.adage_iframe.route("/redactor/preferences", methods=["POST"])
@spectree_serialize(api=blueprint.api, on_success_status=204)
@adage_jwt_required
def save_redactor_preferences(
    body: serialization.redactor.RedactorPreferences,
    authenticated_information: AuthenticatedInformation,
) -> None:
    try:
        redactor_informations = get_redactor_information_from_adage_authentication(authenticated_information)
    except MissingRequiredRedactorInformation:
        raise ApiErrors({"code": 401, "message": "Missing authentication information"})

    redactor = educational_repository.find_redactor_by_email(redactor_informations.email)
    if not redactor:
        raise ApiErrors({"code": 404, "message": "Redactor not found"})

    educational_redactor_api.save_redactor_preferences(redactor, **body.dict())
