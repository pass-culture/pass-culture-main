import abc
from collections.abc import Iterable
import typing

import pytest

from pcapi.core.permissions import factories as perm_factories
import pcapi.core.permissions.models as perm_models
from pcapi.core.users import factories as users_factories
import pcapi.core.users.models as users_models

from . import base


pytestmark = [
    pytest.mark.usefixtures("db_session"),
    pytest.mark.backoffice,
]


class UnauthorizedHelperBase(base.BaseHelper, metaclass=abc.ABCMeta):
    @property
    @abc.abstractmethod
    def needed_permission(self) -> perm_models.Permissions | typing.Iterable[perm_models.Permissions]:
        pass

    @abc.abstractmethod
    def test_missing_permission(self, client):
        pass

    @abc.abstractmethod
    def test_no_backoffice_profile(self, client):
        pass

    @abc.abstractmethod
    def test_not_logged_in(self, client):
        pass

    def setup_user(self) -> users_models.User:
        user = users_factories.UserFactory()

        in_permissions = (
            self.needed_permission if isinstance(self.needed_permission, Iterable) else {self.needed_permission}
        )

        # Create a unique test role which has all permissions but the one required
        perms_in_db = {perm.name: perm for perm in perm_models.Permission.query.all()}
        role = perm_factories.RoleFactory(
            permissions=[perms_in_db[perm.name] for perm in perm_models.Permissions if perm not in in_permissions]
        )

        user.backoffice_profile = perm_models.BackOfficeUserProfile(user=user, roles=[role])

        assert len(user.backoffice_profile.permissions) == len(perm_models.Permissions) - len(in_permissions)
        for perm in in_permissions:
            assert perm not in user.backoffice_profile.permissions

        return user
