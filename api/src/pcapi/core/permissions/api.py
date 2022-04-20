from sqlalchemy.orm import joinedload

from pcapi.core.permissions.models import Role


def list_roles() -> list[Role]:
    roles = Role.query.options(joinedload(Role.permissions)).all()
    return roles
