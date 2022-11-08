from pcapi.core import mails
from pcapi.core.mails import models
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.offerers.models import Venue
from pcapi.utils.urls import build_pc_pro_venue_link


def get_permanent_venue_needs_picture_data(venue: Venue) -> models.TransactionalEmailData:
    return models.TransactionalEmailData(
        template=TransactionalEmail.VENUE_NEEDS_PICTURE.value,
        params={
            "VENUE_NAME": venue.publicName or venue.name,
            "VENUE_FORM_URL": build_pc_pro_venue_link(venue),
        },
    )


def send_permanent_venue_needs_picture(recipient: str, venue: Venue) -> bool:
    data = get_permanent_venue_needs_picture_data(venue)
    return mails.send(recipients=[recipient], data=data)
