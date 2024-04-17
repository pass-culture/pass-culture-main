import datetime
import logging
from typing import Any

import pytest

from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.users import factories as users_factories


pytestmark = pytest.mark.usefixtures("db_session")


class PostUserNewProNavTest:
    def test_post_user_new_pro_nav(self, client: Any) -> None:
        pro_new_nav_state = users_factories.UserProNewNavStateFactory(
            eligibilityDate=datetime.datetime.utcnow() - datetime.timedelta(days=1), newNavDate=None
        )
        user = pro_new_nav_state.user

        client = client.with_session_auth(user.email)

        response = client.post("/users/new-pro-nav")

        assert response.status_code == 204
        assert pro_new_nav_state.newNavDate

    def test_post_user_new_pro_nav_not_eligible_user(self, client: Any) -> None:
        pro_new_nav_state = users_factories.UserProNewNavStateFactory(eligibilityDate=None, newNavDate=None)
        user = pro_new_nav_state.user

        client = client.with_session_auth(user.email)

        response = client.post("/users/new-pro-nav")

        assert response.status_code == 400
        assert not pro_new_nav_state.newNavDate

    def test_user_can_successfully_submit_side_nav_review(self, client, caplog):
        pro_new_nav_state = users_factories.UserProNewNavStateFactory(
            eligibilityDate=None, newNavDate=datetime.datetime.utcnow()
        )
        user = pro_new_nav_state.user
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=user, offerer=offerer)

        expected_data = {
            "isConvenient": True,
            "isPleasant": False,
            "comment": "c'est quand même très blanc",
            "offererId": offerer.id,
            "location": f"/offerers/{id}",
        }

        client = client.with_session_auth(user.email)

        with caplog.at_level(logging.INFO):
            response = client.post("/users/log-new-nav-review", json=expected_data)

        assert response.status_code == 204
        assert "User with new nav activated submitting review" in caplog.messages
        assert caplog.records[0].extra["user_id"] == user.id
        assert caplog.records[0].extra["offerer_id"] == offerer.id
        assert caplog.records[0].extra["isConvenient"] == expected_data["isConvenient"]
        assert caplog.records[0].extra["isPleasant"] == expected_data["isPleasant"]
        assert caplog.records[0].extra["comment"] == expected_data["comment"]
        assert caplog.records[0].extra["source_page"] == f"/offerers/{id}"

    def test_user_without_new_nav_activated_cant_submit_review(self, client, caplog):
        pro_new_nav_state = users_factories.UserProNewNavStateFactory(newNavDate=None)
        user = pro_new_nav_state.user
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=user, offerer=offerer)

        data = {
            "isConvenient": False,
            "isPleasant": False,
            "comment": "messing with statistics",
            "offererId": offerer.id,
            "location": f"/offerers/{id}/",
        }

        client = client.with_session_auth(user.email)

        with caplog.at_level(logging.INFO):
            response = client.post("/users/log-new-nav-review", json=data)

        assert response.status_code == 403
        assert "User with new nav activated submitting review" not in caplog.messages

    def test_user_cannot_submit_review_for_foreign_offerer(self, client, caplog):
        pro_new_nav_state = users_factories.UserProNewNavStateFactory(newNavDate=None)
        user = pro_new_nav_state.user
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=user, offerer=offerer)
        foreign_offerer = offerers_factories.OffererFactory()

        data = {
            "isConvenient": False,
            "isPleasant": False,
            "comment": "messing with statistics again è_é",
            "offererId": foreign_offerer.id,
            "location": f"/offerers/{id}/",
        }

        client = client.with_session_auth(user.email)

        with caplog.at_level(logging.INFO):
            response = client.post("/users/log-new-nav-review", json=data)

        assert response.status_code == 403
        assert "User with new nav activated submitting review" not in caplog.messages
