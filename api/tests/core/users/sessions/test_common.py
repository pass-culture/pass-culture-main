from datetime import timedelta

import pytest

from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as users_models
from pcapi.core.users.sessions import delete_expired_sessions
from pcapi.models import db
from pcapi.utils.date import get_naive_utc_now


pytestmark = [
    pytest.mark.usefixtures("db_session"),
]


class DeleteExpiredSessionsTest:
    def test_delete_expired_sessions(self):
        user = users_factories.BaseUserFactory()
        valid_session = users_factories.UserSessionFactory(user=user)
        users_factories.UserSessionFactory(user=user, expirationDatetime=get_naive_utc_now() - timedelta(days=1))

        delete_expired_sessions()

        assert db.session.query(users_models.UserSession).count() == 1
        assert db.session.query(users_models.UserSession.id).scalar() == valid_session.id
