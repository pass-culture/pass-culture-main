import sqlalchemy as sa
from sqlalchemy.sql.elements import ColumnElement
from sqlalchemy.sql.functions import Function

from pcapi.core.users.models import User
from pcapi.models import db


def find_pro_users_by_email_provider(email_provider: str) -> list[User]:
    formatted_email_provider = f"%@{email_provider}"
    return (
        db.session.query(User)
        .filter_by(is_beneficiary=False, isActive=True)
        .filter(User.UserOfferers.any())
        .filter(sa.func.lower(User.email).like(sa.func.lower(formatted_email_provider)))
        .all()
    )


def matching(column: str, search_value: str) -> ColumnElement[sa.Boolean]:
    return _sanitized_string(column) == _sanitized_string(search_value)


def _sanitized_string(value: str) -> Function:
    sanitized = sa.func.replace(value, "-", "")
    sanitized = sa.func.replace(sanitized, " ", "")
    sanitized = sa.func.unaccent(sanitized)
    sanitized = sa.func.lower(sanitized)
    return sanitized
