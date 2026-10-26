from datetime import UTC
from datetime import datetime
from datetime import timedelta

import sqlalchemy.orm as sa_orm
from sqlalchemy.orm import Query

from pcapi.core.history import constants as history_constants
from pcapi.models import db

from . import constants
from . import models


def get_latest_venue_closure_event(venue_id: int) -> models.ActionHistory | None:
    return (
        db.session.query(models.ActionHistory)
        .filter(
            models.ActionHistory.venueId == venue_id,
            models.ActionHistory.actionType == history_constants.ActionType.VENUE_CLOSED,
        )
        .order_by(models.ActionHistory.id.desc())
        .limit(1)
        .one_or_none()
    )


def get_events_regarding_venue_closure_before(days_count: int) -> Query:
    before = datetime.now(UTC).replace(tzinfo=None) - timedelta(days=days_count)
    return (
        db.session.query(models.ActionHistory)
        .filter(models.ActionHistory.actionType == constants.ActionType.VENUE_ADD_CLOSURE_TAG)
        .filter(models.ActionHistory.actionDate <= before)
        .options(sa_orm.selectinload(models.ActionHistory.venue))
    )
