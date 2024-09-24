from datetime import datetime

from pcapi.connectors import typeform
from pcapi.core.offerers import models as offerers_models
from pcapi.models import db

from . import models


def create_special_event_from_typeform(
    form_id: str, *, event_date: datetime | None = None, offerer_id: int | None = None, venue_id: int | None = None
) -> models.SpecialEvent:
    if venue_id:
        venue = offerers_models.Venue.query.filter_by(id=venue_id).one_or_none()
        if not venue:
            raise ValueError(f"Le lieu {venue_id} n'existe pas")
        if offerer_id and offerer_id != venue.managingOffererId:
            raise ValueError(f"Le lieu {venue_id} n'appartient pas à la structure {offerer_id}")
        if not offerer_id:
            offerer_id = venue.managingOffererId
    elif offerer_id:
        offerer = offerers_models.Venue.query.filter_by(id=venue_id).one_or_none()
        if not offerer:
            raise ValueError(f"La structure {offerer_id} n'existe pas")

    data = typeform.get_form(form_id)

    special_event = models.SpecialEvent(
        externalId=data.form_id,
        title=data.title,
        eventDate=event_date,
        offererId=offerer_id,
        venueId=venue_id,
    )
    db.session.add(special_event)

    for field in data.fields:
        db.session.add(
            models.SpecialEventQuestion(eventId=special_event.id, externalId=field.field_id, title=field.title)
        )

    db.session.flush()

    return special_event
