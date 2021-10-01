import enum
import logging
from typing import Optional

from pydantic import BaseModel
from pydantic import ValidationError

from pcapi.core.educational.exceptions import MissingRequiredRedactorInformation


logger = logging.getLogger(__name__)


class AdageFrontRoles(enum.Enum):
    REDACTOR = "redactor"
    READONLY = "readonly"


class AuthenticatedInformation(BaseModel):
    civility: Optional[str]
    lastname: Optional[str]
    firstname: Optional[str]
    email: str
    uai: Optional[str]


class AuthenticatedResponse(BaseModel):
    role: AdageFrontRoles

    class Config:
        use_enum_values = True


class RedactorInformation(BaseModel):
    civility: str
    lastname: str
    firstname: str
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
