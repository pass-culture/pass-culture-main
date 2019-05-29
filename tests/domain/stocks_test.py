from datetime import datetime, timedelta

import pytest
from freezegun import freeze_time

from domain.stocks import delete_stock_and_cancel_bookings, TooLateToDeleteError
from tests.test_utils import create_stock, create_booking, create_user

user1 = create_user()
user2 = create_user()


@pytest.mark.standalone
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

        def test_unused_bookings_are_cancelled(self):
            # given
            self.stock.bookings = [
                create_booking(user1, is_used=True, is_cancelled=False),
                create_booking(user2, is_used=False, is_cancelled=False)
            ]

            # when
            bookings = delete_stock_and_cancel_bookings(self.stock)

            # then
            unused_bookings = filter(lambda b: not b.isUsed, bookings)
            assert all(map(lambda b: b.isCancelled, unused_bookings))

        def test_used_bookings_are_not_cancelled(self):
            # given
            self.stock.bookings = [
                create_booking(user1, is_used=True, is_cancelled=False),
                create_booking(user2, is_used=False, is_cancelled=False)
            ]

            # when
            bookings = delete_stock_and_cancel_bookings(self.stock)

            # then
            used_bookings = filter(lambda b: b.isUsed, bookings)
            assert all(map(lambda b: not b.isCancelled, used_bookings))

    class WhenProductIsAnEvent:
        class WhenMoreThan72HoursBeforeItStarts:
            def setup_method(self, method):
                now = datetime.utcnow()
                self.stock = create_stock(
                    beginning_datetime=now + timedelta(days=4),
                    end_datetime=now + timedelta(days=5),
                    is_soft_deleted=False
                )

            def test_the_stock_is_soft_deleted(self):
                # when
                delete_stock_and_cancel_bookings(self.stock)

                # then
                assert self.stock.isSoftDeleted

            def test_unused_bookings_are_cancelled(self):
                # given
                self.stock.bookings = [
                    create_booking(user1, is_used=False, is_cancelled=False),
                    create_booking(user2, is_used=False, is_cancelled=False),
                ]

                # when
                bookings = delete_stock_and_cancel_bookings(self.stock)

                # then
                unused_bookings = filter(lambda b: not b.isUsed, bookings)
                assert all(map(lambda b: b.isCancelled, unused_bookings))

            def test_used_bookings_are_not_cancelled(self):
                # given
                self.stock.bookings = [
                    create_booking(user1, is_used=True, is_cancelled=False),
                    create_booking(user2, is_used=True, is_cancelled=False),
                ]

                # when
                bookings = delete_stock_and_cancel_bookings(self.stock)

                # then
                used_bookings = filter(lambda b: b.isUsed, bookings)
                assert all(map(lambda b: not b.isCancelled, used_bookings))

        class WhenBetween72HoursBeforeItStartsAnd48HoursAfterItEnds:
            def setup_method(self, method):
                now = datetime.utcnow()
                self.stock = create_stock(
                    beginning_datetime=now - timedelta(days=1),
                    end_datetime=now + timedelta(days=1),
                    is_soft_deleted=False
                )

            def test_the_stock_is_soft_deleted(self):
                # when
                delete_stock_and_cancel_bookings(self.stock)

                # then
                assert self.stock.isSoftDeleted

            def test_unused_bookings_are_cancelled(self):
                # given
                self.stock.bookings = [
                    create_booking(user1, is_used=False, is_cancelled=False),
                    create_booking(user2, is_used=False, is_cancelled=False),
                ]

                # when
                bookings = delete_stock_and_cancel_bookings(self.stock)

                # then
                unused_bookings = filter(lambda b: not b.isUsed, bookings)
                assert all(map(lambda b: b.isCancelled, unused_bookings))

            def test_used_bookings_are_cancelled(self):
                # given
                self.stock.bookings = [
                    create_booking(user1, is_used=True, is_cancelled=False),
                    create_booking(user2, is_used=True, is_cancelled=False),
                ]

                # when
                bookings = delete_stock_and_cancel_bookings(self.stock)

                # then
                unused_bookings = filter(lambda b: b.isUsed, bookings)
                assert all(map(lambda b: b.isCancelled, unused_bookings))

        class WhenMoreThan48HoursAfterItEnds:
            def setup_method(self, method):
                now = datetime.utcnow()
                self.stock = create_stock(
                    beginning_datetime=now - timedelta(days=4),
                    end_datetime=now - timedelta(days=3),
                    is_soft_deleted=False
                )

            def test_the_stock_is_not_soft_deleted(self):
                # when
                with pytest.raises(TooLateToDeleteError):
                    delete_stock_and_cancel_bookings(self.stock)

                # then
                assert not self.stock.isSoftDeleted

            def test_unused_bookings_are_not_cancelled(self):
                # given
                self.stock.bookings = [
                    create_booking(user1, is_used=False, is_cancelled=False),
                    create_booking(user2, is_used=False, is_cancelled=False),
                ]

                # when
                with pytest.raises(TooLateToDeleteError):
                    bookings = delete_stock_and_cancel_bookings(self.stock)

                    # then
                    unused_bookings = filter(lambda b: not b.isUsed, bookings)
                    assert all(map(lambda b: not b.isCancelled, unused_bookings))

            def test_used_bookings_are_not_cancelled(self):
                # given
                self.stock.bookings = [
                    create_booking(user1, is_used=True, is_cancelled=False),
                    create_booking(user2, is_used=True, is_cancelled=False),
                ]

                # when
                with pytest.raises(TooLateToDeleteError):
                    bookings = delete_stock_and_cancel_bookings(self.stock)

                    # then
                    used_bookings = filter(lambda b: b.isUsed, bookings)
                    assert all(map(lambda b: not b.isCancelled, used_bookings))
