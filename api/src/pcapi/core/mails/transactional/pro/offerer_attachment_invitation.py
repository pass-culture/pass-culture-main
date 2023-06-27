from pcapi.core import mails
from pcapi.core.mails import models
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail


def retrieve_data_for_offerer_attachment_invitation() -> models.TransactionalEmailData:
    return models.TransactionalEmailData(template=TransactionalEmail.OFFERER_ATTACHMENT_INVITATION.value)


def retrieve_data_for_offerer_attachment_invitation_accepted() -> models.TransactionalEmailData:
    return models.TransactionalEmailData(template=TransactionalEmail.OFFERER_ATTACHMENT_INVITATION_ACCEPTED.value)


def retrieve_data_for_offerer_attachment_invitation_confirmed() -> models.TransactionalEmailData:
    return models.TransactionalEmailData(template=TransactionalEmail.OFFERER_ATTACHMENT_INVITATION_CONFIRMED.value)


def send_offerer_attachment_invitation(recipient_emails: list[str]) -> bool:
    offerer_attachment_invitation_data = retrieve_data_for_offerer_attachment_invitation()
    return mails.send(recipients=recipient_emails, data=offerer_attachment_invitation_data)


def send_offerer_attachment_invitation_accepted(receipient_emails: list[str]) -> bool:
    offerer_attachment_invitation_accepted_data = retrieve_data_for_offerer_attachment_invitation_accepted()
    return mails.send(recipients=receipient_emails, data=offerer_attachment_invitation_accepted_data)


def send_offerer_attachment_invitation_confirmed(recipient_emails: list[str]) -> bool:
    offerer_attachment_invitation_confirmed = retrieve_data_for_offerer_attachment_invitation_confirmed()
    return mails.send(recipients=recipient_emails, data=offerer_attachment_invitation_confirmed)
