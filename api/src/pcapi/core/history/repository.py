import pcapi.core.users.models as users_models
from pcapi.models import db

from . import models


def get_latest_venue_closure_user(venue_id: int) -> users_models.User | None:
    return (
        db.session.query(users_models.User)
        .join(models.ActionHistory, models.ActionHistory.authorUserId == users_models.User.id)
        .filter(
            models.ActionHistory.venueId == venue_id,
            models.ActionHistory.actionType == models.ActionType.VENUE_CLOSED,
        )
        .order_by(models.ActionHistory.id.desc())
        .limit(1)
        .one_or_none()
    )
