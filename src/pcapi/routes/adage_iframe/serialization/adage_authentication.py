import enum
from typing import Optional

from pydantic import BaseModel


class AdageFrontRoles(enum.Enum):
    REDACTOR = "redactor"
    READONLY = "readonly"


class AuthenticatedInformation(BaseModel):
    civility: str
    lastname: str
    firstname: str
    email: str
    uai: Optional[str]


class AuthenticatedResponse(BaseModel):
    role: AdageFrontRoles

    class Config:
        use_enum_values = True
