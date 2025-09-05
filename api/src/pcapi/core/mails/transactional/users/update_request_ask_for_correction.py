from pcapi.core import mails
from pcapi.core.mails import models
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.users import models as users_models


def send_beneficiary_update_request_ask_for_correction(
    update_request: users_models.UserAccountUpdateRequest,
    correction_reason: str,
) -> None:
    data = models.TransactionalEmailData(
        template=TransactionalEmail.UPDATE_REQUEST_ASK_FOR_CORRECTION.value,
        params={"CORRECTION_REASON": correction_reason, "DS_APPLICATION_NUMBER": update_request.dsApplicationId},
    )
    mails.send(recipients=[update_request.email], data=data)
