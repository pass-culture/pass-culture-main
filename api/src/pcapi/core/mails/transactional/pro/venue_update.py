from pcapi.core import mails
from pcapi.core.mails import models
from pcapi.core.mails.transactional.brevo_template_ids import TransactionalEmail
from pcapi.core.offerers import models as offerers_models
from pcapi.models import db


def get_siret_updated_email_data(venue: offerers_models.Venue) -> models.TransactionalEmailData:
    return models.TransactionalEmailData(
        template=TransactionalEmail.VENUE_CLOSED_CONFIRMATION.value,
        params={
            "SIRET": venue.siret,
            "ADDRESS": venue.offererAddress.address.fullAddress,
        },
    )


def send_updated_siret_notification(venue_id: int, recipients: list[str]) -> None:
    venue = db.session.query(offerers_models.Venue).filter_by(id=venue_id).one()
    mails.send(recipients=recipients, data=get_siret_updated_email_data(venue))
