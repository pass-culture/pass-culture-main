import uuid

import pytest

from pcapi.models import UserSession
from pcapi.repository import repository
from pcapi.repository.user_session_queries import delete_user_session
import pytest


class DeleteUserSessionTest:
    @pytest.mark.usefixtures("db_session")
    def test_do_not_try_to_delete_session_when_session_does_not_exist(self, app):
        # given
        user_id = 1
        session_id = uuid.uuid4()

        # when
        try:
            delete_user_session(user_id, session_id)
        except:
            pytest.fail('Should not raise an error when no session found')

    @pytest.mark.usefixtures("db_session")
    def test_remove_session_for_user(self, app):
        # given
        user_id = 1
        session_id = uuid.uuid4()

        session = UserSession()
        session.userId = user_id
        session.uuid = session_id
        repository.save(session)

        # when
        delete_user_session(user_id, session_id)

        # then
        assert UserSession.query.count() == 0
