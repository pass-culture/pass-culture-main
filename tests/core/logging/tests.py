import uuid

import pytest
from requests.auth import _basic_auth_str

from pcapi.core import logging
import pcapi.core.users.factories as users_factories


class GetOrSetCorrelationIdTest:
    def test_request_with_no_header(self, app):
        with app.test_request_context():
            correlation_id = logging.get_or_set_correlation_id()
            assert correlation_id == ""

    def test_request_with_header(self, app):
        headers = {"X-Request-Id": uuid.uuid4().hex}
        with app.test_request_context(headers=headers):
            correlation_id = logging.get_or_set_correlation_id()
            assert correlation_id == headers["X-Request-Id"]


@pytest.mark.usefixtures("db_session")
class GetLoggedInUserIdTest:
    def test_request_from_anonymous_user(self, app):
        with app.test_request_context():
            user_id = logging.get_logged_in_user_id()
            assert user_id is None

    def test_request_from_authenticated_user(self, app):
        user = users_factories.UserFactory()
        headers = {"Authorization": _basic_auth_str(user.email, users_factories.DEFAULT_PASSWORD)}
        with app.test_request_context(headers=headers):
            user_id = logging.get_logged_in_user_id()
            assert user_id == user.id
