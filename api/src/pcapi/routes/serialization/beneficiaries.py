from datetime import datetime
from typing import Optional

from pydantic import BaseModel
from pydantic.class_validators import validator

from pcapi.core.users.api import get_domains_credit
from pcapi.core.users.models import ExpenseDomain
from pcapi.core.users.models import User
from pcapi.core.users.models import UserRole
from pcapi.models.api_errors import ApiErrors
from pcapi.serialization.utils import humanize_field
from pcapi.serialization.utils import to_camel
from pcapi.serialization.utils import validate_not_empty_string_when_provided
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
    departementCode: Optional[str]
    deposit_version: Optional[int]
    domainsCredit: Optional[DomainsCredit]
    email: str
    firstName: Optional[str]
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
    roles: list[UserRole]

    _humanize_id = humanize_field("id")

    @classmethod
    def from_orm(cls, user: User):  # type: ignore
        user.pk = user.id
        user.domainsCredit = get_domains_credit(user)
        result = super().from_orm(user)
        result.isBeneficiary = user.is_beneficiary
        return result

    class Config:
        orm_mode = True
        json_encoders = {datetime: format_into_utc_date}
        use_enum_values = True


class PatchBeneficiaryBodyModel(BaseModel):
    public_name: Optional[str]
    has_seen_tutorials: Optional[bool]
    needs_to_fill_cultural_survey: Optional[bool]
    cultural_survey_id: Optional[str]
    cultural_survey_filled_date: Optional[datetime]

    _validate_public_name = validate_not_empty_string_when_provided("public_name")
    _validate_cultural_survey_id = validate_not_empty_string_when_provided("cultural_survey_id")
    _validate_cultural_survey_filled_date = validate_not_empty_string_when_provided("cultural_survey_filled_date")

    class Config:
        alias_generator = to_camel
        extra = "forbid"
        json_encoders = {datetime: format_into_utc_date}


class SendPhoneValidationRequest(BaseModel):
    phone_number: Optional[str]

    class Config:
        alias_generator = to_camel


class ValidatePhoneNumberRequest(BaseModel):
    code: str
