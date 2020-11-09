from datetime import datetime
from datetime import timedelta

import pytest

from pcapi.algolia.domain.rules_engine import is_eligible_for_reindexing
from pcapi.model_creators.generic_creators import create_offerer
from pcapi.model_creators.generic_creators import create_stock
from pcapi.model_creators.generic_creators import create_venue
from pcapi.model_creators.specific_creators import create_offer_with_event_product
from pcapi.model_creators.specific_creators import create_offer_with_thing_product
from pcapi.repository import repository


class IsEligibleForReindexingTest:
    @pytest.mark.usefixtures("db_session")
    def test_should_return_false_when_offer_name_has_not_changed(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer=offerer)
        offer = create_offer_with_thing_product(thing_name='super offre', venue=venue)
        stock = create_stock(offer=offer)
        repository.save(stock)

        # When
        is_offer_eligible = is_eligible_for_reindexing(offer=offer,
                                                       offer_details={'name': 'super offre',
                                                                      'dateRange': [],
                                                                      'dates': [],
                                                                      'prices': [10.0]})

        # Then
        assert not is_offer_eligible

    @pytest.mark.usefixtures("db_session")
    def test_should_return_true_when_offer_name_has_changed(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer=offerer)
        offer = create_offer_with_thing_product(thing_name='super offre de dingue', venue=venue)
        stock = create_stock(offer=offer)
        repository.save(stock)

        # When
        is_offer_eligible = is_eligible_for_reindexing(offer=offer,
                                                       offer_details={'name': 'super offre',
                                                                      'dateRange': [],
                                                                      'dates': [],
                                                                      'prices': [10.0]})

        # Then
        assert is_offer_eligible

    @pytest.mark.usefixtures("db_session")
    def test_should_return_true_when_stocks_beginning_datetime_have_changed(self, app):
        # Given
        offerer = create_offerer(is_active=True, validation_token=None)
        venue = create_venue(offerer=offerer, validation_token=None)
        offer = create_offer_with_event_product(event_name='super offre', venue=venue)
        stock = create_stock(beginning_datetime=datetime(2020, 1, 1), offer=offer)
        repository.save(stock)

        # When
        is_offer_eligible = is_eligible_for_reindexing(offer=offer,
                                                       offer_details={'name': 'super offre',
                                                                      'dateRange': ['2020-01-01 00:00:00',
                                                                                    '2020-01-02 00:00:00'],
                                                                      'dates': [1578614400.0],
                                                                      'prices': [10.0]})

        # Then
        assert is_offer_eligible

    @pytest.mark.usefixtures("db_session")
    def test_should_return_false_when_stocks_beginning_datetime_have_not_changed(self, app):
        # Given
        offerer = create_offerer(is_active=True, validation_token=None)
        venue = create_venue(offerer=offerer, validation_token=None)
        offer = create_offer_with_event_product(event_name='super offre', venue=venue)
        stock = create_stock(beginning_datetime=datetime(2020, 1, 1), offer=offer)
        repository.save(stock)

        # When
        is_offer_eligible = is_eligible_for_reindexing(offer=offer,
                                                       offer_details={'name': 'super offre',
                                                                      'dateRange': ['2020-01-01 00:00:00',
                                                                                    '2020-01-02 00:00:00'],
                                                                      'dates': [1577836800.0],
                                                                      'prices': [10.0]})

        # Then
        assert not is_offer_eligible

    @pytest.mark.usefixtures("db_session")
    def test_should_return_true_when_stocks_prices_have_changed(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer=offerer)
        offer = create_offer_with_event_product(event_name='super offre', venue=venue)
        stock = create_stock(beginning_datetime=datetime(2020, 1, 1), offer=offer, price=10)
        repository.save(stock)

        # When
        is_offer_eligible = is_eligible_for_reindexing(offer=offer,
                                                       offer_details={'name': 'super offre',
                                                                      'dateRange': ['2020-01-01 00:00:00',
                                                                                    '2020-01-02 00:00:00'],
                                                                      'dates': [1577836800],
                                                                      'prices': [11.0]})

        # Then
        assert is_offer_eligible

    @pytest.mark.usefixtures("db_session")
    def test_should_return_true_when_stocks_prices_have_not_changed(self, app):
        # Given
        offerer = create_offerer(is_active=True, validation_token=None)
        venue = create_venue(offerer=offerer, validation_token=None)
        offer = create_offer_with_event_product(event_name='super offre', venue=venue)
        stock = create_stock(beginning_datetime=datetime(2020, 1, 1), offer=offer, price=10)
        repository.save(stock)

        # When
        is_offer_eligible = is_eligible_for_reindexing(offer=offer,
                                                       offer_details={'name': 'super offre',
                                                                      'dateRange': ['2020-01-01 00:00:00',
                                                                                    '2020-01-02 00:00:00'],
                                                                      'dates': [1577836800],
                                                                      'prices': [10.0]})

        # Then
        assert not is_offer_eligible
