from datetime import datetime

import pytest

import pcapi.core.bookings.factories as bookings_factories
from pcapi.core.educational.factories import CollectiveBookingFactory
from pcapi.core.educational.factories import CollectiveOfferTemplateFactory
from pcapi.core.educational.models import CollectiveBookingStatus
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.users.factories as users_factories
from pcapi.models.offer_mixin import OfferValidationStatus
from pcapi.utils.human_ids import humanize

from tests.conftest import TestClient


class Returns200Test:
    @pytest.mark.usefixtures("db_session")
    def when_pro_user_has_rights_on_managing_offerer(self, app):
        # given
        booking = bookings_factories.BookingFactory()
        bookings_factories.UsedBookingFactory(stock=booking.stock)
        venue = booking.venue
        venue_owner = offerers_factories.UserOffererFactory(offerer=venue.managingOfferer).user

        # validated booking + not active not sold out offer
        CollectiveBookingFactory(
            collectiveStock__collectiveOffer__venue=venue,
            collectiveStock__collectiveOffer__validation=OfferValidationStatus.APPROVED,
            status=CollectiveBookingStatus.CONFIRMED,
            cancellationLimitDate=datetime(2001, 10, 10),
            collectiveStock__bookingLimitDatetime=datetime(2001, 10, 10),
        )
        # active booking since status is pending but bookinglimitdatetime has not passed + sold out offer
        # bookingLimitDatetime is in 2222 because sql now() function can't be mocked
        CollectiveBookingFactory(
            collectiveStock__collectiveOffer__venue=venue,
            collectiveStock__collectiveOffer__validation=OfferValidationStatus.APPROVED,
            status=CollectiveBookingStatus.PENDING,
            collectiveStock__bookingLimitDatetime=datetime(2222, 10, 10),
        )
        # inactive booking since status is pending but bookinglimitdatetime has passed + expired offer
        CollectiveBookingFactory(
            collectiveStock__collectiveOffer__venue=venue,
            collectiveStock__collectiveOffer__validation=OfferValidationStatus.APPROVED,
            status=CollectiveBookingStatus.PENDING,
            collectiveStock__bookingLimitDatetime=datetime(2001, 10, 10),
        )
        # active offer
        CollectiveOfferTemplateFactory(venue=venue)

        auth_request = TestClient(app.test_client()).with_session_auth(email=venue_owner.email)

        # when
        response = auth_request.get("/venues/%s/stats" % humanize(venue.id))

        # then
        assert response.status_code == 200
        response_json = response.json
        assert response_json["activeBookingsQuantity"] == 2
        assert response_json["validatedBookingsQuantity"] == 2
        assert response_json["activeOffersCount"] == 2
        assert response_json["soldOutOffersCount"] == 1


class Returns403Test:
    @pytest.mark.usefixtures("db_session")
    def when_pro_user_does_not_have_rights(self, app):
        # given
        pro_user = users_factories.ProFactory()
        venue = offerers_factories.VenueFactory()

        auth_request = TestClient(app.test_client()).with_session_auth(email=pro_user.email)

        # when
        response = auth_request.get("/venues/%s/stats" % humanize(venue.id))

        # then
        assert response.status_code == 403
        assert response.json["global"] == [
            "Vous n'avez pas les droits d'accès suffisant pour accéder à cette information."
        ]
