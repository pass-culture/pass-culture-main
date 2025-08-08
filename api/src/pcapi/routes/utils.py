from datetime import time

from pcapi.core.offerers import models as offerers_models
from pcapi.core.opening_hours import schemas as opening_hours_schemas


def format_offer_opening_hours(
    opening_hours: list[offerers_models.OpeningHours] | None,
) -> opening_hours_schemas.WeekdayOpeningHoursTimespans:
    """Format DB data to the expected pydantic model format

    From: [NumericRange(600, 720), NumericRange(780, 1200)]
    To: [["10:00", "12:00"], ["13:00", "20:00"]]
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

        if timespans:
            formatted[oh.weekday.value] = timespans

    return opening_hours_schemas.WeekdayOpeningHoursTimespans(**formatted)  # type: ignore[arg-type]
