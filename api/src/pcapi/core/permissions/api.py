import typing

from sqlalchemy.orm import joinedload

from pcapi.core.permissions.models import Permission
from pcapi.core.permissions.models import Role
from pcapi.repository import repository


def list_roles() -> list[Role]:
    roles = Role.query.options(joinedload(Role.permissions)).all()
    return roles


def list_permissions() -> list[Permission]:
    permissions = Permission.query.all()
    return permissions


def create_role(name: str, permission_ids: typing.Iterable[int]) -> Role:
    if not name:
        raise ValueError("Role name cannot be empty")
    permissions = Permission.query.filter(Permission.id.in_(permission_ids))
    role = Role(name=name, permissions=permissions.all())
    repository.save(role)
    return role
