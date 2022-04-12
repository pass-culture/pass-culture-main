import pytest

from pcapi.core.educational.factories import CollectiveBookingFactory
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.users.factories as users_factories


@pytest.mark.usefixtures("db_session")
class Returns200Test:
    def test_user_has_collective_bookings(self, client):
        # given
        user = users_factories.UserFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=user, offerer=offerer)

        CollectiveBookingFactory(offerer=offerer, collectiveStock__collectiveOffer__venue__managingOfferer=offerer)

        # when
        response = client.with_session_auth(user.email).get("/collective/bookings/pro/userHasBookings")

        # then
        assert response.status_code == 200
        user_has_bookings = response.json["hasBookings"]
        assert user_has_bookings

    def when_offerer_id_does_not_exist(self, client):
        # given
        user = users_factories.UserFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=user, offerer=offerer)

        # when
        response = client.with_session_auth(user.email).get("/collective/bookings/pro/userHasBookings")

        # then
        assert response.status_code == 200
        user_has_bookings = response.json["hasBookings"]
        assert not user_has_bookings
