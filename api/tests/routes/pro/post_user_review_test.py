import logging

import pytest

from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.users import factories as users_factories


pytestmark = pytest.mark.usefixtures("db_session")


class PostUserReviewTest:

    def test_user_can_successfully_submit_review(self, client, caplog):
        user = users_factories.ProFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=user, offerer=offerer)

        expected_data = {
            "userSatisfaction": "Bonne",
            "userComment": "c'est quand même très blanc",
            "offererId": offerer.id,
            "location": f"/pro/offerers/{id}",
        }

        client = client.with_session_auth(user.email)

        with caplog.at_level(logging.INFO):
            response = client.post("/pro/users/log-user-review", json=expected_data)

        assert response.status_code == 204
        assert "User submitting review" in caplog.messages
        assert caplog.records[0].extra["offerer_id"] == offerer.id
        assert caplog.records[0].extra["user_satisfaction"] == expected_data["userSatisfaction"]
        assert caplog.records[0].extra["user_comment"] == expected_data["userComment"]
        assert caplog.records[0].extra["source_page"] == f"/pro/offerers/{id}"
        assert caplog.records[0].technical_message_id == "user_review"

    def test_user_cannot_submit_review_for_foreign_offerer(self, client, caplog):
        user = users_factories.ProFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=user, offerer=offerer)
        foreign_offerer = offerers_factories.OffererFactory()

        data = {
            "userSatisfaction": "Mauvaise",
            "userComment": "messing with statistics again è_é",
            "offererId": foreign_offerer.id,
            "location": f"/pro/offerers/{id}/",
        }

        client = client.with_session_auth(user.email)

        with caplog.at_level(logging.INFO):
            response = client.post("/pro/users/log-user-review", json=data)

        assert response.status_code == 403
        assert "User submitting review" not in caplog.messages
