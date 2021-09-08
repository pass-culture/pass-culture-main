import pytest

import pcapi.core.bookings.api as bookings_api
import pcapi.core.bookings.factories as bookings_factories
from pcapi.core.finance import api
from pcapi.core.finance import models


pytestmark = pytest.mark.usefixtures("db_session")


def test_integration():
    booking = bookings_factories.BookingFactory()
    bookings_api.mark_as_used(booking)
    pricing = api.price_booking(booking)
    assert pricing.status == models.PricingStatus.VALIDATED
