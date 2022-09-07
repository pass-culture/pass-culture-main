from datetime import datetime
import typing

from jwt import DecodeError
from jwt import ExpiredSignatureError
from jwt import InvalidSignatureError
from jwt import InvalidTokenError
import pydantic
from pydantic import EmailStr
from pydantic.class_validators import validator

from pcapi.core.users import models as user_models
from pcapi.core.users.utils import decode_jwt_token
from pcapi.core.users.utils import sanitize_email
from pcapi.domain.password import check_password_strength
from pcapi.routes.serialization import BaseModel
from pcapi.serialization.utils import humanize_field
from pcapi.serialization.utils import to_camel
from pcapi.serialization.utils import validate_not_empty_string_when_provided
from pcapi.serialization.utils import validate_phone_number_format
from pcapi.utils import phone_number as phone_number_utils
from pcapi.utils.date import format_into_utc_date


class PatchProUserBodyModel(BaseModel):
    first_name: str | None
    last_name: str | None
    email: pydantic.EmailStr | None
    phone_number: str | None

    _validate_first_name = validate_not_empty_string_when_provided("first_name")
    _validate_last_name = validate_not_empty_string_when_provided("last_name")
    _validate_email = validate_not_empty_string_when_provided("email")

    @validator("phone_number")
    def validate_phone_number(cls, phone_number: str) -> str:  # pylint: disable=no-self-argument
        if phone_number is None:
            return phone_number

        try:
            return phone_number_utils.ParsedPhoneNumber(phone_number).phone_number
        except Exception:
            raise ValueError(f"numéro de téléphone invalide: {phone_number}")

    class Config:
        alias_generator = to_camel
        extra = "forbid"


class PatchProUserResponseModel(BaseModel):
    firstName: str | None
    lastName: str | None
    email: pydantic.EmailStr
    phoneNumber: str | None

    class Config:
        alias_generator = to_camel
        orm_mode = True


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
    def validate_phone_number(cls, phone_number: str) -> str:  # pylint: disable=no-self-argument
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
    public_name: str
    siren: str
    contact_ok: bool

    @validator("password")
    def validate_password_strength(cls, password: str) -> str:  # typing: ignore # pylint: disable=no-self-argument
        check_password_strength("password", password)
        return password

    # FIXME (dbaty, 2022-09-09): we need this validator because the
    # first request with an unchecked box comes with the empty string.
    # Subsequent requests correctly come with `false`, which does not
    # require this validator. It may be a bug in the frontend. Revisit
    # this when we have switched the frontend from "pcapi" to "apiClient".
    @validator("contact_ok", pre=True, always=True)
    def cast_contact_ok_to_bool(  # typing: ignore # pylint: disable=no-self-argument
        cls, contact_ok: bool | None
    ) -> bool:
        return bool(contact_ok)

    _validate_phone_number_format = validate_phone_number_format("phone_number")

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
    civility: user_models.GenderEnum | None
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
    id: str
    nonHumanizedId: str
    isAdmin: bool
    isEmailValidated: bool
    lastConnectionDate: datetime | None
    lastName: str | None
    needsToFillCulturalSurvey: bool | None
    phoneNumber: str | None
    postalCode: str | None
    publicName: str | None
    roles: list[user_models.UserRole]

    _normalize_id = humanize_field("id")

    class Config:
        json_encoders = {datetime: format_into_utc_date}
        orm_mode = True
        alias_generator = to_camel
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        use_enum_values = True

    @classmethod
    def from_orm(cls, user):  # type: ignore [no-untyped-def]
        user.isAdmin = user.has_admin_role
        user.nonHumanizedId = user.id
        result = super().from_orm(user)
        return result


class SharedCurrentUserResponseModel(BaseModel):

    activity: str | None
    address: str | None
    city: str | None
    civility: user_models.GenderEnum | None
    dateCreated: datetime
    dateOfBirth: datetime | None
    departementCode: str | None
    email: str
    externalIds: typing.Dict | None
    firstName: str | None
    hasPhysicalVenues: bool | None
    hasSeenProTutorials: bool | None
    hasSeenProRgs: bool | None
    id: str
    nonHumanizedId: str
    idPieceNumber: str | None
    isAdmin: bool
    isEmailValidated: bool
    lastConnectionDate: datetime | None
    lastName: str | None
    needsToFillCulturalSurvey: bool | None
    notificationSubscriptions: typing.Dict | None
    phoneNumber: str | None
    phoneValidationStatus: user_models.PhoneValidationStatusType | None
    postalCode: str | None
    publicName: str | None
    roles: list[user_models.UserRole]

    _normalize_id = humanize_field("id")

    class Config:
        json_encoders = {datetime: format_into_utc_date}
        alias_generator = to_camel
        orm_mode = True

    @classmethod
    def from_orm(cls, user):  # type: ignore [no-untyped-def]
        user.isAdmin = user.has_admin_role
        user.nonHumanizedId = user.id
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
