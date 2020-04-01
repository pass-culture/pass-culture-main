from datetime import datetime, timedelta

import pytest
from freezegun import freeze_time

from domain.stocks import delete_stock_and_cancel_bookings, TooLateToDeleteError
from tests.model_creators.generic_creators import create_booking, create_user, create_stock

user1 = create_user()
user2 = create_user()
user3 = create_user()
user4 = create_user()


@freeze_time('2019-05-07 09:21:34')
class DeleteStockAndCancelBookingsTest:
    class WhenProductIsAThing:
        def setup_method(self, method):
            self.stock = create_stock(is_soft_deleted=False)

        def test_the_stock_is_soft_deleted(self):
            # when
            delete_stock_and_cancel_bookings(self.stock)

            # then
            assert self.stock.isSoftDeleted

        def test_only_unused_bookings_are_cancelled_and_returned(self):
            # given
            self.stock.bookings = [
                create_booking(user=user1, is_cancelled=False, is_used=True),
                create_booking(user=user2, is_cancelled=False, is_used=False)
            ]

            # when
            bookings = delete_stock_and_cancel_bookings(self.stock)

            # then
            assert all(map(lambda b: b.isCancelled, bookings))
            assert all(map(lambda b: not b.isUsed, bookings))

        def test_should_not_return_previously_cancelled_bookings(self):
            # Given
            booking1 = create_booking(user=user1, is_cancelled=False, is_used=True)
            booking2 = create_booking(user=user2, is_cancelled=False, is_used=False)
            booking3 = create_booking(user=user3, is_cancelled=True, is_used=False)
            booking4 = create_booking(user=user4, is_cancelled=True, is_used=True)
            self.stock.bookings = [
                booking1, booking2, booking3, booking4
            ]

            # When
            bookings = delete_stock_and_cancel_bookings(self.stock)

            # Then
            assert bookings == [booking2]
            assert all(map(lambda b: not b.isUsed, bookings))

    class WhenProductIsAnEvent:
        class WhenLessThan48HoursAfterItEnds:
            def setup_method(self, method):
                now = datetime.utcnow()
                self.stock = create_stock(beginning_datetime=now - timedelta(days=1), is_soft_deleted=False)

            def test_the_stock_is_soft_deleted(self):
                # when
                delete_stock_and_cancel_bookings(self.stock)

                # then
                assert self.stock.isSoftDeleted

            def test_all_bookings_are_cancelled(self):
                # given
                self.stock.bookings = [
                    create_booking(user=user1, is_cancelled=False, is_used=False),
                    create_booking(user=user2, is_cancelled=False, is_used=False),
                ]

                # when
                bookings = delete_stock_and_cancel_bookings(self.stock)

                # then
                assert all(map(lambda b: b.isCancelled, bookings))

            def test_should_not_return_previously_cancelled_bookings(self):
                # Given
                booking1 = create_booking(user=user1, is_cancelled=False, is_used=True)
                booking2 = create_booking(user=user2, is_cancelled=False, is_used=False)
                booking3 = create_booking(user=user3, is_cancelled=True, is_used=False)
                booking4 = create_booking(user=user4, is_cancelled=True, is_used=True)
                self.stock.bookings = [
                    booking1, booking2, booking3, booking4
                ]

                # When
                bookings = delete_stock_and_cancel_bookings(self.stock)

                # Then
                assert bookings == [booking1, booking2]

        class WhenMoreThan48HoursAfterItEnds:
            def setup_method(self, method):
                now = datetime.utcnow()
                self.stock = create_stock(beginning_datetime=now - timedelta(days=4), is_soft_deleted=False)

            def test_the_stock_is_not_soft_deleted(self):
                # when
                with pytest.raises(TooLateToDeleteError):
                    delete_stock_and_cancel_bookings(self.stock)

                # then
                assert not self.stock.isSoftDeleted

            def test_all_bookings_are_not_cancelled(self):
                # given
                self.stock.bookings = [
                    create_booking(user=user1, is_cancelled=False, is_used=False),
                    create_booking(user=user2, is_cancelled=False, is_used=False),
                ]

                # when
                with pytest.raises(TooLateToDeleteError):
                    bookings = delete_stock_and_cancel_bookings(self.stock)

                    # then
                    assert all(map(lambda b: not b.isCancelled, bookings))
