from unittest.mock import Mock, patch

from pcapi.admin.base_configuration import BaseAdminView
from pcapi.models import BookingSQLEntity

fake_db_session = [Mock()]


class DummyAdminView(BaseAdminView):
    pass


class BaseAdminViewTest:
    class DefaultConfigurationTest:
        def test_model_in_admin_view_is_not_deletable(self):
            # when
            view = DummyAdminView(BookingSQLEntity, fake_db_session)

            # then
            assert view.can_delete is False, \
                'Deletion from admin views is strictly forbidden to guarantee data consistency'

        def test_model_in_admin_view_is_not_creatable(self):
            # when
            view = DummyAdminView(BookingSQLEntity, fake_db_session)

            # then
            assert view.can_create is False, \
                'Creation from admin views is strictly forbidden to guarantee data consistency'

        def test_model_in_admin_view_is_not_editable_by_default(self):
            # when
            view = DummyAdminView(BookingSQLEntity, fake_db_session)

            # then
            assert view.can_edit is False, \
                'Edition from admin views is disabled by default. It can be enabled on a custom view'

    class IsAccessibleTest:
        @patch('pcapi.admin.base_configuration.current_user')
        def test_access_is_forbidden_for_anonymous_users(self, current_user):
            # given
            current_user.is_authenticated = False

            # when
            view = DummyAdminView(BookingSQLEntity, fake_db_session)

            # then
            assert view.is_accessible() is False

        @patch('pcapi.admin.base_configuration.current_user')
        def test_access_is_forbidden_for_non_admin_users(self, current_user):
            # given
            current_user.is_authenticated = True
            current_user.isAdmin = False

            # when
            view = DummyAdminView(BookingSQLEntity, fake_db_session)

            # then
            assert view.is_accessible() is False

        @patch('pcapi.admin.base_configuration.current_user')
        def test_access_is_authorized_for_admin_users(self, current_user):
            # given
            current_user.is_authenticated = True
            current_user.isAdmin = True

            # when
            view = DummyAdminView(BookingSQLEntity, fake_db_session)

            # then
            assert view.is_accessible() is True
