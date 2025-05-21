import logging

from pydantic.v1 import Field
from pydantic.v1 import ValidationError

from pcapi.core.educational import models as educational_models
from pcapi.core.educational.exceptions import MissingRequiredRedactorInformation
from pcapi.core.educational.models import AdageFrontRoles
from pcapi.routes.serialization import BaseModel
from pcapi.serialization.educational.adage.shared import RedactorInformation
from pcapi.serialization.utils import to_camel

from .redactor import RedactorPreferences


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


class EducationalInstitutionProgramModel(BaseModel):
    name: str
    label: str | None
    description: str | None

    class Config:
        orm_mode = True
        alias_generator = to_camel
        allow_population_by_field_name = True


class AuthenticatedResponse(BaseModel):
    role: AdageFrontRoles
    uai: str | None = None
    departmentCode: str | None = None
    institutionName: str | None = None
    institutionCity: str | None = None
    email: str | None = None
    preferences: RedactorPreferences | None = None
    lat: float | None = None
    lon: float | None = None
    favoritesCount: int = 0
    offersCount: int = 0
    institution_rural_level: educational_models.InstitutionRuralLevel | None = None
    programs: list[EducationalInstitutionProgramModel] = Field(default_factory=list)
    canPrebook: bool | None = None

    class Config:
        use_enum_values = True
        alias_generator = to_camel
        allow_population_by_field_name = True


def get_redactor_information_from_adage_authentication(
    authenticated_information: AuthenticatedInformation,
) -> RedactorInformation:
    try:
        redactor_information: RedactorInformation = RedactorInformation(**authenticated_information.dict())
    except ValidationError:
        raise MissingRequiredRedactorInformation()
    return redactor_information
