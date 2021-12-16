import pytest

from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as users_models


class Returns200Test:
    @pytest.mark.usefixtures("db_session")
    def when_current_user_changes_password(self, client):
        # given
        user = users_factories.UserFactory(email="user@example.com")
        data = {
            "oldPassword": user.clearTextPassword,
            "newPassword": "N3W_p4ssw0rd",
            "newConfirmationPassword": "N3W_p4ssw0rd",
        }
        user_id = user.id

        # when
        client = client.with_session_auth(user.email)
        response = client.post("/users/current/change-password", json=data)

        # then
        user = users_models.User.query.get(user_id)
        assert user.checkPassword("N3W_p4ssw0rd") is True
        assert response.status_code == 204


class Returns400Test:
    @pytest.mark.usefixtures("db_session")
    def when_data_is_empty_in_the_request_body(self, client):
        # given
        user = users_factories.UserFactory(email="user@example.com")
        data = {
            "oldPassword": "",
            "newPassword": "",
            "newConfirmationPassword": "",
        }

        # when
        client = client.with_session_auth(user.email)
        response = client.post("/users/current/change-password", json=data)

        # then
        assert response.status_code == 400
        assert response.json["oldPassword"] == ["Ce champ est obligatoire"]
        assert response.json["newPassword"] == ["Ce champ est obligatoire"]
        assert response.json["newConfirmationPassword"] == ["Ce champ est obligatoire"]

    @pytest.mark.usefixtures("db_session")
    def when_data_is_missing_in_the_request_body(self, client):
        # given
        user = users_factories.UserFactory(email="user@example.com")
        data = {}

        # when
        client = client.with_session_auth(user.email)
        response = client.post("/users/current/change-password", json=data)

        # then
        assert response.status_code == 400
        assert response.json["oldPassword"] == ["Ce champ est obligatoire"]
        assert response.json["newPassword"] == ["Ce champ est obligatoire"]
        assert response.json["newConfirmationPassword"] == ["Ce champ est obligatoire"]
