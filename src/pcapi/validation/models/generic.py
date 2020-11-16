import sqlalchemy
from sqlalchemy import CHAR
from sqlalchemy import Column
from sqlalchemy import Float
from sqlalchemy import Integer
from sqlalchemy import String

from pcapi.models import ApiErrors
from pcapi.models.db import Model


def validate_generic(model: Model) -> ApiErrors:
    api_errors = ApiErrors()
    columns = model.__class__.__table__.columns._data

    for key in columns.keys():
        column = columns[key]
        value = getattr(model, key)

        if not isinstance(column, Column):
            continue

        if (
            not column.nullable
            and not column.foreign_keys
            and not column.primary_key
            and column.default is None
            and column.server_default is None
            and value is None
        ):
            api_errors.add_error(key, "Cette information est obligatoire")

        if value is None:
            continue

        if (
            (isinstance(column.type, String) or isinstance(column.type, CHAR))
            and not isinstance(column.type, sqlalchemy.Enum)
            and not isinstance(value, str)
        ):
            api_errors.add_error(key, "doit être une chaîne de caractères")

        if (
            (isinstance(column.type, String) or isinstance(column.type, CHAR))
            and isinstance(value, str)
            and column.type.length
            and len(value) > column.type.length
        ):
            api_errors.add_error(key, f"Vous devez saisir moins de {str(column.type.length)} caractères")

        if isinstance(column.type, Integer) and not isinstance(value, int):
            api_errors.add_error(key, "doit être un entier")

        if isinstance(column.type, Float) and not isinstance(value, float):
            api_errors.add_error(key, "doit être un nombre")

    return api_errors
