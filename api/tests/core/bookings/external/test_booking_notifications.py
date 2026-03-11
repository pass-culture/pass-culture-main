from datetime import timedelta

import pytest

from pcapi.core.bookings import constants
from pcapi.core.bookings import factories as bookings_factories
from pcapi.core.bookings.external.booking_notifications import notify_users_bookings_not_retrieved
from pcapi.core.external.batch import testing
from pcapi.core.offers import factories as offers_factories
from pcapi.core.users import factories as users_factories
from pcapi.utils import date as date_utils


@pytest.mark.usefixtures("db_session")
@pytest.mark.settings(SOON_EXPIRING_BOOKINGS_DAYS_BEFORE_EXPIRATION=3)
def test_notify_users_bookings_not_retrieved() -> None:
    user = users_factories.BeneficiaryGrant18Factory()
    stock = offers_factories.ThingStockFactory()
    creation_date = date_utils.get_naive_utc_now() - constants.BOOKINGS_AUTO_EXPIRY_DELAY + timedelta(days=3)

    # booking that will expire in three days
    booking = bookings_factories.BookingFactory(user=user, stock=stock, dateCreated=creation_date)

    notify_users_bookings_not_retrieved()
    assert len(testing.requests) == 1

    data = testing.requests[0]
    assert data["user_ids"] == [booking.userId]
    assert data["message"]["title"] == "Tu n'as pas récupéré ta réservation"
    assert (
        data["message"]["body"] == f'Vite, il ne te reste plus que 3 jours pour récupérer "{booking.stock.offer.name}"'
    )
