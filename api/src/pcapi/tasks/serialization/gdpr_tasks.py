from datetime import date
from datetime import datetime

from pydantic.v1 import BaseModel
from pydantic.v1 import Field

from pcapi.core.history import models as history_models
from pcapi.core.users import models as users_models


class ExtractBeneficiaryDataRequest(BaseModel):
    extract_id: int


class UserSerializer(BaseModel):
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
    marriedName: str | None = Field(alias="married_name")
    postalCode: str | None
    schoolType: users_models.SchoolTypeEnum | None
    validatedBirthDate: date | None

    class Config:
        orm_mode = True


class Marketing(BaseModel):
    marketingEmails: bool
    marketingNotifications: bool


class LoginDeviceHistorySerializer(BaseModel):
    dateCreated: datetime
    deviceId: str
    location: str | None
    source: str | None
    os: str | None

    class Config:
        orm_mode = True


class EmailHistory(BaseModel):
    dateCreated: datetime
    newEmail: str | None
    oldEmail: str


class DepositSerializer(BaseModel):
    dateCreated: datetime
    dateUpdated: datetime | None
    expirationDate: datetime | None
    amount: float
    source: str
    type: str


class BookingSerializer(BaseModel):
    cancellationDate: datetime | None
    dateCreated: datetime
    dateUsed: datetime | None
    quantity: int
    amount: float
    status: str
    name: str
    venue: str
    offerer: str


class ActionHistorySerializer(BaseModel):
    actionDate: datetime
    actionType: history_models.ActionType

    class Config:
        orm_mode = True


class BeneficiaryValidation(BaseModel):
    dateCreated: datetime
    eligibilityType: str | None
    status: str | None
    type: str
    updatedAt: datetime | None


class Internal(BaseModel):
    user: UserSerializer
    marketing: Marketing
    loginDevices: list[LoginDeviceHistorySerializer]
    emailsHistory: list[EmailHistory]
    actionsHistory: list[ActionHistorySerializer]
    beneficiaryValidations: list[BeneficiaryValidation]
    deposits: list[DepositSerializer]
    bookings: list[BookingSerializer]


class External(BaseModel):
    brevo: dict


class DataContainer(BaseModel):
    generationDate: datetime
    internal: Internal
    external: External
