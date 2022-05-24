import datetime
import typing

import pydantic

from pcapi.core.fraud import models as fraud_models
from pcapi.core.subscription import models as subscription_models
from pcapi.core.users import models as users_models
from pcapi.routes.serialization import BaseModel


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


class PublicAccountSearchQuery(BaseModel):
    q: str


class ListPublicAccountsResponseModel(BaseModel):
    class Config:
        orm_mode = True

    accounts: list[PublicAccount]


class GetBeneficiaryCreditResponseModel(BaseModel):
    initialCredit: float
    remainingCredit: float
    remainingDigitalCredit: float


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
            fraud_check.sourceId = str(dms_content.procedure_id)
            fraud_check.authorEmail = dms_content.get_author_email()

        return super().from_orm(fraud_check)

    type: fraud_models.FraudCheckType
    dateCreated: datetime.datetime
    thirdPartyId: str
    status: typing.Optional[fraud_models.FraudCheckStatus]
    reason: typing.Optional[str]
    reasonCodes: typing.Optional[list[fraud_models.FraudReasonCode]]
    technicalDetails: typing.Optional[dict]
    sourceId: typing.Optional[str] = None  # DMS only
    authorEmail: typing.Optional[str] = None  # DMS only


class EligibilitySubscriptionHistoryModel(BaseModel):
    subscriptionItems: list[SubscriptionItemModel]
    idCheckHistory: list[typing.Union[IdCheckItemModel]]


class GetUserSubscriptionHistoryResponseModel(BaseModel):
    subscriptions: dict[str, EligibilitySubscriptionHistoryModel]


class BeneficiaryReviewRequestModel(BaseModel):
    class Config:
        extra = pydantic.Extra.forbid

    reason: str
    review: fraud_models.FraudReviewStatus
    eligibility: typing.Optional[users_models.EligibilityType]


class BeneficiaryReviewResponseModel(BeneficiaryReviewRequestModel):
    userId: int
    authorId: int
