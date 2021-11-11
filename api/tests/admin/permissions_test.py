from pcapi.admin import permissions
from pcapi.core.testing import override_settings
import pcapi.core.users.factories as users_factories


class HasPermissionTest:
    def _make_user(self, email, is_admin=True):
        return users_factories.UserFactory.build(email=email, isAdmin=is_admin)

    @override_settings(PERMISSIONS="")
    def test_empty_permission_list(self):
        user = self._make_user("jane@example.com")
        assert not permissions.has_permission(user, "unknown-permission")

    @override_settings(
        PERMISSIONS="\n".join(
            (
                "can-frobulate: jane@example.com",
                "can-durlingate: john@example.com",
                "can-tergonize: roger@example.com, jane@example.com",
            )
        )
    )
    def test_basics(self):
        jane = self._make_user("jane@example.com")
        john = self._make_user("john@example.com")
        roger = self._make_user("roger@example.com")
        assert permissions.has_permission(jane, "can-frobulate")
        assert not permissions.has_permission(john, "can-frobulate")
        assert not permissions.has_permission(jane, "can-durlingate")
        assert permissions.has_permission(john, "can-durlingate")
        assert permissions.has_permission(jane, "can-tergonize")
        assert not permissions.has_permission(john, "can-tergonize")
        assert permissions.has_permission(roger, "can-tergonize")

    @override_settings(PERMISSIONS="can-frobulate: *")
    def test_star(self):
        user = self._make_user("jane@example.com")
        assert permissions.has_permission(user, "can-frobulate")

    @override_settings(PERMISSIONS="can-frobulate: *")
    def test_admin_check(self):
        user = users_factories.UserFactory.build(isAdmin=False, email="jane@example.com")
        assert not permissions.has_permission(user, "can-frobulate")
