from datetime import date
from datetime import datetime

import pydantic as pydantic_v2

from pcapi.connectors.dms import models as dms_models
from pcapi.core.history import models as history_models
from pcapi.core.users import models as users_models


class GdprSerializer(pydantic_v2.BaseModel):
    model_config = pydantic_v2.ConfigDict(from_attributes=True)


class GdprUserSerializer(GdprSerializer):
    activity: str | None = None
    address: str | None = None
    civility: str | None = None
    city: str | None = None
    culturalSurveyFilledDate: datetime | None = None
    departementCode: str | None = None
    dateCreated: datetime
    dateOfBirth: datetime | None = None
    email: str
    firstName: str | None = None
    isActive: bool
    isEmailValidated: bool | None = None
    lastName: str | None = None
    marriedName: str | None = pydantic_v2.Field(alias="married_name", default=None)
    postalCode: str | None = None
    schoolType: users_models.SchoolTypeEnum | None = None
    validatedBirthDate: date | None = None


class GdprChronicleData(GdprSerializer):
    age: int | None = None
    city: str | None = None
    content: str
    dateCreated: datetime
    ean: str | None = None
    allocineId: str | None = None
    visa: str | None = None
    productIdentifier: str
    productIdentifierType: str
    email: str
    firstName: str | None = None
    isIdentityDiffusible: bool
    isSocialMediaDiffusible: bool
    productName: str | None = None


class GdprAccountUpdateRequests(GdprSerializer):
    allConditionsChecked: bool
    birthDate: date | None = None
    dateCreated: datetime
    dateLastInstructorMessage: datetime | None = None
    dateLastStatusUpdate: datetime | None = None
    dateLastUserMessage: datetime | None = None
    email: str | None = None
    firstName: str | None = None
    lastName: str | None = None
    newEmail: str | None = None
    newFirstName: str | None = None
    newLastName: str | None = None
    newPhoneNumber: str | None = None
    oldEmail: str | None = None
    status: dms_models.GraphQLApplicationStates
    updateTypes: list[str]


class GdprMarketing(GdprSerializer):
    marketingEmails: bool
    marketingNotifications: bool


class GdprLoginDeviceHistorySerializer(GdprSerializer):
    dateCreated: datetime
    deviceId: str
    location: str | None = None
    source: str | None = None
    os: str | None = None


class GdprEmailHistory(GdprSerializer):
    dateCreated: datetime
    newEmail: str | None = None
    oldEmail: str


class GdprDepositSerializer(GdprSerializer):
    dateCreated: datetime
    dateUpdated: datetime | None = None
    expirationDate: datetime | None = None
    amount: float
    source: str
    type: str


class GdprBookingSerializer(GdprSerializer):
    cancellationDate: datetime | None = None
    dateCreated: datetime
    dateUsed: datetime | None = None
    quantity: int
    amount: float
    status: str
    name: str
    venue: str
    offerer: str


class GdprActionHistorySerializer(GdprSerializer):
    actionDate: datetime | None = None
    actionType: history_models.ActionType


class GdprBeneficiaryValidation(GdprSerializer):
    dateCreated: datetime
    eligibilityType: str | None
    status: str | None
    type: str
    updatedAt: datetime | None


class GdprInternal(GdprSerializer):
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


class GdprExternal(GdprSerializer):
    brevo: dict


class GdprDataContainer(GdprSerializer):
    generationDate: datetime
    internal: GdprInternal
    external: GdprExternal
