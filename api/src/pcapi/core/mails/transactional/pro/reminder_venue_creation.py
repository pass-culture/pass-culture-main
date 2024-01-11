from pcapi.core import mails
from pcapi.core.mails import models
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
import pcapi.core.offerers.exceptions as offerers_exceptions
import pcapi.core.offerers.models as offerers_models
import pcapi.core.offerers.repository as offerers_repository
from pcapi.settings import PRO_URL


def get_reminder_venue_creation_email_data(offerer: offerers_models.Offerer) -> models.TransactionalEmailData:
    return models.TransactionalEmailData(
        template=TransactionalEmail.REMINDER_VENUE_CREATION_TO_PRO.value,
        params={
            "PRO_URL": PRO_URL,
            "OFFERER_ID": offerer.id,
        },
    )


def send_reminder_venue_creation_to_pro(offerer: offerers_models.Offerer) -> None:
    try:
        recipient = offerers_repository.find_new_offerer_user_email(offerer.id)
    except offerers_exceptions.CannotFindOffererUserEmail:
        return
    data = get_reminder_venue_creation_email_data(offerer)
    mails.send(recipients=[recipient], data=data)
