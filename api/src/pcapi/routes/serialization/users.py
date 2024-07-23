from datetime import date
from datetime import datetime

import flask
import pydantic.v1 as pydantic_v1
from pydantic.v1 import EmailStr
from pydantic.v1.class_validators import validator

from pcapi.core.history import models as history_models
from pcapi.core.users import models as users_models
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


class ProUserCreationBodyV2Model(BaseModel):
    email: pydantic_v1.EmailStr
    first_name: str
    last_name: str
    password: str
    phone_number: str
    contact_ok: bool
    token: str

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
    captcha_token: str | None = None

    class Config:
        alias_generator = to_camel


class NavStateResponseModel(BaseModel):
    newNavDate: datetime | None
    eligibilityDate: datetime | None

    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True
        orm_mode = True


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
    # FIXME (mageoffray, 2022-04-04): Optional can be removed after
    # post-deploy migrations have been done
    hasSeenProRgs: bool | None
    hasUserOfferer: bool | None
    id: int
    isAdmin: bool
    isEmailValidated: bool
    lastConnectionDate: datetime | None
    lastName: str | None
    needsToFillCulturalSurvey: bool | None
    phoneNumber: str | None
    postalCode: str | None
    roles: list[users_models.UserRole]
    navState: NavStateResponseModel | None
    hasPartnerPage: bool | None

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
        user.hasUserOfferer = user.has_user_offerer
        user.navState = NavStateResponseModel.from_orm(user.pro_new_nav_state)
        user.hasPartnerPage = user.has_partner_page
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
    hasSeenProRgs: bool | None
    hasUserOfferer: bool | None
    id: int
    idPieceNumber: str | None
    isAdmin: bool
    isEmailValidated: bool
    lastConnectionDate: datetime | None
    lastName: str | None
    needsToFillCulturalSurvey: bool | None
    notificationSubscriptions: dict | None
    phoneNumber: str | None
    phoneValidationStatus: users_models.PhoneValidationStatusType | None
    postalCode: str | None
    roles: list[users_models.UserRole]
    navState: NavStateResponseModel | None
    hasPartnerPage: bool | None
    isImpersonated: bool = False

    class Config:
        json_encoders = {datetime: format_into_utc_date}
        alias_generator = to_camel
        orm_mode = True

    @classmethod
    def from_orm(cls, user: users_models.User) -> "SharedCurrentUserResponseModel":
        user.isAdmin = user.has_admin_role
        user.hasUserOfferer = user.has_user_offerer
        user.navState = NavStateResponseModel.from_orm(user.pro_new_nav_state)
        user.hasPartnerPage = user.has_partner_page
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
    isPleasant: bool
    isConvenient: bool
    comment: str
    offererId: int
    location: str


class GdprUserSerializer(BaseModel):
    activity: str | None
    address: str | None
    civility: str | None
    city: str | None
    culturalSurveyFilledDate: datetime | None
    departementCode: str | None
    dateCreated: datetime
    dateOfBirth: datetime | None
    email: str
    firstName: str | None
    isActive: bool
    isEmailValidated: bool | None
    lastName: str | None
    marriedName: str | None = pydantic_v1.Field(alias="married_name")
    postalCode: str | None
    schoolType: users_models.SchoolTypeEnum | None
    validatedBirthDate: date | None

    class Config:
        orm_mode = True


class GdprMarketing(BaseModel):
    marketingEmails: bool
    marketingNotifications: bool


class GdprLoginDeviceHistorySerializer(BaseModel):
    dateCreated: datetime
    deviceId: str
    location: str | None
    source: str | None
    os: str | None

    class Config:
        orm_mode = True


class GdprEmailHistory(BaseModel):
    dateCreated: datetime
    newEmail: str | None
    oldEmail: str


class GdprDepositSerializer(BaseModel):
    dateCreated: datetime
    dateUpdated: datetime | None
    expirationDate: datetime | None
    amount: float
    source: str
    type: str


class GdprBookingSerializer(BaseModel):
    cancellationDate: datetime | None
    dateCreated: datetime
    dateUsed: datetime | None
    quantity: int
    amount: float
    status: str
    name: str
    venue: str
    offerer: str


class GdprActionHistorySerializer(BaseModel):
    actionDate: datetime
    actionType: history_models.ActionType

    class Config:
        orm_mode = True


class GdprBeneficiaryValidation(BaseModel):
    dateCreated: datetime
    eligibilityType: str | None
    status: str | None
    type: str
    updatedAt: datetime | None


class GdprInternal(BaseModel):
    user: GdprUserSerializer
    marketing: GdprMarketing
    loginDevices: list[GdprLoginDeviceHistorySerializer]
    emailsHistory: list[GdprEmailHistory]
    actionsHistory: list[GdprActionHistorySerializer]
    beneficiaryValidations: list[GdprBeneficiaryValidation]
    deposits: list[GdprDepositSerializer]
    bookings: list[GdprBookingSerializer]


class GdprExternal(BaseModel):
    brevo: dict


class GdprDataContainer(BaseModel):
    generationDate: datetime
    internal: GdprInternal
    external: GdprExternal
