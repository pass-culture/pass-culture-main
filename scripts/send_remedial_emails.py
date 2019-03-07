from repository import email_queries
from utils.mailing import send_content_and_update


def send_remedial_emails():
    emails_failed = email_queries.find_all_in_error()
    for email_failed in emails_failed:
        send_content_and_update(email_failed)
