from pcapi import settings
from pcapi.core import mails
from pcapi.core.offers.models import Offer
from pcapi.core.users.models import User
from pcapi.emails.offer_report import build_offer_report_data


def send_report_notification(user: User, offer: Offer, reason: str, custom_reason: str) -> bool:
    data = build_offer_report_data(user, offer, reason, custom_reason)
    return mails.send(recipients=[settings.COMPLIANCE_EMAIL_ADDRESS], data=data)
