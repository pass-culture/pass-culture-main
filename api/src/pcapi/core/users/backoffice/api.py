import typing

import sqlalchemy.orm as sa_orm

from pcapi.core.permissions import api as perm_api
from pcapi.core.permissions import models as perm_models
from pcapi.core.users import models
from pcapi.models import db


def upsert_roles(
    user: models.User, roles: typing.Collection[perm_models.Roles]
) -> perm_models.BackOfficeUserProfile | None:
    if not user.backoffice_profile:
        perm_api.create_backoffice_profile(user)

    if not user.backoffice_profile.roles:
        user.backoffice_profile.roles = []

    concrete_roles = perm_api.get_concrete_roles(roles)
    user.backoffice_profile.roles = concrete_roles

    return user.backoffice_profile


def fetch_user_with_profile(user_id: int) -> models.User | None:
    return (
        db.session.query(models.User)
        .filter_by(id=user_id)
        .options(
            sa_orm.joinedload(models.User.backoffice_profile)
            .joinedload(perm_models.BackOfficeUserProfile.roles)
            .joinedload(perm_models.Role.permissions)
        )
        .options(
            sa_orm.load_only(
                models.User.id, models.User.email, models.User.firstName, models.User.lastName, models.User.roles
            )
        )
        .one_or_none()
    )
