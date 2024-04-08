from sqlalchemy import Boolean
from sqlalchemy import func
from sqlalchemy.sql.elements import ColumnElement
from sqlalchemy.sql.functions import Function

from pcapi.core.users.models import User


def find_pro_users_by_email_provider(email_provider: str) -> list[User]:
    formatted_email_provider = f"%@{email_provider}"
    return (
        User.query.filter_by(is_beneficiary=False, isActive=True)
        .filter(User.UserOfferers.any())
        .filter(func.lower(User.email).like(func.lower(formatted_email_provider)))
        .all()
    )


def matching(column: str, search_value: str) -> ColumnElement[Boolean]:
    return _sanitized_string(column) == _sanitized_string(search_value)


def _sanitized_string(value: str) -> Function:
    sanitized = func.replace(value, "-", "")
    sanitized = func.replace(sanitized, " ", "")
    sanitized = func.unaccent(sanitized)
    sanitized = func.lower(sanitized)
    return sanitized
