from pcapi import settings
from pcapi.core import mails
from pcapi.core.offers.models import Offer
from pcapi.core.users.models import User
from pcapi.emails.offer_report import build_offer_report_data


def send_report_notification(user: User, offer: Offer, reason: str) -> bool:
    data = build_offer_report_data(user, offer, reason)
    return mails.send(recipients=[settings.SUPPORT_EMAIL_ADDRESS], data=data)
