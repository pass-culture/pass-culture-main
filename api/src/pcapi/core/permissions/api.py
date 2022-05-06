import typing

from sqlalchemy.orm import joinedload

from pcapi.core.permissions.models import Permission
from pcapi.core.permissions.models import Role
from pcapi.models import db
from pcapi.repository import repository


def raise_error_on_empty_role_name(name: str) -> None:
    if not name:
        raise ValueError("Role name cannot be empty")


def list_roles() -> list[Role]:
    roles = Role.query.options(joinedload(Role.permissions)).all()
    return roles


def list_permissions() -> list[Permission]:
    permissions = Permission.query.all()
    return permissions


def create_role(name: str, permission_ids: typing.Iterable[int]) -> Role:
    raise_error_on_empty_role_name(name)
    permissions = Permission.query.filter(Permission.id.in_(permission_ids))
    role = Role(name=name, permissions=permissions.all())
    repository.save(role)
    return role


def update_role(id_: int, name: str, permission_ids: typing.Iterable[int]) -> Role:
    raise_error_on_empty_role_name(name)
    permissions = Permission.query.filter(Permission.id.in_(permission_ids))
    role = Role.query.get(id_)
    role.name = name
    role.permissions = permissions.all()
    repository.save(role)
    return role


def delete_role(id_: int) -> None:
    role = Role.query.get(id_)
    if role.name == "admin":
        raise ValueError("Cannot delete admin role")
    role.permissions = []
    repository.save()
    db.session.delete(role)
