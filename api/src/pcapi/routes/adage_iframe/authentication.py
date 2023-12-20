import typing

from pcapi.core.educational import models as educational_models
from pcapi.core.educational import repository as educational_repository
from pcapi.core.educational.api import favorites as educational_api_favorite
from pcapi.core.educational.api import institution as institution_api
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
from pcapi.routes.adage_iframe.serialization.adage_authentication import EducationalInstitutionProgramModel
from pcapi.routes.adage_iframe.serialization.adage_authentication import get_offers_count
from pcapi.routes.adage_iframe.serialization.redactor import RedactorPreferences
from pcapi.serialization.decorator import spectree_serialize


OptionalRedactor = educational_models.EducationalRedactor | None
OptionalInstitution = educational_models.EducationalInstitution | None


@blueprint.adage_iframe.route("/authenticate", methods=["GET"])
@spectree_serialize(api=blueprint.api, response_model=AuthenticatedResponse)
@adage_jwt_required
def authenticate(authenticated_information: AuthenticatedInformation) -> AuthenticatedResponse:
    if authenticated_information.uai is not None:
        institution = find_educational_institution_by_uai_code(authenticated_information.uai)
        department_code = get_educational_institution_department_code(institution) if institution else None
        institution_full_name = institution.full_name if institution else None

        redactor = _get_redactor(authenticated_information)
        preferences = _get_preferences(redactor)
        favorites_count = _get_favorites_count(redactor)
        offer_count = get_offers_count(authenticated_information)
        institution_rural_level = typing.cast(
            educational_models.InstitutionRuralLevel | None, institution_api.get_institution_rural_level(institution)
        )
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
            institution_rural_level=institution_rural_level,
            programs=programs,
        )
    return AuthenticatedResponse(role=AdageFrontRoles.READONLY)


def _get_redactor(authenticated_information: AuthenticatedInformation) -> OptionalRedactor:
    try:
        redactor_informations = get_redactor_information_from_adage_authentication(authenticated_information)
    except MissingRequiredRedactorInformation:
        return None
    return educational_repository.find_or_create_redactor(redactor_informations)


def _get_preferences(redactor: OptionalRedactor) -> RedactorPreferences | None:
    if redactor:
        return RedactorPreferences(**redactor.preferences)
    return None


def _get_favorites_count(redactor: OptionalRedactor) -> int:
    if redactor:
        return educational_api_favorite.get_redactor_all_favorites_count(redactor.id)
    return 0


def _get_programs(institution: OptionalInstitution) -> list:
    if not institution:
        return []
    return [EducationalInstitutionProgramModel.from_orm(program) for program in institution.programs]
