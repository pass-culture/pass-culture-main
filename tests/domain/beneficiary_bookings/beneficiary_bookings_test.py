from datetime import datetime

from freezegun import freeze_time

from domain.beneficiary_bookings.beneficiary_bookings import BeneficiaryBooking, compute_offer_is_fully_booked
from domain.beneficiary_bookings.stock import Stock


class BeneficiaryBookingTest:
    class IsFullyBookedTest:
        @freeze_time('2020-4-4')
        def should_returns_true_when_no_remaining_quantity_on_stocks(self):
            # Given
            stocks = [
                Stock(
                    id=1,
                    quantity=6,
                    offerId=1,
                    price=12.99,
                    dateCreated=datetime(2020, 1, 5),
                    dateModified=datetime(2020, 1, 7),
                    remainingQuantity=0,
                    beginningDatetime=datetime(2020, 2, 5),
                    bookingLimitDatetime=datetime(2020, 2, 3),
                    isSoftDeleted=False,
                    isOfferActive=True,
                ),
                Stock(
                    id=2,
                    quantity=4,
                    offerId=1,
                    price=12.99,
                    dateCreated=datetime(2020, 1, 5),
                    dateModified=datetime(2020, 1, 7),
                    remainingQuantity=0,
                    beginningDatetime=None,
                    bookingLimitDatetime=None,
                    isSoftDeleted=False,
                    isOfferActive=True,
                ),
            ]

            # When
            offer_is_fully_booked = compute_offer_is_fully_booked(stocks)

            # Then
            assert offer_is_fully_booked is True

        @freeze_time('2020-4-4')
        def should_returns_true_when_stocks_with_passed_booking_limit_datetimes_are_ignored(self):
            # Given
            stocks = [
                Stock(
                    id=1,
                    quantity=6,
                    offerId=1,
                    price=12.99,
                    dateCreated=datetime(2019, 1, 5),
                    dateModified=datetime(2019, 1, 7),
                    remainingQuantity=2,
                    beginningDatetime=datetime(2019, 2, 5),
                    bookingLimitDatetime=datetime(2019, 2, 3),
                    isSoftDeleted=False,
                    isOfferActive=True,
                ),
                Stock(
                    id=2,
                    quantity=4,
                    offerId=1,
                    price=12.99,
                    dateCreated=datetime(2020, 1, 5),
                    dateModified=datetime(2020, 1, 7),
                    remainingQuantity=0,
                    beginningDatetime=None,
                    bookingLimitDatetime=None,
                    isSoftDeleted=False,
                    isOfferActive=True,
                ),
            ]

            # When
            offer_is_fully_booked = compute_offer_is_fully_booked(stocks)

            # Then
            assert offer_is_fully_booked is True

        def should_returns_false_when_stocks_have_no_available_quantity(self):
            # Given
            stocks = [
                Stock(
                    id=1,
                    quantity=None,
                    offerId=1,
                    price=12.99,
                    dateCreated=datetime(2019, 1, 5),
                    dateModified=datetime(2019, 1, 7),
                    remainingQuantity=2,
                    beginningDatetime=datetime(2019, 2, 5),
                    bookingLimitDatetime=datetime(2019, 2, 3),
                    isSoftDeleted=False,
                    isOfferActive=True,
                )
            ]

            # When
            offer_is_fully_booked = compute_offer_is_fully_booked(stocks)

            # Then
            assert offer_is_fully_booked is False
