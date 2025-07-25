import typing
from datetime import time

from psycopg2.extras import NumericRange

import pcapi.utils.date as date_utils
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import models as offers_models
from pcapi.models import db
from pcapi.utils.date import timespan_str_to_numrange

from . import schemas


def _timespan_to_numeric_range(timespans: schemas.OpeningHoursTimespans) -> list[NumericRange]:
    def _format_timespan(hours: schemas.OpeningHours) -> NumericRange:
        to_time_objects = [time.fromisoformat(t) for t in hours]
        ts = sorted(to_time_objects, key=lambda t: (t.hour, t.minute))

        start = ts[0].hour * 60 + ts[0].minute
        end = ts[1].hour * 60 + ts[1].minute
        return NumericRange(start, end, "[]")

    return [_format_timespan(ts) for ts in timespans if ts]


def upsert_opening_hours(
    target: typing.Union[offers_models.Offer, offerers_models.Venue],
    *,
    opening_hours: schemas.WeekdayOpeningHoursTimespans | None = None,
    full_replace: bool = True,
) -> dict[offerers_models.Weekday, schemas.OpeningHoursTimespans | None]:
    """Upsert an offer or a venue's opening hours, deleting previous ones (if asked for)

    The default behaviour is to delete all existing opening hours before
    adding fresh new ones (which make the update process easier). This
    can be avoided by setting `full_replace` to `False`: only targetted
    days will be removed; use this to run a partial update instead of a
    full (week) update.

    And return the updates' new values that can be used to log an
    offer's or a venue's opening hours change.
    """
    offer = target if isinstance(target, offers_models.Offer) else None
    venue = target if isinstance(target, offerers_models.Venue) else None

    delete_query = db.session.query(offerers_models.OpeningHours)

    if offer:
        delete_query = delete_query.filter_by(offerId=offer.id)
    elif venue:
        delete_query = delete_query.filter_by(venueId=venue.id)

    updates: dict[offerers_models.Weekday, schemas.OpeningHoursTimespans | None] = {}
    if not full_replace:
        filtered_opening_hours = opening_hours.dict(exclude_unset=True).keys() if opening_hours else []
        target_weekdays = [offerers_models.Weekday[raw_weekday] for raw_weekday in filtered_opening_hours]
        delete_query = delete_query.filter(offerers_models.OpeningHours.weekday.in_(target_weekdays))

        # in case of a partial update, do not track unwanted week days
        updates = {weekday: None for weekday in target_weekdays}
    else:
        updates = {weekday: None for weekday in offerers_models.Weekday}

    delete_query.delete(synchronize_session="evaluate")

    for raw_weekday, timespans in opening_hours or []:
        if not timespans:
            continue

        weekday = offerers_models.Weekday[raw_weekday]
        db.session.add(
            offerers_models.OpeningHours(
                offer=offer,  # type: ignore[arg-type]
                venue=venue,
                weekday=weekday,
                timespan=timespan_str_to_numrange(timespans),
            )
        )

        updates[weekday] = timespans

    db.session.flush()
    return updates


def old_opening_hours(
    target: typing.Union[offers_models.Offer, offerers_models.Venue],
) -> dict[offerers_models.Weekday, schemas.OpeningHoursTimespans | None]:
    """Keep a track of an offer or a venue's existing opening hours"""
    if isinstance(target, offers_models.Offer):
        query = db.session.query(offerers_models.OpeningHours).filter_by(offer=target)
    else:
        query = db.session.query(offerers_models.OpeningHours).filter_by(venue=target)

    old: dict[offerers_models.Weekday, schemas.OpeningHoursTimespans | None] = {}
    for opening_hours in query:
        if opening_hours.timespan is None:
            old[opening_hours.weekday] = None
        else:
            timespans = date_utils.numranges_to_timespan_str(opening_hours.timespan)
            old[opening_hours.weekday] = schemas.OpeningHoursTimespans(timespans)
    return old


def compute_upsert_changes(
    old_values: dict[offerers_models.Weekday, schemas.OpeningHoursTimespans | None],
    updates: dict[offerers_models.Weekday, schemas.OpeningHoursTimespans | None],
) -> dict[offerers_models.Weekday, dict[typing.Literal["old", "new"], schemas.OpeningHoursTimespans | None]]:
    return {weekday: {"old": old_values.get(weekday), "new": timespans} for weekday, timespans in updates.items()}
