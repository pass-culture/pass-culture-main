from datetime import datetime
import enum
from functools import singledispatch
from typing import Any

from psycopg2._range import DateTimeRange
import sqlalchemy
from sqlalchemy import Integer

from pcapi.utils.date import DateTimes
from pcapi.utils.date import format_into_utc_date
from pcapi.utils.human_ids import humanize


@singledispatch
def serialize(value, column=None):  # type: ignore [no-untyped-def]
    return value


@serialize.register(int)
def _(value: Any, column: sqlalchemy.orm.properties.ColumnProperty | None = None):  # type: ignore [no-untyped-def]
    if column is not None and isinstance(column.expression.type, Integer) and column.key.lower().endswith("id"):
        return humanize(value)

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


@serialize.register(DateTimes)
def _(value, column=None):  # type: ignore [no-untyped-def]
    return [format_into_utc_date(v) for v in value.datetimes]
