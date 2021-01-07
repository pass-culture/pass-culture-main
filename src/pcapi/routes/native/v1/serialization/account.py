from datetime import date
from typing import Optional

from pydantic import BaseModel

from pcapi.serialization.utils import to_camel


class AccountRequest(BaseModel):
    email: str
    password: str
    birthdate: date
    has_allowed_recommendations: bool
    token: str

    class Config:
        alias_generator = to_camel


class UserProfileResponse(BaseModel):
    first_name: Optional[str]
    email: str
    is_beneficiary: bool

    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True


class ResendEmailValidationRequest(BaseModel):
    email: str
