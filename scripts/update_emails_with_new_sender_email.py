from models import PcObject
from repository import email_queries

NEW_FROM_EMAIL = 'support@passculture.app'


def update_emails_with_new_sender_email():
    failed_emails = email_queries.find_all_in_error()

    updated_emails = []
    for failed_email in failed_emails:
        new_content = {
            'FromEmail': NEW_FROM_EMAIL,
            'FromName': failed_email.content['FromName'],
            'Subject': failed_email.content['Subject']
        }
        if 'Text-Part' in failed_email.content:
            new_content['Text-Part'] = failed_email.content['Text-Part']

        if 'Html-part' in failed_email.content:
            new_content['Html-part'] = failed_email.content['Html-part']

        failed_email.content = new_content
        updated_emails.append(failed_email)

    if (updated_emails):
        PcObject.check_and_save(*updated_emails)
