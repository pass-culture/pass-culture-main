from datetime import datetime

from freezegun import freeze_time

from domain.offers import find_first_matching_booking_from_offer_by_user, \
    has_at_least_one_stock_in_the_future, \
    has_remaining_stocks, is_from_allocine, update_is_active_status
from models import Offer
from tests.conftest import clean_database
from tests.model_creators.generic_creators import (create_booking,
                                                   create_deposit,
                                                   create_offerer,
                                                   create_provider,
                                                   create_stock, create_user,
                                                   create_venue)
from tests.model_creators.specific_creators import \
    create_offer_with_event_product


class UpdateIsActiveStatusTest:
    @clean_database
    def test_activate_offer(self, app):
        # given
        offerer = create_offerer()
        venue = create_venue(offerer)
        offers = [create_offer_with_event_product(venue, is_active=True),
                  create_offer_with_event_product(venue, is_active=False)]
        status = True

        # when
        updated_offers = update_is_active_status(offers, status)

        # then
        for updated_offer in updated_offers:
            assert updated_offer.isActive

    @clean_database
    def test_deactivate_offer(self, app):
        # given
        offerer = create_offerer()
        venue = create_venue(offerer)
        offers = [create_offer_with_event_product(venue, is_active=True),
                  create_offer_with_event_product(venue, is_active=False)]
        status = False

        # when
        updated_offers = update_is_active_status(offers, status)

        # then
        for updated_offer in updated_offers:
            assert not updated_offer.isActive

    @clean_database
    def test_deactivate_offer_should_keep_booking_state(self, app):
        # given
        user = create_user()
        offerer = create_offerer()
        venue = create_venue(offerer)
        existing_offer = create_offer_with_event_product(venue, is_active=True)
        stock = create_stock(offer=existing_offer)
        booking = create_booking(user=user, stock=stock)
        offers = [existing_offer]
        status = False

        # when
        updated_offers = update_is_active_status(offers, status)

        # then
        assert any(not updated_offer.isActive for updated_offer in updated_offers)
        assert not booking.isCancelled


class HasRemainingStocksTest:
    def test_should_return_true_when_at_least_one_stock_is_unlimited(self):
        # Given
        stock1 = create_stock(available=None)
        stock2 = create_stock(available=10)
        stocks = [stock1, stock2]

        # When
        result = has_remaining_stocks(stocks=stocks)

        # Then
        assert result is True

    def test_should_return_true_when_at_least_one_stock_is_superior_to_zero(self):
        # Given
        stock1 = create_stock(available=0)
        stock1.remainingQuantity = 0
        stock2 = create_stock(available=10)
        stock2.remainingQuantity = 8
        stocks = [stock1, stock2]

        # When
        result = has_remaining_stocks(stocks=stocks)

        # Then
        assert result is True

    def test_should_return_false_when_no_stock_available(self):
        # Given
        stock1 = create_stock(available=0)
        stock1.remainingQuantity = 0
        stock2 = create_stock(available=0)
        stock2.remainingQuantity = 0
        stocks = [stock1, stock2]

        # When
        result = has_remaining_stocks(stocks=stocks)

        # Then
        assert result is False


class HasStocksInFutureTest:
    @freeze_time('2020-01-10 10:00:00')
    def test_should_return_true_when_at_least_one_stock_has_no_booking_limit_date_time(self):
        # Given
        stock1 = create_stock(available=0, booking_limit_datetime=None)
        stock1.remainingQuantity = 0
        stock2 = create_stock(available=0)
        stock2.remainingQuantity = 0
        stocks = [stock1, stock2]

        # When
        result = has_at_least_one_stock_in_the_future(stocks)

        # Then
        assert result is True

    @freeze_time('2020-01-10 10:00:00')
    def test_should_return_true_when_at_least_one_stock_has_a_booking_limit_date_time_after_now(self):
        # Given
        stock1 = create_stock(available=0, booking_limit_datetime=datetime(2020, 1, 8, 9, 0, 0))
        stock1.remainingQuantity = 0
        stock2 = create_stock(available=0)
        stock2.remainingQuantity = 0
        stocks = [stock1, stock2]

        # When
        result = has_at_least_one_stock_in_the_future(stocks)

        # Then
        assert result is True

    @freeze_time('2020-01-10 10:00:00')
    def test_should_return_false_when_stocks_are_expired(self):
        # Given
        stock1 = create_stock(available=0, booking_limit_datetime=datetime(2020, 1, 1, 9, 0, 0))
        stock1.remainingQuantity = 0
        stock2 = create_stock(available=0, booking_limit_datetime=datetime(2020, 1, 2, 9, 0, 0))
        stock2.remainingQuantity = 0
        stocks = [stock1, stock2]

        # When
        result = has_at_least_one_stock_in_the_future(stocks)

        # Then
        assert result is False


class IsFromAllocineTest:
    def test_should_return_true_when_offer_is_from_allocine_provider(self):
        # Given
        offer = Offer()
        offer.lastProviderId = 1
        offer.lastProvider = create_provider(local_class='AllocineStocks')

        # When
        result = is_from_allocine(offer)

        # Then
        assert result is True

    def test_should_return_false_when_offer_is_from_open_agenda(self):
        # Given
        offer = Offer()
        offer.lastProviderId = 2
        offer.lastProvider = create_provider(local_class='OpenAgenda')

        # When
        result = is_from_allocine(offer)

        # Then
        assert result is False

    def test_should_return_false_when_offer_is_not_imported(self):
        # Given
        offer = Offer()
        offer.lastProvider = None

        # When
        result = is_from_allocine(offer)

        # Then
        assert result is False


class FindFirstMatchingBookingFromOfferByUserTest:
    def test_should_return_nothing_when_no_bookings(self):
        # Given
        beneficiary = create_user()
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_event_product(venue=venue)

        # When
        booking = find_first_matching_booking_from_offer_by_user(offer, beneficiary)

        # Then
        assert booking is None

    def test_should_return_nothing_when_beneficiary_has_no_bookings(self):
        # Given
        beneficiary = create_user(idx=1)
        other_beneficiary = create_user(email='other_beneficiary@example.com', idx=2)
        create_deposit(user=other_beneficiary)
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_event_product(venue=venue)
        stock = create_stock(offer=offer)
        create_booking(user=other_beneficiary, stock=stock, date_created=datetime(2020, 1, 1))

        # When
        booking = find_first_matching_booking_from_offer_by_user(offer, beneficiary)

        # Then
        assert booking is None

    def test_should_return_first_booking_for_user(self):
        # Given
        beneficiary = create_user(idx=1)
        create_deposit(user=beneficiary)
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_event_product(venue=venue)
        stock = create_stock(offer=offer)
        create_booking(user=beneficiary, stock=stock, date_created=datetime(2020, 1, 3))
        my_booking = create_booking(user=beneficiary, stock=stock, date_created=datetime(2020, 1, 10))

        # When
        booking = find_first_matching_booking_from_offer_by_user(offer, beneficiary)

        # Then
        assert booking.userId == beneficiary.id
        assert booking.dateCreated == my_booking.dateCreated
