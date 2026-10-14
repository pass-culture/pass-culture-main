from pcapi import settings
from pcapi.core import mails
from pcapi.core.mails import models
from pcapi.core.mails.transactional.brevo_template_ids import TransactionalEmail
from pcapi.core.offerers import models as offerers_models
from pcapi.models import db


def get_venue_closure_request_email_data(venue: offerers_models.Venue) -> models.TransactionalEmailData:
    return models.TransactionalEmailData(
        template=TransactionalEmail.VENUE_PRICING_POINT_CLOSURE_REQUESTED.value,
        params={
            "VENUE_PUBLIC_NAME": venue.publicName,
            "SIRET": venue.siret,
            "OFFERER_NAME": venue.managingOfferer.name,
        },
    )


def send_venue_closure_request_email(venue_id: int) -> None:
    venue = db.session.query(offerers_models.Venue).filter_by(id=venue_id).one()
    data = get_venue_closure_request_email_data(venue)
    mails.send(recipients=[settings.SUPPORT_PRO_EMAIL_ADDRESS], data=data)
