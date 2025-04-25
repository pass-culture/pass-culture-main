import abc
from collections.abc import Iterable
import typing

import pytest

from pcapi.core.permissions import api as perm_api
from pcapi.core.permissions import factories as perm_factories
from pcapi.core.permissions import models as perm_models
from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as users_models
from pcapi.models import db

from . import base


pytestmark = [
    pytest.mark.usefixtures("db_session"),
    pytest.mark.backoffice,
]


class AuthenticatedHelperBase(base.BaseHelper, metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def test_not_logged_in(self, client):
        pass


class UnauthorizedHelperBase(AuthenticatedHelperBase):
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

    def setup_user(self) -> users_models.User:
        user = users_factories.UserFactory()

        in_permissions = (
            self.needed_permission if isinstance(self.needed_permission, Iterable) else {self.needed_permission}
        )

        # Create a unique test role which has all permissions but the one required
        perms_in_db = {perm.name: perm for perm in db.session.query(perm_models.Permission).all()}
        role = perm_factories.RoleFactory(
            permissions=[perms_in_db[perm.name] for perm in perm_models.Permissions if perm not in in_permissions]
        )

        perm_api.create_backoffice_profile(user, roles=[role])

        assert len(user.backoffice_profile.permissions) == len(perm_models.Permissions) - len(in_permissions)
        for perm in in_permissions:
            assert perm not in user.backoffice_profile.permissions

        return user
