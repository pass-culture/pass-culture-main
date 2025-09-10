import enum
import logging
import typing
from datetime import date
from datetime import datetime

import pydantic.v1 as pydantic_v1
from pydantic.v1.class_validators import validator

from pcapi.connectors.dms import models as dms_models
from pcapi.core.history import models as history_models
from pcapi.core.users import models as users_models
from pcapi.core.users.password_utils import check_password_strength
from pcapi.routes.serialization import BaseModel
from pcapi.routes.serialization import to_camel


if typing.TYPE_CHECKING:
    pass


class T_UNCHANGED(enum.Enum):
    TOKEN = 0


UNCHANGED = T_UNCHANGED.TOKEN

EMAIL_CONFIRMATION_TEST_EMAIL_PATTERN = "+e2e@"


logger = logging.getLogger(__name__)


class ProUserCreationBodyV2Model(BaseModel):
    email: pydantic_v1.EmailStr
    first_name: str
    last_name: str
    password: str
    phone_number: str | None = None
    contact_ok: bool
    token: str

    @validator("password")
    def validate_password_strength(cls, password: str) -> str:
        check_password_strength("password", password)
        return password

    class Config:
        alias_generator = to_camel
        extra = "forbid"


class GdprChronicleData(BaseModel):
    age: int | None
    city: str | None
    content: str
    dateCreated: datetime
    ean: str | None
    allocineId: str | None
    visa: str | None
    productIdentifier: str
    productIdentifierType: str
    email: str
    firstName: str | None
    isIdentityDiffusible: bool
    isSocialMediaDiffusible: bool
    productName: str | None = None

    class Config:
        orm_mode = True


class GdprAccountUpdateRequests(BaseModel):
    allConditionsChecked: bool
    birthDate: date | None
    dateCreated: datetime
    dateLastInstructorMessage: datetime | None
    dateLastStatusUpdate: datetime | None
    dateLastUserMessage: datetime | None
    email: str | None
    firstName: str | None
    lastName: str | None
    newEmail: str | None
    newFirstName: str | None
    newLastName: str | None
    newPhoneNumber: str | None
    oldEmail: str | None
    status: dms_models.GraphQLApplicationStates
    updateTypes: list[str]

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


class GdprDepositSerializer(BaseModel):
    dateCreated: datetime
    dateUpdated: datetime | None
    expirationDate: datetime | None
    amount: float
    source: str
    type: str


class GdprEmailHistory(BaseModel):
    dateCreated: datetime
    newEmail: str | None
    oldEmail: str


class GdprActionHistorySerializer(BaseModel):
    actionDate: datetime | None
    actionType: history_models.ActionType

    class Config:
        orm_mode = True


class GdprBeneficiaryValidation(BaseModel):
    dateCreated: datetime
    eligibilityType: str | None
    status: str | None
    type: str
    updatedAt: datetime | None


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


class GdprInternal(BaseModel):
    user: GdprUserSerializer
    marketing: GdprMarketing
    loginDevices: list[GdprLoginDeviceHistorySerializer]
    emailsHistory: list[GdprEmailHistory]
    actionsHistory: list[GdprActionHistorySerializer]
    beneficiaryValidations: list[GdprBeneficiaryValidation]
    deposits: list[GdprDepositSerializer]
    bookings: list[GdprBookingSerializer]
    chronicles: list[GdprChronicleData]
    accountUpdateRequests: list[GdprAccountUpdateRequests]


class GdprExternal(BaseModel):
    brevo: dict


class GdprDataContainer(BaseModel):
    generationDate: datetime
    internal: GdprInternal
    external: GdprExternal
