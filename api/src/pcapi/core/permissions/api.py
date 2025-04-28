import typing

from sqlalchemy.orm import joinedload

from pcapi.core.history import api as history_api
from pcapi.core.history import models as history_models
from pcapi.core.permissions import models as perm_models
from pcapi.core.users import models as users_models
from pcapi.models import db


def raise_error_on_empty_role_name(name: str) -> None:
    if not name:
        raise ValueError("Role name cannot be empty")


def list_roles() -> list[perm_models.Role]:
    roles = db.session.query(perm_models.Role).options(joinedload(perm_models.Role.permissions)).all()
    return roles


def list_permissions() -> list[perm_models.Permission]:
    permissions = db.session.query(perm_models.Permission).all()
    return permissions


def update_role(
    id_: int, name: str, permission_ids: typing.Iterable[int], author: users_models.User, comment: str
) -> perm_models.Role:
    raise_error_on_empty_role_name(name)

    permissions = db.session.query(perm_models.Permission).filter(perm_models.Permission.id.in_(permission_ids)).all()
    role = db.session.query(perm_models.Role).filter_by(id=id_).one()

    added_roles = set(permissions) - set(role.permissions)
    removed_roles = set(role.permissions) - set(permissions)
    if not (added_roles or removed_roles):
        return role

    modified_info = {}
    for permission in added_roles:
        modified_info[permission.name] = {"old_info": False, "new_info": True}
    for permission in removed_roles:
        modified_info[permission.name] = {"old_info": True, "new_info": False}

    role.name = name
    role.permissions = permissions
    db.session.flush()

    history_api.add_action(
        history_models.ActionType.ROLE_PERMISSIONS_CHANGED,
        author=author,
        comment=comment,
        role_name=role.name,
        modified_info=modified_info,
    )

    return role


def get_concrete_roles(roles: typing.Collection[perm_models.Roles]) -> typing.Collection[perm_models.Role]:
    names = [role.value for role in roles]
    return db.session.query(perm_models.Role).filter(perm_models.Role.name.in_(names)).all()


def create_backoffice_profile(user: users_models.User, roles: list[perm_models.Role] | None = None) -> None:
    backoffice_profile = perm_models.BackOfficeUserProfile(user=user, roles=roles or [])
    db.session.add(backoffice_profile)
    user.backoffice_profile = backoffice_profile
