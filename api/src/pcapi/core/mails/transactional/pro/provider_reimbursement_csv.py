from pcapi.core import mails
from pcapi.core.mails import models
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail


def send_provider_reimbursement_email(user_email: str, link_to_csv: str) -> None:
    data = models.TransactionalEmailData(
        template=TransactionalEmail.PROVIDER_REIMBURSEMENT_CSV.value, params={"LINK_TO_CSV": link_to_csv}
    )
    mails.send(recipients=[user_email], data=data)
