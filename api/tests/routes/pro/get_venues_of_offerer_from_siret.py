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

        with assert_num_queries(testing.AUTHENTICATION_QUERIES + 1 + 1):  # retrieve Offerer  # retrieve Venues
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

        with assert_num_queries(testing.AUTHENTICATION_QUERIES + 1 + 1):  # retrieve Offerer  # retrieve Venues
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

        with assert_num_queries(4):
            response = auth_request.get("/venues/siret/%s" % "12312312312332")

        assert response.status_code == 200
        assert len(response.json["venues"]) == 0
        assert response.json["offererName"] == offerer.name
        assert response.json["offererSiren"] == offerer.siren

    def test_get_venues_of_offerer_from_siret_no_result(self, client):
        user_offerer = offerers_factories.UserOffererFactory(user__email="user.pro1@test.com")

        auth_request = client.with_session_auth(email=user_offerer.user.email)

        with assert_num_queries(3):
            response = auth_request.get("/venues/siret/%s" % "12312312312332")

        assert response.status_code == 200
        assert len(response.json["venues"]) == 0
        assert response.json["offererName"] is None
        assert response.json["offererSiren"] is None


class Returns401Test:
    @pytest.mark.usefixtures("db_session")
    def test_user_not_logged(self, client):
        response = client.get("/venues/siret/%s" % "12312312312312")

        # then
        assert response.status_code == 401
        assert response.json["global"] == ["Authentification nécessaire"]
