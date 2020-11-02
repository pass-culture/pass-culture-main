from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

from pcapi.models import OfferSQLEntity
from pcapi.repository import repository
from pcapi.scripts.deactivate_offers_during_quarantine.deactivate_offers import \
    build_query_offers_with_max_stock_date_between_today_and_end_of_quarantine, deactivate_offers, \
    deactivate_offers_with_max_stock_date_between_today_and_end_of_quarantine, \
    get_offers_with_max_stock_date_between_today_and_end_of_quarantine
import pytest
from pcapi.model_creators.generic_creators import create_offerer, create_venue, create_stock
from pcapi.model_creators.specific_creators import create_offer_with_event_product, create_offer_with_thing_product

FIRST_DAY_AFTER_QUARANTINE = datetime(2020, 4, 16)
TODAY = datetime(2020, 4, 10)


class GetOffersWithMaxStockDateBetweenTodayAndEndOfQuarantineTest:
    @patch('pcapi.scripts.deactivate_offers_during_quarantine.'
           'deactivate_offers.build_query_offers_with_max_stock_date_between_today_and_end_of_quarantine')
    def test_should_call_build_offers_query(self, stub_build_query):
        # When
        get_offers_with_max_stock_date_between_today_and_end_of_quarantine(FIRST_DAY_AFTER_QUARANTINE,
                                                                           TODAY)

        # Then
        stub_build_query.assert_called_once_with(FIRST_DAY_AFTER_QUARANTINE, TODAY)


class BuildQueryOffersWithMaxStockDateBetweenTodayAndEndOfQuarantineTest:
    @pytest.mark.usefixtures("db_session")
    def test_should_not_get_offers_with_dates_only_before_today(self, app):
        # Given
        yesterday = TODAY - timedelta(days=1)

        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_event_product(venue)
        stock = create_stock(beginning_datetime=yesterday, offer=offer)

        repository.save(stock)

        # When
        offers = build_query_offers_with_max_stock_date_between_today_and_end_of_quarantine(FIRST_DAY_AFTER_QUARANTINE,
                                                                                            TODAY).all()

        # Then
        assert offers == []

    @pytest.mark.usefixtures("db_session")
    def test_should_get_offer_with_a_date_between_today_and_15_04(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_event_product(venue)
        stock = create_stock(beginning_datetime=datetime(2020, 4, 15, 23, 59), offer=offer)

        repository.save(stock)

        # When
        offers = build_query_offers_with_max_stock_date_between_today_and_end_of_quarantine(FIRST_DAY_AFTER_QUARANTINE,
                                                                                            TODAY).all()

        # Then
        assert offers == [offer]

    @pytest.mark.usefixtures("db_session")
    def test_should_not_get_offer_with_a_date_after_15_04(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_event_product(venue)
        stock = create_stock(beginning_datetime=datetime(2020, 4, 16), offer=offer)

        repository.save(stock)

        # When
        offers = build_query_offers_with_max_stock_date_between_today_and_end_of_quarantine(FIRST_DAY_AFTER_QUARANTINE,
                                                                                            TODAY).all()

        # Then
        assert offers == []

    @pytest.mark.usefixtures("db_session")
    def test_should_not_get_offer_with_a_date_between_today_and_the_15_04_and_another_after_15_04(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_event_product(venue)
        stock1 = create_stock(beginning_datetime=datetime(2020, 4, 16), offer=offer)
        stock2 = create_stock(beginning_datetime=datetime(2020, 4, 14), offer=offer)

        repository.save(stock1, stock2)

        # When
        offers = build_query_offers_with_max_stock_date_between_today_and_end_of_quarantine(FIRST_DAY_AFTER_QUARANTINE,
                                                                                            TODAY).all()

        # Then
        assert offers == []

    @pytest.mark.usefixtures("db_session")
    def test_should_not_get_offers_on_things(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock = create_stock(beginning_datetime=None, offer=offer)

        repository.save(stock)

        # When
        offers = build_query_offers_with_max_stock_date_between_today_and_end_of_quarantine(FIRST_DAY_AFTER_QUARANTINE,
                                                                                            TODAY).all()

        # Then
        assert offers == []


class DeactivateOffersTest:
    @pytest.mark.usefixtures("db_session")
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
        updated_offers = OfferSQLEntity.query.filter_by(id=offer.id).all()
        for offer in updated_offers:
            assert offer.isActive is False


class DeactivateOffersWithMaxStockDateBetweenTodayAndEndOfQuarantineTest:
    @pytest.mark.usefixtures("db_session")
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

    @pytest.mark.usefixtures("db_session")
    @patch('pcapi.scripts.deactivate_offers_during_quarantine.deactivate_offers.delete_expired_offers')
    def test_should_unindex_offers(self, mocked_delete_expired_offers):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer_to_deactivate = create_offer_with_event_product(venue)
        offer_not_to_deactivate = create_offer_with_event_product(venue)
        get_offers = MagicMock()
        get_offers.return_value = [offer_to_deactivate]

        repository.save(offer_to_deactivate, offer_not_to_deactivate)

        # When
        deactivate_offers_with_max_stock_date_between_today_and_end_of_quarantine(
            FIRST_DAY_AFTER_QUARANTINE, TODAY, get_offers
        )

        assert mocked_delete_expired_offers.call_args[0][1] == [offer_to_deactivate.id]
