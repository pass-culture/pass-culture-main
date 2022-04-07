from sqlalchemy.exc import DataError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.exc import InternalError

from pcapi.models import Model
from pcapi.models import db
from pcapi.models.api_errors import ApiErrors
from pcapi.models.pc_object import PcObject
from pcapi.validation.models import entity_validator


def delete(*models: Model) -> None:  # type: ignore [valid-type]
    for model in models:
        db.session.delete(model)
    db.session.commit()


def save(*models: Model) -> None:  # type: ignore [valid-type]
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
        api_errors.add_error(*models[0].restize_data_error(data_error))  # type: ignore [attr-defined]
        db.session.rollback()
        raise api_errors
    except IntegrityError as integrity_error:
        api_errors.add_error(*models[0].restize_integrity_error(integrity_error))  # type: ignore [attr-defined]
        db.session.rollback()
        raise api_errors
    except InternalError as internal_error:
        api_errors.add_error(*models[0].restize_internal_error(internal_error))  # type: ignore [attr-defined]
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

    return None
