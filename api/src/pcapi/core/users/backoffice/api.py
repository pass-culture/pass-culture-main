import typing

from sqlalchemy import orm

from pcapi.core.permissions import api as perm_api
from pcapi.core.permissions import models as perm_models
from pcapi.core.users import models


def upsert_roles(
    user: models.User, roles: typing.Collection[perm_models.Roles]
) -> perm_models.BackOfficeUserProfile | None:
    if not user.backoffice_profile:
        user.backoffice_profile = perm_models.BackOfficeUserProfile(user=user)

    if not user.backoffice_profile.roles:
        user.backoffice_profile.roles = []

    current_roles = {perm_models.Roles.from_role(role) for role in user.backoffice_profile.roles}
    new_roles = current_roles | set(roles)
    concrete_roles = perm_api.get_concrete_roles(new_roles)

    user.backoffice_profile.roles = concrete_roles

    return user.backoffice_profile


def fetch_user_with_profile(user_id: int) -> models.User | None:
    return (
        models.User.query.filter_by(id=user_id)
        .options(
            orm.joinedload(models.User.backoffice_profile)
            .joinedload(perm_models.BackOfficeUserProfile.roles)
            .joinedload(perm_models.Role.permissions)
        )
        .options(orm.load_only(models.User.id, models.User.email))
        .one_or_none()
    )
