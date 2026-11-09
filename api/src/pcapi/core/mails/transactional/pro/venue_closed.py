from pcapi.core import mails
from pcapi.core.history import models as history_models
from pcapi.core.history import repository as history_repository
from pcapi.core.mails import models
from pcapi.core.mails.transactional.brevo_template_ids import TransactionalEmail
from pcapi.core.offerers import models as offerers_models
from pcapi.core.users import models as users_models
from pcapi.models import db


def get_venue_closed_email_data(
    venue: offerers_models.Venue, history_event: history_models.ActionHistory, author: users_models.User | None
) -> models.TransactionalEmailData:
    return models.TransactionalEmailData(
        template=TransactionalEmail.VENUE_CLOSED_CONFIRMATION.value,
        params={
            "VENUE_NAME": venue.publicName,
            "SIRET": venue.siret,
            "OFFERER_NAME": venue.managingOfferer.name,
            "USER_FIRST_NAME": author.firstName if author else None,
            "USER_LAST_NAME": author.lastName if author else None,
            "USER_EMAIL": author.email if author else None,
            "REQUEST_DATE": history_event.actionDate.date(),
            "REQUEST_TIME": history_event.actionDate.time(),
        },
    )


def send_venue_closed_email(venue_id: int) -> None:
    recipients: list[str] = []

    venue = db.session.query(offerers_models.Venue).filter_by(id=venue_id).one()
    history_event = history_repository.get_latest_venue_closure_event(venue.id)
    if not history_event:
        return

    author = db.session.query(users_models.User).filter_by(id=history_event.authorUserId).one_or_none()
    if author:
        if not author.backoffice_profile:
            recipients = [author.email]
        else:
            author = None
    if not author:
        if venue.bookingEmail:
            recipients = [venue.bookingEmail]
        else:
            recipients = [v.bookingEmail for v in venue.managingOfferer.managedVenues if v.bookingEmail]

    if not recipients:
        return

    data = get_venue_closed_email_data(venue, history_event, author)
    mails.send(recipients=recipients, data=data)
