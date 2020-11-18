from typing import Callable
from typing import Dict
from typing import List

from pcapi.models import Offer
from pcapi.models import Offerer
from pcapi.models import UserOfferer
from pcapi.models import UserSQLEntity
from pcapi.utils.mailing import ADMINISTRATION_EMAIL_ADDRESS
from pcapi.utils.mailing import compute_email_html_part_and_recipients
from pcapi.utils.mailing import make_activation_users_email
from pcapi.utils.mailing import make_offer_creation_notification_email
from pcapi.utils.mailing import make_payment_details_email
from pcapi.utils.mailing import make_payment_message_email
from pcapi.utils.mailing import make_payments_report_email
from pcapi.utils.mailing import make_validation_email_object
from pcapi.utils.mailing import make_wallet_balances_email


def maybe_send_offerer_validation_email(
    offerer: Offerer, user_offerer: UserOfferer, send_email: Callable[[dict], bool]
) -> bool:
    if offerer.isValidated and user_offerer.isValidated:
        return
    email = make_validation_email_object(offerer, user_offerer)
    recipients = [ADMINISTRATION_EMAIL_ADDRESS]
    email["Html-part"], email["To"] = compute_email_html_part_and_recipients(email["Html-part"], recipients)
    return send_email(data=email)


def send_payment_message_email(
    xml_attachment: str, checksum: bytes, recipients: List[str], send_email: Callable[[dict], bool]
) -> bool:
    email = make_payment_message_email(xml_attachment, checksum)
    email["Html-part"], email["To"] = compute_email_html_part_and_recipients(email["Html-part"], recipients)
    return send_email(data=email)


def send_payment_details_email(csv_attachment: str, recipients: List[str], send_email: Callable[[dict], bool]) -> bool:
    email = make_payment_details_email(csv_attachment)
    email["Html-part"], email["To"] = compute_email_html_part_and_recipients("", recipients)
    return send_email(data=email)


def send_wallet_balances_email(csv_attachment: str, recipients: List[str], send_email: Callable[[dict], bool]) -> bool:
    email = make_wallet_balances_email(csv_attachment)
    email["Html-part"], email["To"] = compute_email_html_part_and_recipients("", recipients)
    return send_email(data=email)


def send_users_activation_report(
    csv_attachment: str, recipients: List[str], send_email: Callable[[dict], bool]
) -> bool:
    email = make_activation_users_email(csv_attachment)
    email["Html-part"], email["To"] = compute_email_html_part_and_recipients("", recipients)
    return send_email(data=email)


def send_payments_report_emails(
    not_processable_payments_csv: str,
    error_payments_csv: str,
    grouped_payments: Dict,
    recipients: List[str],
    send_email: Callable[[dict], bool],
) -> bool:
    email = make_payments_report_email(not_processable_payments_csv, error_payments_csv, grouped_payments)
    email["Html-part"], email["To"] = compute_email_html_part_and_recipients(email["Html-part"], recipients)
    return send_email(data=email)


def send_offer_creation_notification_to_administration(
    offer: Offer, author: UserSQLEntity, send_email: Callable[[dict], bool]
) -> bool:
    email = make_offer_creation_notification_email(offer, author)
    email["Html-part"], email["To"] = compute_email_html_part_and_recipients(email["Html-part"], email["To"])
    return send_email(data=email)
