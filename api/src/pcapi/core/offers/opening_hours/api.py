from datetime import time

from psycopg2.extras import NumericRange

from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import models
from pcapi.core.offers import schemas
from pcapi.models import db
from pcapi.utils.date import timespan_str_to_numrange


def _timespan_to_numeric_range(timespans: schemas.OpeningHoursTimespans) -> list[NumericRange]:
    def _format_timespan(hours: schemas.OpeningHours) -> NumericRange:
        to_time_objects = [time.fromisoformat(t) for t in hours]
        ts = sorted(to_time_objects, key=lambda t: (t.hour, t.minute))

        start = ts[0].hour * 60 + ts[0].minute
        end = ts[1].hour * 60 + ts[1].minute
        return NumericRange(start, end, "[]")

    return [_format_timespan(ts) for ts in timespans if ts]


def upsert_opening_hours(offer: models.Offer, opening_hours: schemas.WeekdayOpeningHoursTimespans | None) -> None:
    """Upsert an offer's opening hours, erasing previous ones (if any)"""
    db.session.query(offerers_models.OpeningHours).filter_by(offerId=offer.id).delete(synchronize_session="evaluate")

    # for some obscure reason, inspecting offer's opening hours from
    # a breakpoint can keep the deleted objects... which can be very
    # confusing. This should not happen otherwise, but just in case
    # it might be safer to keep this assert (even though it might be
    # turned off).
    assert not offer.openingHours

    for raw_weekday, timespans in opening_hours or []:
        if not timespans:
            continue

        numeric_ranges = timespan_str_to_numrange(timespans)

        weekday = offerers_models.Weekday[raw_weekday]
        oh = offerers_models.OpeningHours(offer=offer, weekday=weekday, timespan=numeric_ranges)
        db.session.add(oh)

    db.session.flush()
