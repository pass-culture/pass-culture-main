import pytest

import pcapi.core.bookings.factories as bookings_factories
from pcapi.core.bookings.models import BookingStatus
import pcapi.core.offers.factories as offers_factories
import pcapi.core.users.factories as users_factories
from pcapi.utils.human_ids import humanize

from tests.conftest import TestClient


class Returns200Test:
    @pytest.mark.usefixtures("db_session")
    def when_pro_user_has_rights_on_managing_offerer(self, app):
        # given
        booking = bookings_factories.BookingFactory()
        bookings_factories.BookingFactory(isUsed=True, status=BookingStatus.USED, stock=booking.stock)
        venue = booking.stock.offer.venue
        venue_owner = offers_factories.UserOffererFactory(offerer=venue.managingOfferer).user

        auth_request = TestClient(app.test_client()).with_auth(email=venue_owner.email)

        # when
        response = auth_request.get("/venues/%s/stats" % humanize(venue.id))

        # then
        assert response.status_code == 200
        response_json = response.json
        assert response_json["activeBookingsQuantity"] == 1
        assert response_json["validatedBookingsQuantity"] == 1
        assert response_json["activeOffersCount"] == 1
        assert response_json["soldOutOffersCount"] == 0


class Returns403Test:
    @pytest.mark.usefixtures("db_session")
    def when_pro_user_does_not_have_rights(self, app):
        # given
        pro_user = users_factories.ProFactory()
        venue = offers_factories.VenueFactory()

        auth_request = TestClient(app.test_client()).with_auth(email=pro_user.email)

        # when
        response = auth_request.get("/venues/%s/stats" % humanize(venue.id))

        # then
        assert response.status_code == 403
        assert response.json["global"] == [
            "Vous n'avez pas les droits d'accès suffisant pour accéder à cette information."
        ]
