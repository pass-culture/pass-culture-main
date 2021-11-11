from pcapi.routes.adage_iframe import blueprint
from pcapi.routes.adage_iframe.security import adage_jwt_required
from pcapi.routes.adage_iframe.serialization.adage_authentication import AdageFrontRoles
from pcapi.routes.adage_iframe.serialization.adage_authentication import AuthenticatedInformation
from pcapi.routes.adage_iframe.serialization.adage_authentication import AuthenticatedResponse
from pcapi.serialization.decorator import spectree_serialize


@blueprint.adage_iframe.route("/authenticate", methods=["GET"])
@spectree_serialize(api=blueprint.api, response_model=AuthenticatedResponse)
@adage_jwt_required
def authenticate(authenticated_information: AuthenticatedInformation) -> AuthenticatedResponse:
    if authenticated_information.uai is not None:
        return AuthenticatedResponse(role=AdageFrontRoles.REDACTOR)
    return AuthenticatedResponse(role=AdageFrontRoles.READONLY)
