from datetime import datetime, timedelta

from algolia.rules_engine import is_eligible_for_indexing, is_eligible_for_reindexing
from repository import repository
from tests.conftest import clean_database
from tests.model_creators.generic_creators import create_offerer, create_stock, create_venue, create_booking, \
    create_user, create_deposit
from tests.model_creators.specific_creators import create_offer_with_thing_product, create_offer_with_event_product

YESTERDAY = datetime.now() - timedelta(days=1)
TOMORROW = datetime.now() + timedelta(days=1)


class IsEligibleForIndexingTest:
    @clean_database
    def test_should_return_false_when_none_is_given(self, app):
        # Given
        offerer = create_offerer(is_active=True, validation_token=None)
        venue = create_venue(offerer=offerer, validation_token=None)
        offer = create_offer_with_thing_product(venue=venue, is_active=True)
        stock = create_stock(offer=offer, booking_limit_datetime=TOMORROW, available=None, is_soft_deleted=False)
        repository.save(stock)

        # When
        is_eligible = is_eligible_for_indexing(None)

        # Then
        assert is_eligible is False

    @clean_database
    def test_should_return_false_when_offerer_is_not_active(self, app):
        # Given
        offerer = create_offerer(is_active=False, validation_token=None)
        venue = create_venue(offerer=offerer, validation_token=None)
        offer = create_offer_with_thing_product(venue=venue, is_active=True)
        stock = create_stock(offer=offer, booking_limit_datetime=TOMORROW, available=None, is_soft_deleted=False)
        repository.save(stock)

        # When
        is_eligible = is_eligible_for_indexing(offer)

        # Then
        assert is_eligible is False

    @clean_database
    def test_should_return_false_when_offerer_is_active_but_is_not_validated(self, app):
        # Given
        offerer = create_offerer(is_active=True, validation_token='FAKE_TOKEN')
        venue = create_venue(offerer=offerer, validation_token=None)
        offer = create_offer_with_thing_product(venue=venue, is_active=True)
        stock = create_stock(offer=offer, booking_limit_datetime=TOMORROW, available=None, is_soft_deleted=False)
        repository.save(stock)

        # When
        is_eligible = is_eligible_for_indexing(offer)

        # Then
        assert is_eligible is False

    @clean_database
    def test_should_return_false_when_offer_is_not_active(self, app):
        # Given
        offerer = create_offerer(is_active=True, validation_token=None)
        venue = create_venue(offerer=offerer, validation_token=None)
        offer = create_offer_with_thing_product(venue=venue, is_active=False)
        stock = create_stock(offer=offer, booking_limit_datetime=TOMORROW, available=None, is_soft_deleted=False)
        repository.save(stock)

        # When
        is_eligible = is_eligible_for_indexing(offer)

        # Then
        assert is_eligible is False

    @clean_database
    def test_should_return_false_when_offer_has_no_remaining_quantity(self, app):
        # Given
        beneficiary = create_user()
        create_deposit(user=beneficiary)
        offerer = create_offerer(is_active=True, validation_token=None)
        venue = create_venue(offerer=offerer, validation_token=None)
        offer = create_offer_with_thing_product(venue=venue, is_active=True)
        stock1 = create_stock(offer=offer, booking_limit_datetime=TOMORROW, available=1, is_soft_deleted=False)
        stock2 = create_stock(offer=offer, booking_limit_datetime=TOMORROW, available=1, is_soft_deleted=False)
        booking1 = create_booking(user=beneficiary, stock=stock1)
        booking2 = create_booking(user=beneficiary, stock=stock2)
        repository.save(booking1, booking2)

        # When
        is_eligible = is_eligible_for_indexing(offer)

        # Then
        assert is_eligible is False

    @clean_database
    def test_should_return_false_when_booking_limit_datetime_is_outdated(self, app):
        # Given
        offerer = create_offerer(is_active=True, validation_token=None)
        venue = create_venue(offerer=offerer, validation_token=None)
        offer = create_offer_with_thing_product(venue=venue, is_active=True)
        stock = create_stock(offer=offer, booking_limit_datetime=YESTERDAY, available=None, is_soft_deleted=False)
        repository.save(stock)

        # When
        is_eligible = is_eligible_for_indexing(offer)

        # Then
        assert is_eligible is False

    @clean_database
    def test_should_return_false_when_all_stocks_are_soft_deleted(self, app):
        # Given
        offerer = create_offerer(is_active=True, validation_token=None)
        venue = create_venue(offerer=offerer, validation_token=None)
        offer = create_offer_with_thing_product(venue=venue, is_active=True)
        stock = create_stock(offer=offer, booking_limit_datetime=TOMORROW, available=None, is_soft_deleted=True)
        repository.save(stock)

        # When
        is_eligible = is_eligible_for_indexing(offer)

        # Then
        assert is_eligible is False

    @clean_database
    def test_should_return_false_when_venue_is_not_validated(self, app):
        # Given
        offerer = create_offerer(is_active=True, validation_token=None)
        venue = create_venue(offerer=offerer, validation_token='FAKE_TOKEN')
        offer = create_offer_with_thing_product(venue=venue, is_active=True)
        stock = create_stock(offer=offer, booking_limit_datetime=TOMORROW, available=None, is_soft_deleted=False)
        repository.save(stock)

        # When
        is_eligible = is_eligible_for_indexing(offer)

        # Then
        assert is_eligible is False

    @clean_database
    def test_should_return_true_when_offer_is_eligible(self, app):
        # Given
        offerer = create_offerer(is_active=True, validation_token=None)
        venue = create_venue(offerer=offerer, validation_token=None)
        offer = create_offer_with_thing_product(venue=venue, is_active=True)
        stock = create_stock(offer=offer, booking_limit_datetime=TOMORROW, available=1, is_soft_deleted=False)
        repository.save(stock)

        # When
        is_eligible = is_eligible_for_indexing(offer)

        # Then
        assert is_eligible is True

    @clean_database
    def test_should_return_true_when_offer_is_eligible_with_unlimited_stock(self, app):
        # Given
        offerer = create_offerer(is_active=True, validation_token=None)
        venue = create_venue(offerer=offerer, validation_token=None)
        offer = create_offer_with_thing_product(venue=venue, is_active=True)
        stock = create_stock(offer=offer, booking_limit_datetime=TOMORROW, available=None, is_soft_deleted=False)
        repository.save(stock)

        # When
        is_eligible = is_eligible_for_indexing(offer)

        # Then
        assert is_eligible is True

    @clean_database
    def test_should_return_true_when_offer_is_eligible_with_no_booking_datetime_limit(self, app):
        # Given
        offerer = create_offerer(is_active=True, validation_token=None)
        venue = create_venue(offerer=offerer, validation_token=None)
        offer = create_offer_with_thing_product(venue=venue, is_active=True)
        stock = create_stock(offer=offer, booking_limit_datetime=None, available=1, is_soft_deleted=False)
        repository.save(stock)

        # When
        is_eligible = is_eligible_for_indexing(offer)

        # Then
        assert is_eligible is True


class IsEligibleForReindexingTest:
    @clean_database
    def test_should_return_false_when_offer_name_has_not_changed(self, app):
        # Given
        offerer = create_offerer(is_active=True, validation_token=None)
        venue = create_venue(offerer=offerer, validation_token=None)
        offer = create_offer_with_thing_product(thing_name='super offre', venue=venue)
        stock = create_stock(offer=offer)
        repository.save(stock)

        # When
        result = is_eligible_for_reindexing(offer=offer, offer_details={'name': 'super offre', 'dateRange': []})

        # Then
        assert result is False

    @clean_database
    def test_should_return_true_when_offer_name_has_changed(self, app):
        # Given
        offerer = create_offerer(is_active=True, validation_token=None)
        venue = create_venue(offerer=offerer, validation_token=None)
        offer = create_offer_with_thing_product(thing_name='super offre de dingue', venue=venue)
        stock = create_stock(offer=offer)
        repository.save(stock)

        # When
        result = is_eligible_for_reindexing(offer=offer, offer_details={'name': 'super offre', 'dateRange': []})

        # Then
        assert result is True

    @clean_database
    def test_should_return_false_when_stocks_have_not_changed(self, app):
        # Given
        offerer = create_offerer(is_active=True, validation_token=None)
        venue = create_venue(offerer=offerer, validation_token=None)
        offer = create_offer_with_event_product(event_name='super offre', venue=venue)
        stock = create_stock(beginning_datetime=datetime(2020, 1, 1), end_datetime=datetime(2020, 1, 2), offer=offer)
        repository.save(stock)

        # When
        result = is_eligible_for_reindexing(offer=offer,
                                            offer_details={'name': 'super offre',
                                                           'dateRange': ['2020-01-01 00:00:00', '2020-01-02 00:00:00']})

        # Then
        assert result is False

    @clean_database
    def test_should_return_true_when_stocks_have_changed(self, app):
        # Given
        offerer = create_offerer(is_active=True, validation_token=None)
        venue = create_venue(offerer=offerer, validation_token=None)
        offer = create_offer_with_event_product(event_name='super offre', venue=venue)
        stock = create_stock(beginning_datetime=datetime(2020, 1, 1), end_datetime=datetime(2020, 1, 2), offer=offer)
        repository.save(stock)

        # When
        result = is_eligible_for_reindexing(offer=offer,
                                            offer_details={'name': 'super offre',
                                                           'dateRange': ['2019-01-01 00:00:00', '2019-01-02 00:00:00']})

        # Then
        assert result is True
