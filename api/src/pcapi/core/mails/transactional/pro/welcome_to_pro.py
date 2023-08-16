from pcapi.core import mails
from pcapi.core.mails import models
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.offerers.models import Venue
from pcapi.core.users.models import User
from pcapi.utils.urls import build_pc_pro_venue_link


def get_welcome_to_pro_email_data(venue: Venue) -> models.TransactionalEmailData:
    return models.TransactionalEmailData(
        template=TransactionalEmail.WELCOME_TO_PRO.value,
        params={"PC_PRO_VENUE_LINK": build_pc_pro_venue_link(venue=venue)},
    )


def send_welcome_to_pro_email(user: User, venue: Venue) -> bool:
    data = get_welcome_to_pro_email_data(venue)
    return mails.send(recipients=[user.email], data=data)
