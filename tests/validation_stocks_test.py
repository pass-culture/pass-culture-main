from datetime import datetime, timedelta

import pytest

from models import ApiErrors, Venue
from models.pc_object import serialize
from tests.test_utils import create_thing_offer, create_event_offer
from utils.human_ids import humanize
from validation.stocks import check_stock_has_dates_for_event_offer


@pytest.mark.standalone
class CheckStockHasDatesForEventOfferTest:
    class OfferIsOnThingTest:
        def test_with_beginning_and_end_datetimes_only(self):
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
                check_stock_has_dates_for_event_offer(data, offer)

            # Then
            assert e.value.errors['global'] == [
                'Impossible de mettre des dates de début et fin si l\'offre ne porte pas sur un évenement'
            ]

        def test_with_beginning_datetime_only(self):
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
                check_stock_has_dates_for_event_offer(data, offer)

            # Then
            assert e.value.errors['global'] == [
                'Impossible de mettre des dates de début et fin si l\'offre ne porte pas sur un évenement'
            ]

        def test_with_end_datetime_only(self):
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
                check_stock_has_dates_for_event_offer(data, offer)

            # Then
            assert e.value.errors['global'] == [
                'Impossible de mettre des dates de début et fin si l\'offre ne porte pas sur un évenement'
            ]

    class OfferIsOnEventTest:
        def test_with_missing_end_datetime(self):
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
                check_stock_has_dates_for_event_offer(data, offer)

            # Then
            assert e.value.errors['endDatetime'] == [
                'Ce paramètre est obligatoire'
            ]

        def test_with_missing_beginning_datetime(self):
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
                check_stock_has_dates_for_event_offer(data, offer)

            # Then
            assert e.value.errors['beginningDatetime'] == [
                'Ce paramètre est obligatoire'
            ]
