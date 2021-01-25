import datetime
from datetime import date
from decimal import Decimal
from typing import List
from typing import Optional

from pydantic import BaseModel
from pydantic.class_validators import validator

from pcapi.core.users.models import ExpenseDomain
from pcapi.core.users.models import VOID_FIRST_NAME
from pcapi.serialization.utils import to_camel


class AccountRequest(BaseModel):
    email: str
    password: str
    birthdate: date
    has_allowed_recommendations: bool
    token: str

    class Config:
        alias_generator = to_camel


def convert_to_cent(amount: Decimal) -> int:
    return int(amount * 100)


class Expense(BaseModel):
    domain: ExpenseDomain
    current: int
    limit: int

    _convert_current = validator("current", pre=True, allow_reuse=True)(convert_to_cent)
    _convert_max = validator("limit", pre=True, allow_reuse=True)(convert_to_cent)

    class Config:
        orm_mode = True


class UserProfileResponse(BaseModel):
    @classmethod
    def from_orm(cls, user):  # type: ignore
        user.firstName = user.firstName if user.firstName != VOID_FIRST_NAME else None

        return super().from_orm(user)

    dateOfBirth: Optional[datetime.datetime]
    deposit_version: Optional[int]
    email: str
    expenses: List[Expense]
    firstName: Optional[str]
    hasAllowedRecommendations: bool
    lastName: Optional[str]
    isBeneficiary: bool
    phoneNumber: Optional[str]

    class Config:
        orm_mode = True
        alias_generator = to_camel
        allow_population_by_field_name = True


class ResendEmailValidationRequest(BaseModel):
    email: str
