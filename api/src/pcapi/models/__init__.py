import functools
import json

from flask_sqlalchemy import SQLAlchemy
import pydantic.json

from pcapi import settings


def install_models() -> None:
    """Let SQLAlchemy know about our database models."""
    # pylint: disable=unused-import
    import pcapi.core.bookings.models
    import pcapi.core.educational.models
    import pcapi.core.finance.models
    import pcapi.core.fraud.models
    import pcapi.core.mails.models
    import pcapi.core.offerers.models
    import pcapi.core.offers.models
    import pcapi.core.payments.models
    import pcapi.core.providers.models
    import pcapi.core.reference.models
    import pcapi.core.subscription.models
    import pcapi.core.users.models
    import pcapi.models.bank_information
    import pcapi.models.beneficiary_import
    import pcapi.models.beneficiary_import_status
    import pcapi.models.criterion
    import pcapi.models.feature
    import pcapi.models.local_provider_event
    import pcapi.models.offer_criterion
    import pcapi.models.payment
    import pcapi.models.payment_message
    import pcapi.models.payment_status
    import pcapi.models.product
    import pcapi.models.user_offerer
    import pcapi.models.user_session


_engine_options = {
    "json_serializer": functools.partial(json.dumps, default=pydantic.json.pydantic_encoder),
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

db = SQLAlchemy(engine_options=_engine_options)
Model = db.Model
