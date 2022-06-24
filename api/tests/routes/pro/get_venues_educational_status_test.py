import typing

import pytest

from pcapi.core import testing
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.users.factories as users_factories


class Returns401Test:
    @pytest.mark.usefixtures("db_session")
    def test_when_user_offerer_does_not_exist(self, client: typing.Any):
        response = client.get("/venues-educational-statuses")
        assert response.status_code == 401


class Returns200Test:
    @pytest.mark.usefixtures("db_session")
    def test_when_user_can_retrieve_the_statues(self, client: typing.Any):
        pro = users_factories.ProFactory()

        offerers_factories.VenueEducationalStatusFactory(
            id=2,
            name="Établissement public",
        )
        offerers_factories.VenueEducationalStatusFactory(id=3, name="Association")
        offerers_factories.VenueEducationalStatusFactory(id=4, name="Établissement privé")
        offerers_factories.VenueEducationalStatusFactory(id=5, name="micro-entreprise, auto-entrepreneur")

        n_queries = testing.AUTHENTICATION_QUERIES
        n_queries += 1  # query to retrieve all the venues educational status
        auth_client = client.with_session_auth(pro.email)
        with testing.assert_num_queries(n_queries):
            response = auth_client.get("/venues-educational-statuses")

        expected_serialized_offerer = {
            "statuses": [
                {"id": 3, "name": "Association"},
                {"id": 4, "name": "Établissement privé"},
                {"id": 2, "name": "Établissement public"},
                {"id": 5, "name": "micro-entreprise, auto-entrepreneur"},
            ]
        }

        assert response.status_code == 200
        assert response.json == expected_serialized_offerer
