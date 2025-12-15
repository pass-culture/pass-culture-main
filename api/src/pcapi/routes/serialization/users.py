import typing
from datetime import datetime

import pydantic as pydantic_v2

from pcapi.core.users import models as users_models
from pcapi.core.users.password_utils import check_password_strength
from pcapi.routes.serialization import HttpBodyModel
from pcapi.routes.serialization import HttpQueryParamsModel
from pcapi.serialization.exceptions import PydanticError
from pcapi.utils import phone_number as phone_number_utils
from pcapi.utils.email import sanitize_email


class UserIdentityResponseModel(HttpBodyModel):
    first_name: str
    last_name: str


class UserIdentityBodyModel(HttpBodyModel):
    first_name: str
    last_name: str


class UserPhoneResponseModel(HttpBodyModel):
    phone_number: str


def validate_phone_number(phone_number: str) -> str:
    try:
        return phone_number_utils.ParsedPhoneNumber(phone_number).phone_number
    except Exception:
        raise PydanticError(f"numéro de téléphone invalide: {phone_number}")


class UserPhoneBodyModel(HttpBodyModel):
    phone_number: typing.Annotated[str, pydantic_v2.AfterValidator(validate_phone_number)]


class UserResetEmailBodyModel(HttpBodyModel):
    email: pydantic_v2.EmailStr
    password: str

    @pydantic_v2.field_validator("email", mode="before")
    @classmethod
    def validate_emails(cls, email: str) -> str:
        try:
            return sanitize_email(email)
        except Exception as e:
            raise PydanticError(email) from e


class UserEmailValidationResponseModel(HttpBodyModel):
    new_email: str | None = None


def validate_password_strength(password: str) -> str:
    check_password_strength("password", password)
    return password


class ProUserCreationBodyV2Model(HttpBodyModel):
    email: pydantic_v2.EmailStr
    first_name: str
    last_name: str
    password: typing.Annotated[str, pydantic_v2.AfterValidator(validate_password_strength)]
    phone_number: str | None = None
    contact_ok: bool
    token: str

    @pydantic_v2.field_validator("email", mode="after")
    @classmethod
    def sanitize_email(cls, value: pydantic_v2.EmailStr) -> str:
        return value.lower()


class LoginUserBodyModel(HttpBodyModel):
    identifier: str
    password: str
    captcha_token: str | None = None


class SharedLoginUserResponseModel(HttpBodyModel):
    activity: str | None = None
    address: str | None = None
    city: str | None = None
    civility: users_models.GenderEnum | None = None
    dateCreated: datetime
    dateOfBirth: datetime | None = None
    departementCode: str | None = None
    email: str
    firstName: str | None = None
    hasSeenProTutorials: bool | None = None
    has_user_offerer: bool | None = None
    id: int
    isEmailValidated: bool
    lastConnectionDate: datetime | None = None
    lastName: str | None = None
    needsToFillCulturalSurvey: bool | None = None
    phoneNumber: str | None = None
    postalCode: str | None = None
    roles: list[users_models.UserRole]

    model_config = pydantic_v2.ConfigDict(use_enum_values=True, arbitrary_types_allowed=True)


class SharedCurrentUserResponseModel(HttpBodyModel):
    activity: str | None = None
    address: str | None = None
    city: str | None = None
    civility: users_models.GenderEnum | None = None
    dateCreated: datetime
    dateOfBirth: datetime | None = None
    departementCode: str | None = None
    email: str
    externalIds: dict | None = None
    firstName: str | None = None
    hasSeenProTutorials: bool | None = None
    has_user_offerer: bool | None = None
    id: int
    idPieceNumber: str | None = None
    isEmailValidated: bool
    lastConnectionDate: datetime | None = None
    lastName: str | None = None
    needsToFillCulturalSurvey: bool | None = None
    notificationSubscriptions: dict | None = None
    phoneNumber: str | None = None
    phoneValidationStatus: users_models.PhoneValidationStatusType | None = None
    postalCode: str | None = None
    roles: list[users_models.UserRole]
    isImpersonated: bool = False

    @classmethod
    def instantiate_model(cls, user: users_models.User, is_impersonated: bool) -> "SharedCurrentUserResponseModel":
        instance = cls.model_validate(user)
        instance.isImpersonated = is_impersonated
        return instance


class ChangeProEmailBody(HttpBodyModel):
    token: str


class ChangePasswordBodyModel(HttpBodyModel):
    old_password: str
    new_password: str
    new_confirmation_password: str


class ProFlagsQueryModel(HttpQueryParamsModel):
    firebase: dict


class SubmitReviewRequestModel(HttpBodyModel):
    user_satisfaction: str
    user_comment: str
    offerer_id: int
    location: str
    page_title: str
