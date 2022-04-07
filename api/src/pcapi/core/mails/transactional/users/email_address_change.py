from pcapi.core import mails
from pcapi.core.mails.models.sendinblue_models import SendinblueTransactionalEmailData
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.users.models import User


def get_information_email_change_data(first_name: str) -> SendinblueTransactionalEmailData:
    return SendinblueTransactionalEmailData(
        template=TransactionalEmail.EMAIL_CHANGE_REQUEST.value,
        params={
            "FIRSTNAME": first_name,
        },
    )


def send_information_email_change_email(user: User) -> bool:
    data = get_information_email_change_data(user.firstName)  # type: ignore [arg-type]
    return mails.send(recipients=[user.email], data=data)


def get_confirmation_email_change_data(first_name: str, confirmation_link: str) -> SendinblueTransactionalEmailData:
    return SendinblueTransactionalEmailData(
        template=TransactionalEmail.EMAIL_CHANGE_CONFIRMATION.value,
        params={"FIRSTNAME": first_name, "CONFIRMATION_LINK": confirmation_link},
    )


def send_confirmation_email_change_email(user: User, new_email: str, confirmation_link: str) -> bool:
    data = get_confirmation_email_change_data(user.firstName, confirmation_link)  # type: ignore [arg-type]
    return mails.send(recipients=[new_email], data=data)
