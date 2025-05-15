import pcapi.core.users.models as users_models
from pcapi.core import mails
from pcapi.core.mails import models
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail


def send_beneficiary_pre_anonymization_email(user: users_models.User) -> None:
    data = models.TransactionalEmailData(template=TransactionalEmail.BENEFICIARY_PRE_ANONYMIZATION.value)
    mails.send(recipients=[user.email], data=data)
