from datetime import datetime, timedelta

from domain.beneficiary_bookings.stock import Stock


def create_domain_beneficiary_booking_stock(self):
    return Stock(
        id=1,
        quantity=None,
        offerId=1,
        price=12.99,
        dateCreated=datetime(2019, 1, 5),
        dateModified=datetime(2019, 1, 7),
        beginningDatetime=datetime.utcnow() - timedelta(days=1),
        bookingLimitDatetime=datetime.utcnow() - timedelta(days=2),
        isSoftDeleted=False,
        isOfferActive=True,
    )


class StockTest:
    class HasBookingLimitDatetimesPassedTest:
        def should_returns_true_when_stock_has_booking_limit_datetime_is_passed(self):
            # Given
            stock = Stock(
                id=1,
                quantity=None,
                offerId=1,
                price=12.99,
                dateCreated=datetime(2019, 1, 5),
                dateModified=datetime(2019, 1, 7),
                beginningDatetime=datetime(2019, 2, 5),
                bookingLimitDatetime=datetime(2019, 2, 3),
                isSoftDeleted=False,
                isOfferActive=True,
            )

            # When / Then
            assert stock.has_booking_limit_datetime_passed is True

        def should_returns_false_when_stock_has_future_booking_limit_datetime(self):
            # Given
            stock = Stock(
                id=1,
                quantity=None,
                offerId=1,
                price=12.99,
                dateCreated=datetime(2019, 1, 5),
                dateModified=datetime(2019, 1, 7),
                beginningDatetime=datetime.now() + timedelta(days=4),
                bookingLimitDatetime=datetime.now() + timedelta(days=2),
                isSoftDeleted=False,
                isOfferActive=True,
            )

            # When / Then
            assert stock.has_booking_limit_datetime_passed is False

    class IsAvailableForBookingTest:
        def should_not_be_available_when_booking_limit_datetime_has_passed(self):
            # Given
            limit_datetime = datetime.utcnow() - timedelta(days=2)
            stock = Stock(
                id=1,
                quantity=None,
                offerId=1,
                price=12.99,
                dateCreated=datetime(2019, 1, 5),
                dateModified=datetime(2019, 1, 7),
                beginningDatetime=datetime.utcnow(),
                bookingLimitDatetime=limit_datetime,
                isSoftDeleted=False,
                isOfferActive=True,
            )

            # When
            is_available_for_booking = stock.is_available_for_booking

            # Then
            assert not is_available_for_booking

        def should_not_be_available_when_offer_is_not_active(self):
            # Given
            stock = Stock(
                id=1,
                quantity=None,
                offerId=1,
                price=12.99,
                dateCreated=datetime(2019, 1, 5),
                dateModified=datetime(2019, 1, 7),
                beginningDatetime=datetime.utcnow(),
                bookingLimitDatetime=datetime.utcnow() - timedelta(days=1),
                isSoftDeleted=False,
                isOfferActive=False,
            )

            # When
            is_available_for_booking = stock.is_available_for_booking

            # Then
            assert not is_available_for_booking

        def should_not_be_available_when_stock_is_soft_deleted(self):
            # Given
            stock = Stock(
                id=1,
                quantity=None,
                offerId=1,
                price=12.99,
                dateCreated=datetime(2019, 1, 5),
                dateModified=datetime(2019, 1, 7),
                beginningDatetime=datetime.utcnow(),
                bookingLimitDatetime=datetime.utcnow() - timedelta(days=1),
                isSoftDeleted=True,
                isOfferActive=True,
            )

            # When
            is_available_for_booking = stock.is_available_for_booking

            # Then
            assert not is_available_for_booking

        def should_return_false_when_offer_is_event_with_passed_begining_datetime(self):
            # Given
            stock = Stock(
                id=1,
                quantity=None,
                offerId=1,
                price=12.99,
                dateCreated=datetime(2019, 1, 5),
                dateModified=datetime(2019, 1, 7),
                beginningDatetime=datetime.utcnow() - timedelta(days=1),
                bookingLimitDatetime=datetime.utcnow() - timedelta(days=2),
                isSoftDeleted=False,
                isOfferActive=True,
            )

            # When
            is_available_for_booking = stock.is_available_for_booking

            # Then
            assert not is_available_for_booking

        def test_should_return_true_when_stock_requirements_are_fulfilled(self):
            # Given
            stock = Stock(
                id=1,
                quantity=None,
                offerId=1,
                price=12.99,
                dateCreated=datetime(2019, 1, 5),
                dateModified=datetime(2019, 1, 7),
                beginningDatetime=datetime.utcnow() + timedelta(days=2),
                bookingLimitDatetime=datetime.utcnow() + timedelta(days=1),
                isSoftDeleted=False,
                isOfferActive=True,
            )

            # When
            is_available_for_booking = stock.is_available_for_booking

            # Then
            assert is_available_for_booking
