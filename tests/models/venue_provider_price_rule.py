import pytest

from models import PcObject, VenueProviderPriceRule, ApiErrors
from local_providers.price_rule import PriceRule
from repository.provider_queries import get_provider_by_local_class
from tests.conftest import clean_database
from tests.test_utils import create_venue_provider, create_venue, create_offerer


class VenueProviderPriceRuleTest:
    @clean_database
    def test_should_add_price_rules_to_venue_provider(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer)
        allocine_provider = get_provider_by_local_class('AllocineStocks')
        allocine_provider.isActive = True
        venue_provider = create_venue_provider(venue, allocine_provider)
        venue_provider_price_rule = VenueProviderPriceRule()
        venue_provider_price_rule.priceRule = PriceRule.default
        venue_provider_price_rule.price = 10
        venue_provider_price_rule.venueProvider = venue_provider

        # When
        PcObject.save(venue_provider_price_rule)

        # Then
        assert len(venue_provider.priceRules) == 1

    @clean_database
    def test_should_raise_error_when_price_is_negative(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer)
        allocine_provider = get_provider_by_local_class('AllocineStocks')
        allocine_provider.isActive = True
        venue_provider = create_venue_provider(venue, allocine_provider)
        venue_provider_price_rule = VenueProviderPriceRule()
        venue_provider_price_rule.priceRule = PriceRule.default
        venue_provider_price_rule.price = -4
        venue_provider_price_rule.venueProvider = venue_provider

        # When
        with pytest.raises(ApiErrors) as error:
            PcObject.save(venue_provider_price_rule)

        # Then
        assert error.value.errors['global'] == ['Vous ne pouvez renseigner un prix négatif']

    @clean_database
    def test_should_raise_error_when_saving_existing_rule_price_for_venue_provider(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer)
        allocine_provider = get_provider_by_local_class('AllocineStocks')
        allocine_provider.isActive = True
        venue_provider = create_venue_provider(venue, allocine_provider)
        venue_provider_price_rule = VenueProviderPriceRule()
        venue_provider_price_rule.priceRule = PriceRule.default
        venue_provider_price_rule.price = 10
        venue_provider_price_rule.venueProvider = venue_provider
        PcObject.save(venue_provider_price_rule)
        venue_provider_price_rule2 = VenueProviderPriceRule()
        venue_provider_price_rule2.priceRule = PriceRule.default
        venue_provider_price_rule2.price = 12
        venue_provider_price_rule2.venueProvider = venue_provider

        # When
        with pytest.raises(ApiErrors) as error:
            PcObject.save(venue_provider_price_rule2)

        # Then
        assert error.value.errors['global'] == ['Vous ne pouvez avoir qu''un seul prix par catégorie']
