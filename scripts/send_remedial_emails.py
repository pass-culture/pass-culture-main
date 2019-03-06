from flask import current_app as app

from repository import email_queries


def send_remedial_emails():
    emails_failed = email_queries.find_all_in_error()
    for email_failed in emails_failed:
        app.mailjet_client.send.create(data=email_failed.content)
