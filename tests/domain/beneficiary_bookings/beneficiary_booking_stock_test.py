from datetime import datetime, timedelta

from domain.beneficiary_bookings.stock import Stock


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
