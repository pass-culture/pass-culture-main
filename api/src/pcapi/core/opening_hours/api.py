import typing

import pcapi.utils.date as date_utils
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import models as offers_models
from pcapi.models import db
from pcapi.utils.date import timespan_str_to_numrange

from . import deprecated  # noqa: F401
from . import schemas


MappedWeekdayOpeningHours = typing.Mapping[offerers_models.Weekday, schemas.OpeningHoursTimespans | None]


def upsert_opening_hours(
    target: typing.Union[offers_models.Offer, offerers_models.Venue],
    *,
    opening_hours: schemas.WeekdayOpeningHoursTimespans | None = None,
) -> None:
    """Upsert an offer or a venue's opening hours, deleting previous ones."""
    offer = target if isinstance(target, offers_models.Offer) else None
    venue = target if isinstance(target, offerers_models.Venue) else None

    delete_query = db.session.query(offerers_models.OpeningHours)

    if offer:
        delete_query = delete_query.filter_by(offerId=offer.id)
    elif venue:
        delete_query = delete_query.filter_by(venueId=venue.id)

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

    db.session.flush()


def get_current_opening_hours(
    target: typing.Union[offers_models.Offer, offerers_models.Venue],
) -> dict[offerers_models.Weekday, schemas.OpeningHoursTimespans | None]:
    """Keep a track of an offer or a venue's existing opening hours"""
    if isinstance(target, offers_models.Offer):
        query = db.session.query(offerers_models.OpeningHours).filter_by(offer=target)
    else:
        query = db.session.query(offerers_models.OpeningHours).filter_by(venue=target)

    current: dict[offerers_models.Weekday, schemas.OpeningHoursTimespans | None] = {}
    for opening_hours in query:
        if opening_hours.timespan is None:
            current[opening_hours.weekday] = None
        else:
            timespans = date_utils.numranges_to_timespan_str(opening_hours.timespan)
            current[opening_hours.weekday] = schemas.OpeningHoursTimespans(timespans)
    return current


def compute_upsert_changes(
    old_values: MappedWeekdayOpeningHours, updates: MappedWeekdayOpeningHours
) -> dict[offerers_models.Weekday, dict[typing.Literal["old", "new"], schemas.OpeningHoursTimespans | None]]:
    return {weekday: {"old": old_values.get(weekday), "new": timespans} for weekday, timespans in updates.items()}
