import sqlalchemy
from sqlalchemy import CHAR
from sqlalchemy import Float
from sqlalchemy import Integer
from sqlalchemy import String

from pcapi.models import Model
from pcapi.models.api_errors import ApiErrors


def validate_generic(model: Model) -> ApiErrors:  # type: ignore [valid-type]
    api_errors = ApiErrors()
    columns = model.__mapper__.column_attrs  # type: ignore [attr-defined]

    for key in columns.keys():
        if key.startswith("_sa_"):
            continue

        column = columns[key]
        value = getattr(model, key)

        if (  # pylint: disable=too-many-boolean-expressions
            not getattr(column.expression, "nullable", False)
            and not column.expression.foreign_keys
            and not column.expression.primary_key
            and getattr(column.expression, "default", ...) is None
            and getattr(column.expression, "server_default", ...) is None
            and value is None
        ):
            api_errors.add_error(key, "Cette information est obligatoire")

        if value is None:
            continue

        if (
            isinstance(column.expression.type, (String, CHAR))
            and not isinstance(column.expression.type, sqlalchemy.Enum)
            and not isinstance(value, str)
        ):
            api_errors.add_error(key, "doit être une chaîne de caractères")

        if (
            isinstance(column.expression.type, (String, CHAR))
            and isinstance(value, str)
            and column.expression.type.length
            and len(value) > column.expression.type.length
        ):
            api_errors.add_error(key, f"Vous devez saisir moins de {str(column.expression.type.length)} caractères")

        if isinstance(column.expression.type, Integer) and not isinstance(value, int):
            api_errors.add_error(key, "doit être un entier")

        if isinstance(column.expression.type, Float) and not isinstance(value, float):
            api_errors.add_error(key, "doit être un nombre")

    return api_errors
