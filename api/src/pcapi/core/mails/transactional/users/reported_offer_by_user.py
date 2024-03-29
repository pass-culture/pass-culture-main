from pcapi import settings
from pcapi.core import mails
from pcapi.core.mails import models
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import Reason
from pcapi.core.users.models import User
from pcapi.utils.urls import build_pc_pro_offer_link


def send_email_reported_offer_by_user(user: User, offer: Offer, reason: Reason, custom_reason: str | None) -> None:
    data = get_reported_offer_email_data(user, offer, reason, custom_reason)
    recipients = [settings.REPORT_OFFER_EMAIL_ADDRESS]
    if reason == Reason.OTHER:
        recipients = [settings.SUPPORT_EMAIL_ADDRESS]
    mails.send(recipients=recipients, data=data)


def get_reported_offer_email_data(
    user: User, offer: Offer, reason: Reason, custom_reason: str | None = None
) -> models.TransactionalEmailData:
    reason_value = Reason.get_meta(reason.value).title
    if custom_reason:
        reason_value = f"[{reason_value.title}] {custom_reason}"

    return models.TransactionalEmailData(
        template=TransactionalEmail.REPORTED_OFFER_BY_USER.value,
        params={
            "USER_ID": user.id,
            "OFFER_ID": offer.id,
            "OFFER_NAME": offer.name,
            "REASON": reason_value,
            "OFFER_URL": build_pc_pro_offer_link(offer),
        },
    )
