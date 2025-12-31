import pytest

import pcapi.core.offerers.factories as offerers_factories
from pcapi.core.offers import factories as offers_factories
from pcapi.core.testing import assert_num_queries


pytestmark = pytest.mark.usefixtures("db_session")


class Returns401Test:
    def test_return_403_if_user_is_not_authorized(self, client):
        user_offerer = offerers_factories.UserOffererFactory()
        # authorized offer
        offers_factories.OfferFactory(venue__managingOfferer=user_offerer.offerer)
        offer_unauthorized = offers_factories.OfferFactory()

        client = client.with_session_auth(user_offerer.user.email)
        expected_num_queries = 7  #  offer +  session + offer + venue + SELECT EXISTS user_offerer + rollback + rollback
        with assert_num_queries(expected_num_queries):
            response = client.get(f"/bookings/offer/{offer_unauthorized.id}/excel?event_date=2021-01-01&status=all")
            assert response.status_code == 403

        assert response.json == {"global": "You are not allowed to access this offer"}
