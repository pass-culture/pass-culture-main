import pytest

from pcapi.core import testing
import pcapi.core.offerers.factories as offerers_factories
from pcapi.core.testing import assert_num_queries


@pytest.mark.usefixtures("db_session")
class Returns200Test:
    def test_get_venues_of_offerer_from_siret(self, client):
        siren = "123123123"
        offerer = offerers_factories.OffererFactory(siren=siren)
        user_offerer = offerers_factories.UserOffererFactory(user__email="user.pro@test.com", offerer=offerer)

        first_venue = offerers_factories.VenueFactory(
            name="Venue",
            managingOfferer=user_offerer.offerer,
            siret=f"{siren}12321",
            isPermanent=True,
            publicName="0 - Venue",
        )

        second_venue = offerers_factories.VenueFactory(
            name="Venue 1",
            managingOfferer=user_offerer.offerer,
            siret=f"{siren}12323",
            isPermanent=False,
            publicName="1 - Venue",
        )

        auth_request = client.with_session_auth(email=user_offerer.user.email)
        num_queries = testing.AUTHENTICATION_QUERIES
        num_queries += 1  # select offerer
        num_queries += 1  # select venues
        with assert_num_queries(num_queries):
            response = auth_request.get("/venues/siret/%s" % "12312312312332")
            assert response.status_code == 200

        assert len(response.json["venues"]) == 2
        assert response.json["venues"][0]["name"] == first_venue.name
        assert response.json["venues"][0]["isPermanent"] == first_venue.isPermanent
        assert response.json["offererName"] == offerer.name
        assert response.json["offererSiren"] == offerer.siren
        assert response.json["venues"][1]["name"] == second_venue.name
        assert response.json["venues"][1]["isPermanent"] == second_venue.isPermanent

    def test_get_venues_of_offerer_from_siret_match_should_be_first(self, client):
        siren = "123123123"
        offerer = offerers_factories.OffererFactory(siren=siren)
        user_offerer = offerers_factories.UserOffererFactory(user__email="user.pro@test.com", offerer=offerer)

        first_venue = offerers_factories.VenueFactory(
            name="Venue",
            managingOfferer=user_offerer.offerer,
            siret=f"{siren}12321",
            isPermanent=True,
            publicName="0 - Venue",
        )

        matching_venue = offerers_factories.VenueFactory(
            name="Venue 1",
            managingOfferer=user_offerer.offerer,
            siret=f"{siren}12332",
            isPermanent=True,
            publicName="1 - Venue",
        )

        auth_request = client.with_session_auth(email=user_offerer.user.email)
        num_queries = testing.AUTHENTICATION_QUERIES
        num_queries += 1  # select offerer
        num_queries += 1  # select venues
        with assert_num_queries(num_queries):
            response = auth_request.get("/venues/siret/%s" % "12312312312332")
            assert response.status_code == 200

        assert len(response.json["venues"]) == 2
        assert response.json["venues"][0]["name"] == matching_venue.name
        assert response.json["venues"][1]["name"] == first_venue.name

    def test_get_venues_of_offerer_from_siret_no_venue_one_offerer(self, client):
        siren = "123123123"
        offerer = offerers_factories.OffererFactory(siren=siren)
        user_offerer = offerers_factories.UserOffererFactory(user__email="user.pro@test.com", offerer=offerer)

        auth_request = client.with_session_auth(email=user_offerer.user.email)
        num_queries = testing.AUTHENTICATION_QUERIES
        num_queries += 1  # select offerer
        num_queries += 1  # select venues
        with assert_num_queries(num_queries):
            response = auth_request.get("/venues/siret/%s" % "12312312312332")
            assert response.status_code == 200

        assert len(response.json["venues"]) == 0
        assert response.json["offererName"] == offerer.name
        assert response.json["offererSiren"] == offerer.siren

    def test_get_venues_of_offerer_from_siret_no_result(self, client):
        user_offerer = offerers_factories.UserOffererFactory(user__email="user.pro1@test.com")

        auth_request = client.with_session_auth(email=user_offerer.user.email)

        num_queries = testing.AUTHENTICATION_QUERIES
        num_queries += 1  # select offerer
        with assert_num_queries(num_queries):
            response = auth_request.get("/venues/siret/%s" % "12312312312332")
            assert response.status_code == 200

        assert len(response.json["venues"]) == 0
        assert response.json["offererName"] is None
        assert response.json["offererSiren"] is None

    def test_get_venues_of_rejected_offerer(self, client):
        # New offerer subscription should not ask to join an existing offerer
        rejected_offerer = offerers_factories.RejectedOffererFactory()
        offerers_factories.VenueFactory(managingOfferer=rejected_offerer)
        user_offerer = offerers_factories.RejectedUserOffererFactory(offerer=rejected_offerer)

        auth_request = client.with_session_auth(email=user_offerer.user.email)

        num_queries = testing.AUTHENTICATION_QUERIES
        num_queries += 1  # select offerer
        with assert_num_queries(num_queries):
            response = auth_request.get("/venues/siret/%s" % "12312312312332")
            assert response.status_code == 200

        assert len(response.json["venues"]) == 0
        assert response.json["offererName"] is None
        assert response.json["offererSiren"] is None


class Returns401Test:
    @pytest.mark.usefixtures("db_session")
    def test_user_not_logged(self, client):
        with testing.assert_num_queries(0):
            response = client.get("/venues/siret/%s" % "12312312312312")
            assert response.status_code == 401

        assert response.json["global"] == ["Authentification nécessaire"]
