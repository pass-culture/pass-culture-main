from datetime import datetime
import enum
from functools import singledispatch

from psycopg2._range import DateTimeRange
import sqlalchemy

from pcapi.utils.date import format_into_utc_date


@singledispatch
def serialize(value, column=None):  # type: ignore [no-untyped-def]
    return value


@serialize.register(sqlalchemy.Enum)
def _(value, column=None):  # type: ignore [no-untyped-def]
    return value.name


@serialize.register(enum.Enum)
def _(value, column=None):  # type: ignore [no-untyped-def]
    return value.value


@serialize.register(datetime)
def _(value, column=None):  # type: ignore [no-untyped-def]
    return format_into_utc_date(value)


@serialize.register(DateTimeRange)
def _(value, column=None):  # type: ignore [no-untyped-def]
    return {"start": value.lower, "end": value.upper}


@serialize.register(bytes)
def _(value, column=None):  # type: ignore [no-untyped-def]
    return list(value)


@serialize.register(list)
def _(value, column=None):  # type: ignore [no-untyped-def]
    return [serialize(d) for d in value]
