from pcapi.models import db

from . import models


def get_latest_venue_closure_event(venue_id: int) -> models.ActionHistory | None:
    return (
        db.session.query(models.ActionHistory)
        .filter(
            models.ActionHistory.venueId == venue_id,
            models.ActionHistory.actionType == models.ActionType.VENUE_CLOSED,
        )
        .order_by(models.ActionHistory.id.desc())
        .limit(1)
        .one_or_none()
    )
