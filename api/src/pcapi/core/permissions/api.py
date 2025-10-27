import typing

from pcapi.core.history import api as history_api
from pcapi.core.history import models as history_models
from pcapi.core.permissions import models as perm_models
from pcapi.core.users import models as users_models
from pcapi.models import db


def update_role(
    id_: int, name: str, permission_ids: typing.Iterable[int], author: users_models.User, comment: str
) -> perm_models.Role:
    if not name:
        raise ValueError("Role name cannot be empty")

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


def create_backoffice_profile(user: users_models.User, roles: list[perm_models.Role] | None = None) -> None:
    backoffice_profile = perm_models.BackOfficeUserProfile(user=user, roles=roles or [])
    db.session.add(backoffice_profile)
    user.backoffice_profile = backoffice_profile
