from datetime import datetime
from typing import List
from typing import Optional

from pydantic import BaseModel
from pydantic.class_validators import validator

from pcapi.core.users.models import ExpenseDomain
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


class BeneficiaryAccountResponse(BaseModel):
    _humanize_id = humanize_field("id")

    activity: Optional[str]
    address: Optional[str]
    city: Optional[str]
    civility: Optional[str]
    dateCreated: datetime
    dateOfBirth: Optional[datetime]
    departementCode: str
    deposit_version: Optional[int]
    email: str
    expenses: List[Expense]
    # @debt api-data "asaunier: Seuls quelques comptes n'ont pas cette information. Elle devrait être rendue obligatoire"
    firstName: Optional[str]
    hasAllowedRecommendations: bool
    hasPhysicalVenues: bool
    id: str
    isActive: bool
    isAdmin: bool
    isBeneficiary: bool
    isEmailValidated: bool
    # @debt api-data "asaunier: Seuls quelques comptes n'ont pas cette information. Elle devrait être rendue obligatoire"
    lastName: Optional[str]
    needsToFillCulturalSurvey: bool
    needsToSeeTutorials: bool
    phoneNumber: Optional[str]
    postalCode: Optional[str]
    publicName: str
    suspensionReason: Optional[str]
    wallet_balance: float
    wallet_date_created: Optional[datetime]
    wallet_is_activated: bool

    class Config:
        orm_mode = True
        json_encoders = {datetime: format_into_utc_date}
