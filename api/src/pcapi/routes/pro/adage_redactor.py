from pcapi.core.educational import repository as educational_repository
import pcapi.core.educational.api.redactor as educational_redactor_api
from pcapi.models.api_errors import ApiErrors
from pcapi.routes.pro import adage_blueprint
from pcapi.routes.pro.adage_security import adage_jwt_required
from pcapi.routes.serialization import redactor as serialized_redactor
from pcapi.routes.serialization.adage_authentication import AuthenticatedInformation
from pcapi.serialization.decorator import spectree_serialize


@adage_blueprint.adage_iframe.route("/redactor/preferences", methods=["POST"])
@spectree_serialize(api=adage_blueprint.api, on_success_status=204)
@adage_jwt_required
def save_redactor_preferences(
    body: serialized_redactor.RedactorPreferences,
    authenticated_information: AuthenticatedInformation,
) -> None:
    redactor = educational_repository.find_redactor_by_email(authenticated_information.email)
    if not redactor:
        raise ApiErrors({"message": "Redactor not found"}, status_code=403)

    educational_redactor_api.save_redactor_preferences(redactor, **body.dict())
