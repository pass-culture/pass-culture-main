from pcapi.core import mails
from pcapi.core.mails import models
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.offerers import models as offerers_models
from pcapi.core.users import models as users_models


def send_pre_anonymization_email_to_pro(
    user: users_models.User, offerer: offerers_models.Offerer | None = None
) -> None:
    mails.send(
        recipients=[user.email],
        data=models.TransactionalEmailData(
            template=TransactionalEmail.PRO_PRE_ANONYMIZATION.value,
            params={
                "OFFERER_NAME": offerer.name if offerer else None,
            },
        ),
    )
