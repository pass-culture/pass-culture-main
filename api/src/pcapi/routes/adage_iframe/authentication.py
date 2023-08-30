from pcapi.core.educational import repository as educational_repository
from pcapi.core.educational.api.institution import get_educational_institution_department_code
from pcapi.core.educational.exceptions import MissingRequiredRedactorInformation
from pcapi.core.educational.repository import find_educational_institution_by_uai_code
from pcapi.routes.adage_iframe import blueprint
from pcapi.routes.adage_iframe.security import adage_jwt_required
from pcapi.routes.adage_iframe.serialization.adage_authentication import (
    get_redactor_information_from_adage_authentication,
)
from pcapi.routes.adage_iframe.serialization.adage_authentication import AdageFrontRoles
from pcapi.routes.adage_iframe.serialization.adage_authentication import AuthenticatedInformation
from pcapi.routes.adage_iframe.serialization.adage_authentication import AuthenticatedResponse
from pcapi.routes.adage_iframe.serialization.redactor import RedactorPreferences
from pcapi.serialization.decorator import spectree_serialize


@blueprint.adage_iframe.route("/authenticate", methods=["GET"])
@spectree_serialize(api=blueprint.api, response_model=AuthenticatedResponse)
@adage_jwt_required
def authenticate(authenticated_information: AuthenticatedInformation) -> AuthenticatedResponse:
    if authenticated_information.uai is not None:
        institution = find_educational_institution_by_uai_code(authenticated_information.uai)
        department_code = get_educational_institution_department_code(institution) if institution else None
        institution_full_name = f"{institution.institutionType} {institution.name}".strip() if institution else None

        try:
            redactor_informations = get_redactor_information_from_adage_authentication(authenticated_information)
        except MissingRequiredRedactorInformation:
            preferences = None
        else:
            redactor = educational_repository.find_or_create_redactor(redactor_informations)
            preferences = RedactorPreferences(**redactor.preferences)

        return AuthenticatedResponse(
            role=AdageFrontRoles.REDACTOR if institution else AdageFrontRoles.READONLY,
            uai=authenticated_information.uai,
            departmentCode=department_code,
            institutionName=institution_full_name,
            institutionCity=institution.city if institution else None,
            email=authenticated_information.email,
            preferences=preferences,
            lat=authenticated_information.lat,
            lon=authenticated_information.lon,
        )
    return AuthenticatedResponse(role=AdageFrontRoles.READONLY)
