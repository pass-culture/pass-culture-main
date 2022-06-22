import datetime
import enum
import typing

import psycopg2.extras
import pytz
import sqlalchemy as sqla
import sqlalchemy.dialects.postgresql.json as sqla_json
import sqlalchemy.ext.mutable as sqla_mutable
import sqlalchemy.types as sqla_types

from pcapi.models import db


def get_batches(query, key, batch_size):  # type: ignore [no-untyped-def]
    """Return a list of queries to process the requested query by batches.

    It supposes that keys are evenly spread (i.e there are no gaps of
    varying size). Otherwise it will work but the batches will not be
    of the same size, which may lead to the very performance issues
    you are trying to avoid.

    WARNING: if your initial query is ordered in DESCending order, the
    returned batch queries will NOT be ordered correctly. You will
    have to reverse the order of the returned iterator.
    """
    sub = query.subquery()
    min_key, max_key = db.session.query(sqla.func.min(sub.c.id), sqla.func.max(sub.c.id)).one()

    if (min_key, max_key) == (None, None):
        return

    ranges = [(i, i + batch_size - 1) for i in range(min_key, max_key + 1, batch_size)]
    for start, end in ranges:
        yield query.filter(key.between(start, end))


class MagicEnum(sqla_types.TypeDecorator):
    """A column type that stores an instance of a Python Enum object as a
    string or integer (depending on the type of the enum).

    It automatically converts from/to the raw value (string or
    integer), which means that you always handle enums and never have
    to specify access to the ``value`` attribute.

    Usage:

         class Color(enum.Enum):
             RED = "red"
             BLUE = "blue"

         class Wall(Model):
             color = sqla.Column(MagicEnum(Color))

         wall = Wall(color=Color.RED)  # not `Color.RED.value`
         wall = Wall.query.first()
         assert wall.color == Color.RED  # again, not `Color.RED.value`
    """

    def __init__(self, enum_class):  # type: ignore [no-untyped-def] # pylint: disable=super-init-not-called
        self.enum = enum_class
        first_value = list(enum_class)[0].value
        if isinstance(first_value, str):
            self.impl = sqla_types.Text()
        elif isinstance(first_value, int):
            self.impl = sqla_types.Integer()
        else:
            raise ValueError(f"Unsupported type of value for {enum_class}")

    # Avoid pylint `abstract-method` warning. It's not actually required
    # to implement this method.
    process_literal_param = sqla_types.TypeDecorator.process_literal_param

    @property
    def python_type(self):  # type: ignore [no-untyped-def]
        return self.enum

    def copy(self):  # type: ignore [no-untyped-def]
        return self.__class__(self.enum)

    def process_bind_param(self, value, dialect) -> typing.Optional[str]:  # type: ignore [no-untyped-def]
        if value is None:
            return None
        return value.value

    def process_result_value(self, value, dialect) -> enum.Enum:  # type: ignore [no-untyped-def]
        if value is None:
            return None  # type: ignore [return-value]
        return self.enum(value)


SafeJsonB = sqla_mutable.MutableDict.as_mutable(sqla_json.JSONB)


def make_timerange(
    start: datetime.datetime,
    end: typing.Optional[datetime.datetime] = None,
    bounds: str = "[)",
) -> psycopg2.extras.DateTimeRange:
    return psycopg2.extras.DateTimeRange(
        lower=start.astimezone(pytz.utc).isoformat(),
        upper=end.astimezone(pytz.utc).isoformat() if end else None,
        bounds=bounds,
    )
