import pytest

import pcapi.core.users.factories as users_factories
from pcapi.core.users.models import User
from pcapi.utils.human_ids import humanize

from tests.conftest import TestClient


@pytest.mark.usefixtures("db_session")
def test_mark_as_seen(app):
    user = users_factories.UserFactory(hasSeenProTutorials=False)

    client = TestClient(app.test_client()).with_session_auth(user.email)
    response = client.patch("/users/tuto-seen")

    assert response.status_code == 204
    assert user.hasSeenProTutorials == True


class LegacyRouteTest:
    @pytest.mark.usefixtures("db_session")
    class Returns204Test:
        def when_user_is_logged_in(self, app):
            # given
            user = users_factories.UserFactory(hasSeenProTutorials=False)

            # when
            client = TestClient(app.test_client()).with_session_auth(user.email)
            response = client.patch(f"/users/{humanize(user.id)}/tuto-seen")

            # then
            updated_user = User.query.one()
            assert response.status_code == 204
            assert updated_user.hasSeenProTutorials == True

    @pytest.mark.usefixtures("db_session")
    class Returns404Test:
        def when_user_does_not_exist(self, app):
            # given
            user = users_factories.UserFactory(hasSeenProTutorials=False)

            # when
            client = TestClient(app.test_client()).with_session_auth(user.email)
            response = client.patch(f"/users/{humanize(12345)}/tuto-seen")

            # then
            assert response.status_code == 404

    @pytest.mark.usefixtures("db_session")
    class Returns403Test:
        def when_user_is_not_logged_in(self, app):
            # given
            user = users_factories.UserFactory(hasSeenProTutorials=False)

            # when
            response = TestClient(app.test_client()).patch(f"/users/{humanize(user.id)}/tuto-seen")

            # then
            updated_user = User.query.one()
            assert response.status_code == 401
            assert updated_user.hasSeenProTutorials == False

        def when_user_has_no_rights(self, app):
            # given
            user_logged_in = users_factories.UserFactory()
            user_to_update = users_factories.UserFactory(hasSeenProTutorials=False)

            # when
            response = (
                TestClient(app.test_client())
                .with_session_auth(email=user_logged_in.email)
                .patch(f"/users/{humanize(user_to_update.id)}/tuto-seen")
            )

            # then
            updated_user = User.query.filter_by(id=user_to_update.id).one()
            assert response.status_code == 403
            assert updated_user.hasSeenProTutorials == False
