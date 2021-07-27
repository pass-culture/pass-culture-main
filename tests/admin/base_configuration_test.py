from unittest.mock import Mock
from unittest.mock import patch

import flask_login

from pcapi.admin.base_configuration import BaseAdminView
from pcapi.core.testing import override_settings
from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as users_models
from pcapi.flask_app import db
from pcapi.models import Booking


fake_db_session = [Mock()]


class DummyAdminView(BaseAdminView):
    pass


class AnonymousUser(flask_login.AnonymousUserMixin):
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
    @patch("flask_login.utils._get_user")
    def test_access_is_forbidden_for_anonymous_users(self, get_user):
        # given
        get_user.return_value = AnonymousUser()

        # when
        view = DummyAdminView(Booking, fake_db_session)

        # then
        assert not view.is_accessible()

    @patch("flask_login.utils._get_user")
    def test_access_is_forbidden_for_non_admin_users(self, get_user):
        # given
        get_user.return_value = users_factories.UserFactory.build(isAdmin=False)

        # when
        view = DummyAdminView(Booking, fake_db_session)

        # then
        assert not view.is_accessible()

    @patch("flask_login.utils._get_user")
    def test_access_is_authorized_for_admin_users(self, get_user):
        # given
        get_user.return_value = users_factories.AdminFactory.build()

        # when
        view = DummyAdminView(Booking, fake_db_session)

        # then
        assert view.is_accessible() is True

    @patch("flask_login.utils._get_user")
    @override_settings(SUPER_ADMIN_EMAIL_ADDRESSES="", IS_PROD=True)
    def test_check_super_admins_is_false_for_non_super_admin_users(self, get_user):
        # given
        get_user.return_value = users_factories.UserFactory.build(email="dummy@email.com")

        # when
        view = DummyAdminView(Booking, fake_db_session)

        # then
        assert view.check_super_admins() is False

    @patch("flask_login.utils._get_user")
    @override_settings(SUPER_ADMIN_EMAIL_ADDRESSES="super@admin.user", IS_PROD=True)
    def test_check_super_admins_is_true_for_super_admin_users(self, get_user):
        # given
        get_user.return_value = users_factories.UserFactory.build(email="super@admin.user")

        # when
        view = DummyAdminView(Booking, fake_db_session)

        # then
        assert view.check_super_admins() is True

    @patch("flask_login.utils._get_user")
    @override_settings(SUPER_ADMIN_EMAIL_ADDRESSES="")
    def test_check_super_admins_is_deactived_in_non_prod_environments(self, get_user):
        # given
        get_user.return_value = users_factories.AdminFactory.build(email="dummy@example.com")

        # when
        view = DummyAdminView(Booking, fake_db_session)

        # then
        assert view.check_super_admins() is True


class DummyUserView(BaseAdminView):
    @property
    def form_columns(self):
        fields = ("email",)
        if self.check_super_admins():
            fields += ("firstName", "lastName")
        return fields


class BaseAdminFormTest:
    def test_ensure_no_cache(self, app):
        view = DummyUserView(name="user", url="/user", model=users_models.User, session=db.session)
        with app.test_request_context(method="POST", data={}):
            with patch.object(view, "check_super_admins", return_value=True):
                form = view.get_edit_form()
                assert hasattr(form, "firstName")
                assert hasattr(form, "lastName")

            with patch.object(view, "check_super_admins", return_value=False):
                form = view.get_edit_form()
                assert hasattr(form, "firstName") is False
                assert hasattr(form, "lastName") is False
