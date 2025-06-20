import pytest
import time_machine

import pcapi.core.mails.testing as mails_testing
from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as users_models
from pcapi.models import db


pytestmark = pytest.mark.usefixtures("db_session")


class Returns200Test:
    @time_machine.travel("2020-11-17 15:00:00")
    def when_current_user_changes_password(self, client):
        # given
        user = users_factories.ProFactory(email="user@example.com")

        data = {
            "oldPassword": user.clearTextPassword,
            "newPassword": "N3W_p4ssw0rd",
            "newConfirmationPassword": "N3W_p4ssw0rd",
        }
        user_id = user.id

        # when
        client = client.with_session_auth(user.email)
        response = client.post("/users/password", json=data)

        # then
        user = db.session.get(users_models.User, user_id)
        assert user.checkPassword("N3W_p4ssw0rd") is True
        assert response.status_code == 204
        assert len(mails_testing.outbox) == 1
        expected_params = {"EVENT_DATE": "mardi 17 novembre 2020", "EVENT_HOUR": "16h00"}
        assert mails_testing.outbox[0]["params"] == expected_params

    @time_machine.travel("2020-11-17 15:00:00")
    def when_current_user_who_lives_at_wallis_changes_password(self, client):
        # given
        user = users_factories.ProFactory(email="user@example.com", departementCode="986")
        data = {
            "oldPassword": user.clearTextPassword,
            "newPassword": "N3W_p4ssw0rd",
            "newConfirmationPassword": "N3W_p4ssw0rd",
        }

        client = client.with_session_auth(user.email)
        client.post("/users/password", json=data)
        assert len(mails_testing.outbox) == 1
        assert mails_testing.outbox[0]["params"] == {"EVENT_DATE": "mercredi 18 novembre 2020", "EVENT_HOUR": "03h00"}


class Returns400Test:
    def when_data_is_empty_in_the_request_body(self, client):
        # given
        user = users_factories.ProFactory(email="user@example.com")
        data = {
            "oldPassword": "",
            "newPassword": "",
            "newConfirmationPassword": "",
        }

        # when
        client = client.with_session_auth(user.email)
        response = client.post("/users/password", json=data)
        # then
        assert response.status_code == 400
        assert response.json["oldPassword"] == ["Le mot de passe actuel est incorrect."]
        assert "Le mot de passe doit contenir au moins :" in response.json["newPassword"][0]

    def when_data_password_don_t_match_in_the_request_body(self, client):
        # given
        user = users_factories.ProFactory(email="user@example.com")
        data = {
            "oldPassword": user.clearTextPassword,
            "newPassword": "N3W_Valid_p4ssw0rd",
            "newConfirmationPassword": "N3W_NotMatch_p4ssw0rd",
        }

        # when
        client = client.with_session_auth(user.email)
        response = client.post("/users/password", json=data)
        # then
        assert response.status_code == 400
        assert response.json["newConfirmationPassword"] == ["Les deux mots de passe ne sont pas identiques."]

    def when_data_is_missing_in_the_request_body(self, client):
        # given
        user = users_factories.ProFactory(email="user@example.com")
        data = {}

        # when
        client = client.with_session_auth(user.email)
        response = client.post("/users/password", json=data)

        # then
        assert response.status_code == 400
        assert response.json["oldPassword"] == ["Ce champ est obligatoire"]
        assert response.json["newPassword"] == ["Ce champ est obligatoire"]
        assert response.json["newConfirmationPassword"] == ["Ce champ est obligatoire"]
