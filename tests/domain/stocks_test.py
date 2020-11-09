from datetime import datetime
from datetime import timedelta

from freezegun import freeze_time
import pytest

from pcapi.domain.stocks import TooLateToDeleteError
from pcapi.domain.stocks import delete_stock_and_cancel_bookings
from pcapi.domain.stocks import have_beginning_date_been_modified
from pcapi.model_creators.generic_creators import create_booking
from pcapi.model_creators.generic_creators import create_provider
from pcapi.model_creators.generic_creators import create_stock
from pcapi.model_creators.generic_creators import create_user
from pcapi.model_creators.specific_creators import create_offer_with_event_product
from pcapi.model_creators.specific_creators import create_offer_with_thing_product
from pcapi.models import ApiErrors


user1 = create_user()
user2 = create_user()
user3 = create_user()
user4 = create_user()


@freeze_time('2019-05-07 09:21:34')
class DeleteStockAndCancelBookingsTest:
    class WhenProductIsAThing:
        def setup_method(self, method):
            self.stock = create_stock(is_soft_deleted=False)
            offer = create_offer_with_thing_product(venue=None, last_provider_id=None)
            self.stock.offer = offer

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
                offer = create_offer_with_event_product(venue=None, last_provider_id=None)
                self.stock.offer = offer

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
                offer = create_offer_with_event_product(venue=None, last_provider_id=None)
                self.stock.offer = offer

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

        class WhenOfferIsImported:
            def setup_method(self, method):
                self.stock = create_stock(is_soft_deleted=False)

            def test_the_stock_is_not_soft_deleted(self):
                # given
                provider = create_provider(local_class='TiteLiveStocks', idx=1)
                offer = create_offer_with_event_product(venue=None, last_provider_id=1, last_provider=provider)
                self.stock.offer = offer

                # when
                with pytest.raises(ApiErrors):
                    delete_stock_and_cancel_bookings(self.stock)

                # then
                assert not self.stock.isSoftDeleted

            def test_the_stock_is_soft_deleted(self):
                # given
                provider = create_provider(local_class='AllocineStocks', idx=1)
                offer = create_offer_with_event_product(venue=None, last_provider_id=1, last_provider=provider)
                self.stock.offer = offer

                # when
                delete_stock_and_cancel_bookings(self.stock)

                # then
                assert self.stock.isSoftDeleted


class CheckDateHaveBeenModifiedTest:
    def setup_method(self):
        self.stock = create_stock(beginning_datetime=datetime(2020, 4, 12, 12, 0, 0))

    def test_should_return_true_when_beginning_date_time_have_been_changed_with_ymdthmsfz_pattern(self):
        # Given
        request_data = {
            'beginningDatetime': '2020-02-08T14:30:00.000Z'
        }

        # When
        check_date = have_beginning_date_been_modified(request_data, self.stock.beginningDatetime)

        # Then
        assert check_date is True

    def test_should_return_true_when_beginning_date_time_have_been_changed_with_ymdthmsz_pattern(self):
        # Given
        request_data = {
            'beginningDatetime': '2020-02-08T14:30:00Z'
        }

        # When
        check_date = have_beginning_date_been_modified(request_data, self.stock.beginningDatetime)

        # Then
        assert check_date is True

    def test_should_return_true_when_beginning_date_time_have_been_changed_with_ymdthmsfs_pattern(self):
        # Given
        request_data = {
            'beginningDatetime': '2020-02-08T14:30:00'
        }

        # When
        check_date = have_beginning_date_been_modified(request_data, self.stock.beginningDatetime)

        # Then
        assert check_date is True

    def test_should_return_false_when_beginning_date_time_in_ymdthmsz_format_have_not_been_changed(self):
        # Given
        request_data = {
            'beginningDatetime': '2020-04-12T12:00:00Z'
        }

        # When
        check_date = have_beginning_date_been_modified(request_data, self.stock.beginningDatetime)

        # Then
        assert check_date is False

    def test_should_return_false_when_beginning_date_time_in_ymdthmsfz_format_have_not_been_changed(self):
        # Given
        request_data = {
            'beginningDatetime': '2020-04-12T12:00:00.000Z'
        }

        # When
        check_date = have_beginning_date_been_modified(request_data, self.stock.beginningDatetime)

        # Then
        assert check_date is False

    def test_should_return_false_when_beginning_date_time_in_ymdthmsfs_format_have_not_been_changed(self):
        # Given
        request_data = {
            'beginningDatetime': '2020-04-12T12:00:00'
        }

        # When
        check_date = have_beginning_date_been_modified(request_data, self.stock.beginningDatetime)

        # Then
        assert check_date is False
