import enum
import logging

from pydantic.v1 import ValidationError

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
    uai: str | None = None
    departmentCode: str | None = None
    institutionName: str | None = None
    institutionCity: str | None = None
    email: str | None = None
    preferences: RedactorPreferences | None = None
    lat: float | None = None
    lon: float | None = None
    favoritesCount: int = 0

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
