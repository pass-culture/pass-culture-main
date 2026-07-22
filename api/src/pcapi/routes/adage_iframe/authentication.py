from pcapi.core.educational import models as educational_models
from pcapi.core.educational import repository as educational_repository
from pcapi.core.educational.api import adage as educational_api_adage
from pcapi.core.educational.api.institution import get_educational_institution_department_code
from pcapi.core.educational.api.institution import get_offers_count_for_my_institution
from pcapi.core.educational.exceptions import MissingRequiredRedactorInformation
from pcapi.core.educational.models import AdageFrontRoles
from pcapi.core.educational.repository import find_educational_institution_by_uai_code
from pcapi.routes.adage_iframe import blueprint
from pcapi.routes.adage_iframe.security import adage_jwt_required
from pcapi.routes.adage_iframe.serialization.adage_authentication import AuthenticatedInformation
from pcapi.routes.adage_iframe.serialization.adage_authentication import AuthenticatedResponse
from pcapi.routes.adage_iframe.serialization.adage_authentication import EducationalInstitutionProgramModel
from pcapi.routes.adage_iframe.serialization.adage_authentication import (
    get_redactor_information_from_adage_authentication,
)
from pcapi.routes.adage_iframe.serialization.redactor import RedactorPreferencesV2
from pcapi.serialization.decorator import spectree_serialize
from pcapi.utils import date as date_utils
from pcapi.utils.transaction_manager import atomic


@blueprint.adage_iframe.route("/authenticate", methods=["GET"])
@atomic()
@adage_jwt_required
@spectree_serialize(api=blueprint.api, response_model=AuthenticatedResponse)
def authenticate(authenticated_information: AuthenticatedInformation) -> AuthenticatedResponse:
    # Warning: this GET route can create an object in db (_get_redactor -> find_or_create_redactor)

    if authenticated_information.uai is not None:
        institution = find_educational_institution_by_uai_code(authenticated_information.uai)
        department_code = get_educational_institution_department_code(institution) if institution else None
        institution_full_name = institution.full_name if institution else None

        redactor = _get_redactor(authenticated_information)
        preferences = RedactorPreferencesV2(**redactor.preferences) if redactor else None
        favorites_count = educational_api_adage.get_redactor_favorites_count(redactor.id) if redactor else 0
        offer_count = get_offers_count_for_my_institution(authenticated_information.uai)
        programs = _get_programs(institution)

        return AuthenticatedResponse(
            role=AdageFrontRoles.REDACTOR if institution else AdageFrontRoles.READONLY,
            uai=authenticated_information.uai,
            department_code=department_code,
            institution_name=institution_full_name,
            institution_city=institution.city if institution else None,
            email=authenticated_information.email,
            preferences=preferences,
            lat=authenticated_information.lat,
            lon=authenticated_information.lon,
            favorites_count=favorites_count,
            offers_count=offer_count,
            institution_rural_level=institution.ruralLevel if institution else None,
            programs=programs,
            can_prebook=authenticated_information.canPrebook,
        )

    return AuthenticatedResponse(
        role=AdageFrontRoles.READONLY,
        uai=None,
        department_code=None,
        institution_name=None,
        institution_city=None,
        email=None,
        preferences=None,
        lat=None,
        lon=None,
        favorites_count=0,
        offers_count=0,
        institution_rural_level=None,
        programs=[],
        can_prebook=False,
    )


def _get_redactor(authenticated_information: AuthenticatedInformation) -> educational_models.EducationalRedactor | None:
    try:
        redactor_informations = get_redactor_information_from_adage_authentication(authenticated_information)
    except MissingRequiredRedactorInformation:
        return None
    return educational_repository.find_or_create_redactor(redactor_informations)


def _get_programs(institution: educational_models.EducationalInstitution | None) -> list:
    if not institution:
        return []

    return [
        EducationalInstitutionProgramModel.model_validate(program)
        for program in institution.programs_at_date(date_utils.get_naive_utc_now())
    ]
