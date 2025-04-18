from pcapi.core import mails
from pcapi.core.mails import models
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail


def get_fraudulent_booking_suspicion_email_data(token_list: list[str]) -> models.TransactionalEmailData:
    data = models.TransactionalEmailData(
        template=TransactionalEmail.FRAUDULENT_BOOKING_SUSPICION.value,
        params={"TOKEN_LIST": ", ".join(token_list)},
    )
    return data


def send_fraudulent_booking_suspicion_email(recipient: str, token_list: list[str]) -> None:
    data = get_fraudulent_booking_suspicion_email_data(token_list)
    mails.send(recipients=[recipient], data=data)
