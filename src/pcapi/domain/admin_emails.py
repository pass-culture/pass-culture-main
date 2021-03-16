from typing import Dict
from typing import List

from pcapi import settings
from pcapi.core import mails
from pcapi.core.offerers.models import Offerer
from pcapi.core.users.models import User
from pcapi.models import Offer
from pcapi.models import UserOfferer
from pcapi.utils.mailing import make_offer_creation_notification_email
from pcapi.utils.mailing import make_payment_details_email
from pcapi.utils.mailing import make_payment_message_email
from pcapi.utils.mailing import make_payments_report_email
from pcapi.utils.mailing import make_validation_email_object
from pcapi.utils.mailing import make_wallet_balances_email


def maybe_send_offerer_validation_email(offerer: Offerer, user_offerer: UserOfferer) -> bool:
    if offerer.isValidated and user_offerer.isValidated:
        return None
    email = make_validation_email_object(offerer, user_offerer)
    recipients = [settings.ADMINISTRATION_EMAIL_ADDRESS]
    return mails.send(recipients=recipients, data=email)


def send_payment_message_email(xml_attachment: str, checksum: bytes, recipients: List[str]) -> bool:
    email = make_payment_message_email(xml_attachment, checksum)
    return mails.send(recipients=recipients, data=email)


def send_payment_details_email(csv_attachment: str, recipients: List[str]) -> bool:
    email = make_payment_details_email(csv_attachment)
    return mails.send(recipients=recipients, data=email)


def send_wallet_balances_email(csv_attachment: str, recipients: List[str]) -> bool:
    email = make_wallet_balances_email(csv_attachment)
    return mails.send(recipients=recipients, data=email)


def send_payments_report_emails(
    not_processable_payments_csv: str,
    error_payments_csv: str,
    grouped_payments: Dict,
    recipients: List[str],
) -> bool:
    email = make_payments_report_email(not_processable_payments_csv, error_payments_csv, grouped_payments)
    return mails.send(recipients=recipients, data=email)


def send_offer_creation_notification_to_administration(offer: Offer, author: User) -> bool:
    email = make_offer_creation_notification_email(offer, author)
    return mails.send(recipients=[settings.ADMINISTRATION_EMAIL_ADDRESS], data=email)
