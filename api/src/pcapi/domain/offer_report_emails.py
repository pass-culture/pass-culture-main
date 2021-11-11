from typing import Optional

from pcapi import settings
from pcapi.core import mails
from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import Reason
from pcapi.core.users.models import User
from pcapi.emails.offer_report import build_offer_report_data


def send_report_notification(user: User, offer: Offer, reason: str, custom_reason: Optional[str]) -> bool:
    data = build_offer_report_data(user, offer, reason, custom_reason)
    recipients = [settings.REPORT_OFFER_EMAIL_ADDRESS]
    if reason == Reason.OTHER.value:
        recipients = [settings.SUPPORT_EMAIL_ADDRESS]
    return mails.send(recipients=recipients, data=data)
