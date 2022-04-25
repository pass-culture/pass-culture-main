from sqlalchemy.orm import joinedload

from pcapi.core.permissions.models import Permission
from pcapi.core.permissions.models import Role


def list_roles() -> list[Role]:
    roles = Role.query.options(joinedload(Role.permissions)).all()
    return roles


def list_permissions() -> list[Permission]:
    permissions = Permission.query.all()
    return permissions
