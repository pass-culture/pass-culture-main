from datetime import datetime, timedelta

import pytest

from models import ApiErrors, Venue, Provider
from routes.serialization import serialize
from tests.model_creators.generic_creators import create_offerer, create_venue
from tests.model_creators.specific_creators import create_offer_with_thing_product, create_offer_with_event_product
from utils.human_ids import humanize
from validation.routes.stocks import check_dates_are_allowed_on_new_stock, \
    check_dates_are_allowed_on_existing_stock, \
    check_stocks_are_editable_for_offer, check_stocks_are_editable_in_patch_stock, get_updated_fields_after_patch, \
    check_only_editable_fields_will_be_updated


class CheckDatesAreAllowedOnNewStockTest:
    class OfferIsOnThingTest:
        def test_raises_error_with_beginning_and_end_datetimes(self):
            # Given
            offer = create_offer_with_thing_product(Venue())
            beginningDatetime = datetime(2019, 2, 14)

            data = {
                'price': 0,
                'offerId': humanize(offer.id),
                'beginningDatetime': serialize(beginningDatetime),
                'endDatetime': serialize(beginningDatetime + timedelta(days=1))
            }

            # When
            with pytest.raises(ApiErrors) as e:
                check_dates_are_allowed_on_new_stock(data, offer)

            # Then
            assert e.value.errors['global'] == [
                'Impossible de mettre des dates de début et fin si l\'offre ne porte pas sur un évenement'
            ]

        def test_raises_error_with_beginning_datetime_only(self):
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
                'Impossible de mettre des dates de début et fin si l\'offre ne porte pas sur un évenement'
            ]

        def test_raises_error_with_end_datetime_only(self):
            # Given
            offer = create_offer_with_thing_product(Venue())
            beginningDatetime = datetime(2019, 2, 14)

            data = {
                'price': 0,
                'offerId': humanize(offer.id),
                'endDatetime': serialize(beginningDatetime)
            }

            # When
            with pytest.raises(ApiErrors) as e:
                check_dates_are_allowed_on_new_stock(data, offer)

            # Then
            assert e.value.errors['global'] == [
                'Impossible de mettre des dates de début et fin si l\'offre ne porte pas sur un évenement'
            ]

        def test_doesnt_raise_error_with_missing_booking_limit_datetime(self):
            # Given
            offer = create_offer_with_thing_product(Venue())
            beginningDatetime = datetime(2019, 2, 14)

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

        def test_doesnt_raise_error_with_none_booking_limit_datetime(self):
            # Given
            offer = create_offer_with_thing_product(Venue())
            data = {
                'price': 0,
                'offerId': humanize(offer.id),
                'bookingLimitDatetime': None
            }

            # Then
            try:
                check_dates_are_allowed_on_new_stock(data, offer)

            except ApiErrors:
                # Then
                assert pytest.fail("Should not fail with valid params")

    class OfferIsOnEventTest:
        def test_raises_error_with_missing_end_datetime(self):
            # Given
            offer = create_offer_with_event_product()
            beginningDatetime = datetime(2019, 2, 14)

            data = {
                'price': 0,
                'offerId': humanize(offer.id),
                'beginningDatetime': serialize(beginningDatetime),
                'bookingLimitDatetime': serialize(datetime(2019, 2, 14)),
            }

            # When
            with pytest.raises(ApiErrors) as e:
                check_dates_are_allowed_on_new_stock(data, offer)

            # Then
            assert e.value.errors['endDatetime'] == [
                'Ce paramètre est obligatoire'
            ]

        def test_raises_error_with_none_end_datetime(self):
            # Given
            offer = create_offer_with_event_product()
            beginningDatetime = datetime(2019, 2, 14)

            data = {
                'price': 0,
                'offerId': humanize(offer.id),
                'beginningDatetime': serialize(beginningDatetime),
                'endDatetime': None,
                'bookingLimitDatetime': serialize(datetime(2019, 2, 14)),
            }

            # When
            with pytest.raises(ApiErrors) as e:
                check_dates_are_allowed_on_new_stock(data, offer)

            # Then
            assert e.value.errors['endDatetime'] == [
                'Ce paramètre est obligatoire'
            ]

        def test_raises_error_with_missing_beginning_datetime(self):
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

        def test_raises_error_with_none_beginning_datetime(self):
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

        def test_raises_error_with_missing_booking_limit_datetime(self):
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

        def test_raises_error_with_none_booking_limit_datetime(self):
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
        def test_raises_error_with_beginning_datetime_only(self):
            # Given
            offer = create_offer_with_thing_product(Venue())
            data = {'beginningDatetime': serialize(datetime(2019, 2, 14))}

            # When
            with pytest.raises(ApiErrors) as e:
                check_dates_are_allowed_on_existing_stock(data, offer)

            # Then
            assert e.value.errors['global'] == [
                'Impossible de mettre des dates de début et fin si l\'offre ne porte pas sur un évenement'
            ]

        def test_raises_error_with_end_datetime_only(self):
            # Given
            offer = create_offer_with_thing_product(Venue())
            data = {'endDatetime': serialize(datetime(2019, 2, 14))}

            # When
            with pytest.raises(ApiErrors) as e:
                check_dates_are_allowed_on_existing_stock(data, offer)

            # Then
            assert e.value.errors['global'] == [
                'Impossible de mettre des dates de début et fin si l\'offre ne porte pas sur un évenement'
            ]

        def test_doesnt_raise_error_with_missing_booking_limit_datetime(self):
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

        def test_doesnt_raise_error_with_none_booking_limit_datetime(self):
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
        def test_raises_error_with_none_beginning_datetime(self):
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

        def test_raises_error_with_none_end_datetime(self):
            # Given
            offer = create_offer_with_event_product()
            data = {'endDatetime': None}

            # When
            with pytest.raises(ApiErrors) as e:
                check_dates_are_allowed_on_existing_stock(data, offer)

            # Then
            assert e.value.errors['endDatetime'] == [
                'Ce paramètre est obligatoire'
            ]

        def test_raises_error_with_none_booking_limit_datetime(self):
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

    def test_does_not_raise_an_error_when_offer_is_not_from_provider(self, app):
        # given
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        offer.lastProviderId = None
        offer.lastProvider = None

        # when
        check_stocks_are_editable_for_offer(offer)


class CheckStocksAreEditableInPatchStockTest:
    def test_fail_when_offer_is_from_titeliveprovider(self, app):
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
            check_stocks_are_editable_in_patch_stock(offer)

        # Then
        assert e.value.errors['global'] == [
            'Les offres importées ne sont pas modifiables'
        ]

    def test_does_not_raise_an_error_when_offer_is_not_from_provider(self, app):
        # given
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        offer.lastProviderId = None
        offer.lastProvider = None

        # when
        check_stocks_are_editable_in_patch_stock(offer)

    def test_does_not_raise_an_error_when_offer_is_not_from_allocine_provider(self, app):
        # given
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        offer.lastProviderId = None
        offer.lastProvider = None

        # when
        check_stocks_are_editable_in_patch_stock(offer)


class CheckOnlyEditableFieldsWillBeUpdatedTest:
    def test_raise_an_error_when_trying_to_update_a_non_editable_field_in_stock(self):
        # given
        editable_fields = ['price', 'bookingLimitDatetime', 'available']

        updated_fields = ['price', 'endDatetime']

        # When
        with pytest.raises(ApiErrors) as e:
            check_only_editable_fields_will_be_updated(updated_fields, editable_fields)

        # Then
        assert e.value.errors['global'] == [
            'Pour les offres importées, certains champs ne sont pas modifiables'
        ]

    def test_does_not_raise_an_error_when_trying_to_update_an_editable_field_in_stock(self):
        # given
        editable_fields = ['price', 'bookingLimitDatetime', 'available']

        updated_fields = ['price', 'bookingLimitDatetime']

        # then
        check_only_editable_fields_will_be_updated(updated_fields, editable_fields)

    def test_does_not_raise_an_error_when_there_is_no_update(self):
        # given
        editable_fields = ['price', 'bookingLimitDatetime', 'available']

        updated_fields = []

        # then
        check_only_editable_fields_will_be_updated(updated_fields, editable_fields)


class GetUpdatedFieldsAfterPatchTest:
    def test_should_return_updated_fields_after_pro_user_changes_one_field_in_stock(self):
        # given
        stock_before_update = {'available': None, 'beginningDatetime': '2020-02-08T14:30:00Z',
                               'bookingLimitDatetime': '2020-02-08T14:30:00Z', 'bookingRecapSent': None,
                               'dateCreated': '2020-01-29T14:33:08.746369Z',
                               'dateModified': '2020-01-29T14:33:08.746382Z',
                               'dateModifiedAtLastProvider': '2020-01-29T14:33:07.803374Z',
                               'endDatetime': '2020-02-08T14:30:01Z', 'fieldsUpdated': [], 'groupSize': 1, 'id': 'AGXA',
                               'idAtProviders': 'TW92aWU6MjY1NTcy%22222222311111#LOCAL/2020-02-08T15:30:00',
                               'isSoftDeleted': False, 'lastProviderId': 'BY', 'modelName': 'Stock', 'offerId': 'QY',
                               'price': 22.0, 'remainingQuantity': 0}

        stock_data = {'bookingLimitDatetime': '2020-02-08T12:30:00Z', 'id': 'AGXA'}

        # when
        stock_updated_fields = get_updated_fields_after_patch(stock_before_update, stock_data)

        # then
        assert set(stock_updated_fields) == {'bookingLimitDatetime'}

    def test_should_return_updated_fields_after_pro_user_action_in_stock(self):
        # given
        stock_before_update = {'available': None, 'beginningDatetime': '2020-02-08T14:30:00Z',
                               'bookingLimitDatetime': '2020-02-08T14:30:00Z', 'bookingRecapSent': None,
                               'dateCreated': '2020-01-29T14:33:08.746369Z',
                               'dateModified': '2020-01-29T14:33:08.746382Z',
                               'dateModifiedAtLastProvider': '2020-01-29T14:33:07.803374Z',
                               'endDatetime': '2020-02-08T14:30:01Z', 'fieldsUpdated': [], 'groupSize': 1, 'id': 'AGXA',
                               'idAtProviders': 'TW92aWU6MjY1NTcy%22222222311111#LOCAL/2020-02-08T15:30:00',
                               'isSoftDeleted': False, 'lastProviderId': 'BY', 'modelName': 'Stock', 'offerId': 'QY',
                               'price': 22.0, 'remainingQuantity': 0}

        stock_data = {'available': None, 'bookingLimitDatetime': '2020-02-08T12:30:00Z', 'id': 'AGXA', 'offerId': 'QY',
                      'offererId': 'A4', 'price': 25, 'beginningDatetime': '2020-02-08T14:30:00Z',
                      'endDatetime': '2020-02-08T14:30:01Z', 'beginningTime': '15:30', 'endTime': '15:30'}

        # when
        stock_updated_fields = get_updated_fields_after_patch(stock_before_update, stock_data)

        # then
        assert set(stock_updated_fields) == {'price', 'bookingLimitDatetime'}
