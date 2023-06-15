from datetime import datetime
import typing

from jwt import DecodeError
from jwt import ExpiredSignatureError
from jwt import InvalidSignatureError
from jwt import InvalidTokenError
import pydantic
from pydantic import EmailStr
from pydantic.class_validators import validator

from pcapi.core.users import models as users_models
from pcapi.core.users.utils import decode_jwt_token
from pcapi.domain.password import check_password_strength
from pcapi.routes.serialization import BaseModel
from pcapi.serialization.utils import to_camel
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


class UserEmailValidationResponseModel(BaseModel):
    newEmail: str | None

    class Config:
        orm_mode = True


class ProUserCreationBodyModel(BaseModel):
    address: str
    city: str
    email: pydantic.EmailStr
    first_name: str
    last_name: str
    latitude: float | None
    longitude: float | None
    name: str
    password: str
    phone_number: str
    postal_code: str
    siren: str
    contact_ok: bool

    @validator("password")
    def validate_password_strength(cls, password: str) -> str:
        check_password_strength("password", password)
        return password

    class Config:
        alias_generator = to_camel
        extra = "forbid"


class ProUserCreationBodyV2Model(BaseModel):
    email: pydantic.EmailStr
    first_name: str
    last_name: str
    password: str
    phone_number: str
    contact_ok: bool

    @validator("password")
    def validate_password_strength(cls, password: str) -> str:
        check_password_strength("password", password)
        return password

    class Config:
        alias_generator = to_camel
        extra = "forbid"


class LoginUserBodyModel(BaseModel):
    identifier: str
    password: str


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
    hasPhysicalVenues: bool | None
    hasSeenProTutorials: bool | None
    # FIXME (mageoffray, 2022-04-04): Optional can be removed after
    # post-deploy migrations have been done
    hasSeenProRgs: bool | None
    nonHumanizedId: int
    isAdmin: bool
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
        user.isAdmin = user.has_admin_role
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
    externalIds: typing.Dict | None
    firstName: str | None
    hasPhysicalVenues: bool | None
    hasSeenProTutorials: bool | None
    hasSeenProRgs: bool | None
    nonHumanizedId: int
    idPieceNumber: str | None
    isAdmin: bool
    isEmailValidated: bool
    lastConnectionDate: datetime | None
    lastName: str | None
    needsToFillCulturalSurvey: bool | None
    notificationSubscriptions: typing.Dict | None
    phoneNumber: str | None
    phoneValidationStatus: users_models.PhoneValidationStatusType | None
    postalCode: str | None
    roles: list[users_models.UserRole]

    class Config:
        json_encoders = {datetime: format_into_utc_date}
        alias_generator = to_camel
        orm_mode = True

    @classmethod
    def from_orm(cls, user: users_models.User) -> "SharedCurrentUserResponseModel":
        user.isAdmin = user.has_admin_role
        result = super().from_orm(user)
        return result


class ChangeProEmailBody(BaseModel):
    token: str


class ChangeEmailTokenContent(BaseModel):
    current_email: EmailStr
    new_email: EmailStr
    user_id: int

    @validator("current_email", "new_email", pre=True)
    @classmethod
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

        if not {"new_email", "current_email", "user_id"} <= set(jwt_payload):
            raise InvalidTokenError()

        current_email = jwt_payload["current_email"]
        new_email = jwt_payload["new_email"]
        user_id = jwt_payload["user_id"]
        return cls(current_email=current_email, new_email=new_email, user_id=user_id)


class ChangePasswordBodyModel(BaseModel):
    oldPassword: str
    newPassword: str
    newConfirmationPassword: str


class ProFlagsQueryModel(BaseModel):
    firebase: dict
