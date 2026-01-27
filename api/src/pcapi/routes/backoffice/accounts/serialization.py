import abc
import datetime
import decimal

import sqlalchemy as sa
from flask import url_for
from markupsafe import Markup
from pydantic import BaseModel as BaseModelV2

from pcapi import settings
from pcapi.core.finance import models as finance_models
from pcapi.core.finance import utils as finance_utils
from pcapi.core.history import models as history_models
from pcapi.core.permissions import models as perm_models
from pcapi.core.subscription import models as subscription_models
from pcapi.core.subscription import schemas as subscription_schemas
from pcapi.core.subscription.dms import schemas as dms_schemas
from pcapi.core.users import constants as users_constants
from pcapi.core.users import models as users_models
from pcapi.core.users import utils as users_utils
from pcapi.models.beneficiary_import import BeneficiaryImport
from pcapi.models.beneficiary_import_status import BeneficiaryImportStatus
from pcapi.routes.serialization import BaseModel


def get_fraud_check_eligibility_type(
    fraud_check: subscription_models.BeneficiaryFraudCheck,
) -> users_models.EligibilityType | None:
    if fraud_check.eligibilityType:
        return fraud_check.eligibilityType

    user = fraud_check.user

    if not user.dateOfBirth:
        return None

    age_at_fraud_check_date = users_utils.get_age_at_date(
        birth_date=user.dateOfBirth,
        specified_datetime=fraud_check.dateCreated,
        department_code=user.departementCode,
    )

    if user.dateCreated < settings.CREDIT_V3_DECREE_DATETIME:
        if age_at_fraud_check_date < users_constants.ELIGIBILITY_AGE_18:
            return users_models.EligibilityType.UNDERAGE
        return users_models.EligibilityType.AGE18

    return users_models.EligibilityType.AGE17_18


def _format_amount_for_recredit_action(amount: decimal.Decimal, user: users_models.User) -> str:
    formatted_amount = finance_utils.format_currency_for_backoffice(amount)

    if user is not None and user.is_caledonian:
        formatted_amount += f" ({finance_utils.format_currency_for_backoffice(amount, use_xpf=True)})"

    return formatted_amount


class SubscriptionItemModel(BaseModel):
    class Config:
        orm_mode = True
        use_enum_values = True

    type: subscription_schemas.SubscriptionStep
    status: subscription_schemas.SubscriptionItemStatus


class IdCheckItemModel(BaseModel):
    class Config:
        use_enum_values = True

    id: int
    type: subscription_models.FraudCheckType
    dateCreated: datetime.datetime
    thirdPartyId: str
    status: subscription_models.FraudCheckStatus | None
    reason: str | None
    reasonCodes: list[subscription_models.FraudReasonCode] | None
    technicalDetails: dict | None
    sourceId: str | None = None  # DMS only
    eligibilityType: users_models.EligibilityType | None
    applicable_eligibilities: list[users_models.EligibilityType]

    @classmethod
    def build(cls, fraud_check: subscription_models.BeneficiaryFraudCheck) -> "IdCheckItemModel":
        if fraud_check.resultContent:
            technical_data = fraud_check.source_data()
            technical_details = (
                technical_data.model_dump() if isinstance(technical_data, BaseModelV2) else technical_data.dict()
            )
        else:
            technical_details = None

        if fraud_check.type == subscription_models.FraudCheckType.DMS and fraud_check.resultContent is not None:
            dms_content = dms_schemas.DMSContent(**fraud_check.resultContent)
            source_id = str(dms_content.procedure_number)
        else:
            source_id = None

        if not fraud_check.is_id_check_ok_across_eligibilities_or_age:
            eligibility_type = get_fraud_check_eligibility_type(fraud_check)
            applicable_eligibilities = [eligibility_type] if eligibility_type else []
        else:
            applicable_eligibilities = fraud_check.applicable_eligibilities

        return cls(
            id=fraud_check.id,
            type=fraud_check.type,
            dateCreated=fraud_check.dateCreated,
            thirdPartyId=fraud_check.thirdPartyId,
            status=fraud_check.status,
            reason=fraud_check.reason,
            reasonCodes=fraud_check.reasonCodes,
            technicalDetails=technical_details,
            sourceId=source_id,
            eligibilityType=fraud_check.eligibilityType,
            applicable_eligibilities=applicable_eligibilities,
        )


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
            case users_models.EmailHistoryEventTypeEnum.NEW_EMAIL_SELECTION:
                return "Saisie d'une nouvelle adresse email"
            case users_models.EmailHistoryEventTypeEnum.CONFIRMATION:
                return "Confirmation de changement d'email"
            case users_models.EmailHistoryEventTypeEnum.CANCELLATION:
                return "Annulation de changement d'email"
            case users_models.EmailHistoryEventTypeEnum.VALIDATION:
                return "Validation de changement d'email"
            case users_models.EmailHistoryEventTypeEnum.ADMIN_VALIDATION:
                return "Validation (admin) de changement d'email"
            case (
                users_models.EmailHistoryEventTypeEnum.ADMIN_UPDATE_REQUEST
                | users_models.EmailHistoryEventTypeEnum.ADMIN_UPDATE
            ):
                return "Changement d'email par l'admin"
            case _:
                return "Action de changement d'email inconnue"

    @property
    def actionDate(self) -> datetime.datetime | None:
        return self._email_change.creationDate

    @property
    def comment(self) -> str | None:
        if not self._email_change.newEmail:
            return f"Lien envoyé à {self._email_change.oldEmail} pour choisir une nouvelle adresse email"
        return f"de {self._email_change.oldEmail} à {self._email_change.newEmail}"


class FraudCheckAction(AccountAction):
    def __init__(
        self, fraud_check: subscription_models.BeneficiaryFraudCheck, bo_user: users_models.User | None = None
    ):
        self._fraud_check = fraud_check
        self._bo_user = bo_user

    @property
    def actionType(self) -> history_models.ActionType | str:
        return "Étape de vérification"

    @property
    def actionDate(self) -> datetime.datetime | None:
        return self._fraud_check.dateCreated

    @property
    def comment(self) -> str | None:
        if self._fraud_check.reasonCodes:
            if self._fraud_check.type != subscription_models.FraudCheckType.QF_BONUS_CREDIT or (
                self._bo_user
                and perm_models.Permissions.READ_BENEFICIARY_BONUS_CREDIT
                in self._bo_user.backoffice_profile.permissions
            ):
                reason_codes = [getattr(reason, "value", str(reason)) for reason in self._fraud_check.reasonCodes]
            else:
                reason_codes = ["raison confidentielle"]
        else:
            reason_codes = ["raison inconnue"]
        return (
            f"{self._fraud_check.type.value}, {getattr(self._fraud_check.eligibilityType, 'value', '[éligibilité inconnue]')}, "
            f"{self._fraud_check.status.value if self._fraud_check.status else 'Statut inconnu'}, "
            f"{' + '.join(reason_codes)}, {self._fraud_check.reason}"
        )


class ReviewAction(AccountAction):
    def __init__(self, review: subscription_models.BeneficiaryFraudReview):
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


class DepositAction(AccountAction):
    def __init__(self, deposit: finance_models.Deposit):
        self._deposit = deposit

    @property
    def actionType(self) -> history_models.ActionType | str:
        return "Attribution d'un crédit"

    @property
    def actionDate(self) -> datetime.datetime | None:
        return self._deposit.dateCreated

    @property
    def comment(self) -> str | None:
        match self._deposit.type:
            case finance_models.DepositType.GRANT_15_17:
                deposit_type = "ancien crédit 15-17"
            case finance_models.DepositType.GRANT_18:
                deposit_type = "ancien crédit 18"
            case finance_models.DepositType.GRANT_17_18:
                deposit_type = "crédit 17-18"
            case _:
                deposit_type = "crédit d'origine inconnue"

        initial_recredit = self._deposit.initial_recredit
        initial_amount = self._deposit.amount - sum(
            recredit.amount for recredit in self._deposit.recredits if recredit != initial_recredit
        )

        return f"Attribution d'un {deposit_type} de {_format_amount_for_recredit_action(initial_amount, self._deposit.user)}"


class RecreditAction(AccountAction):
    def __init__(self, recredit: finance_models.Recredit):
        self._recredit = recredit

    @property
    def actionType(self) -> history_models.ActionType | str:
        return "Recrédit du compte"

    @property
    def actionDate(self) -> datetime.datetime | None:
        return self._recredit.dateCreated

    @property
    def comment(self) -> str | None:
        match self._recredit.recreditType:
            case finance_models.RecreditType.RECREDIT_15:
                recredit_type = "Recrédit à 15 ans"
            case finance_models.RecreditType.RECREDIT_16:
                recredit_type = "Recrédit à 16 ans"
            case finance_models.RecreditType.RECREDIT_17:
                recredit_type = "Recrédit à 17 ans"
            case finance_models.RecreditType.RECREDIT_18:
                recredit_type = "Recrédit à 18 ans"
            case finance_models.RecreditType.BONUS_CREDIT:
                recredit_type = "Recrédit issu de la bonification"
            case finance_models.RecreditType.MANUAL_MODIFICATION:
                recredit_type = "Recrédit par une action manuelle"
            case finance_models.RecreditType.PREVIOUS_DEPOSIT:
                recredit_type = "Recrédit de l'argent restant du crédit précédent"
            case finance_models.RecreditType.FINANCE_INCIDENT_RECREDIT:
                recredit_type = "Recrédit suite à un incident finance sur l'ancien crédit expiré"
            case _:
                recredit_type = "Recrédit d'origine inconnue"

        match self._recredit.deposit.type:
            case finance_models.DepositType.GRANT_15_17:
                deposit_type = "ancien crédit 15-17"
            case finance_models.DepositType.GRANT_18:
                deposit_type = "ancien crédit 18"
            case finance_models.DepositType.GRANT_17_18:
                deposit_type = "crédit 17-18"
            case _:
                deposit_type = "crédit inconnu"

        return (
            f"{recredit_type} de {_format_amount_for_recredit_action(self._recredit.amount, self._recredit.deposit.user)} sur un {deposit_type}"
            + (f" ({self._recredit.comment})" if self._recredit.comment else "")
        )


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


class BeneficiaryActivity(abc.ABC):
    """
    Used to put all user's chronicles, special events, etc in one table
    """

    @property
    @abc.abstractmethod
    def activityType(self) -> str:
        pass

    @property
    def activityDate(self) -> datetime.datetime | None:
        return None

    @property
    def comment(self) -> str | None:
        return None


class SpecialEventActivity(BeneficiaryActivity):
    def __init__(self, special_event_response: sa.engine.Row):
        self._special_event_response = special_event_response

    @property
    def activityType(self) -> str:
        return "Opération spéciale"

    @property
    def activityDate(self) -> datetime.datetime | None:
        return self._special_event_response.dateSubmitted

    @property
    def comment(self) -> str | None:
        from pcapi.routes.backoffice.filters import format_special_event_response_status  # avoid circular import

        comment = Markup(
            """Candidature à l'opération spéciale <a class="link-primary" href="{url}">{title}</a> : {status}"""
        ).format(
            url=url_for(
                "backoffice_web.operations.get_event_details", special_event_id=self._special_event_response.eventId
            ),
            title=self._special_event_response.title,
            status=format_special_event_response_status(self._special_event_response.status),
        )
        return comment


class ChronicleActivity(BeneficiaryActivity):
    def __init__(self, chronicle: sa.engine.Row):
        self._chronicle = chronicle

    @property
    def activityType(self) -> str:
        return "Chronique"

    @property
    def activityDate(self) -> datetime.datetime | None:
        return self._chronicle.dateCreated

    @property
    def comment(self) -> str | None:
        comment = Markup(
            """Rédaction d'une chronique sur <a class="link-primary" href="{url}">{title}</a> : {status}"""
        ).format(
            url=url_for("backoffice_web.chronicles.details", chronicle_id=self._chronicle.id),
            title=self._chronicle.title or "une œuvre",
            status="publiée" if self._chronicle.isPublished else "non publiée",
        )
        return comment
