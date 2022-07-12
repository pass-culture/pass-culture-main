import logging
import typing

from markupsafe import Markup

from pcapi.core.fraud import models as fraud_models
from pcapi.core.subscription import models as subscription_models
from pcapi.core.users import models as users_models
import pcapi.core.users.constants as users_constants


logger = logging.getLogger(__name__)


def yesno(value: typing.Any) -> str:
    return Markup("""<span class="badge badge-{css_class}">{text}</span>""").format(
        css_class="success" if value else "danger",
        text="Oui" if value else "Non",
    )


def account_state_format(state: users_models.AccountState) -> str:
    context = {
        users_models.AccountState.ACTIVE: {"css_class": "success", "text": "Activé"},
        users_models.AccountState.INACTIVE: {"css_class": "danger", "text": "Non activé"},
        users_models.AccountState.SUSPENDED: {"css_class": "info", "text": "Suspendu"},
        users_models.AccountState.SUSPENDED_UPON_USER_REQUEST: {"css_class": "info", "text": "Suspendu"},
        users_models.AccountState.DELETED: {"css_class": "warning", "text": "Supprimé"},
    }

    return _account_state_format(**context[state])


def _account_state_format(css_class: str, text: str) -> str:
    return Markup("""<span class="badge badge-{css_class}">{text}</span>""").format(
        css_class=css_class,
        text=text,
    )


SUBSCRIPTION_STATUS_FORMATS = {
    subscription_models.SubscriptionItemStatus.KO: {"css_class": "danger", "text": "KO"},
    subscription_models.SubscriptionItemStatus.NOT_APPLICABLE: {"css_class": "void", "text": "N/A"},
    subscription_models.SubscriptionItemStatus.NOT_ENABLED: {"css_class": "void", "text": "Désactivé"},
    subscription_models.SubscriptionItemStatus.OK: {"css_class": "success", "text": "OK"},
    subscription_models.SubscriptionItemStatus.PENDING: {"css_class": "warning", "text": "PENDING"},
    subscription_models.SubscriptionItemStatus.SUSPICIOUS: {"css_class": "warning", "text": "SUSPICIOUS"},
    subscription_models.SubscriptionItemStatus.TODO: {"css_class": "info", "text": "TODO"},
    subscription_models.SubscriptionItemStatus.VOID: {"css_class": "void", "text": "vide"},
}

FRAUD_CHECK_STATUS_FORMATS = {
    fraud_models.FraudCheckStatus.KO: "danger",
    fraud_models.FraudCheckStatus.ERROR: "danger",
    fraud_models.FraudCheckStatus.OK: "success",
    fraud_models.FraudCheckStatus.PENDING: "warning",
    fraud_models.FraudCheckStatus.STARTED: "warning",
    fraud_models.FraudCheckStatus.SUSPICIOUS: "warning",
    fraud_models.FraudCheckStatus.CANCELED: "warning",
}


def subscription_status_format(subscription_status: subscription_models.SubscriptionItemStatus) -> str:
    return Markup("""<span class="badge badge-{css_class}">{text}</span>""").format(
        css_class=SUBSCRIPTION_STATUS_FORMATS[subscription_status]["css_class"],
        text=SUBSCRIPTION_STATUS_FORMATS[subscription_status]["text"],
    )


def fraud_check_status_format(status: fraud_models.FraudCheckStatus | None) -> str:
    if status is None:
        css_class = "void"
        text = "vide"
    elif status in FRAUD_CHECK_STATUS_FORMATS:
        css_class = FRAUD_CHECK_STATUS_FORMATS[status]
        text = status.name
    else:
        logger.error("Fraud check status %s not defined in FRAUD_CHECK_STATUS_FORMATS", status)
        css_class = "void"
        text = status.name

    return Markup("""<span class="badge badge-{css_class}">{text}</span>""").format(css_class=css_class, text=text)


def eligibility_format(eligibility_type: users_models.EligibilityType) -> str:
    if eligibility_type == users_models.EligibilityType.UNDERAGE:
        text = "pass 15-17"
    elif eligibility_type == users_models.EligibilityType.AGE18:
        text = "pass 18"
    else:
        text = "vide"

    return Markup("""<span class="badge badge-{css_class}">{text}</span>""").format(
        css_class="info" if eligibility_type else "void",
        text=text,
    )


def suspension_event_format(event_type: users_constants.SuspensionEventType) -> str:
    return Markup("<span>{text}</span>").format(text=dict(users_constants.SUSPENSION_EVENT_TYPE_CHOICES)[event_type])


def suspension_reason_format(suspension_reason: users_constants.SuspensionReason | None) -> str:
    text = dict(users_constants.SUSPENSION_REASON_CHOICES)[suspension_reason] if suspension_reason else ""
    return Markup("<span>{text}</span>").format(text=text)
