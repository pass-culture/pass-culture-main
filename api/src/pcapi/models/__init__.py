import functools
import json
import typing

import flask_sqlalchemy
import pydantic.v1 as pydantic_v1
from sqlalchemy.orm import declarative_base

from pcapi import settings


def install_models() -> None:
    """Let SQLAlchemy know about our database models."""

    import pcapi.core.achievements.models
    import pcapi.core.artist.models
    import pcapi.core.bookings.models
    import pcapi.core.criteria.models
    import pcapi.core.educational.models
    import pcapi.core.finance.models
    import pcapi.core.fraud.models
    import pcapi.core.geography.models
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


_engine_options = {
    "json_serializer": functools.partial(json.dumps, default=pydantic_v1.json.pydantic_encoder),
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
if _db_options:
    _engine_options["connect_args"] = {"options": " ".join(_db_options)}

Base = declarative_base()

db = flask_sqlalchemy.SQLAlchemy(engine_options=_engine_options)

# This is a workaround for a limitation of mypy.  Check if it's still
# necessary when we migrate to flask_sqlalchemy >= 3.0.1, which
# exports better typing.
if typing.TYPE_CHECKING:

    class Model(flask_sqlalchemy.Model):
        pass
else:
    Model = db.Model

# else:
#     import re
#     import threading
#
#     from sqlalchemy import create_engine
#     from sqlalchemy.orm import declarative_base
#     from sqlalchemy.schema import _get_table_key
#
#     thread_local = threading.local()
#
#     class DBClass:
#         """Compatibility class that mimic the one from flask_sqlalchemy"""
#
#         engine_key = "thread_engine"
#         session_key = "thread_session"
#
#         def __init__(self, engine_options: dict):
#             self.Model = declarative_base()
#             self.engine_options = dict(engine_options)
#
#             # TODO rpa 23/05/2025 remove pool_size from the configuration and hard set it to 1
#             self.engine_options["pool_size"] = 1
#
#         @property
#         def session(self) -> sa.orm.session.Session | None:
#             session = getattr(thread_local, self.session_key, None)
#             if session is None:
#                 session = None
#                 setattr(thread_local, self.session_key, session)
#             return session
#
#         @property
#         def engine(self):  # type: ignore[no-untyped-def]
#             engine = getattr(thread_local, self.engine_key, None)
#             if engine is None:
#                 engine = create_engine(settings.DATABASE_URL, **self.engine_options)
#                 setattr(thread_local, self.engine_key, engine)
#             return engine
#
#     db = DBClass(engine_options=_engine_options)  # type: ignore
#
# Model = db.Model  # type: ignore
