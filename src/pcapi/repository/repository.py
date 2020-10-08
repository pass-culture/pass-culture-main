from typing import List

from sqlalchemy.exc import DataError, IntegrityError, InternalError

from pcapi.models import (ApiErrors, PcObject)
from pcapi.models.db import Model, db
from pcapi.validation.models import entity_validator


def delete(*models: List[Model]) -> None:
    for model in models:
        db.session.delete(model)
    db.session.commit()


def save(*models: Model) -> None:
    if not models:
        return None

    api_errors = ApiErrors()
    for model in models:
        with db.session.no_autoflush:
            model_api_errors = entity_validator.validate(model)
        if model_api_errors.errors.keys():
            api_errors.errors.update(model_api_errors.errors)
        else:
            db.session.add(model)

    if api_errors.errors.keys():
        db.session.rollback()
        raise api_errors

    try:
        db.session.commit()
    except DataError as data_error:
        api_errors.add_error(*model.restize_data_error(data_error))
        db.session.rollback()
        raise api_errors
    except IntegrityError as integrity_error:
        api_errors.add_error(*model.restize_integrity_error(integrity_error))
        db.session.rollback()
        raise api_errors
    except InternalError as internal_error:
        api_errors.add_error(*model.restize_internal_error(internal_error))
        db.session.rollback()
        raise api_errors
    except TypeError as type_error:
        api_errors.add_error(*PcObject.restize_type_error(type_error))
        db.session.rollback()
        raise api_errors
    except ValueError as value_error:
        api_errors.add_error(*PcObject.restize_value_error(value_error))
        db.session.rollback()
        raise api_errors

    if api_errors.errors.keys():
        raise api_errors
