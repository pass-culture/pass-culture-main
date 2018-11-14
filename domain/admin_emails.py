from utils.mailing import write_object_validation_email, check_if_email_sent, make_payment_transaction_email, \
    make_venue_validation_email, edit_email_html_part_and_recipients


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
    recipients = ['passculture@beta.gouv.fr']
    email['Html-part'], email['To'] = edit_email_html_part_and_recipients(email['Html-part'], recipients)
    mail_result = send_create_email(data=email)

    check_if_email_sent(mail_result)


def send_payment_transaction_email(xml_attachment, send_create_email):
    email = make_payment_transaction_email(xml_attachment)
    recipients = ["passculture-dev@beta.gouv.fr"]
    email['Html-part'], email['To'] = edit_email_html_part_and_recipients(email['Html-part'], recipients)
    mail_result = send_create_email(data=email)
    check_if_email_sent(mail_result)


def send_venue_validation_email(venue, send_create_email):
    email = make_venue_validation_email(venue)
    recipients = ['passculture@beta.gouv.fr']
    email['Html-part'], email['To'] = edit_email_html_part_and_recipients(email['Html-part'], recipients)
    mail_result = send_create_email(data=email)
    check_if_email_sent(mail_result)
