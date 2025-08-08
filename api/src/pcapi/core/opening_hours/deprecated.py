"""
Opening hours deprecated functions that follow the old update-existing
logic. Please use or migrate to .api module's functions that follow the
delete and create logic that will be easier to use and track.
"""

import typing

from pcapi.core.offerers import models as offerers_models
from pcapi.models import db
from pcapi.utils.date import timespan_str_to_numrange

from . import schemas


MappedWeekdayOpeningHours = typing.Mapping[offerers_models.Weekday, schemas.OpeningHoursTimespans | None]


def get_venue_openings_hours_updates(opening_hours: schemas.WeekdayOpeningHoursTimespans) -> MappedWeekdayOpeningHours:
    updates = opening_hours.dict(exclude_unset=True) if opening_hours else {}
    return {offerers_models.Weekday[weekday]: timespans for weekday, timespans in updates.items()}


def get_venue_opening_hours_by_weekday(
    venue: offerers_models.Venue, weekday: offerers_models.Weekday
) -> offerers_models.OpeningHours:
    for opening_hours in venue.openingHours:
        if opening_hours.weekday == weekday:
            return opening_hours
    return offerers_models.OpeningHours(venue=venue, weekday=weekday)


def upsert_venue_opening_hours(venue: offerers_models.Venue, opening_hours: MappedWeekdayOpeningHours) -> None:
    """
    Create and attach OpeningHours for a givent set of days.
    Update (replace) an existing OpeningHours list otherwise.
    """
    for weekday, timespan in opening_hours.items():
        venue_opening_hours = get_venue_opening_hours_by_weekday(venue, weekday)
        venue_opening_hours.timespan = timespan_str_to_numrange(timespan) if timespan else None
        db.session.add(venue_opening_hours)
    db.session.flush()
