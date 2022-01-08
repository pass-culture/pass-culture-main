import typing

from markupsafe import Markup

from pcapi.core.subscription import models as subscription_models
from pcapi.core.users import models as users_models


def yesno(value: typing.Any) -> str:
    return Markup("""<span class="badge badge-{css_class}">{text}</span>""").format(
        css_class="success" if value else "danger",
        text="Oui" if value else "Non",
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


def subscription_status_format(subscription_status: subscription_models.SubscriptionItemStatus) -> str:
    return Markup("""<span class="badge badge-{css_class}">{text}</span>""").format(
        css_class=SUBSCRIPTION_STATUS_FORMATS[subscription_status]["css_class"],
        text=SUBSCRIPTION_STATUS_FORMATS[subscription_status]["text"],
    )


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
