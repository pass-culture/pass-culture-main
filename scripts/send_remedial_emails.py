from repository import email_queries
from utils.mailing import resend_email


def send_remedial_emails():
    emails_failed = email_queries.find_all_in_error()
    for email_failed in emails_failed:
        successfully_sent = resend_email(email_failed)
        if not successfully_sent:
            break
