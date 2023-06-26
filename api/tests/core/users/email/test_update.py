import pytest

from pcapi.core.users import factories as users_factories
import pcapi.core.users.email.update as email_update
from pcapi.core.users.models import EmailHistoryEventTypeEnum
from pcapi.core.users.models import User


pytestmark = pytest.mark.usefixtures("db_session")


class RequestEmailUpdateTest:
    def test_request_email_update_history(self):
        old_email = "py@test.com"
        password = "p@ssword"
        user = users_factories.UserFactory(email=old_email, password=password)
        new_email = "pypy@test.com"

        email_update.request_email_update(user, new_email, password)

        reloaded_user = User.query.get(user.id)
        assert len(reloaded_user.email_history) == 1

        history = reloaded_user.email_history[0]
        assert history.oldEmail == old_email
        assert history.newEmail == new_email
        assert history.eventType == EmailHistoryEventTypeEnum.UPDATE_REQUEST
        assert history.id is not None
