from typing import Annotated

import pydantic as pydantic_v2
from pydantic import AfterValidator
from pydantic import StringConstraints


Hour = Annotated[
    str, StringConstraints(pattern=r"^(([0-1][0-9])|(2[0-3])):[0-5][0-9]$", strip_whitespace=True, strict=True)
]


def validate_opening_hours(opening_hours: list[Hour]) -> list[Hour]:
    if len(opening_hours) < 2:
        raise ValueError("ensure this value has at least 2 items")
    if len(opening_hours) > 2:
        raise ValueError("ensure this value has at most 2 items")
    start, end = opening_hours
    if start >= end:
        raise ValueError("opening hours start ({}) cannot be after end ({}), nor can they be equal".format(start, end))
    return opening_hours


OpeningHours = Annotated[list[Hour], AfterValidator(validate_opening_hours)]


def validate_opening_hours_timespan(timespan: list[OpeningHours]) -> list[OpeningHours]:
    timespan_length = len(timespan)
    hashable_timespans = set(tuple(hours) for hours in timespan)
    has_unique_items = len(hashable_timespans) == timespan_length
    if timespan_length < 1:
        raise ValueError("ensure this value has at least 1 item")
    if timespan_length > 2:
        raise ValueError("ensure this value has at most 2 items")
    if not has_unique_items:
        raise ValueError("Invalid opening hours timespan")

    previous_end = timespan[0][1]
    for start, end in timespan[1:]:
        if start < previous_end:
            raise ValueError(f"overlapping opening hours: {start} <> {previous_end}")
        previous_end = end

    return timespan


OpeningHoursTimespans = Annotated[list[OpeningHours], AfterValidator(validate_opening_hours_timespan)]


class WeekdayOpeningHoursTimespans(pydantic_v2.BaseModel):
    MONDAY: OpeningHoursTimespans | None = None
    TUESDAY: OpeningHoursTimespans | None = None
    WEDNESDAY: OpeningHoursTimespans | None = None
    THURSDAY: OpeningHoursTimespans | None = None
    FRIDAY: OpeningHoursTimespans | None = None
    SATURDAY: OpeningHoursTimespans | None = None
    SUNDAY: OpeningHoursTimespans | None = None

    model_config = pydantic_v2.ConfigDict(extra="forbid")
