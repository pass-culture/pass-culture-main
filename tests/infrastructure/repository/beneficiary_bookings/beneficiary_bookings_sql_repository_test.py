from datetime import datetime
from datetime import timedelta

import pytest

from pcapi.core.bookings.factories import BookingFactory
from pcapi.core.bookings.models import BookingStatus
from pcapi.core.offers.factories import EventOfferFactory
from pcapi.core.offers.factories import EventStockFactory
from pcapi.core.offers.factories import ThingOfferFactory
from pcapi.core.offers.factories import ThingStockFactory
from pcapi.core.users.factories import UserFactory
from pcapi.domain.beneficiary_bookings.beneficiary_bookings_with_stocks import BeneficiaryBookingsWithStocks
from pcapi.infrastructure.repository.beneficiary_bookings.beneficiary_bookings_sql_repository import (
    BeneficiaryBookingsSQLRepository,
)
from pcapi.infrastructure.repository.beneficiary_bookings.beneficiary_bookings_sql_repository import (
    _get_stocks_information,
)
from pcapi.utils.human_ids import humanize


class BeneficiaryBookingsSQLRepositoryTest:
    @pytest.mark.usefixtures("db_session")
    def test_should_return_beneficiary_bookings_with_expected_information(self, app):
        # Given
        user = UserFactory()
        offer = ThingOfferFactory(isActive=True, url="http://url.com", product__thumbCount=1)
        stock = ThingStockFactory(offer=offer, price=0, quantity=10)
        booking = BookingFactory(
            user=user,
            stock=stock,
            token="ABCDEF",
            dateCreated=datetime(2020, 4, 22, 0, 0),
            dateUsed=datetime(2020, 5, 5, 0, 0),
            isUsed=True,
            status=BookingStatus.USED,
            quantity=2,
        )

        # When
        result = BeneficiaryBookingsSQLRepository().get_beneficiary_bookings(beneficiary_id=user.id)

        # Then
        assert isinstance(result, BeneficiaryBookingsWithStocks)
        assert len(result.bookings) == 1
        expected_booking = result.bookings[0]
        assert expected_booking.amount == 0.0
        assert expected_booking.cancellationDate is None
        assert expected_booking.dateCreated == datetime(2020, 4, 22, 0, 0)
        assert expected_booking.dateUsed == datetime(2020, 5, 5, 0, 0)
        assert expected_booking.id == booking.id
        assert expected_booking.isCancelled is False
        assert expected_booking.isUsed is True
        assert expected_booking.status is BookingStatus.USED
        assert expected_booking.quantity == 2
        assert expected_booking.stockId == stock.id
        assert expected_booking.token == booking.token
        assert expected_booking.userId == user.id
        assert expected_booking.offerId == stock.offer.id
        assert expected_booking.name == stock.offer.name
        assert expected_booking.type == stock.offer.type
        assert expected_booking.url == stock.offer.url
        assert expected_booking.email == user.email
        assert expected_booking.beginningDatetime == stock.beginningDatetime
        assert expected_booking.venueId == stock.offer.venue.id
        assert expected_booking.departementCode == stock.offer.venue.departementCode
        assert (
            expected_booking.thumb_url == f"http://localhost/storage/thumbs/products/{humanize(stock.offer.productId)}"
        )

    @pytest.mark.usefixtures("db_session")
    def test_should_return_bookings_by_beneficiary_id(self, app):
        # Given
        user1 = UserFactory()
        user2 = UserFactory()
        offer = EventOfferFactory()
        stock = EventStockFactory(offer=offer)
        booking1 = BookingFactory(user=user1, stock=stock)
        BookingFactory(user=user2, stock=stock)

        # When
        result = BeneficiaryBookingsSQLRepository().get_beneficiary_bookings(beneficiary_id=user1.id)

        # Then
        assert len(result.bookings) == 1
        assert result.bookings[0].id == booking1.id

    @pytest.mark.usefixtures("db_session")
    def test_should_not_return_activation_bookings(self, app):
        # Given
        user = UserFactory()
        offer1 = EventOfferFactory(type="ThingType.ACTIVATION")
        offer2 = EventOfferFactory(type="ThingType.ACTIVATION")
        offer3 = EventOfferFactory(type="ThingType.ANY")
        stock1 = EventStockFactory(offer=offer1)
        stock2 = EventStockFactory(offer=offer2)
        stock3 = EventStockFactory(offer=offer3)
        BookingFactory(user=user, stock=stock1)
        BookingFactory(user=user, stock=stock2)
        booking3 = BookingFactory(user=user, stock=stock3)

        # When
        result = BeneficiaryBookingsSQLRepository().get_beneficiary_bookings(beneficiary_id=user.id)

        # Then
        assert len(result.bookings) == 1
        assert result.bookings[0].id == booking3.id

    @pytest.mark.usefixtures("db_session")
    def test_should_return_only_most_recent_booking_when_two_cancelled_on_same_stock(self, app):
        # Given
        now = datetime.utcnow()
        two_days_ago = now - timedelta(days=2)
        three_days_ago = now - timedelta(days=3)
        user = UserFactory()
        offer = EventOfferFactory()
        stock = EventStockFactory(offer=offer)
        booking1 = BookingFactory(user=user, stock=stock, dateCreated=two_days_ago, isCancelled=True)
        BookingFactory(user=user, stock=stock, dateCreated=three_days_ago, isCancelled=True)

        # When
        result = BeneficiaryBookingsSQLRepository().get_beneficiary_bookings(beneficiary_id=user.id)

        # Then
        assert len(result.bookings) == 1
        assert result.bookings[0].id == booking1.id

    @pytest.mark.usefixtures("db_session")
    def test_should_return_bookings(self, app):
        # Given
        now = datetime.utcnow()
        two_days = now + timedelta(days=2, hours=10)
        two_days_bis = now + timedelta(days=2, hours=20)
        three_days = now + timedelta(days=3)

        user = UserFactory()

        booking1 = BookingFactory(
            user=user,
            stock=EventStockFactory(
                beginningDatetime=three_days,
                bookingLimitDatetime=now,
            ),
        )
        booking2 = BookingFactory(
            user=user,
            stock=EventStockFactory(
                beginningDatetime=two_days,
                bookingLimitDatetime=now,
            ),
        )
        booking3 = BookingFactory(
            user=user,
            stock=EventStockFactory(
                beginningDatetime=two_days_bis,
                bookingLimitDatetime=now,
            ),
        )

        # When
        result = BeneficiaryBookingsSQLRepository().get_beneficiary_bookings(beneficiary_id=user.id)

        # Then
        assert len(result.bookings) == 3
        assert set(booking.id for booking in result.bookings) == {booking1.id, booking2.id, booking3.id}


class GetStocksInformationTest:
    @pytest.mark.usefixtures("db_session")
    def test_should_return_get_stocks_information(self, app):
        # Given
        offer = ThingOfferFactory(url="http://url.com")
        stock1 = ThingStockFactory(
            beginningDatetime=datetime(2020, 3, 5),
            bookingLimitDatetime=datetime(2020, 1, 6),
            dateCreated=datetime(2020, 1, 4),
            dateModified=datetime(2020, 1, 7),
            offer=offer,
            price=0,
        )
        stock2 = ThingStockFactory(
            beginningDatetime=datetime(2020, 4, 5),
            bookingLimitDatetime=datetime(2020, 2, 6),
            dateCreated=datetime(2020, 2, 4),
            dateModified=datetime(2020, 2, 7),
            offer=offer,
            price=12,
        )

        # When
        results = _get_stocks_information(offers_ids=[offer.id])

        # Then
        assert set(results) == {
            (
                datetime(2020, 1, 4, 0, 0),
                datetime(2020, 3, 5, 0, 0),
                datetime(2020, 1, 6, 0, 0),
                datetime(2020, 1, 7, 0, 0),
                offer.id,
                1000,
                0.00,
                stock1.id,
                False,
                True,
            ),
            (
                datetime(2020, 2, 4, 0, 0),
                datetime(2020, 4, 5, 0, 0),
                datetime(2020, 2, 6, 0, 0),
                datetime(2020, 2, 7, 0, 0),
                offer.id,
                1000,
                12.00,
                stock2.id,
                False,
                True,
            ),
        }
