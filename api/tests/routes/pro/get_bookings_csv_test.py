import csv
from datetime import datetime
from datetime import timedelta
from io import StringIO

import pytest

from pcapi.core.bookings import factories as bookings_factories
import pcapi.core.offerers.factories as offerers_factories
from pcapi.core.offers import factories as offers_factories
from pcapi.core.testing import assert_num_queries
from pcapi.core.users import factories as users_factories


pytestmark = pytest.mark.usefixtures("db_session")


class Returns200Test:
    def test_user_can_filter_bookings_by_offerer(self, client):
        pro_user = users_factories.ProFactory()
        offerer1 = offerers_factories.UserOffererFactory(user=pro_user).offerer
        offerer2 = offerers_factories.UserOffererFactory(user=pro_user).offerer

        venue1 = offerers_factories.VenueFactory(managingOfferer=offerer1)
        venue2 = offerers_factories.VenueFactory(managingOfferer=offerer2)

        booked_date = datetime.utcnow()

        booking1 = bookings_factories.BookingFactory(dateCreated=booked_date, stock__offer__venue=venue1)
        bookings_factories.BookingFactory(dateCreated=booked_date, stock__offer__venue=venue2)

        client = client.with_session_auth(pro_user.email)

        response = client.get(
            f"/bookings/csv?page=1&offererId={offerer1.id}&bookingStatusFilter=booked&bookingPeriodBeginningDate={(booked_date-timedelta(days=1)).strftime('%Y-%m-%d')}&bookingPeriodEndingDate={(booked_date+timedelta(days=1)).strftime('%Y-%m-%d')}"
        )
        reader = csv.DictReader(StringIO(response.data.decode("utf-8-sig")), delimiter=";")
        rows = list(reader)
        assert len(rows) == 1
        for row in rows:
            assert row["Structure"] == venue1.common_name
            assert row["Nom de l’offre"] == booking1.stock.offer.name
            assert (
                row["Localisation"]
                == f"{venue1.common_name} - {venue1.offererAddress.address.street} {venue1.offererAddress.address.postalCode} {venue1.offererAddress.address.city}"
            )


class Returns401Test:
    def test_return_403_if_user_is_not_authorized(self, client):
        user_offerer = offerers_factories.UserOffererFactory()
        # authorized offer
        offers_factories.OfferFactory(venue__managingOfferer=user_offerer.offerer)
        offer_unauthorized = offers_factories.OfferFactory()

        client = client.with_session_auth(user_offerer.user.email)
        expected_num_queries = 5  # session + user + venue + SELECT EXISTS user_offerer
        with assert_num_queries(expected_num_queries):
            response = client.get(f"/bookings/offer/{offer_unauthorized.id}/csv?event_date=2021-01-01&status=all")
            assert response.status_code == 403

        assert response.json == {"global": "You are not allowed to access this offer"}
