import enum
import logging

from pydantic import ValidationError

from pcapi.core.educational.exceptions import MissingRequiredRedactorInformation
from pcapi.routes.serialization import BaseModel

from .redactor import RedactorPreferences


logger = logging.getLogger(__name__)


class AdageFrontRoles(enum.Enum):
    REDACTOR = "redactor"
    READONLY = "readonly"


class AuthenticatedInformation(BaseModel):
    civility: str | None
    lastname: str | None
    firstname: str | None
    email: str | None
    uai: str | None
    lat: float | None
    lon: float | None


class AuthenticatedResponse(BaseModel):
    role: AdageFrontRoles
    uai: str | None
    departmentCode: str | None
    institutionName: str | None
    institutionCity: str | None
    email: str | None
    preferences: RedactorPreferences | None
    lat: float | None
    lon: float | None

    class Config:
        use_enum_values = True


class RedactorInformation(BaseModel):
    civility: str | None
    lastname: str | None
    firstname: str | None
    email: str
    uai: str


def get_redactor_information_from_adage_authentication(
    authenticated_information: AuthenticatedInformation,
) -> RedactorInformation:
    try:
        redactor_information: RedactorInformation = RedactorInformation(**authenticated_information.dict())
    except ValidationError:
        raise MissingRequiredRedactorInformation()
    return redactor_information
