import typing

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

    names = [role.value for role in roles]
    concrete_roles = db.session.query(perm_models.Role).filter(perm_models.Role.name.in_(names)).all()
    user.backoffice_profile.roles = concrete_roles

    return user.backoffice_profile
