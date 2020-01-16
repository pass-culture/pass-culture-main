from decimal import Decimal

import pytest

from local_providers.price_rule import PriceRule
from models import VenueProviderPriceRule, ApiErrors
from repository.venue_provider_price_rule_queries import save_venue_provider_price_rule
from tests.conftest import clean_database
from tests.model_creators.generic_creators import create_venue_provider, create_offerer, create_venue
from tests.model_creators.provider_creators import activate_provider


class SaveVenueProviderPriceRuleTest:
    @clean_database
    def test_should_create_one_venue_provider_price_rule_in_database(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer)
        allocine_provider = activate_provider('AllocineStocks')
        venue_provider = create_venue_provider(venue, allocine_provider)
        price = Decimal(10.0)

        # When
        save_venue_provider_price_rule(venue_provider, price)

        # Then
        venue_provider_price_rule = VenueProviderPriceRule.query.one()
        assert venue_provider_price_rule.venueProvider == venue_provider
        assert venue_provider_price_rule.price == price
        assert venue_provider_price_rule.priceRule == PriceRule.default

    @clean_database
    def test_should_not_save_new_venue_provider_price_rule(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer)
        allocine_provider = activate_provider('AllocineStocks')
        venue_provider = create_venue_provider(venue, allocine_provider)
        price = 'wrong_price_format'

        # When
        with pytest.raises(ApiErrors):
            save_venue_provider_price_rule(venue_provider, price)

        # Then
        assert VenueProviderPriceRule.query.count() == 0
