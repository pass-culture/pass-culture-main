from datetime import datetime
import enum
from functools import singledispatch
import typing

from psycopg2._range import DateTimeRange
import sqlalchemy

from pcapi.utils.date import format_into_utc_date


@singledispatch
def serialize(value: typing.Any, column: typing.Any = None) -> typing.Any:
    return value


@serialize.register(sqlalchemy.Enum)
def _(value: sqlalchemy.Enum, column: typing.Any = None) -> str:
    return value.name


@serialize.register(enum.Enum)
def _(value: enum.Enum, column: typing.Any = None) -> str:
    return value.value


@serialize.register(datetime)
def _(value: datetime, column: typing.Any = None) -> str:
    return format_into_utc_date(value)


@serialize.register(DateTimeRange)
def _(value: DateTimeRange, column: typing.Any = None) -> dict[str, str]:
    return {"start": value.lower, "end": value.upper}


@serialize.register(bytes)
def _(value: bytes, column: typing.Any = None) -> list:
    return list(value)


@serialize.register(list)
def _(value: list, column: typing.Any = None) -> list:
    return [serialize(d) for d in value]
