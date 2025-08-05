import logging
import typing
from contextlib import contextmanager

from sqlalchemy.exc import DataError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.exc import InternalError

from pcapi.models import Model
from pcapi.models import db
from pcapi.models.api_errors import ApiErrors
from pcapi.models.pc_object import PcObject
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


# DEPRECATED in favor of @atomic() and db.session.delete because committing or
# rollbacking should be done by a transaction context manager, not manually
def delete(*models: Model) -> None:
    for model in models:
        db.session.delete(model)
    if is_managed_transaction():
        db.session.flush()
    else:
        db.session.commit()


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


# DEPRECATED in favor of @atomic() and db.session.add because committing or
# rollbacking should be done by a transaction context manager, not manually
def save(*models: Model, commit: bool = True) -> None:
    add_to_session(*models)

    if not commit:
        return None

    api_errors = ApiErrors()
    try:
        if is_managed_transaction():
            db.session.flush()
        else:
            db.session.commit()
    except DataError as data_error:
        logger.exception("Error in repository.save: %s", data_error, extra={"models": models})
        api_errors.add_error(*models[0].restize_data_error(data_error))
        if is_managed_transaction():
            mark_transaction_as_invalid()
        else:
            db.session.rollback()
        raise api_errors
    except IntegrityError as integrity_error:
        logger.exception("Error in repository.save: %s", integrity_error, extra={"models": models})
        api_errors.add_error(*models[0].restize_integrity_error(integrity_error))
        if is_managed_transaction():
            mark_transaction_as_invalid()
        else:
            db.session.rollback()
        raise api_errors
    except InternalError as internal_error:
        logger.exception("Error in repository.save: %s", internal_error, extra={"models": models})
        api_errors.add_error(*models[0].restize_internal_error(internal_error))
        if is_managed_transaction():
            mark_transaction_as_invalid()
        else:
            db.session.rollback()
        raise api_errors
    except TypeError as type_error:
        logger.exception("Error in repository.save: %s", type_error, extra={"models": models})
        api_errors.add_error(*PcObject.restize_type_error(type_error))
        if is_managed_transaction():
            mark_transaction_as_invalid()
        else:
            db.session.rollback()
        raise api_errors
    except ValueError as value_error:
        logger.exception("Error in repository.save: %s", value_error, extra={"models": models})
        api_errors.add_error(*PcObject.restize_value_error(value_error))
        if is_managed_transaction():
            mark_transaction_as_invalid()
        else:
            db.session.rollback()
        raise api_errors

    if api_errors.errors.keys():
        raise api_errors

    return None
