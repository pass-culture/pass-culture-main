import typing

import pytest

from pcapi.core import testing
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.users.factories as users_factories


class Returns401Test:

    def test_when_user_not_logged_in(self, client: typing.Any):
        response = client.get("/venues-educational-statuses")
        assert response.status_code == 401


class Returns200Test:

    def test_when_user_can_retrieve_the_statues(self, client: typing.Any):
        pro = users_factories.ProFactory()

        offerers_factories.VenueEducationalStatusFactory(
            id=2,
            name="Établissement public",
        )
        offerers_factories.VenueEducationalStatusFactory(id=3, name="Association")
        offerers_factories.VenueEducationalStatusFactory(id=4, name="Établissement privé")
        offerers_factories.VenueEducationalStatusFactory(id=5, name="micro-entreprise, auto-entrepreneur")

        auth_client = client.with_session_auth(pro.email)
        with testing.assert_no_duplicated_queries():
            response = auth_client.get("/venues-educational-statuses")

        expected_serialized_offerer = {
            "statuses": [
                {"id": 2, "name": "Établissement public"},
                {"id": 3, "name": "Association"},
                {"id": 4, "name": "Établissement privé"},
                {"id": 5, "name": "micro-entreprise, auto-entrepreneur"},
            ]
        }

        assert response.status_code == 200

        found_offerer = response.json
        found_offerer["statuses"] = sorted(found_offerer["statuses"], key=lambda o: o["id"])

        assert found_offerer == expected_serialized_offerer
