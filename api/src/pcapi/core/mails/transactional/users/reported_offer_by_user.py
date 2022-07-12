from pcapi import settings
from pcapi.core import mails
from pcapi.core.mails.models.sendinblue_models import SendinblueTransactionalEmailData
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import Reason
from pcapi.core.users.models import User
from pcapi.utils.mailing import build_pc_pro_offer_link


def send_email_reported_offer_by_user(user: User, offer: Offer, reason: str, custom_reason: str | None) -> bool:
    data = get_reported_offer_email_data(user, offer, reason, custom_reason)
    recipients = [settings.REPORT_OFFER_EMAIL_ADDRESS]
    if reason == Reason.OTHER.value:
        recipients = [settings.SUPPORT_EMAIL_ADDRESS]
    return mails.send(recipients=recipients, data=data)


def get_reported_offer_email_data(
    user: User, offer: Offer, reason: str, custom_reason: str | None = None
) -> SendinblueTransactionalEmailData:
    reason = Reason.get_meta(reason).title
    if custom_reason:
        reason = f"[{reason}] {custom_reason}"

    return SendinblueTransactionalEmailData(
        template=TransactionalEmail.REPORTED_OFFER_BY_USER.value,
        params={
            "USER_ID": user.id,
            "OFFER_ID": offer.id,
            "OFFER_NAME": offer.name,
            "REASON": reason,
            "OFFER_URL": build_pc_pro_offer_link(offer),
        },
    )
