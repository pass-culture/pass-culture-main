import factory

from pcapi.core.factories import BaseFactory
from pcapi.core.permissions import models as perm_models
from pcapi.core.permissions.models import Permission


class PermissionFactory(BaseFactory):
    class Meta:
        model = perm_models.Permission

    name = factory.Sequence(lambda n: f"permission #{n:04}")
    category: str | None = None


class RoleFactory(BaseFactory):
    class Meta:
        model = perm_models.Role

    name = factory.Sequence(lambda n: f"role #{n:04}")
    permissions: list[Permission] = []


class RolePermissionFactory(BaseFactory):
    class Meta:
        model = perm_models.RolePermission


class BackOfficeUserProfileFactory(BaseFactory):
    class Meta:
        model = perm_models.BackOfficeUserProfile

    user = factory.SubFactory("pcapi.core.users.factories.AdminFactory")
