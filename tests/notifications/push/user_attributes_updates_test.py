from datetime import datetime

import pytest

from pcapi.core.bookings.factories import BookingFactory
from pcapi.core.offers.factories import OfferFactory
from pcapi.core.testing import assert_num_queries
from pcapi.core.users.factories import BeneficiaryFactory
from pcapi.notifications.push.user_attributes_updates import BATCH_DATETIME_FORMAT
from pcapi.notifications.push.user_attributes_updates import TRACKED_PRODUCT_IDS
from pcapi.notifications.push.user_attributes_updates import get_user_attributes


pytestmark = pytest.mark.usefixtures("db_session")

MAX_BATCH_PARAMETER_SIZE = 30


class GetUserAttributesTest:
    def test_get_attributes(self):
        user = BeneficiaryFactory(dateOfBirth=datetime(2000, 1, 1))
        offer = OfferFactory(product__id=list(TRACKED_PRODUCT_IDS.keys())[0])
        b1 = BookingFactory(user=user, amount=10, stock__offer=offer)
        b2 = BookingFactory(user=user, amount=10, dateUsed=datetime(2021, 5, 6), stock__offer=offer)
        b3 = BookingFactory(user=user, amount=100, isCancelled=True)

        n_query_get_user = 1
        n_query_get_bookings = 1
        n_query_get_deposit = 1

        with assert_num_queries(n_query_get_user + n_query_get_bookings + n_query_get_deposit):
            attributes = get_user_attributes(user)

        last_date_created = max(booking.dateCreated for booking in [b1, b2, b3])

        assert attributes == {
            "date(u.date_of_birth)": "2000-01-01T00:00:00",
            "date(u.date_created)": user.dateCreated.strftime(BATCH_DATETIME_FORMAT),
            "date(u.deposit_expiration_date)": user.deposit.expirationDate.strftime(BATCH_DATETIME_FORMAT),
            "date(u.last_booking_date)": last_date_created.strftime(BATCH_DATETIME_FORMAT),
            "date(u.product_brut_x_use)": "2021-05-06T00:00:00",
            "u.credit": 48000,
            "u.departement_code": "75",
            "u.is_beneficiary": True,
            "ut.booking_categories": ["ThingType.AUDIOVISUEL"],
            "u.marketing_push_subscription": True,
            "u.postal_code": None,
        }

        for attribute in attributes:
            if attribute.startswith("date"):
                attribute = attribute.split("date(")[1].split(")")[0]

            parameter_name = attribute.split(".")[1]
            assert len(parameter_name) <= MAX_BATCH_PARAMETER_SIZE

    def test_get_attributes_without_bookings(self):
        user = BeneficiaryFactory()

        n_query_get_user = 1
        n_query_get_bookings = 1
        n_query_get_deposit = 1

        with assert_num_queries(n_query_get_user + n_query_get_bookings + n_query_get_deposit):
            attributes = get_user_attributes(user)

        assert attributes["date(u.last_booking_date)"] == None
        assert attributes["u.credit"] == 50000

        assert "ut.booking_categories" not in attributes
