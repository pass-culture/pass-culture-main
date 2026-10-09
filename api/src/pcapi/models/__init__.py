import functools
import json
import typing

import flask_sqlalchemy
import pydantic as pydantic_v2
import pydantic.v1 as pydantic_v1
from pydantic_core import to_jsonable_python
from sqlalchemy.orm import DeclarativeBase

from pcapi import settings


DATABASE_ALLOWED_SSLMODES = ["disable", "allow", "prefer", "require", "verify-ca", "verify-full"]


def install_models() -> None:
    """Let SQLAlchemy know about our database models."""

    import pcapi.core.achievements.models
    import pcapi.core.artist.models
    import pcapi.core.bookings.models
    import pcapi.core.criteria.models
    import pcapi.core.cultural_outreach.models
    import pcapi.core.educational.models
    import pcapi.core.favorites.models
    import pcapi.core.finance.models
    import pcapi.core.fraud.models
    import pcapi.core.geography.models
    import pcapi.core.highlights.models
    import pcapi.core.history.models
    import pcapi.core.mails.models
    import pcapi.core.offerers.models
    import pcapi.core.offers.models
    import pcapi.core.operations.models
    import pcapi.core.permissions.models
    import pcapi.core.providers.models
    import pcapi.core.reactions.models
    import pcapi.core.reference.models
    import pcapi.core.reminders.models
    import pcapi.core.subscription.models
    import pcapi.core.users.models
    import pcapi.models.beneficiary_import
    import pcapi.models.beneficiary_import_status
    import pcapi.models.feature


def json_serializer(obj: typing.Any) -> str:
    if isinstance(obj, pydantic_v2.BaseModel):
        return to_jsonable_python(obj)
    else:
        # TODO(pydantic_v1): remove the pydantic v1 JSON encoder
        return pydantic_v1.json.pydantic_encoder(obj)


def check_database_ssl_settings() -> None:
    """Raise a ValueError if the database SSL settings are inconsistent."""
    ssl_mode = settings.DATABASE_SSLMODE

    if not ssl_mode:
        return

    if ssl_mode not in DATABASE_ALLOWED_SSLMODES:
        raise ValueError(f"Invalid DATABASE_SSLMODE: {ssl_mode}. Allowed values are: {', '.join(DATABASE_ALLOWED_SSLMODES)}")

    if ssl_mode in ("verify-ca", "verify-full"):
        for name in ("DATABASE_SSLROOTCERT", "DATABASE_SSLCERT", "DATABASE_SSLKEY"):
            if not getattr(settings, name):
                raise ValueError(f"DATABASE_SSLMODE is {ssl_mode} but environment variable with name `{name}` is not set.")


def get_db_connection_args(options: list[str]) -> dict[str, str]:
    """Build psycopg connection arguments from `-c` options and SSL settings."""
    connect_args: dict[str, str] = {}
    if options:
        connect_args["options"] = " ".join(options)
    if settings.DATABASE_SSLMODE:
        connect_args["sslmode"] = settings.DATABASE_SSLMODE
    if settings.DATABASE_SSLROOTCERT:
        connect_args["sslrootcert"] = settings.DATABASE_SSLROOTCERT
    if settings.DATABASE_SSLCERT:
        connect_args["sslcert"] = settings.DATABASE_SSLCERT
    if settings.DATABASE_SSLKEY:
        connect_args["sslkey"] = settings.DATABASE_SSLKEY
    return connect_args


check_database_ssl_settings()


_engine_options = {
    "json_serializer": functools.partial(json.dumps, default=json_serializer),
    "pool_size": settings.DATABASE_POOL_SIZE,
}

_db_options = []
if settings.DATABASE_LOCK_TIMEOUT:
    _db_options.append("-c lock_timeout=%i" % settings.DATABASE_LOCK_TIMEOUT)
if settings.DATABASE_STATEMENT_TIMEOUT:
    _db_options.append("-c statement_timeout=%i" % settings.DATABASE_STATEMENT_TIMEOUT)
if settings.DATABASE_IDLE_IN_TRANSACTION_SESSION_TIMEOUT:
    _db_options.append(
        "-c idle_in_transaction_session_timeout=%i" % settings.DATABASE_IDLE_IN_TRANSACTION_SESSION_TIMEOUT
    )

_connection_args = get_db_connection_args(_db_options)
if _connection_args:
    _engine_options["connect_args"] = _connection_args


class Base(DeclarativeBase):
    pass


db = flask_sqlalchemy.SQLAlchemy(engine_options=_engine_options, model_class=Base)

# db.Model is not mypy-compliant ("Variable is not valid as a type" error)
# we define a custom typing to reflect the flask-sqlalchemy logic
if typing.TYPE_CHECKING:
    from flask_sqlalchemy.model import Model as FSQLAModel

    class Model(FSQLAModel, Base):
        pass
else:
    Model = db.Model
