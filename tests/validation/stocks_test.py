from datetime import datetime, timedelta

import pytest

from models import ApiErrors, Venue, Provider
from routes.serialization import serialize
from tests.model_creators.generic_creators import create_offerer, create_venue
from tests.model_creators.specific_creators import create_offer_with_thing_product, create_offer_with_event_product
from utils.human_ids import humanize
from validation.routes.stocks import check_dates_are_allowed_on_new_stock, \
    check_dates_are_allowed_on_existing_stock, \
    check_stocks_are_editable_for_offer, check_stocks_are_editable_in_patch_stock


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
