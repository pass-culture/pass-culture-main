from datetime import datetime, timedelta
from unittest.mock import MagicMock

from models import Offer
from repository import repository
from scripts.deactivate_offers_during_quatantine.deactivate_offers import \
    get_offers_with_max_stock_date_between_today_and_end_of_quarantine, deactivate_offers, \
    deactivate_offers_with_max_stock_date_between_today_and_end_of_quarantine
from tests.conftest import clean_database
from tests.model_creators.generic_creators import create_offerer, create_venue, create_stock
from tests.model_creators.specific_creators import create_offer_with_event_product

FIRST_DAY_AFTER_QUARANTINE = datetime(2020, 4, 16)
TODAY = datetime(2020, 4, 10)


class GetOffersWithMaxStockDateBetweenTodayAndEndOfQuarantineTest:
    @clean_database
    def test_should_not_get_offers_with_dates_only_before_today(self, app):
        # Given
        yesterday = TODAY - timedelta(days=1)

        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_event_product(venue)
        stock = create_stock(offer=offer, beginning_datetime=yesterday)

        repository.save(stock)

        # When
        offers = get_offers_with_max_stock_date_between_today_and_end_of_quarantine(FIRST_DAY_AFTER_QUARANTINE, TODAY)

        # Then
        assert offers == []


    @clean_database
    def test_should_get_offer_with_a_date_between_today_and_15_04(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_event_product(venue)
        stock = create_stock(offer=offer, beginning_datetime=datetime(2020, 4, 15, 23, 59))

        repository.save(stock)

        # When
        offers = get_offers_with_max_stock_date_between_today_and_end_of_quarantine(FIRST_DAY_AFTER_QUARANTINE, TODAY)

        # Then
        assert offers == [offer]


    @clean_database
    def test_should_not_get_offer_with_a_date_after_15_04(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_event_product(venue)
        stock = create_stock(offer=offer, beginning_datetime=datetime(2020, 4, 16))

        repository.save(stock)

        # When
        offers = get_offers_with_max_stock_date_between_today_and_end_of_quarantine(FIRST_DAY_AFTER_QUARANTINE, TODAY)

        # Then
        assert offers == []


    @clean_database
    def test_should_not_get_offer_with_a_date_between_today_and_the_15_04_and_another_after_15_04(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_event_product(venue)
        stock1 = create_stock(offer=offer, beginning_datetime=datetime(2020, 4, 16))
        stock2 = create_stock(offer=offer, beginning_datetime=datetime(2020, 4, 14))

        repository.save(stock1, stock2)

        # When
        offers = get_offers_with_max_stock_date_between_today_and_end_of_quarantine(FIRST_DAY_AFTER_QUARANTINE, TODAY)

        # Then
        assert offers == []

class DeactivateOffersTest:
    @clean_database
    def test_should_deactivate_given_offers(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_event_product(venue)
        offers = [offer]

        repository.save(*offers)

        # When
        deactivate_offers(offers)

        # Then
        updated_offers = Offer.query.filter_by(id=offer.id).all()
        for offer in updated_offers:
            assert offer.isActive is False


class DeactivateOffersWithMaxStockDateBetweenTodayAndEndOfQuarantineTest:
    @clean_database
    def test_should_deactivate_offers(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer_to_deactivate = create_offer_with_event_product(venue)
        offer_not_to_deactivate = create_offer_with_event_product(venue)
        get_offers = MagicMock()
        get_offers.return_value = [offer_to_deactivate]

        repository.save(offer_to_deactivate, offer_not_to_deactivate)

        # When
        deactivate_offers_with_max_stock_date_between_today_and_end_of_quarantine(FIRST_DAY_AFTER_QUARANTINE, TODAY,
                                                                                  get_offers)

        # Then
        assert offer_to_deactivate.isActive is False
        assert offer_not_to_deactivate.isActive is True
