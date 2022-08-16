from pcapi.core.educational.api import get_educational_institution_department_code
from pcapi.core.educational.repository import find_educational_institution_by_uai_code
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
        institution = find_educational_institution_by_uai_code(authenticated_information.uai)
        department_code = get_educational_institution_department_code(institution) if institution else None
        institution_full_name = f"{institution.institutionType} {institution.name}".strip() if institution else None
        return AuthenticatedResponse(
            role=AdageFrontRoles.REDACTOR,
            uai=authenticated_information.uai,
            departmentCode=department_code,
            institutionName=institution_full_name,
            institutionCity=institution.city if institution else None,
        )
    return AuthenticatedResponse(role=AdageFrontRoles.READONLY)
