import pytest

from pcapi.routes.public.united.endpoints.venues import list_venues

from tests.routes.public.united import helpers


pytestmark = pytest.mark.usefixtures("db_session")


class ListVenuesTest(helpers.PublicApiBaseTest, helpers.UnauthenticatedMixin):
    controller = list_venues
    num_queries = 2

    def test_list_venues(self, api_client, venue, unrelated_venue):
        with self.assert_valid_response(api_client, length=1) as data:
            assert data["id"] == venue.id

    def test_no_venues(self, api_client):
        with self.assert_valid_response(api_client) as data:
            assert not data
