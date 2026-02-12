import logging
import typing
from contextlib import contextmanager

from pcapi.models import Model
from pcapi.models import db
from pcapi.models.api_errors import ApiErrors
from pcapi.utils.transaction_manager import atomic
from pcapi.utils.transaction_manager import is_managed_transaction
from pcapi.utils.transaction_manager import mark_transaction_as_invalid
from pcapi.validation.models import entity_validator


logger = logging.getLogger(__name__)


# DEPRECATED in favor of @atomic() because @transaction() is not reentrant
@contextmanager
def transaction() -> typing.Iterator[None]:
    if is_managed_transaction():
        with atomic():
            yield
    else:
        try:
            yield
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise


# DEPRECATED in favor of @atomic() and db.session.add because committing or
# rollbacking should be done by a transaction context manager, not manually
def add_to_session(*models: Model) -> None:
    """Validate models and add them to session."""
    if not models:
        return

    api_errors = ApiErrors()
    for model in models:
        with db.session.no_autoflush:
            model_api_errors = entity_validator.validate(model)
        if model_api_errors.errors.keys():
            api_errors.errors.update(model_api_errors.errors)
        else:
            db.session.add(model)

    if api_errors.errors.keys():
        if is_managed_transaction():
            # not a real rollback but the decorator/context manager will rollback instead of commit
            mark_transaction_as_invalid()
        else:
            db.session.rollback()
        raise api_errors
