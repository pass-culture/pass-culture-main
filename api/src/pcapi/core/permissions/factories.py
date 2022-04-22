import factory

from pcapi.core.permissions import models as perm_models
from pcapi.core.permissions.models import Permission
from pcapi.core.testing import BaseFactory


class PermissionFactory(BaseFactory):
    class Meta:
        model = perm_models.Permission

    name = factory.Sequence(lambda n: f"permission #{n:04}")
    category = None


class RoleFactory(BaseFactory):
    class Meta:
        model = perm_models.Role

    name: str = factory.Sequence(lambda n: f"role #{n:04}")
    permissions: list[Permission] = []
