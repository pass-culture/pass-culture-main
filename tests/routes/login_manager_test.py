import base64

import pytest

import pcapi.core.users.factories as users_factories


@pytest.mark.usefixtures("db_session")
class BasicAuthenticationTest:
    def test_good_password(self, client):
        password = "sécrét"
        user = users_factories.UserFactory(password=password)
        auth = base64.b64encode(f"{user.email}:{password}".encode("utf-8")).decode()
        headers = {"Authorization": f"Basic {auth}"}
        response = client.get("/v2/bookings/token/-", headers=headers)
        assert response.status_code == 404

    def test_wrong_password(self, client):
        auth = base64.b64encode("unknown:wrøng".encode("utf-8")).decode()
        headers = {"Authorization": f"Basic {auth}"}
        response = client.get("/v2/bookings/token/-", headers=headers)
        assert response.status_code == 401

    def test_badly_encoded_header(self, client):
        user = users_factories.UserFactory()
        auth = base64.b64encode(f"{user.email}:wrøng".encode("latin1")).decode()
        headers = {"Authorization": f"Basic {auth}"}
        response = client.get("/v2/bookings/token/-", headers=headers)
        assert response.status_code == 401  # no internal error
