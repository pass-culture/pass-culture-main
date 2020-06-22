import enum
from datetime import datetime
from functools import singledispatch

import sqlalchemy
from psycopg2._range import DateTimeRange
from sqlalchemy import Integer

from utils.date import DateTimes, format_into_utc_date
from utils.human_ids import humanize


@singledispatch
def serialize(value, column=None):
    return value


@serialize.register(int)
def _(value, column=None):
    if column is not None and isinstance(column.type, Integer) and column.key.lower().endswith('id'):
        return humanize(value)

    return value


@serialize.register(sqlalchemy.Enum)
def _(value, column=None):
    return value.name


@serialize.register(enum.Enum)
def _(value, column=None):
    return value.value


@serialize.register(datetime)
def _(value, column=None):
    return format_into_utc_date(value)


@serialize.register(DateTimeRange)
def _(value, column=None):
    return {'start': value.lower, 'end': value.upper}


@serialize.register(bytes)
def _(value, column=None):
    return list(value)


@serialize.register(list)
def _(value, column=None):
    return list(map(lambda d: serialize(d), value))


@serialize.register(DateTimes)
def _(value, column=None):
    return [format_into_utc_date(v) for v in value.datetimes]
