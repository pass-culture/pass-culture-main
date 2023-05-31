import abc
import datetime

from pcapi.core.fraud import models as fraud_models
from pcapi.core.history import models as history_models
from pcapi.core.subscription import models as subscription_models
from pcapi.core.users import models as users_models
from pcapi.models.beneficiary_import import BeneficiaryImport
from pcapi.models.beneficiary_import_status import BeneficiaryImportStatus
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
        if fraud_check.resultContent:
            fraud_check.technicalDetails = fraud_check.source_data()
        else:
            fraud_check.technicalDetails = None

        if fraud_check.type == fraud_models.FraudCheckType.DMS and fraud_check.resultContent is not None:
            dms_content = fraud_models.DMSContent(**fraud_check.resultContent)
            fraud_check.sourceId = str(dms_content.procedure_number)

        return super().from_orm(fraud_check)

    id: int
    type: fraud_models.FraudCheckType
    dateCreated: datetime.datetime
    thirdPartyId: str
    status: fraud_models.FraudCheckStatus | None
    reason: str | None
    reasonCodes: list[fraud_models.FraudReasonCode] | None
    technicalDetails: dict | None
    sourceId: str | None = None  # DMS only
    eligibilityType: users_models.EligibilityType | None
    applicable_eligibilities: list[users_models.EligibilityType]


class EligibilitySubscriptionHistoryModel(BaseModel):
    subscriptionItems: list[SubscriptionItemModel]
    idCheckHistory: list[IdCheckItemModel]


class AccountAction(abc.ABC):
    """
    Same behavior as an ActionHistory object so that we can use the same template as for pro histories, when public
    account history also shows rows from other tables.
    """

    @property
    @abc.abstractmethod
    def actionType(self) -> history_models.ActionType | str:
        pass

    @property
    @abc.abstractmethod
    def actionDate(self) -> datetime.datetime | None:
        return None

    @property
    def authorUser(self) -> users_models.User | None:
        return None

    @property
    def comment(self) -> str | None:
        return None

    @property
    def extraData(self) -> dict | None:
        return None


class EmailChangeAction(AccountAction):
    def __init__(self, user_email_history: users_models.UserEmailHistory):
        self._email_change = user_email_history

    @property
    def actionType(self) -> history_models.ActionType | str:
        match self._email_change.eventType:
            case users_models.EmailHistoryEventTypeEnum.UPDATE_REQUEST:
                return "Demande de changement d'email"
            case users_models.EmailHistoryEventTypeEnum.VALIDATION:
                return "Validation de changement d'email"
            case users_models.EmailHistoryEventTypeEnum.ADMIN_VALIDATION:
                return "Validation (admin) de changement d'email"
            case users_models.EmailHistoryEventTypeEnum.ADMIN_UPDATE_REQUEST | users_models.EmailHistoryEventTypeEnum.ADMIN_UPDATE:
                return "Changement d'email par l'admin"
            case _:
                return "Action de changement d'email inconnue"

    @property
    def actionDate(self) -> datetime.datetime | None:
        return self._email_change.creationDate

    @property
    def comment(self) -> str | None:
        return (
            f"de {self._email_change.oldUserEmail}@{self._email_change.oldDomainEmail} "
            f"à {self._email_change.newUserEmail}@{self._email_change.newDomainEmail}"
        )


class FraudCheckAction(AccountAction):
    def __init__(self, fraud_check: fraud_models.BeneficiaryFraudCheck):
        self._fraud_check = fraud_check

    @property
    def actionType(self) -> history_models.ActionType | str:
        return "Étape de vérification"

    @property
    def actionDate(self) -> datetime.datetime | None:
        return self._fraud_check.dateCreated

    @property
    def comment(self) -> str | None:
        return (
            f"{self._fraud_check.type.value}, {getattr(self._fraud_check.eligibilityType, 'value', '[éligibilité inconnue]')}, "
            f"{self._fraud_check.status.value if self._fraud_check.status else 'Statut inconnu'}, "
            f"{getattr(self._fraud_check.reasonCodes, 'value', '[raison inconnue]')}, {self._fraud_check.reason}"
        )


class ReviewAction(AccountAction):
    def __init__(self, review: fraud_models.BeneficiaryFraudReview):
        self._review = review

    @property
    def actionType(self) -> history_models.ActionType | str:
        return "Revue manuelle"

    @property
    def actionDate(self) -> datetime.datetime | None:
        return self._review.dateReviewed

    @property
    def authorUser(self) -> users_models.User | None:
        return self._review.author

    @property
    def comment(self) -> str | None:
        return f"Revue {self._review.review.value if self._review.review else 'sans état'} : {self._review.reason}"


class ImportStatusAction(AccountAction):
    def __init__(self, import_: BeneficiaryImport, status: BeneficiaryImportStatus):
        self._import = import_
        self._status = status

    @property
    def actionType(self) -> history_models.ActionType | str:
        return f"Import {self._import.source}"

    @property
    def actionDate(self) -> datetime.datetime | None:
        return self._status.date

    @property
    def authorUser(self) -> users_models.User | None:
        return self._status.author

    @property
    def comment(self) -> str | None:
        return f"{self._status.status.value} ({self._status.detail})"


class AccountCreatedAction(AccountAction):
    def __init__(self, user: users_models.User):
        self._user = user

    @property
    def actionType(self) -> history_models.ActionType:
        return history_models.ActionType.USER_CREATED

    @property
    def actionDate(self) -> datetime.datetime | None:
        return self._user.dateCreated

    @property
    def authorUser(self) -> users_models.User | None:
        return self._user
