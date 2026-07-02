import abc
import datetime
import decimal

from pcapi.core.finance import models as finance_models
from pcapi.core.finance import utils as finance_utils
from pcapi.core.history import models as history_models
from pcapi.core.permissions import models as perm_models
from pcapi.core.subscription import models as subscription_models
from pcapi.core.users import models as users_models
from pcapi.models.beneficiary_import import BeneficiaryImport
from pcapi.models.beneficiary_import_status import BeneficiaryImportStatus
from pcapi.routes.backoffice import filters


def _format_amount_for_recredit_action(amount: decimal.Decimal, user: users_models.User) -> str:
    formatted_amount = finance_utils.format_currency_for_backoffice(amount)

    if user is not None and user.is_caledonian:
        formatted_amount += f" ({finance_utils.format_currency_for_backoffice(amount, use_xpf=True)})"

    return formatted_amount


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
            if self._fraud_check.type not in subscription_models.BONUS_CREDIT_CHECK_TYPES or (
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
        deposit_type = filters.format_deposit_type(self._deposit)
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
        recredit_type = filters.format_recredit_type(self._recredit)
        deposit_type = filters.format_deposit_type(self._recredit.deposit)
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


def get_default_user_history(user: users_models.User) -> list[AccountAction | history_models.ActionHistory]:
    # All data should have been joinloaded with user
    history: list[history_models.ActionHistory | AccountAction] = list(user.action_history)

    if history_models.ActionType.USER_CREATED not in (action.actionType for action in user.action_history):
        history.append(AccountCreatedAction(user))

    for change in user.email_history:
        history.append(EmailChangeAction(change))

    history = sorted(history, key=lambda item: item.actionDate or datetime.datetime.min, reverse=True)

    return history
