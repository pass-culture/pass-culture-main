import pytest

import pcapi.core.users.factories as users_factories


@pytest.mark.usefixtures("db_session")
def test_mark_as_seen(client):
    user = users_factories.UserFactory(hasSeenProTutorials=False)

    response = client.with_session_auth(user.email).patch("/users/tuto-seen")

    assert response.status_code == 204
    assert user.hasSeenProTutorials is True


@pytest.mark.usefixtures("db_session")
def test_mark_as_seen_without_auth(client):
    user = users_factories.UserFactory(hasSeenProTutorials=False)

    response = client.patch("/users/tuto-seen")

    assert response.status_code == 401
    assert user.hasSeenProTutorials is False
