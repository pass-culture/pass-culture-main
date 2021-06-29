from unittest.mock import Mock
from unittest.mock import patch

from pcapi.admin.base_configuration import BaseAdminView
from pcapi.core.testing import override_settings
from pcapi.models import Booking


fake_db_session = [Mock()]


class DummyAdminView(BaseAdminView):
    pass


class DefaultConfigurationTest:
    def test_model_in_admin_view_is_not_deletable(self):
        # when
        view = DummyAdminView(Booking, fake_db_session)

        # then
        assert view.can_delete is False, "Deletion from admin views is strictly forbidden to guarantee data consistency"

    def test_model_in_admin_view_is_not_creatable(self):
        # when
        view = DummyAdminView(Booking, fake_db_session)

        # then
        assert view.can_create is False, "Creation from admin views is strictly forbidden to guarantee data consistency"

    def test_model_in_admin_view_is_not_editable_by_default(self):
        # when
        view = DummyAdminView(Booking, fake_db_session)

        # then
        assert (
            view.can_edit is False
        ), "Edition from admin views is disabled by default. It can be enabled on a custom view"


class IsAccessibleTest:
    @patch("pcapi.admin.base_configuration.current_user")
    def test_access_is_forbidden_for_anonymous_users(self, current_user):
        # given
        current_user.is_authenticated = False

        # when
        view = DummyAdminView(Booking, fake_db_session)

        # then
        assert not view.is_accessible()

    @patch("pcapi.admin.base_configuration.current_user")
    def test_access_is_forbidden_for_non_admin_users(self, current_user):
        # given
        current_user.is_authenticated = True
        current_user.isAdmin = False

        # when
        view = DummyAdminView(Booking, fake_db_session)

        # then
        assert not view.is_accessible()

    @patch("pcapi.admin.base_configuration.current_user")
    def test_access_is_authorized_for_admin_users(self, current_user):
        # given
        current_user.is_authenticated = True
        current_user.isAdmin = True

        # when
        view = DummyAdminView(Booking, fake_db_session)

        # then
        assert view.is_accessible() is True

    @patch("pcapi.admin.base_configuration.current_user")
    @override_settings(SUPER_ADMIN_EMAIL_ADDRESSES="", IS_PROD=True)
    def test_check_super_admins_is_false_for_non_super_admin_users(self, current_user):
        # given
        current_user.email = "dummy@email.com"

        # when
        view = DummyAdminView(Booking, fake_db_session)

        # then
        assert view.check_super_admins() is False

    @patch("pcapi.admin.base_configuration.current_user")
    @override_settings(SUPER_ADMIN_EMAIL_ADDRESSES="super@admin.user", IS_PROD=True)
    def test_check_super_admins_is_true_for_super_admin_users(self, current_user):
        # given
        current_user.email = "super@admin.user"

        # when
        view = DummyAdminView(Booking, fake_db_session)

        # then
        assert view.check_super_admins() is True

    @patch("pcapi.admin.base_configuration.current_user")
    @override_settings(SUPER_ADMIN_EMAIL_ADDRESSES="")
    def test_check_super_admins_is_deactived_in_non_prod_environments(self, current_user):
        # given
        current_user.email = "dummy@email.com"

        # when
        view = DummyAdminView(Booking, fake_db_session)

        # then
        assert view.check_super_admins() is True
