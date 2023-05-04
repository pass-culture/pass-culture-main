import pytest

import pcapi.core.users.factories as users_factories


pytestmark = pytest.mark.usefixtures("db_session")


ROUTE_PATH = "/users/pro_flags"


class Returns204Test:
    def test_new_flags(self, client):
        user = users_factories.UserFactory()

        client = client.with_session_auth(user.email)
        response = client.post(ROUTE_PATH, json={"firebase": {"BETTER_OFFER_CREATION": "true"}})

        assert response.status_code == 204

    def test_same_flags(self, client):
        flags = users_factories.UserProFlagsFactory()
        user = flags.user

        client = client.with_session_auth(user.email)
        response = client.post(ROUTE_PATH, json={"firebase": {"BETTER_OFFER_CREATION": "true"}})

        assert response.status_code == 204

    def test_different_flags(self, client):
        flags = users_factories.UserProFlagsFactory()
        user = flags.user

        client = client.with_session_auth(user.email)
        response = client.post(ROUTE_PATH, json={"firebase": {"BETTER_OFFER_CREATION": "false"}})

        assert response.status_code == 204


class Returns400Test:
    def test_uknown_flags(self, client):
        flags = users_factories.UserProFlagsFactory()
        user = flags.user

        client = client.with_session_auth(user.email)
        response = client.post(ROUTE_PATH, json={"unknwown": {"toto": 10}})

        assert response.status_code == 400
        assert user.pro_flags.firebase == {"BETTER_OFFER_CREATION": "true"}
