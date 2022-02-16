from pcapi.core import mails
from pcapi.emails.offerer_attachment_validation import retrieve_data_for_offerer_attachment_validation_email
from pcapi.models.user_offerer import UserOfferer


def send_attachment_validation_email_to_pro_offerer(user_offerer: UserOfferer) -> bool:
    data = retrieve_data_for_offerer_attachment_validation_email(user_offerer.offerer)
    return mails.send(recipients=[user_offerer.user.email], data=data)
