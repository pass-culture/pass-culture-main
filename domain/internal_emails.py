from utils.mailing import write_object_validation_email, check_if_email_sent


def send_dev_email(subject, html_text, send_create_email):
    email = {
        'FromName': 'Pass Culture Dev',
        'FromEmail': 'passculture-dev@beta.gouv.fr',
        'Subject': subject,
        'Html-part': html_text,
        'To': 'passculture-dev@beta.gouv.fr'
    }
    mail_result = send_create_email(data=email)
    check_if_email_sent(mail_result)



def maybe_send_offerer_validation_email(offerer, user_offerer, send_create_email):
    if offerer.isValidated and user_offerer.isValidated:
        return
    email = write_object_validation_email(offerer, user_offerer)
    mail_result = send_create_email(data=email)

    check_if_email_sent(mail_result)