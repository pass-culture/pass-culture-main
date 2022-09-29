import datetime

from pcapi.core.fraud import models as fraud_models
from pcapi.core.subscription import models as subscription_models
from pcapi.routes.serialization import BaseModel


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
    def from_orm(cls, fraud_check: fraud_models.BeneficiaryFraudCheck) -> "IdCheckItemModel":
        fraud_check.technicalDetails = fraud_check.resultContent

        if fraud_check.type == fraud_models.FraudCheckType.DMS and fraud_check.resultContent is not None:
            dms_content = fraud_models.DMSContent(**fraud_check.resultContent)  # type: ignore [arg-type]
            fraud_check.sourceId = str(dms_content.procedure_number)

        return super().from_orm(fraud_check)

    type: fraud_models.FraudCheckType
    dateCreated: datetime.datetime
    thirdPartyId: str
    status: fraud_models.FraudCheckStatus | None
    reason: str | None
    reasonCodes: list[fraud_models.FraudReasonCode] | None
    technicalDetails: dict | None
    sourceId: str | None = None  # DMS only


class EligibilitySubscriptionHistoryModel(BaseModel):
    subscriptionItems: list[SubscriptionItemModel]
    idCheckHistory: list[IdCheckItemModel]
