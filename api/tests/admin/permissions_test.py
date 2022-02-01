from pcapi.admin import permissions
from pcapi.core.testing import override_settings
import pcapi.core.users.factories as users_factories


class HasPermissionTest:
    @override_settings(PERMISSIONS="")
    def test_empty_permission_list(self):
        user = users_factories.AdminFactory.build(email="jane@example.com")
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
        jane = users_factories.AdminFactory.build(email="jane@example.com")
        john = users_factories.AdminFactory.build(email="john@example.com")
        roger = users_factories.AdminFactory.build(email="roger@example.com")
        assert permissions.has_permission(jane, "can-frobulate")
        assert not permissions.has_permission(john, "can-frobulate")
        assert not permissions.has_permission(jane, "can-durlingate")
        assert permissions.has_permission(john, "can-durlingate")
        assert permissions.has_permission(jane, "can-tergonize")
        assert not permissions.has_permission(john, "can-tergonize")
        assert permissions.has_permission(roger, "can-tergonize")

    @override_settings(PERMISSIONS="can-frobulate: *")
    def test_star(self):
        user = users_factories.AdminFactory.build(email="jane@example.com")
        assert permissions.has_permission(user, "can-frobulate")

    @override_settings(PERMISSIONS="can-frobulate: *")
    def test_admin_check(self):
        user = users_factories.UserFactory.build(email="jane@example.com")
        assert not permissions.has_permission(user, "can-frobulate")
