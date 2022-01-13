from typing import Optional

from jwt import DecodeError
from jwt import ExpiredSignatureError
from jwt import InvalidSignatureError
from jwt import InvalidTokenError
import pydantic
from pydantic import BaseModel
from pydantic.class_validators import validator

from pcapi.core.users.models import ExpenseDomain
from pcapi.core.users.utils import decode_jwt_token
from pcapi.core.users.utils import sanitize_email
from pcapi.models.api_errors import ApiErrors
from pcapi.serialization.utils import to_camel


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


class ChangeBeneficiaryEmailBody(BaseModel):
    token: str


class ChangeEmailTokenContent(BaseModel):
    current_email: pydantic.EmailStr
    new_email: pydantic.EmailStr

    @classmethod
    @validator("current_email,new_email", pre=True)
    def validate_emails(cls, email: str) -> str:
        try:
            return sanitize_email(email)
        except Exception as e:
            raise ValueError(email) from e

    @classmethod
    def from_token(cls, token: str) -> "ChangeEmailTokenContent":
        try:
            jwt_payload = decode_jwt_token(token)
        except (
            ExpiredSignatureError,
            InvalidSignatureError,
            DecodeError,
            InvalidTokenError,
        ) as error:
            raise InvalidTokenError() from error

        if not {"new_email", "current_email"} <= set(jwt_payload):
            raise InvalidTokenError()

        current_email = jwt_payload["current_email"]
        new_email = jwt_payload["new_email"]
        return cls(current_email=current_email, new_email=new_email)


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


class SendPhoneValidationRequest(BaseModel):
    phone_number: Optional[str]

    class Config:
        alias_generator = to_camel


class ValidatePhoneNumberRequest(BaseModel):
    code: str
