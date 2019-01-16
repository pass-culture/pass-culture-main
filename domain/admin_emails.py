from typing import Dict, List, Callable

from utils.mailing import write_object_validation_email, check_if_email_sent, make_payment_transaction_email, \
    make_venue_validation_email, compute_email_html_part_and_recipients, make_payment_details_email, \
    make_payments_report_email, make_wallet_balances_email


def send_dev_email(subject, html_text, send_create_email: Callable[..., None]):
    email = {
        'FromName': 'Pass Culture Dev',
        'FromEmail': 'passculture-dev@beta.gouv.fr',
        'Subject': subject,
        'Html-part': html_text,
        'To': 'passculture-dev@beta.gouv.fr'
    }
    mail_result = send_create_email(data=email)
    check_if_email_sent(mail_result)


def maybe_send_offerer_validation_email(offerer, user_offerer, send_create_email: Callable[..., None]):
    if offerer.isValidated and user_offerer.isValidated:
        return
    email = write_object_validation_email(offerer, user_offerer)
    recipients = ['passculture@beta.gouv.fr']
    email['Html-part'], email['To'] = compute_email_html_part_and_recipients(email['Html-part'], recipients)
    mail_result = send_create_email(data=email)

    check_if_email_sent(mail_result)


def send_payment_transaction_email(xml_attachment: str, checksum: bytes, recipients: List[str],
                                   send_create_email: Callable[..., None]):
    email = make_payment_transaction_email(xml_attachment, checksum)
    email['Html-part'], email['To'] = compute_email_html_part_and_recipients(email['Html-part'], recipients)
    mail_result = send_create_email(data=email)
    check_if_email_sent(mail_result)


def send_payment_details_email(csv_attachment: str, recipients: List[str], send_create_email: Callable[..., None]):
    email = make_payment_details_email(csv_attachment)
    email['Html-part'], email['To'] = compute_email_html_part_and_recipients("", recipients)
    mail_result = send_create_email(data=email)
    check_if_email_sent(mail_result)


def send_wallet_balances_email(csv_attachment: str, recipients: List[str], send_create_email: Callable[..., None]):
    email = make_wallet_balances_email(csv_attachment)
    email['Html-part'], email['To'] = compute_email_html_part_and_recipients("", recipients)
    mail_result = send_create_email(data=email)
    check_if_email_sent(mail_result)


def send_payments_report_emails(not_processable_payments_csv: str, error_payments_csv: str, grouped_payments: Dict,
                                recipients: List[str], send_create_email: Callable[..., None]):
    email = make_payments_report_email(not_processable_payments_csv, error_payments_csv, grouped_payments)
    email['Html-part'], email['To'] = compute_email_html_part_and_recipients("", recipients)
    mail_result = send_create_email(data=email)
    check_if_email_sent(mail_result)


def send_venue_validation_email(venue, send_create_email: Callable[..., None]):
    email = make_venue_validation_email(venue)
    recipients = ['passculture@beta.gouv.fr']
    email['Html-part'], email['To'] = compute_email_html_part_and_recipients(email['Html-part'], recipients)
    mail_result = send_create_email(data=email)
    check_if_email_sent(mail_result)
