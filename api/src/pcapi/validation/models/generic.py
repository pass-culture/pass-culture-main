import sqlalchemy as sa
from sqlalchemy.sql.elements import Label

from pcapi.models import Model
from pcapi.models.api_errors import ApiErrors


def validate_generic(model: Model) -> ApiErrors:
    api_errors = ApiErrors()
    columns = model.__mapper__.column_attrs

    for key in columns.keys():
        if key.startswith("_sa_"):
            continue
        if isinstance(columns[key].expression, Label):
            # Not a Column.
            # Mapped column using `query_expression` filled
            # at runtime during a query.
            # Nothing to validate as it's not part of the table and
            # there is nothing to commit regarding it.
            # If we go further we could it an `InvalidRequestError`
            # trying to access it if it wasn't define in this context
            continue

        column = columns[key]
        value = getattr(model, key)

        if (
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
            isinstance(column.expression.type, (sa.String, sa.CHAR))
            and not isinstance(column.expression.type, sa.Enum)
            and not isinstance(value, str)
        ):
            api_errors.add_error(key, "doit être une chaîne de caractères")

        if (
            isinstance(column.expression.type, (sa.String, sa.CHAR))
            and isinstance(value, str)
            and column.expression.type.length
            and len(value) > column.expression.type.length
        ):
            api_errors.add_error(key, f"Vous devez saisir moins de {str(column.expression.type.length)} caractères")

        if isinstance(column.expression.type, sa.Integer) and not isinstance(value, int):
            api_errors.add_error(key, "doit être un entier")

        if isinstance(column.expression.type, sa.Float) and not isinstance(value, float):
            api_errors.add_error(key, "doit être un nombre")

    return api_errors
