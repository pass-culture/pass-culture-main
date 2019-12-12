from decimal import Decimal

import pytest

from local_providers.price_rule import PriceRule
from models import VenueProviderPriceRule, ApiErrors
from repository.venue_provider_price_rule_queries import save_venue_provider_price_rule
from tests.conftest import clean_database
from tests.test_utils import create_venue_provider, activate_provider, create_offerer, create_venue


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
    def test_should_raise_exception_when_price_in_wrong_format(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer)
        allocine_provider = activate_provider('AllocineStocks')
        venue_provider = create_venue_provider(venue, allocine_provider)
        price = 'wrong_price_format'

        # When
        with pytest.raises(ApiErrors) as error:
            save_venue_provider_price_rule(venue_provider, price)

        # Then
        assert error.value.errors == {'global': ['Le prix doit être un nombre décimal']}
