import pytest

from pcapi.routes.public.united.endpoints.offerers import get_offerer_venues

from tests.routes.public.united import helpers


pytestmark = pytest.mark.usefixtures("db_session")


class GetOfferersVenueTest(helpers.PublicApiBaseTest, helpers.UnauthenticatedMixin):
    controller = get_offerer_venues
    num_queries = 2

    def test_get_offerer_venues(self, api_client, offerer):
        with self.assert_valid_response(api_client, length=1) as data:
            assert data["offerer"]["id"] == offerer.id
            assert {v["id"] for v in data["venues"]} == {v.id for v in offerer.managedVenues}

    def test_filter_by_siren(self, api_client, offerer, related_offerer):
        path = self.build_path(siren=offerer.siren)

        with self.assert_valid_response(api_client, path=path, length=1) as data:
            assert data["offerer"]["id"] == offerer.id
            assert {v["id"] for v in data["venues"]} == {v.id for v in offerer.managedVenues}

    def test_unknown_siren(self, api_client, offerer):
        path = self.build_path(siren="999888777")

        with self.assert_valid_response(api_client, path=path) as data:
            assert not data

    def test_no_offerers(self, api_client):
        with self.assert_valid_response(api_client) as data:
            assert not data
