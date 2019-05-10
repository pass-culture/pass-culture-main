from models import PcObject
from repository import email_queries

DOMAIN_NAME = '@passculture.app'


def update_emails_with_new_sender_email():
    failed_emails = email_queries.find_all_in_error()

    updated_emails = []
    for failed_email in failed_emails:
        from_email = failed_email.content['FromEmail']

        failed_email.content = {
            'FromEmail': replace_from_email(from_email),
            'FromName': failed_email.content['FromName'],
            'Subject': failed_email.content['Subject'],
            'Text-Part': failed_email.content['Text-Part'],
            'Html-part': failed_email.content['Html-part']
        }
        updated_emails.append(failed_email)

    PcObject.check_and_save(*updated_emails)


def replace_from_email(from_email):
    split_from_email = from_email.split('@')
    new_from_email = split_from_email[0] + DOMAIN_NAME

    return new_from_email
