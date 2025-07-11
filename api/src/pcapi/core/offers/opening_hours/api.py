from contextlib import suppress

from psycopg2.extras import NumericRange

from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import models
from pcapi.core.offers import schemas
from pcapi.models import db
from pcapi.utils.date import timespan_str_to_numrange


def _timespan_to_numeric_range(timespans: schemas.OpeningHoursTimespans) -> list[NumericRange]:  # type: ignore[valid-type]
    def _format_timespan(ts: schemas.OpeningHours) -> NumericRange:  # type: ignore[valid-type]
        start = ts[0].hour * 60 + ts[0].minute  # type: ignore[index]
        end = ts[1].hour * 60 + ts[1].minute  # type: ignore[index]
        return NumericRange(start, end, "[]")

    return [_format_timespan(ts) for ts in timespans if ts]  # type: ignore[attr-defined]


def upsert_opening_hours(offer: models.Offer, opening_hours: schemas.WeekdayOpeningHoursTimespans | None) -> None:
    """Upsert an offer's opening hours, erasing previous ones (if any)"""
    db.session.query(offerers_models.OpeningHours).filter_by(offerId=offer.id).delete(synchronize_session="evaluate")

    # for some obscure reason, offer's opening hours still exists within
    # the session without this.
    offer.openingHours = []

    items = opening_hours.items() if opening_hours else []
    for weekday, timespans in items:
        if not timespans:
            continue

        numeric_ranges = timespan_str_to_numrange(timespans)

        # should not happen, but since the pydantic models serializes
        # the enum into its string value the typing is kind of wrong.
        with suppress(KeyError):
            weekday = offerers_models.Weekday[weekday]

        oh = offerers_models.OpeningHours(offer=offer, weekday=weekday, timespan=numeric_ranges)
        db.session.add(oh)
