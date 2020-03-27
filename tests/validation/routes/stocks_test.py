from datetime import datetime, timedelta

import pytest

from models import ApiErrors, Venue, Provider
from repository import repository
from repository.provider_queries import get_provider_by_local_class
from routes.serialization import serialize
from tests.conftest import clean_database
from tests.model_creators.generic_creators import create_offerer, create_venue, create_stock
from tests.model_creators.specific_creators import create_offer_with_thing_product, create_offer_with_event_product
from utils.human_ids import humanize
from validation.routes.stocks import check_dates_are_allowed_on_new_stock, \
    check_dates_are_allowed_on_existing_stock, \
    check_stocks_are_editable_for_offer, check_stock_is_updatable, get_only_fields_with_value_to_be_updated, \
    check_only_editable_fields_will_be_updated


class CheckDatesAreAllowedOnNewStockTest:
    class OfferIsOnThingTest:
        def test_should_raise_error_with_beginning_datetime(self):
            # Given
            offer = create_offer_with_thing_product(Venue())
            beginningDatetime = datetime(2019, 2, 14)

            data = {
                'price': 0,
                'offerId': humanize(offer.id),
                'beginningDatetime': serialize(beginningDatetime)
            }

            # When
            with pytest.raises(ApiErrors) as e:
                check_dates_are_allowed_on_new_stock(data, offer)

            # Then
            assert e.value.errors['global'] == [
                'Impossible de mettre une date de début si l\'offre ne porte pas sur un évenement'
            ]


        def test_should_not_raise_error_with_missing_booking_limit_datetime(self):
            # Given
            offer = create_offer_with_thing_product(Venue())

            data = {
                'price': 0,
                'offerId': humanize(offer.id)
            }

            # When
            try:
                check_dates_are_allowed_on_new_stock(data, offer)

            except ApiErrors:
                # Then
                assert pytest.fail("Should not fail with valid params")

        def test_should_not_raise_error_with_none_booking_limit_datetime(self):
            # Given
            offer = create_offer_with_thing_product(Venue())
            data = {
                'price': 0,
                'offerId': humanize(offer.id),
                'bookingLimitDatetime': None
            }

            # When
            try:
                check_dates_are_allowed_on_new_stock(data, offer)

            except ApiErrors:
                # Then
                assert pytest.fail("Should not fail with valid params")

    class OfferIsOnEventTest:
        def test_should_raise_error_with_missing_beginning_datetime(self):
            # Given
            offer = create_offer_with_event_product()
            beginningDatetime = datetime(2019, 2, 14)

            data = {
                'price': 0,
                'offerId': humanize(offer.id),
                'endDatetime': serialize(beginningDatetime),
                'bookingLimitDatetime': serialize(datetime(2019, 2, 14)),
            }

            # When
            with pytest.raises(ApiErrors) as e:
                check_dates_are_allowed_on_new_stock(data, offer)

            # Then
            assert e.value.errors['beginningDatetime'] == [
                'Ce paramètre est obligatoire'
            ]

        def test_should_raise_error_with_none_beginning_datetime(self):
            # Given
            offer = create_offer_with_event_product()
            data = {
                'price': 0,
                'offerId': humanize(offer.id),
                'beginningDatetime': None,
                'endDatetime': serialize(datetime(2019, 2, 14)),
                'bookingLimitDatetime': serialize(datetime(2019, 2, 14))
            }

            # When
            with pytest.raises(ApiErrors) as e:
                check_dates_are_allowed_on_new_stock(data, offer)

            # Then
            assert e.value.errors['beginningDatetime'] == [
                'Ce paramètre est obligatoire'
            ]

        def test_should_raise_error_with_missing_booking_limit_datetime(self):
            # Given
            offer = create_offer_with_event_product()
            beginningDatetime = datetime(2019, 2, 14)

            data = {
                'price': 0,
                'offerId': humanize(offer.id),
                'endDatetime': serialize(beginningDatetime),
                'beginningDatetime': serialize(beginningDatetime)
            }

            # When
            with pytest.raises(ApiErrors) as e:
                check_dates_are_allowed_on_new_stock(data, offer)

            # Then
            assert e.value.errors['bookingLimitDatetime'] == [
                'Ce paramètre est obligatoire'
            ]

        def test_should_raise_error_with_none_booking_limit_datetime(self):
            # Given
            offer = create_offer_with_event_product()
            data = {
                'price': 0,
                'offerId': humanize(offer.id),
                'bookingLimitDatetime': None,
                'endDatetime': serialize(datetime(2019, 2, 14)),
                'beginningDatetime': serialize(datetime(2019, 2, 14))
            }

            # When
            with pytest.raises(ApiErrors) as e:
                check_dates_are_allowed_on_new_stock(data, offer)

            # Then
            assert e.value.errors['bookingLimitDatetime'] == [
                'Ce paramètre est obligatoire'
            ]


class CheckDatesAreAllowedOnExistingStockTest:
    class OfferIsOnThingTest:
        def test_should_raise_error_with_beginning_datetime(self):
            # Given
            offer = create_offer_with_thing_product(Venue())
            data = {'beginningDatetime': serialize(datetime(2019, 2, 14))}

            # When
            with pytest.raises(ApiErrors) as e:
                check_dates_are_allowed_on_existing_stock(data, offer)

            # Then
            assert e.value.errors['global'] == [
                'Impossible de mettre une date de début si l\'offre ne porte pas sur un évenement'
            ]


        def test_should_not_raise_error_with_missing_booking_limit_datetime(self):
            # Given
            offer = create_offer_with_thing_product(Venue())
            beginningDatetime = datetime(2019, 2, 14)

            data = {
                'price': 0,
                'offerId': humanize(offer.id),
            }

            try:
                check_dates_are_allowed_on_existing_stock(data, offer)

            except ApiErrors:
                # Then
                assert pytest.fail("Should not fail with valid params")

        def test_should_not_raise_error_with_none_booking_limit_datetime(self):
            # Given
            offer = create_offer_with_thing_product(Venue())
            data = {
                'price': 0,
                'offerId': humanize(offer.id),
                'bookingLimitDatetime': None,
            }

            # Then
            try:
                check_dates_are_allowed_on_existing_stock(data, offer)

            except ApiErrors:
                # Then
                assert pytest.fail("Should not fail with valid params")

    class OfferIsOnEventTest:
        def test_should_raise_error_with_none_beginning_datetime(self):
            # Given
            offer = create_offer_with_event_product()
            data = {'beginningDatetime': None}

            # When
            with pytest.raises(ApiErrors) as e:
                check_dates_are_allowed_on_existing_stock(data, offer)

            # Then
            assert e.value.errors['beginningDatetime'] == [
                'Ce paramètre est obligatoire'
            ]


        def test_should_raise_error_with_none_booking_limit_datetime(self):
            # Given
            offer = create_offer_with_event_product()
            data = {
                'price': 0,
                'offerId': humanize(offer.id),
                'bookingLimitDatetime': None,
                'endDatetime': serialize(datetime(2019, 2, 14)),
                'beginningDatetime': serialize(datetime(2019, 2, 14))
            }

            # When
            with pytest.raises(ApiErrors) as e:
                check_dates_are_allowed_on_existing_stock(data, offer)

            # Then
            assert e.value.errors['bookingLimitDatetime'] == [
                'Ce paramètre est obligatoire'
            ]


class CheckStocksAreEditableForOfferTest:
    def test_fail_when_offer_is_from_provider(self, app):
        # Given
        provider = Provider()
        provider.name = 'myProvider'
        provider.localClass = 'TiteLiveClass'
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        offer.lastProviderId = 21
        offer.lastProvider = provider

        # When
        with pytest.raises(ApiErrors) as e:
            check_stocks_are_editable_for_offer(offer)

        # Then
        assert e.value.errors['global'] == [
            'Les offres importées ne sont pas modifiables'
        ]

    def test_does_not_raise_an_error_when_offer_is_not_from_provider(self):
        # given
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue, last_provider_id=None)

        # when
        check_stocks_are_editable_for_offer(offer)


class CheckStockIsUpdatableTest:
    @clean_database
    def test_fail_when_offer_is_from_titeliveprovider(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer)
        provider = get_provider_by_local_class('TiteLiveStocks')
        offer = create_offer_with_thing_product(venue, last_provider_id=provider.id, last_provider=provider)
        stock = create_stock(offer=offer, available=10, id_at_providers='test')

        repository.save(stock)

        # When
        with pytest.raises(ApiErrors) as error:
            check_stock_is_updatable(stock)

        # Then
        assert error.value.errors['global'] == [
            'Les offres importées ne sont pas modifiables'
        ]

    @clean_database
    def test_fail_when_offer_is_from_librairesprovider(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer)
        provider = get_provider_by_local_class('LibrairesStocks')
        offer = create_offer_with_thing_product(venue, last_provider_id=provider.id, last_provider=provider)
        stock = create_stock(offer=offer, available=10, id_at_providers='test')

        repository.save(stock)

        # When
        with pytest.raises(ApiErrors) as error:
            check_stock_is_updatable(stock)

        # Then
        assert error.value.errors['global'] == [
            'Les offres importées ne sont pas modifiables'
        ]

    @clean_database
    def test_does_not_raise_an_error_when_offer_is_not_from_provider(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock = create_stock(offer=offer, available=10)

        # When
        try:
            check_stock_is_updatable(stock)

        except ApiErrors:
            # Then
            assert pytest.fail("Should not fail with valid params")

    @clean_database
    def test_does_not_raise_an_error_when_offer_is_from_allocine_provider(self, app):
        # given
        offerer = create_offerer()
        venue = create_venue(offerer)
        provider = get_provider_by_local_class('AllocineStocks')
        offer = create_offer_with_thing_product(venue, last_provider_id=provider.id)
        stock = create_stock(offer=offer, available=10, id_at_providers='test')

        repository.save(stock)

        # When
        try:
            check_stock_is_updatable(stock)

        except ApiErrors:
            # Then
            assert pytest.fail("Should not fail with valid params")


class CheckOnlyEditableFieldsWillBeUpdatedTest:
    def test_raise_an_error_when_no_editable_fields_in_stock(self):
        # Given
        editable_fields = []

        updated_fields = ['price', 'endDatetime']

        # When
        with pytest.raises(ApiErrors) as error:
            check_only_editable_fields_will_be_updated(updated_fields, editable_fields)

        # Then
        assert error.value.errors['global'] == [
            'Pour les offres importées, certains champs ne sont pas modifiables'
        ]

    def test_raise_an_error_when_trying_to_update_a_non_editable_field_in_stock(self):
        # Given
        editable_fields = ['price', 'bookingLimitDatetime', 'available']

        updated_fields = ['price', 'endDatetime']

        # When
        with pytest.raises(ApiErrors) as error:
            check_only_editable_fields_will_be_updated(updated_fields, editable_fields)

        # Then
        assert error.value.errors['global'] == [
            'Pour les offres importées, certains champs ne sont pas modifiables'
        ]

    def test_does_not_raise_an_error_when_trying_to_update_an_editable_field_in_stock(self):
        # Given
        editable_fields = ['price', 'bookingLimitDatetime', 'available']

        updated_fields = ['price', 'bookingLimitDatetime']

        # When
        try:
            check_only_editable_fields_will_be_updated(updated_fields, editable_fields)

        except ApiErrors:
            # Then
            assert pytest.fail("Should not fail with valid params")

    def test_does_not_raise_an_error_when_there_is_no_update(self):
        # Given
        editable_fields = ['price', 'bookingLimitDatetime', 'available']

        updated_fields = []

        # When
        try:
            check_only_editable_fields_will_be_updated(updated_fields, editable_fields)

        except ApiErrors:
            # Then
            assert pytest.fail("Should not fail with valid params")


class GetOnlyFieldsWithValueToBeUpdatedTest:
    def when_new_stock_data_contains_only_modified_fields(self):
        # Given
        stock_before_update = {'available': None, 'beginningDatetime': '2020-02-08T14:30:00Z',
                               'bookingLimitDatetime': '2020-02-08T14:30:00Z',
                               'dateCreated': '2020-01-29T14:33:08.746369Z',
                               'dateModified': '2020-01-29T14:33:08.746382Z',
                               'dateModifiedAtLastProvider': '2020-01-29T14:33:07.803374Z',
                               'endDatetime': '2020-02-08T14:30:01Z', 'fieldsUpdated': [], 'id': 'AGXA',
                               'idAtProviders': 'TW92aWU6MjY1NTcy%22222222311111#LOCAL/2020-02-08T15:30:00',
                               'isSoftDeleted': False, 'lastProviderId': 'BY', 'modelName': 'Stock', 'offerId': 'QY',
                               'price': 22.0, 'remainingQuantity': 0}

        stock_data = {'bookingLimitDatetime': '2020-02-08T12:30:00Z'}

        # When
        stock_updated_fields = get_only_fields_with_value_to_be_updated(stock_before_update, stock_data)

        # Then
        assert set(stock_updated_fields) == {'bookingLimitDatetime'}

    def when_new_stock_data_contains_all_fields(self):
        # Given
        stock_before_update = {'available': None, 'beginningDatetime': '2020-02-08T14:30:00Z',
                               'bookingLimitDatetime': '2020-02-08T14:30:00Z',
                               'dateCreated': '2020-01-29T14:33:08.746369Z',
                               'dateModified': '2020-01-29T14:33:08.746382Z',
                               'dateModifiedAtLastProvider': '2020-01-29T14:33:07.803374Z',
                               'endDatetime': '2020-02-08T14:30:01Z', 'fieldsUpdated': [], 'id': 'AGXA',
                               'idAtProviders': 'TW92aWU6MjY1NTcy%22222222311111#LOCAL/2020-02-08T15:30:00',
                               'isSoftDeleted': False, 'lastProviderId': 'BY', 'modelName': 'Stock', 'offerId': 'QY',
                               'price': 22.0, 'remainingQuantity': 0}

        stock_data = {'available': None, 'bookingLimitDatetime': '2020-02-08T12:30:00Z', 'id': 'AGXA', 'offerId': 'QY',
                      'offererId': 'A4', 'price': 25, 'beginningDatetime': '2020-02-08T14:30:00Z',
                      'endDatetime': '2020-02-08T14:30:01Z', 'beginningTime': '15:30', 'endTime': '15:30'}

        # When
        stock_updated_fields = get_only_fields_with_value_to_be_updated(stock_before_update, stock_data)

        # Then
        assert set(stock_updated_fields) == {'price', 'bookingLimitDatetime'}
