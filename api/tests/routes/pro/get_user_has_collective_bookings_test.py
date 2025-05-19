import pytest

import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.users.factories as users_factories
from pcapi.core import testing
from pcapi.core.educational.factories import CollectiveBookingFactory


@pytest.mark.usefixtures("db_session")
class Returns200Test:
    num_queries = testing.AUTHENTICATION_QUERIES
    num_queries += 1  # check user has collective_bookings

    def test_user_has_collective_bookings(self, client):
        user = users_factories.UserFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=user, offerer=offerer)

        CollectiveBookingFactory(offerer=offerer, collectiveStock__collectiveOffer__venue__managingOfferer=offerer)
        client = client.with_session_auth(user.email)
        with testing.assert_num_queries(self.num_queries):
            response = client.get("/collective/bookings/pro/userHasBookings")
            assert response.status_code == 200

        user_has_bookings = response.json["hasBookings"]
        assert user_has_bookings

    def when_offerer_id_does_not_exist(self, client):
        user = users_factories.UserFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=user, offerer=offerer)

        client = client.with_session_auth(user.email)

        with testing.assert_num_queries(self.num_queries):
            response = client.get("/collective/bookings/pro/userHasBookings")
            assert response.status_code == 200

        user_has_bookings = response.json["hasBookings"]
        assert not user_has_bookings
