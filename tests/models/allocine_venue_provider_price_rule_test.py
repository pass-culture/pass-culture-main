from decimal import Decimal

import pytest

from local_providers.price_rule import PriceRule
from models import ApiErrors, AllocineVenueProviderPriceRule
from repository import repository
from repository.provider_queries import get_provider_by_local_class
from tests.conftest import clean_database
from tests.model_creators.generic_creators import create_venue, create_offerer, \
    create_allocine_venue_provider_price_rule, create_allocine_venue_provider
from tests.model_creators.provider_creators import activate_provider


class AllocineVenueProviderPriceRuleTest:
    @clean_database
    def test_should_add_price_rules_to_venue_provider(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer)
        allocine_provider = get_provider_by_local_class('AllocineStocks')
        allocine_provider.isActive = True
        allocine_venue_provider = create_allocine_venue_provider(venue, allocine_provider)
        allocine_venue_provider_price_rule = create_allocine_venue_provider_price_rule(allocine_venue_provider,
                                                                                       price_rule=PriceRule.default,
                                                                                       price=10)

        # When
        repository.save(allocine_venue_provider_price_rule)

        # Then
        assert len(allocine_venue_provider.priceRules) == 1

    @clean_database
    def test_should_raise_error_when_price_is_negative(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer)
        allocine_provider = get_provider_by_local_class('AllocineStocks')
        allocine_provider.isActive = True
        allocine_venue_provider = create_allocine_venue_provider(venue, allocine_provider)
        venue_provider_price_rule = create_allocine_venue_provider_price_rule(allocine_venue_provider,
                                                                              price_rule=PriceRule.default,
                                                                              price=-4)

        # When
        with pytest.raises(ApiErrors) as error:
            repository.save(venue_provider_price_rule)

        # Then
        assert error.value.errors['global'] == ['Vous ne pouvez renseigner un prix négatif']

    @clean_database
    def test_should_raise_error_when_saving_existing_rule_price(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer)
        allocine_provider = activate_provider('AllocineStocks')
        allocine_venue_provider = create_allocine_venue_provider(venue, allocine_provider)
        venue_provider_price_rule = create_allocine_venue_provider_price_rule(allocine_venue_provider,
                                                                              price_rule=PriceRule.default, price=10)
        repository.save(venue_provider_price_rule)
        venue_provider_price_rule2 = create_allocine_venue_provider_price_rule(allocine_venue_provider,
                                                                               price_rule=PriceRule.default, price=12)

        # When
        with pytest.raises(ApiErrors) as error:
            repository.save(venue_provider_price_rule2)

        # Then
        assert error.value.errors['global'] == ["Vous ne pouvez avoir qu''un seul prix par catégorie"]

    @clean_database
    def test_should_raise_error_when_saving_wrong_format_price(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer)
        allocine_provider = get_provider_by_local_class('AllocineStocks')
        allocine_venue_provider = create_allocine_venue_provider(venue, allocine_provider)
        price = 'wrong_price_format'
        venue_provider_price_rule = create_allocine_venue_provider_price_rule(allocine_venue_provider,
                                                                              price_rule=PriceRule.default, price=price)

        # When
        with pytest.raises(ApiErrors) as error:
            repository.save(venue_provider_price_rule)

        # Then
        assert error.value.errors == {'global': ["Le prix doit être un nombre décimal"]}


class SaveAllocineVenueProviderPriceRuleTest:
    @clean_database
    def test_should_create_one_venue_provider_price_rule_in_database(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer)
        allocine_provider = activate_provider('AllocineStocks')

        allocine_venue_provider = create_allocine_venue_provider(venue, allocine_provider)

        venue_provider_price_rule = AllocineVenueProviderPriceRule()
        venue_provider_price_rule.allocineVenueProvider = allocine_venue_provider
        venue_provider_price_rule.priceRule = PriceRule.default
        venue_provider_price_rule.price = Decimal(10.0)

        # When
        repository.save(venue_provider_price_rule)

        # Then
        venue_provider_price_rule = AllocineVenueProviderPriceRule.query.one()
        assert venue_provider_price_rule.allocineVenueProvider == allocine_venue_provider
        assert venue_provider_price_rule.price == Decimal(10.0)
        assert venue_provider_price_rule.priceRule == PriceRule.default

    @clean_database
    def test_should_not_save_new_venue_provider_price_rule(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer)
        allocine_provider = activate_provider('AllocineStocks')

        allocine_venue_provider = create_allocine_venue_provider(venue, allocine_provider)

        venue_provider_price_rule = AllocineVenueProviderPriceRule()
        venue_provider_price_rule.allocineVenueProvider = allocine_venue_provider
        venue_provider_price_rule.priceRule = PriceRule.default
        venue_provider_price_rule.price = 'wrong_price_format'

        # When
        with pytest.raises(ApiErrors):
            repository.save(venue_provider_price_rule)

        # Then
        assert AllocineVenueProviderPriceRule.query.count() == 0
