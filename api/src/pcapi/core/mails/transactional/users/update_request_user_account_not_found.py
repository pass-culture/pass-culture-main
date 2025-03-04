from pcapi.core import mails
from pcapi.core.mails import models
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail


def send_update_request_user_account_not_found(email: str, ds_application_id: int) -> None:
    data = models.TransactionalEmailData(
        template=TransactionalEmail.UPDATE_REQUEST_NO_USER_FOUND.value,
        params={"DS_APPLICATION_NUMBER": ds_application_id},
    )
    mails.send(recipients=[email], data=data)
