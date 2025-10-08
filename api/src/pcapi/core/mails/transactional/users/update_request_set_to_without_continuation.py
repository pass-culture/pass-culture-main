from pcapi.core import mails
from pcapi.core.mails import models
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.utils import date as date_utils
from pcapi.utils.date import get_date_formatted_for_email


def send_beneficiary_update_request_set_to_without_continuation(recipient_email: str) -> None:
    data = models.TransactionalEmailData(
        template=TransactionalEmail.UPDATE_REQUEST_MARKED_WITHOUT_CONTINUATION.value,
        params={"DATE_FILECLASSIFIED_DMS": get_date_formatted_for_email(date_utils.get_naive_utc_now())},
    )
    mails.send(recipients=[recipient_email], data=data)
