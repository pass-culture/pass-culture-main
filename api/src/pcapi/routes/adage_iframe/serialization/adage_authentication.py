import logging

from pydantic.v1 import ValidationError

from pcapi.core.educational import models as educational_models
from pcapi.core.educational.exceptions import MissingRequiredRedactorInformation
from pcapi.core.educational.models import AdageFrontRoles
from pcapi.core.educational.schemas import RedactorInformation
from pcapi.routes.adage_iframe.serialization.redactor import RedactorPreferencesV2
from pcapi.routes.serialization import BaseModel
from pcapi.routes.serialization import HttpBodyModel


logger = logging.getLogger(__name__)


class AuthenticatedInformation(BaseModel):
    civility: str | None
    lastname: str | None
    firstname: str | None
    email: str
    uai: str | None
    lat: float | None
    lon: float | None
    canPrebook: bool | None


class EducationalInstitutionProgramModel(HttpBodyModel):
    name: str
    label: str | None
    description: str | None


class AuthenticatedResponse(HttpBodyModel):
    role: AdageFrontRoles
    uai: str | None
    department_code: str | None
    institution_name: str | None
    institution_city: str | None
    email: str | None
    preferences: RedactorPreferencesV2 | None
    lat: float | None
    lon: float | None
    favorites_count: int
    offers_count: int
    institution_rural_level: educational_models.InstitutionRuralLevel | None
    programs: list[EducationalInstitutionProgramModel]
    can_prebook: bool | None


def get_redactor_information_from_adage_authentication(
    authenticated_information: AuthenticatedInformation,
) -> RedactorInformation:
    try:
        redactor_information: RedactorInformation = RedactorInformation(**authenticated_information.dict())
    except ValidationError:
        raise MissingRequiredRedactorInformation()
    return redactor_information
