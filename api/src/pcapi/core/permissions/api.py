import typing

from sqlalchemy.orm import joinedload

from pcapi.core.permissions import models as perm_models
from pcapi.repository import repository


def raise_error_on_empty_role_name(name: str) -> None:
    if not name:
        raise ValueError("Role name cannot be empty")


def list_roles() -> list[perm_models.Role]:
    roles = perm_models.Role.query.options(joinedload(perm_models.Role.permissions)).all()
    return roles


def list_permissions() -> list[perm_models.Permission]:
    permissions = perm_models.Permission.query.all()
    return permissions


def create_role(name: str, permission_ids: typing.Iterable[int]) -> perm_models.Role:
    raise_error_on_empty_role_name(name)
    permissions = perm_models.Permission.query.filter(perm_models.Permission.id.in_(permission_ids))
    role = perm_models.Role(name=name, permissions=permissions.all())
    repository.save(role)
    return role


def update_role(id_: int, name: str, permission_ids: typing.Iterable[int]) -> perm_models.Role:
    raise_error_on_empty_role_name(name)
    permissions = perm_models.Permission.query.filter(perm_models.Permission.id.in_(permission_ids))
    role = perm_models.Role.query.get(id_)
    role.name = name
    role.permissions = permissions.all()
    repository.save(role)
    return role


def delete_role(id_: int) -> tuple[int, str, list[perm_models.Permission]]:
    role = perm_models.Role.query.get(id_)
    role_id, role_name, role_permission = role.id, role.name, role.permissions
    if role.name == "admin":
        raise ValueError("Cannot delete admin role")
    role.permissions = []
    repository.delete(role)
    return role_id, role_name, role_permission
