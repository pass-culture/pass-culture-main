from pcapi.core import mails
from pcapi.core.mails import models
from pcapi.core.mails.transactional.brevo_template_ids import TransactionalEmail
from pcapi.core.offerers.models import Venue
from pcapi.core.users.models import User


def get_venue_reopened_email_data(venue: Venue) -> models.TransactionalEmailData:
    return models.TransactionalEmailData(
        template=TransactionalEmail.VENUE_REOPENED.value,
        params={
            "VENUE_PUBLIC_NAME": venue.publicName,
            "SIRET": venue.siret,
            "OFFERER_NAME": venue.managingOfferer.name,
        },
    )


def send_venue_reopened_email(venue: Venue, original_user: User) -> None:
    data = get_venue_reopened_email_data(venue)
    mails.send(recipients=[original_user.email], data=data)
