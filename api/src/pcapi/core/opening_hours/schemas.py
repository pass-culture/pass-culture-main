import datetime

import pydantic
import typing
import pydantic.types as pydantic_types
from pydantic.v1 import ConstrainedList
from pydantic.v1 import ConstrainedStr
from pydantic.v1 import validator

from pcapi.routes.serialization import BaseModel
from pcapi.routes.serialization import HttpBodyModel


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

"""defines a time string that matches the HH:MM format"""
HourV2 = pydantic_types.constr(strict=True, strip_whitespace=True, pattern=r"^(([0-1][0-9])|(2[0-3])):[0-5][0-9]$")

# defines start and end opening hours
# eg. ["10:00", "18:00"] (from 10:00 to 18:00)
OpeningHoursV2 = pydantic_types.conlist(item_type=HourV2, min_length=2, max_length=2, unique_items=True)


# defines a whole day's opening hours
# eg. [["10:00", "13:00"], ["14:00", "18:00"]]
OpeningHoursTimespansV2 = pydantic_types.conlist(
    item_type=OpeningHoursV2, min_length = 1, max_length = 2, unique_items = True
)


def validate_timespans(timespans: OpeningHoursTimespans|typing.Annotated[list[list[str]], OpeningHoursTimespansV2] | None) -> OpeningHoursTimespans | typing.Annotated[list[list[str]], OpeningHoursTimespansV2]|None:
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


class WeekdayOpeningHoursTimespansV2(HttpBodyModel):
    MONDAY: typing.Annotated[list[list[str]], OpeningHoursTimespansV2, pydantic.AfterValidator(validate_timespans)] | None
    TUESDAY: typing.Annotated[list[list[str]], OpeningHoursTimespansV2, pydantic.AfterValidator(validate_timespans)] | None
    WEDNESDAY: typing.Annotated[list[list[str]], OpeningHoursTimespansV2, pydantic.AfterValidator(validate_timespans)] | None
    THURSDAY: typing.Annotated[list[list[str]], OpeningHoursTimespansV2, pydantic.AfterValidator(validate_timespans)] | None
    FRIDAY: typing.Annotated[list[list[str]], OpeningHoursTimespansV2, pydantic.AfterValidator(validate_timespans)] | None
    SATURDAY: typing.Annotated[list[list[str]], OpeningHoursTimespansV2, pydantic.AfterValidator(validate_timespans)] | None
    SUNDAY: typing.Annotated[list[list[str]], OpeningHoursTimespansV2, pydantic.AfterValidator(validate_timespans)] | None
