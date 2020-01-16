from typing import Dict, List, Callable, Union

from models import Offer, User, Offerer, UserOfferer, Venue
from utils.mailing import make_validation_email_object, make_payment_message_email, \
    make_venue_to_validate_email, compute_email_html_part_and_recipients, make_payment_details_email, \
    make_payments_report_email, make_wallet_balances_email, make_offer_creation_notification_email, \
    make_beneficiaries_import_email, make_activation_users_email, \
    ADMINISTRATION_EMAIL_ADDRESS


def maybe_send_offerer_validation_email(offerer: Offerer, user_offerer: UserOfferer,
                                        send_email: Callable[[dict], bool]) -> bool:
    if offerer.isValidated and user_offerer.isValidated:
        return
    email = make_validation_email_object(offerer, user_offerer)
    recipients = [ADMINISTRATION_EMAIL_ADDRESS]
    email['Html-part'], email['To'] = compute_email_html_part_and_recipients(email['Html-part'], recipients)
    return send_email(data=email)


def send_payment_message_email(xml_attachment: str, checksum: bytes, recipients: List[str],
                               send_email: Callable[[dict], bool]) -> bool:
    email = make_payment_message_email(xml_attachment, checksum)
    email['Html-part'], email['To'] = compute_email_html_part_and_recipients(email['Html-part'], recipients)
    return send_email(data=email)


def send_payment_details_email(csv_attachment: str, recipients: List[str], send_email: Callable[[dict], bool]) -> bool:
    email = make_payment_details_email(csv_attachment)
    email['Html-part'], email['To'] = compute_email_html_part_and_recipients("", recipients)
    return send_email(data=email)


def send_wallet_balances_email(csv_attachment: str, recipients: List[str], send_email: Callable[[dict], bool]) -> bool:
    email = make_wallet_balances_email(csv_attachment)
    email['Html-part'], email['To'] = compute_email_html_part_and_recipients("", recipients)
    return send_email(data=email)


def send_users_activation_report(csv_attachment: str, recipients: List[str], send_email: Callable[[dict], bool]) -> bool:
    email = make_activation_users_email(csv_attachment)
    email['Html-part'], email['To'] = compute_email_html_part_and_recipients("", recipients)
    return send_email(data=email)


def send_payments_report_emails(not_processable_payments_csv: str, error_payments_csv: str, grouped_payments: Dict,
                                recipients: List[str], send_email: Callable[[dict], bool]) -> bool:
    email = make_payments_report_email(not_processable_payments_csv, error_payments_csv, grouped_payments)
    email['Html-part'], email['To'] = compute_email_html_part_and_recipients(email['Html-part'], recipients)
    return send_email(data=email)


def send_venue_validation_email(venue: Venue, send_email: Callable[[dict], bool]) -> bool:
    email = make_venue_to_validate_email(venue)
    recipients = [ADMINISTRATION_EMAIL_ADDRESS]
    email['Html-part'], email['To'] = compute_email_html_part_and_recipients(email['Html-part'], recipients)
    return send_email(data=email)


def send_offer_creation_notification_to_administration(offer: Offer, author: User, app_origin_url: str,
                                                       send_email: Callable[[dict], bool]) -> bool:
    email = make_offer_creation_notification_email(offer, author, app_origin_url)
    email['Html-part'], email['To'] = compute_email_html_part_and_recipients(email['Html-part'], email['To'])
    return send_email(data=email)


def send_remote_beneficiaries_import_report_email(new_beneficiaries: List[User], error_messages: List[str],
                                                  recipients: Union[List, str], send_email: Callable[[dict], bool]) -> bool:
    email = make_beneficiaries_import_email(new_beneficiaries, error_messages)
    email['Html-part'], email['To'] = compute_email_html_part_and_recipients(email['Html-part'], recipients)
    return send_email(data=email)
