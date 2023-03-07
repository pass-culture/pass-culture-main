import datetime
import enum
import hashlib
import json
import typing

import psycopg2.extras
import pytz
import sqlalchemy as sqla
import sqlalchemy.engine as sqla_engine
import sqlalchemy.types as sqla_types

from pcapi.models import Model
from pcapi.models import db


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

         class Wall(Base, Model):
             color = sqla.Column(MagicEnum(Color))

         wall = Wall(color=Color.RED)  # not `Color.RED.value`
         wall = Wall.query.first()
         assert wall.color == Color.RED  # again, not `Color.RED.value`
    """

    cache_ok = True

    def __init__(self, enum_class: typing.Type[enum.Enum]):  # pylint: disable=super-init-not-called
        # WARNING: The attribute MUST have the same name as the
        # argument in `__init__()` for SQLAlchemy to produce a valid
        # cache key. See https://docs.sqlalchemy.org/en/14/core/type_api.html#sqlalchemy.types.ExternalType.cache_ok
        self.enum_class = enum_class
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
    def python_type(self) -> typing.Type[enum.Enum]:
        return self.enum_class

    def copy(self, **kwargs: typing.Any) -> "MagicEnum":
        return self.__class__(self.enum_class)

    def process_bind_param(
        self,
        value: typing.Any,
        dialect: sqla_engine.Dialect,
    ) -> str | None:
        if value is None:
            return None
        return value.value

    def process_result_value(
        self,
        value: typing.Any,
        dialect: sqla_engine.Dialect,
    ) -> enum.Enum | None:
        if value is None:
            return None
        return self.enum_class(value)


def make_timerange(
    start: datetime.datetime,
    end: datetime.datetime | None = None,
    bounds: str = "[)",
) -> psycopg2.extras.DateTimeRange:
    return psycopg2.extras.DateTimeRange(
        lower=start.astimezone(pytz.utc).isoformat(),
        upper=end.astimezone(pytz.utc).isoformat() if end else None,
        bounds=bounds,
    )


class BadSortError(Exception):
    pass


def get_ordering_clauses(
    model: typing.Type[Model],
    sorts: typing.Iterable[str],
) -> list[sqla.sql.elements.ColumnElement | sqla.sql.elements.UnaryExpression]:
    """
    `sorts` should contains string in the form of:
    - an optional `-` prefix specifying a sort descending direction (ascending by default)
    - the name of a `model`'s attribute

    example:
    - "-city" for the `model.city` field in descending order
    - "email" for the `model.email` field in ascending order
    """
    ordering_clauses = []
    bad_sorts = []
    for sort in sorts:
        *desc, field_name = sort.split("-")
        try:
            field = getattr(model, field_name)
        except AttributeError:
            bad_sorts.append(
                (
                    sort,
                    f"model `{model.__name__}` does not have a `{field_name}` attribute",
                )
            )
        else:
            if desc:
                field = field.desc()
            ordering_clauses.append(field)

    if bad_sorts:
        raise BadSortError("bad sort provided: " ", ".join((f"{sort}: {message}" for sort, message in bad_sorts)))

    return ordering_clauses


def get_ordering_clauses_from_json(
    model: typing.Type[Model],
    sorts: str,
) -> list[sqla.sql.ColumnElement | sqla.sql.expression.UnaryExpression]:  # type: ignore [name-defined]
    """
    `sorts` should contain a JSON string specifying a list of dicts containing the following keys:
    - field: the name of a field
    - order: `asc` or `desc` (optional, `asc` by default)

    example:
    - [{"field": "city", "order", "desc"}] for the `model.city` field in descending order
    - [{"field": "email"}] for the `model.email` field in ascending order
    """
    try:
        parsed_sorts = json.loads(sorts)
    except json.JSONDecodeError:
        raise BadSortError("bad sort provided: invalid JSON")

    ordering_clauses = []
    bad_sorts = []
    for sort in parsed_sorts:
        try:
            field_name = sort["field"]
        except KeyError:
            bad_sorts.append("a sort clause is missing the 'field' key")
            continue
        except TypeError:
            bad_sorts.append("bad sort format")
            continue
        else:
            try:
                field = getattr(model, field_name)
            except AttributeError:
                bad_sorts.append(f"model `{model.__name__}` does not have a `{field_name}` attribute")
            else:
                if sort.get("order", "asc") == "desc":
                    field = field.desc()
                ordering_clauses.append(field)

    if bad_sorts:
        raise BadSortError("bad sort provided: " ", ".join((f"{message}" for message in bad_sorts)))

    return ordering_clauses


def acquire_lock(name: str) -> None:
    """Acquire an "advisory xact lock".

    IMPORTANT: This must only be used within a transaction.

    IMPORTANT: Callers should use a specific name for their lock.
    Simply using a stringified object id (such as "1234") is not
    specific enough: other callers could do the same for a different
    object that has the same id. Using a prefixed id is required, for
    example "pricing-point-1234".

    The lock is automatically released at the end of the transaction.
    """
    # We want a numeric lock identifier. Using `pricing_point_id`
    # would not be unique enough, so we add a prefix, hash the
    # resulting string, keep only the first 14 characters to avoid
    # collisions (and still stay within the range of PostgreSQL big
    # int type), and turn it back into an integer.
    lock_bytestring = name.encode()
    lock_id = int(hashlib.sha256(lock_bytestring).hexdigest()[:14], 16)
    db.session.execute(sqla.select([sqla.func.pg_advisory_xact_lock(lock_id)]))
