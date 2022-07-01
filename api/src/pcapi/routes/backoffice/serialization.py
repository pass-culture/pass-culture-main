import datetime
import typing

import pydantic

from pcapi.core.fraud import models as fraud_models
from pcapi.core.subscription import models as subscription_models
from pcapi.core.subscription.phone_validation import exceptions as phone_validation_exceptions
from pcapi.core.users import models as users_models
from pcapi.core.users.utils import sanitize_email
from pcapi.routes.serialization import BaseModel
from pcapi.utils import phone_number as phone_number_utils


class Permission(BaseModel):
    class Config:
        orm_mode = True

    id: int
    name: str
    category: typing.Optional[str]


class Role(BaseModel):
    class Config:
        orm_mode = True

    id: int
    name: str
    permissions: list[Permission]


class ListRoleResponseModel(BaseModel):
    class Config:
        orm_mode = True

    roles: list[Role]


class ListPermissionResponseModel(BaseModel):
    class Config:
        orm_mode = True

    permissions: list[Permission]


class RoleRequestModel(BaseModel):
    name: str = pydantic.Field(..., min_length=1)
    permissionIds: list[int]


class PublicAccount(BaseModel):
    class Config:
        orm_mode = True
        use_enum_values = True

    id: int
    firstName: typing.Optional[str]
    lastName: typing.Optional[str]
    dateOfBirth: typing.Optional[datetime.datetime]
    email: str
    phoneNumber: typing.Optional[str]
    roles: list[users_models.UserRole]
    isActive: bool
    address: typing.Optional[str]
    postalCode: typing.Optional[str]
    city: typing.Optional[str]


class PaginableQuery(BaseModel):
    page: typing.Optional[int] = 1
    perPage: typing.Optional[int] = 20
    sort: typing.Optional[str] = None


class PublicAccountSearchQuery(PaginableQuery):
    q: str


class PaginatedResponse(BaseModel):
    pages: int
    total: int
    page: int
    size: int
    sort: typing.Optional[str]
    data: typing.Any


class ListPublicAccountsResponseModel(PaginatedResponse):
    data: list[PublicAccount]


class PublicAccountUpdateRequest(BaseModel):
    firstName: typing.Optional[str]
    lastName: typing.Optional[str]
    dateOfBirth: typing.Optional[datetime.datetime]
    idPieceNumber: typing.Optional[str]
    email: typing.Optional[pydantic.EmailStr]
    phoneNumber: typing.Optional[str]
    address: typing.Optional[str]
    postalCode: typing.Optional[str]
    city: typing.Optional[str]

    @pydantic.validator("email", pre=True)
    def validate_email(cls, email: str) -> str:  # pylint: disable=no-self-argument
        if not email:
            return email
        return sanitize_email(email)

    @pydantic.validator("phoneNumber")
    def validate_phone_number(cls, phone_number: str) -> str:  # pylint: disable=no-self-argument
        if not phone_number:
            return phone_number

        try:
            # Convert to international format
            return phone_number_utils.ParsedPhoneNumber(phone_number, "FR").phone_number
        except phone_validation_exceptions.InvalidPhoneNumber:
            raise ValueError(f"Format de numéro de téléphone invalide : {phone_number}")


class GetBeneficiaryCreditResponseModel(BaseModel):
    initialCredit: float
    remainingCredit: float
    remainingDigitalCredit: float
    dateCreated: typing.Optional[datetime.datetime]


class AuthTokenQuery(BaseModel):
    token: str


class AuthTokenResponseModel(BaseModel):
    token: str


class SubscriptionItemModel(BaseModel):
    class Config:
        orm_mode = True
        use_enum_values = True

    type: subscription_models.SubscriptionStep
    status: subscription_models.SubscriptionItemStatus


class IdCheckItemModel(BaseModel):
    class Config:
        orm_mode = True
        use_enum_values = True

    @classmethod
    def from_orm(cls: typing.Any, fraud_check: fraud_models.BeneficiaryFraudCheck):  # type: ignore
        fraud_check.technicalDetails = fraud_check.resultContent

        if fraud_check.type == fraud_models.FraudCheckType.DMS and fraud_check.resultContent is not None:
            dms_content = fraud_models.DMSContent(**fraud_check.resultContent)  # type: ignore [arg-type]
            fraud_check.sourceId = str(dms_content.procedure_number)

        return super().from_orm(fraud_check)

    type: fraud_models.FraudCheckType
    dateCreated: datetime.datetime
    thirdPartyId: str
    status: typing.Optional[fraud_models.FraudCheckStatus]
    reason: typing.Optional[str]
    reasonCodes: typing.Optional[list[fraud_models.FraudReasonCode]]
    technicalDetails: typing.Optional[dict]
    sourceId: typing.Optional[str] = None  # DMS only


class EligibilitySubscriptionHistoryModel(BaseModel):
    subscriptionItems: list[SubscriptionItemModel]
    idCheckHistory: list[IdCheckItemModel]


class GetUserSubscriptionHistoryResponseModel(BaseModel):
    subscriptions: dict[str, EligibilitySubscriptionHistoryModel]


class BeneficiaryReviewRequestModel(BaseModel):
    class Config:
        extra = pydantic.Extra.forbid

    reason: str
    review: fraud_models.FraudReviewStatus
    eligibility: typing.Optional[str]


class BeneficiaryReviewResponseModel(BeneficiaryReviewRequestModel):
    userId: int
    authorId: int


class PublicHistoryItem(BaseModel):
    class config:
        extra = pydantic.Extra.forbid

    action: str
    datetime: datetime.datetime
    message: str


class PublicHistoryResponseModel(BaseModel):
    history: list[PublicHistoryItem]
