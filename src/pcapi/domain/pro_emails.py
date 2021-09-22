from pcapi.core import mails
from pcapi.core.offerers.models import Offerer
from pcapi.core.offerers.repository import find_new_offerer_user_email
from pcapi.emails.new_offerer_validation import retrieve_data_for_new_offerer_validation_email
from pcapi.emails.offerer_attachment_validation import retrieve_data_for_offerer_attachment_validation_email
from pcapi.models import UserOfferer


def send_validation_confirmation_email_to_pro(offerer: Offerer) -> None:
    offerer_email = find_new_offerer_user_email(offerer.id)
    data = retrieve_data_for_new_offerer_validation_email(offerer)
    mails.send(recipients=[offerer_email], data=data)


def send_attachment_validation_email_to_pro_offerer(user_offerer: UserOfferer) -> None:
    data = retrieve_data_for_offerer_attachment_validation_email(user_offerer.offerer)
    mails.send(recipients=[user_offerer.user.email], data=data)
