from pcapi.core import mails
from pcapi.core.mails import models
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
import pcapi.core.offerers.models as offerers_models


def send_eac_offerer_activation_email(venue: offerers_models.Venue, emails: list[str]) -> None:
    data = get_data_offerer_activation_email(venue)
    main_recipients, bcc_recipients = [emails[0]], emails[1:]
    mails.send(recipients=main_recipients, bcc_recipients=bcc_recipients, data=data)


def get_data_offerer_activation_email(
    venue: offerers_models.Venue,
) -> models.TransactionalEmailData:
    return models.TransactionalEmailData(
        template=TransactionalEmail.EAC_OFFERER_ACTIVATION_EMAIL.value,
        params={"VENUE_NAME": venue.common_name},
    )
