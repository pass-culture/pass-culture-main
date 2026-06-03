import typing
from datetime import time

import pcapi.utils.date as date_utils
from pcapi.core.offerers import models as offerers_models
from pcapi.models import db

from . import deprecated  # noqa: F401
from . import schemas


MappedWeekdayOpeningHours = typing.Mapping[offerers_models.Weekday, schemas.OpeningHoursTimespans | None]


def get_current_opening_hours(
    venue: offerers_models.Venue,
) -> dict[offerers_models.Weekday, schemas.OpeningHoursTimespans | None]:
    """Keep a track of an offer or a venue's existing opening hours"""
    query = db.session.query(offerers_models.OpeningHours).filter_by(venue=venue)

    current: dict[offerers_models.Weekday, schemas.OpeningHoursTimespans | None] = {}
    for opening_hours in query:
        if opening_hours.timespan is None:
            current[opening_hours.weekday] = None
        else:
            timespans = date_utils.numranges_to_timespan_str(opening_hours.timespan)
            current[opening_hours.weekday] = schemas.OpeningHoursTimespans(typing.cast(list[list[str]], timespans))
    return current


def compute_upsert_changes(
    old_values: MappedWeekdayOpeningHours, updates: MappedWeekdayOpeningHours
) -> dict[offerers_models.Weekday, dict[typing.Literal["old", "new"], schemas.OpeningHoursTimespans | None]]:
    return {weekday: {"old": old_values.get(weekday), "new": timespans} for weekday, timespans in updates.items()}


def format_opening_hours(
    opening_hours: list[offerers_models.OpeningHours] | None,
) -> schemas.WeekdayOpeningHoursTimespans:
    """Format DB data to the expected pydantic model format...

    ...where each week day has its opening hours set (=can be None)
    """
    formatted: dict[str, list[tuple[str, str]] | None] = {weekday.value: None for weekday in offerers_models.Weekday}
    for oh in opening_hours or []:
        timespans = []
        for ts in oh.timespan or []:
            lower = int(ts.lower)
            upper = int(ts.upper)

            start = time(lower // 60, lower % 60).isoformat(timespec="minutes")
            end = time(upper // 60, upper % 60).isoformat(timespec="minutes")

            timespans.append((start, end))
        formatted[oh.weekday.value] = sorted(timespans, key=lambda ts: ts[0]) or None

    return schemas.WeekdayOpeningHoursTimespans(**formatted)
