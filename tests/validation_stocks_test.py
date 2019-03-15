from datetime import datetime, timedelta

import pytest

from models import ApiErrors, Venue
from models.pc_object import serialize
from tests.test_utils import create_thing_offer, create_event_offer
from utils.human_ids import humanize
from validation.stocks import check_new_stock_has_dates, check_existing_stock_has_dates


@pytest.mark.standalone
class CheckNewStockHasDatesTest:
    class OfferIsOnThingTest:
        def test_raises_error_with_beginning_and_end_datetimes(self):
            # Given
            offer = create_thing_offer(Venue())
            beginningDatetime = datetime(2019, 2, 14)

            data = {
                'price': 0,
                'offerId': humanize(offer.id),
                'beginningDatetime': serialize(beginningDatetime),
                'endDatetime': serialize(beginningDatetime + timedelta(days=1))
            }

            # When
            with pytest.raises(ApiErrors) as e:
                check_new_stock_has_dates(data, offer)

            # Then
            assert e.value.errors['global'] == [
                'Impossible de mettre des dates de début et fin si l\'offre ne porte pas sur un évenement'
            ]

        def test_raises_error_with_beginning_datetime_only(self):
            # Given
            offer = create_thing_offer(Venue())
            beginningDatetime = datetime(2019, 2, 14)

            data = {
                'price': 0,
                'offerId': humanize(offer.id),
                'beginningDatetime': serialize(beginningDatetime)
            }

            # When
            with pytest.raises(ApiErrors) as e:
                check_new_stock_has_dates(data, offer)

            # Then
            assert e.value.errors['global'] == [
                'Impossible de mettre des dates de début et fin si l\'offre ne porte pas sur un évenement'
            ]

        def test_raises_error_with_end_datetime_only(self):
            # Given
            offer = create_thing_offer(Venue())
            beginningDatetime = datetime(2019, 2, 14)

            data = {
                'price': 0,
                'offerId': humanize(offer.id),
                'endDatetime': serialize(beginningDatetime)
            }

            # When
            with pytest.raises(ApiErrors) as e:
                check_new_stock_has_dates(data, offer)

            # Then
            assert e.value.errors['global'] == [
                'Impossible de mettre des dates de début et fin si l\'offre ne porte pas sur un évenement'
            ]

    class OfferIsOnEventTest:
        def test_raises_error_with_missing_end_datetime(self):
            # Given
            offer = create_event_offer()
            beginningDatetime = datetime(2019, 2, 14)

            data = {
                'price': 0,
                'offerId': humanize(offer.id),
                'beginningDatetime': serialize(beginningDatetime)
            }

            # When
            with pytest.raises(ApiErrors) as e:
                check_new_stock_has_dates(data, offer)

            # Then
            assert e.value.errors['endDatetime'] == [
                'Ce paramètre est obligatoire'
            ]

        def test_raises_error_with_none_end_datetime(self):
            # Given
            offer = create_event_offer()
            beginningDatetime = datetime(2019, 2, 14)

            data = {
                'price': 0,
                'offerId': humanize(offer.id),
                'beginningDatetime': serialize(beginningDatetime),
                'endDatetime': None
            }

            # When
            with pytest.raises(ApiErrors) as e:
                check_new_stock_has_dates(data, offer)

            # Then
            assert e.value.errors['endDatetime'] == [
                'Ce paramètre est obligatoire'
            ]

        def test_raises_error_with_missing_beginning_datetime(self):
            # Given
            offer = create_event_offer()
            beginningDatetime = datetime(2019, 2, 14)

            data = {
                'price': 0,
                'offerId': humanize(offer.id),
                'endDatetime': serialize(beginningDatetime)
            }

            # When
            with pytest.raises(ApiErrors) as e:
                check_new_stock_has_dates(data, offer)

            # Then
            assert e.value.errors['beginningDatetime'] == [
                'Ce paramètre est obligatoire'
            ]

        def test_raises_error_with_none_beginning_datetime(self):
            # Given
            offer = create_event_offer()
            data = {
                'price': 0,
                'offerId': humanize(offer.id),
                'beginningDatetime': None,
                'endDatetime': serialize(datetime(2019, 2, 14))
            }

            # When
            with pytest.raises(ApiErrors) as e:
                check_new_stock_has_dates(data, offer)

            # Then
            assert e.value.errors['beginningDatetime'] == [
                'Ce paramètre est obligatoire'
            ]


class CheckExistingStockHasDatesTest:
    class OfferIsOnThingTest:
        def test_raises_error_with_beginning_datetime_only(self):
            # Given
            offer = create_thing_offer(Venue())
            data = {'beginningDatetime': serialize(datetime(2019, 2, 14))}

            # When
            with pytest.raises(ApiErrors) as e:
                check_existing_stock_has_dates(data, offer)

            # Then
            assert e.value.errors['global'] == [
                'Impossible de mettre des dates de début et fin si l\'offre ne porte pas sur un évenement'
            ]

        def test_raises_error_with_end_datetime_only(self):
            # Given
            offer = create_thing_offer(Venue())
            data = {'endDatetime': serialize(datetime(2019, 2, 14))}

            # When
            with pytest.raises(ApiErrors) as e:
                check_existing_stock_has_dates(data, offer)

            # Then
            assert e.value.errors['global'] == [
                'Impossible de mettre des dates de début et fin si l\'offre ne porte pas sur un évenement'
            ]

    class OfferIsOnEventTest:
        def test_raises_error_with_none_beginning_datetime(self):
            # Given
            offer = create_event_offer()
            data = {'beginningDatetime': None}

            # When
            with pytest.raises(ApiErrors) as e:
                check_existing_stock_has_dates(data, offer)

            # Then
            assert e.value.errors['beginningDatetime'] == [
                'Ce paramètre est obligatoire'
            ]

        def test_raises_error_with_none_end_datetime(self):
            # Given
            offer = create_event_offer()
            data = {'endDatetime': None}

            # When
            with pytest.raises(ApiErrors) as e:
                check_existing_stock_has_dates(data, offer)

            # Then
            assert e.value.errors['endDatetime'] == [
                'Ce paramètre est obligatoire'
            ]
