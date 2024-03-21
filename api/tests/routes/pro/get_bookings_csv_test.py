import pytest

import pcapi.core.offerers.factories as offerers_factories
from pcapi.core.offers import factories as offers_factories


pytestmark = pytest.mark.usefixtures("db_session")


class Returns401Test:
    def test_return_403_if_user_is_not_authorized(self, client):
        user_offerer = offerers_factories.UserOffererFactory()
        # authorized offer
        offers_factories.OfferFactory(venue__managingOfferer=user_offerer.offerer)
        offer_unauthorized = offers_factories.OfferFactory()
        response = client.with_session_auth(user_offerer.user.email).get(
            f"/bookings/offer/{offer_unauthorized.id}/csv?event_date=2021-01-01&status=all"
        )
        assert response.status_code == 403
        assert response.json == {"global": "You are not allowed to access this offer"}
