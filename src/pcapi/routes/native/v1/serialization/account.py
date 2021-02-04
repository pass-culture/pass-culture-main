import datetime
from datetime import date
from typing import List
from typing import Optional

from pydantic import BaseModel
from pydantic.class_validators import validator
from pydantic.fields import Field

from pcapi.core.users.models import ExpenseDomain
from pcapi.core.users.models import VOID_FIRST_NAME
from pcapi.core.users.models import VOID_PUBLIC_NAME
from pcapi.routes.native.utils import convert_to_cent
from pcapi.serialization.utils import to_camel


class AccountRequest(BaseModel):
    email: str
    password: str
    birthdate: date
    has_allowed_recommendations: bool
    token: str

    class Config:
        alias_generator = to_camel


class Expense(BaseModel):
    domain: ExpenseDomain
    current: int
    limit: int

    _convert_current = validator("current", pre=True, allow_reuse=True)(convert_to_cent)
    _convert_max = validator("limit", pre=True, allow_reuse=True)(convert_to_cent)

    class Config:
        orm_mode = True


class UserProfileResponse(BaseModel):
    dateOfBirth: Optional[datetime.datetime]
    deposit_version: Optional[int]
    email: str
    expenses: List[Expense]
    firstName: Optional[str]
    hasAllowedRecommendations: bool
    is_eligible: bool
    lastName: Optional[str]
    isBeneficiary: bool
    phoneNumber: Optional[str]
    publicName: Optional[str] = Field(None, alias="pseudo")
    needsToFillCulturalSurvey: bool

    class Config:
        orm_mode = True
        alias_generator = to_camel
        allow_population_by_field_name = True

    @validator("publicName", pre=True)
    def format_public_name(cls, publicName: str) -> Optional[str]:  # pylint: disable=no-self-argument
        return publicName if publicName != VOID_PUBLIC_NAME else None

    @validator("firstName", pre=True)
    def format_first_name(cls, firstName: Optional[str]) -> Optional[str]:  # pylint: disable=no-self-argument
        return firstName if firstName != VOID_FIRST_NAME else None


class UserProfileUpdateRequest(BaseModel):
    hasAllowedRecommendations: Optional[bool]


class ResendEmailValidationRequest(BaseModel):
    email: str


class GetIdCheckTokenResponse(BaseModel):
    token: Optional[str]
