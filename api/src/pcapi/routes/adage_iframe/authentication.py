import datetime

from pcapi.core.educational import models as educational_models
from pcapi.core.educational import repository as educational_repository
from pcapi.core.educational.api import adage as educational_api_adage
from pcapi.core.educational.api.institution import get_educational_institution_department_code
from pcapi.core.educational.api.institution import get_offers_count_for_my_institution
from pcapi.core.educational.exceptions import MissingRequiredRedactorInformation
from pcapi.core.educational.models import AdageFrontRoles
from pcapi.core.educational.repository import find_educational_institution_by_uai_code
from pcapi.repository.session_management import atomic
from pcapi.routes.adage_iframe import blueprint
from pcapi.routes.adage_iframe.security import adage_jwt_required
from pcapi.routes.adage_iframe.serialization.adage_authentication import AuthenticatedInformation
from pcapi.routes.adage_iframe.serialization.adage_authentication import AuthenticatedResponse
from pcapi.routes.adage_iframe.serialization.adage_authentication import EducationalInstitutionProgramModel
from pcapi.routes.adage_iframe.serialization.adage_authentication import (
    get_redactor_information_from_adage_authentication,
)
from pcapi.routes.adage_iframe.serialization.redactor import RedactorPreferences
from pcapi.serialization.decorator import spectree_serialize


@blueprint.adage_iframe.route("/authenticate", methods=["GET"])
@atomic()
@spectree_serialize(api=blueprint.api, response_model=AuthenticatedResponse)
@adage_jwt_required
def authenticate(authenticated_information: AuthenticatedInformation) -> AuthenticatedResponse:
    # Warning: this GET route can create an object in db (_get_redactor -> find_or_create_redactor)

    if authenticated_information.uai is not None:
        institution = find_educational_institution_by_uai_code(authenticated_information.uai)
        department_code = get_educational_institution_department_code(institution) if institution else None
        institution_full_name = institution.full_name if institution else None

        redactor = _get_redactor(authenticated_information)
        preferences = _get_preferences(redactor)
        favorites_count = _get_favorites_count(redactor)
        offer_count = get_offers_count_for_my_institution(authenticated_information.uai)
        programs = _get_programs(institution)

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
            favoritesCount=favorites_count,
            offersCount=offer_count,
            institution_rural_level=institution.ruralLevel if institution else None,
            programs=programs,
            canPrebook=authenticated_information.canPrebook,
        )
    return AuthenticatedResponse(role=AdageFrontRoles.READONLY, canPrebook=False)


def _get_redactor(authenticated_information: AuthenticatedInformation) -> educational_models.EducationalRedactor | None:
    try:
        redactor_informations = get_redactor_information_from_adage_authentication(authenticated_information)
    except MissingRequiredRedactorInformation:
        return None
    return educational_repository.find_or_create_redactor(redactor_informations)


def _get_preferences(redactor: educational_models.EducationalRedactor | None) -> RedactorPreferences | None:
    if redactor:
        return RedactorPreferences(**redactor.preferences)
    return None


def _get_favorites_count(redactor: educational_models.EducationalRedactor | None) -> int:
    if redactor:
        return educational_api_adage.get_redactor_favorites_count(redactor.id)
    return 0


def _get_programs(institution: educational_models.EducationalInstitution | None) -> list:
    if not institution:
        return []
    return [
        EducationalInstitutionProgramModel.from_orm(program)
        for program in institution.programs_at_date(datetime.datetime.utcnow())
    ]
