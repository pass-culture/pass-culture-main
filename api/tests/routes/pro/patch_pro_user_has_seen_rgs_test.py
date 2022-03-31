import pytest

import pcapi.core.users.factories as users_factories


@pytest.mark.usefixtures("db_session")
def test_mark_as_seen(app, client):
    user = users_factories.UserFactory(hasSeenProRgs=False)

    client = client.with_session_auth(user.email)
    response = client.patch("/users/rgs-seen")

    assert response.status_code == 204
    assert user.hasSeenProRgs == True


@pytest.mark.usefixtures("db_session")
def test_mark_as_seen_without_auth(app, client):
    user = users_factories.UserFactory(hasSeenProRgs=False)

    response = client.patch("/users/rgs-seen")

    assert response.status_code == 401
    assert user.hasSeenProRgs == False
