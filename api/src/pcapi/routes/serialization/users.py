from datetime import datetime

import flask
from pydantic.v1 import EmailStr
from pydantic.v1.class_validators import validator

from pcapi.core.users import models as users_models
from pcapi.routes.serialization import BaseModel
from pcapi.routes.serialization import to_camel
from pcapi.utils import phone_number as phone_number_utils
from pcapi.utils.date import format_into_utc_date
from pcapi.utils.email import sanitize_email


class UserIdentityResponseModel(BaseModel):
    firstName: str
    lastName: str

    class Config:
        alias_generator = to_camel
        orm_mode = True


class UserIdentityBodyModel(BaseModel):
    first_name: str
    last_name: str

    class Config:
        alias_generator = to_camel
        extra = "forbid"


class UserPhoneResponseModel(BaseModel):
    phoneNumber: str

    class Config:
        alias_generator = to_camel
        orm_mode = True


class UserPhoneBodyModel(BaseModel):
    phone_number: str

    @validator("phone_number")
    def validate_phone_number(cls, phone_number: str) -> str:
        if phone_number is None:
            return phone_number

        try:
            return phone_number_utils.ParsedPhoneNumber(phone_number).phone_number
        except Exception:
            raise ValueError(f"numéro de téléphone invalide: {phone_number}")

    class Config:
        alias_generator = to_camel
        extra = "forbid"


class UserResetEmailBodyModel(BaseModel):
    email: EmailStr
    password: str

    @validator("email", pre=True)
    @classmethod
    def validate_emails(cls, email: str) -> str:
        try:
            return sanitize_email(email)
        except Exception as e:
            raise ValueError(email) from e


class UserEmailValidationResponseModel(BaseModel):
    newEmail: str | None

    class Config:
        orm_mode = True


class LoginUserBodyModel(BaseModel):
    identifier: str
    password: str
    captcha_token: str | None = None

    class Config:
        alias_generator = to_camel


class SharedLoginUserResponseModel(BaseModel):
    activity: str | None
    address: str | None
    city: str | None
    civility: users_models.GenderEnum | None
    dateCreated: datetime
    dateOfBirth: datetime | None
    departementCode: str | None
    email: str
    firstName: str | None
    hasSeenProTutorials: bool | None
    hasUserOfferer: bool | None
    id: int
    isEmailValidated: bool
    lastConnectionDate: datetime | None
    lastName: str | None
    needsToFillCulturalSurvey: bool | None
    phoneNumber: str | None
    postalCode: str | None
    roles: list[users_models.UserRole]

    class Config:
        json_encoders = {datetime: format_into_utc_date}
        orm_mode = True
        alias_generator = to_camel
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        use_enum_values = True

    @classmethod
    def from_orm(cls, user: users_models.User) -> "SharedLoginUserResponseModel":
        user.hasUserOfferer = user.has_user_offerer
        result = super().from_orm(user)
        return result


class SharedCurrentUserResponseModel(BaseModel):
    activity: str | None
    address: str | None
    city: str | None
    civility: users_models.GenderEnum | None
    dateCreated: datetime
    dateOfBirth: datetime | None
    departementCode: str | None
    email: str
    externalIds: dict | None
    firstName: str | None
    hasSeenProTutorials: bool | None
    hasUserOfferer: bool | None
    id: int
    idPieceNumber: str | None
    isEmailValidated: bool
    lastConnectionDate: datetime | None
    lastName: str | None
    needsToFillCulturalSurvey: bool | None
    notificationSubscriptions: dict | None
    phoneNumber: str | None
    phoneValidationStatus: users_models.PhoneValidationStatusType | None
    postalCode: str | None
    roles: list[users_models.UserRole]
    isImpersonated: bool = False

    class Config:
        json_encoders = {datetime: format_into_utc_date}
        alias_generator = to_camel
        orm_mode = True

    @classmethod
    def from_orm(cls, user: users_models.User) -> "SharedCurrentUserResponseModel":
        user.hasUserOfferer = user.has_user_offerer
        user.isImpersonated = flask.session.get("internal_admin_email") is not None
        result = super().from_orm(user)
        return result


class ChangeProEmailBody(BaseModel):
    token: str


class ChangePasswordBodyModel(BaseModel):
    oldPassword: str
    newPassword: str
    newConfirmationPassword: str


class ProFlagsQueryModel(BaseModel):
    firebase: dict


class SubmitReviewRequestModel(BaseModel):
    userSatisfaction: str
    userComment: str
    offererId: int
    location: str
    pageTitle: str
