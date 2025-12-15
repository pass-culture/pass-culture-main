import logging
from unittest import mock

import pytest

from pcapi.connectors.harvestr import HaverstrRequester
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.users import factories as users_factories


pytestmark = pytest.mark.usefixtures("db_session")


@pytest.mark.features(ENABLE_PRO_FEEDBACK=True)
class PostUserReviewTest:
    @mock.patch("pcapi.connectors.harvestr.create_message")
    def test_user_can_successfully_submit_review(self, harvestr_create_message, client, caplog):
        user = users_factories.ProFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=user, offerer=offerer)

        expected_data = {
            "userSatisfaction": "Bonne",
            "userComment": "c'est quand même très blanc",
            "pageTitle": "Un très beau titre",
            "offererId": offerer.id,
            "location": f"/offerers/{offerer.id}",
        }

        client = client.with_session_auth(user.email)

        with caplog.at_level(logging.INFO):
            response = client.post("/users/log-user-review", json=expected_data)

        assert response.status_code == 204
        assert "User submitting review" in caplog.messages
        assert caplog.records[0].extra["offerer_id"] == offerer.id
        assert caplog.records[0].extra["user_satisfaction"] == expected_data["userSatisfaction"]
        assert caplog.records[0].extra["user_comment"] == expected_data["userComment"]
        assert caplog.records[0].extra["source_page"] == f"/offerers/{offerer.id}"
        assert caplog.records[0].technical_message_id == "user_review"
        harvestr_create_message.assert_called_with(
            title="Retour - Un très beau titre",
            content="c'est quand même très blanc",
            requester=HaverstrRequester(
                name=user.full_name,
                externalUid=str(user.id),
                email=user.email,
            ),
            labels=["AC", f"location: /offerers/{offerer.id}"],
        )

    @mock.patch("pcapi.connectors.harvestr.create_message")
    def test_harvestr_is_not_called_when_user_has_no_leaved_any_comment(self, harvestr_create_message, client, caplog):
        user = users_factories.ProFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=user, offerer=offerer)

        expected_data = {
            "userSatisfaction": "Bonne",
            "userComment": "",
            "pageTitle": "Un très beau titre",
            "offererId": offerer.id,
            "location": f"/offerers/{offerer.id}",
        }

        client = client.with_session_auth(user.email)

        with caplog.at_level(logging.INFO):
            response = client.post("/users/log-user-review", json=expected_data)

        assert response.status_code == 204
        assert "User submitting review" in caplog.messages
        assert caplog.records[0].extra["offerer_id"] == offerer.id
        assert caplog.records[0].extra["user_satisfaction"] == expected_data["userSatisfaction"]
        assert caplog.records[0].extra["user_comment"] == expected_data["userComment"]
        assert caplog.records[0].extra["source_page"] == f"/offerers/{offerer.id}"
        assert caplog.records[0].technical_message_id == "user_review"
        harvestr_create_message.assert_not_called()

    @mock.patch("pcapi.connectors.harvestr.create_message")
    def test_user_cannot_submit_review_for_foreign_offerer(self, harvestr_create_message, client, caplog):
        user = users_factories.ProFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=user, offerer=offerer)
        foreign_offerer = offerers_factories.OffererFactory()

        data = {
            "userSatisfaction": "Mauvaise",
            "userComment": "messing with statistics again è_é",
            "pageTitle": "Un très beau titre",
            "offererId": foreign_offerer.id,
            "location": f"/offerers/{id}/",
        }

        client = client.with_session_auth(user.email)

        with caplog.at_level(logging.INFO):
            response = client.post("/users/log-user-review", json=data)

        assert response.status_code == 403
        assert "User submitting review" not in caplog.messages
        harvestr_create_message.assert_not_called()

    @pytest.mark.features(ENABLE_PRO_FEEDBACK=False)
    def test_feature_is_disabled(self, client):
        user = users_factories.ProFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=user, offerer=offerer)
        foreign_offerer = offerers_factories.OffererFactory()

        data = {
            "userSatisfaction": "Mauvaise",
            "userComment": "messing with statistics again è_é",
            "pageTitle": "Un très beau titre",
            "offererId": foreign_offerer.id,
            "location": f"/offerers/{id}/",
        }

        response = client.with_session_auth(user.email).post("/users/log-user-review", json=data)

        assert response.status_code == 503
        assert response.json == {"global": "service not available"}
