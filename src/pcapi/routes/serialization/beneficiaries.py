from datetime import datetime
from typing import List
from typing import Optional

from pydantic import BaseModel
from pydantic.class_validators import validator

from pcapi.core.users.api import get_domains_credit
from pcapi.core.users.models import ExpenseDomain
from pcapi.core.users.models import User
from pcapi.models.api_errors import ApiErrors
from pcapi.serialization.utils import humanize_field
from pcapi.utils.date import format_into_utc_date


class VerifyIdCheckLicenceRequest(BaseModel):
    token: str

    @validator("token")
    def validate_token_not_empty(cls, token: str) -> str:  # typing: ignore # pylint: disable=no-self-argument
        if token == "null":
            raise ApiErrors({"token": "Empty token"})
        return token


class VerifyIdCheckLicenceResponse(BaseModel):
    pass


class ApplicationUpdateRequest(BaseModel):
    id: str


class ApplicationUpdateResponse(BaseModel):
    pass


class ChangeBeneficiaryEmailRequestBody(BaseModel):
    new_email: str
    password: str


class ChangeBeneficiaryEmailBody(BaseModel):
    token: str


class Expense(BaseModel):
    domain: ExpenseDomain
    current: float
    limit: float

    class Config:
        orm_mode = True


class Credit(BaseModel):
    initial: float
    remaining: float

    class Config:
        orm_mode = True


class DomainsCredit(BaseModel):
    all: Credit
    digital: Optional[Credit]
    physical: Optional[Credit]

    class Config:
        orm_mode = True


class BeneficiaryAccountResponse(BaseModel):
    pk: int  # id not humanized
    activity: Optional[str]
    address: Optional[str]
    city: Optional[str]
    civility: Optional[str]
    dateCreated: datetime
    dateOfBirth: Optional[datetime]
    departementCode: str
    deposit_version: Optional[int]
    domainsCredit: Optional[DomainsCredit]
    email: str
    expenses: List[Expense]
    firstName: Optional[str]
    hasAllowedRecommendations: bool
    hasPhysicalVenues: bool
    id: str
    isActive: bool
    isAdmin: bool
    isBeneficiary: bool
    isEmailValidated: bool
    lastName: Optional[str]
    needsToFillCulturalSurvey: bool
    needsToSeeTutorials: bool
    phoneNumber: Optional[str]
    postalCode: Optional[str]
    publicName: str
    suspensionReason: Optional[str]
    wallet_balance: float
    deposit_expiration_date: Optional[datetime]
    wallet_is_activated: bool

    _humanize_id = humanize_field("id")

    @classmethod
    def from_orm(cls, user: User):  # type: ignore
        user.pk = user.id
        user.domainsCredit = get_domains_credit(user)
        return super().from_orm(user)

    class Config:
        orm_mode = True
        json_encoders = {datetime: format_into_utc_date}
