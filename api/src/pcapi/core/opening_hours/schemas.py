import datetime
from typing import Annotated

import pydantic as pydantic_v2
from pydantic import BeforeValidator
from pydantic import StringConstraints
from pydantic.v1 import ConstrainedList
from pydantic.v1 import ConstrainedStr
from pydantic.v1 import validator

from pcapi.routes.serialization import BaseModel


class Hour(ConstrainedStr):
    """defines a time string that matches the HH:MM format"""

    __args__ = (str,)
    regex = r"^(([0-1][0-9])|(2[0-3])):[0-5][0-9]$"
    strip_whitespace = True
    strict = True


class OpeningHours(ConstrainedList):
    """defines start and end opening hours
    eg. ["10:00", "18:00"] (from 10:00 to 18:00)
    """

    __args__ = (Hour,)
    item_type = Hour
    min_items = 2
    max_items = 2
    unique_items = True


class OpeningHoursTimespans(ConstrainedList):
    """defines a whole day's opening hours

    eg. [["10:00", "13:00"], ["14:00", "18:00"]]
    """

    __args__ = (OpeningHours,)
    item_type = OpeningHours
    min_items = 1
    max_items = 2
    unique_items = True


def validate_timespans(timespans: OpeningHoursTimespans | None) -> OpeningHoursTimespans | None:
    """Check that timespans are well-formed (if any)

    -> Each timespan is a (start, end) pair.
    -> Check that start is always before end.
    -> Check that there is no overlapping pair, eg. from 10:00 to
    14:00 and from 13:00 to 17:00.
    """

    def unpack_opening_hours(oh: OpeningHours) -> tuple[datetime.time, datetime.time]:
        start, end = oh
        return datetime.time.fromisoformat(start), datetime.time.fromisoformat(end)

    if timespans is None:
        return None

    # check that start and end pairs are well ordered
    ranges = [unpack_opening_hours(ts) for ts in timespans]

    for start, end in ranges:
        if start >= end:
            raise ValueError(f"opening hours start ({start}) cannot be after end ({end})")

    # check that there is no overlapping (start, end) pair
    ranges = sorted(ranges, key=lambda opening_hours: opening_hours[0])
    previous_end = ranges[0][1]

    for start, end in ranges[1:]:
        if start < previous_end:
            raise ValueError(f"overlapping opening hours: {start} <> {previous_end}")
        previous_end = end

    return timespans


# NOTE(jbaudet - 02/2026): depreacted. Please use
# WeekdayOpeningHoursTimespansV2 instead (pydantic v2 migration)
class WeekdayOpeningHoursTimespans(BaseModel):
    MONDAY: OpeningHoursTimespans | None
    TUESDAY: OpeningHoursTimespans | None
    WEDNESDAY: OpeningHoursTimespans | None
    THURSDAY: OpeningHoursTimespans | None
    FRIDAY: OpeningHoursTimespans | None
    SATURDAY: OpeningHoursTimespans | None
    SUNDAY: OpeningHoursTimespans | None

    _validate_monday = validator("MONDAY", allow_reuse=True)(validate_timespans)
    _validate_tuesday = validator("TUESDAY", allow_reuse=True)(validate_timespans)
    _validate_wednesday = validator("WEDNESDAY", allow_reuse=True)(validate_timespans)
    _validate_thursday = validator("THURSDAY", allow_reuse=True)(validate_timespans)
    _validate_friday = validator("FRIDAY", allow_reuse=True)(validate_timespans)
    _validate_saturday = validator("SATURDAY", allow_reuse=True)(validate_timespans)
    _validate_sunday = validator("SUNDAY", allow_reuse=True)(validate_timespans)

    class Config:
        extra = "forbid"


HourV2 = Annotated[
    str, StringConstraints(pattern=r"^(([0-1][0-9])|(2[0-3])):[0-5][0-9]$", strip_whitespace=True, strict=True)
]


def validate_opening_hours(opening_hours: list[HourV2]) -> list[HourV2]:
    has_unique_items = len(set(opening_hours)) == len(opening_hours)
    has_two_items_exactly = len(opening_hours) == 2
    if not (has_unique_items and has_two_items_exactly):
        raise ValueError("Invalid opening hours")
    return opening_hours


OpeningHoursV2 = Annotated[list[HourV2], BeforeValidator(validate_opening_hours)]


def validate_opening_hours_timespan(timespan: list[OpeningHoursV2]) -> list[OpeningHoursV2]:
    timespan_length = len(timespan)
    hashable_timespans = set(tuple(hours) for hours in timespan)

    has_unique_items = len(hashable_timespans) == timespan_length
    has_one_or_two_items = timespan_length >= 1 and timespan_length <= 2

    if not (has_unique_items and has_one_or_two_items):
        raise ValueError("Invalid opening hours timespan")

    return timespan


OpeningHoursTimespansV2 = Annotated[list[OpeningHoursV2], BeforeValidator(validate_opening_hours_timespan)]


class WeekdayOpeningHoursTimespansV2(pydantic_v2.BaseModel):
    MONDAY: OpeningHoursTimespansV2 | None
    TUESDAY: OpeningHoursTimespansV2 | None
    WEDNESDAY: OpeningHoursTimespansV2 | None
    THURSDAY: OpeningHoursTimespansV2 | None
    FRIDAY: OpeningHoursTimespansV2 | None
    SATURDAY: OpeningHoursTimespansV2 | None
    SUNDAY: OpeningHoursTimespansV2 | None

    model_config = pydantic_v2.ConfigDict(extra="forbid")
