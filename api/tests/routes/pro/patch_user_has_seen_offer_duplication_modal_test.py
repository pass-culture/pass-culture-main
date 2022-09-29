import pytest

import pcapi.core.users.factories as users_factories

from tests.conftest import TestClient


@pytest.mark.usefixtures("db_session")
def test_mark_as_seen(client):
    user = users_factories.UserFactory(hasSeenOfferDuplicationModal=False)

    client = client.with_session_auth(user.email)
    response = client.patch("/users/offer-duplication-modal-seen")

    assert response.status_code == 204
    assert user.hasSeenOfferDuplicationModal == True


@pytest.mark.usefixtures("db_session")
def test_mark_as_seen_without_auth(app):
    user = users_factories.UserFactory(hasSeenOfferDuplicationModal=False)

    client = TestClient(app.test_client())
    response = client.patch("/users/offer-duplication-modal-seen")

    assert response.status_code == 401
    assert user.hasSeenOfferDuplicationModal == False
