from pcapi.core.educational import repository as educational_repository
from pcapi.models import db
from pcapi.models.api_errors import ApiErrors
from pcapi.routes.adage_iframe import blueprint
from pcapi.routes.adage_iframe.security import adage_jwt_required
from pcapi.routes.adage_iframe.serialization.adage_authentication import AuthenticatedInformation
from pcapi.routes.adage_iframe.serialization.redactor import RedactorPreferences
from pcapi.serialization.decorator import spectree_serialize
from pcapi.utils.transaction_manager import atomic


@blueprint.adage_iframe.route("/redactor/preferences", methods=["POST"])
@atomic()
@spectree_serialize(api=blueprint.api, on_success_status=204)
@adage_jwt_required
def save_redactor_preferences(
    body: RedactorPreferences,
    authenticated_information: AuthenticatedInformation,
) -> None:
    redactor = educational_repository.find_redactor_by_email(authenticated_information.email)
    if not redactor:
        raise ApiErrors({"message": "Redactor not found"}, status_code=403)

    redactor.preferences = {**redactor.preferences, **body.dict()}
    db.session.add(redactor)
    db.session.flush()
