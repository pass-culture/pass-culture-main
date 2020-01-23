import pytest

from local_providers.price_rule import PriceRule
from models import ApiErrors
from repository import repository
from repository.provider_queries import get_provider_by_local_class
from tests.conftest import clean_database
from tests.model_creators.generic_creators import create_venue_provider, create_venue, create_offerer, \
    create_venue_provider_price_rule


class VenueProviderPriceRuleTest:
    @clean_database
    def test_should_add_price_rules_to_venue_provider(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer)
        allocine_provider = get_provider_by_local_class('AllocineStocks')
        allocine_provider.isActive = True
        venue_provider = create_venue_provider(venue, allocine_provider)
        venue_provider_price_rule = create_venue_provider_price_rule(venue_provider, price_rule=PriceRule.default, price=10)

        # When
        repository.save(venue_provider_price_rule)

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
        venue_provider_price_rule = create_venue_provider_price_rule(venue_provider,
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
        allocine_provider = get_provider_by_local_class('AllocineStocks')
        allocine_provider.isActive = True
        venue_provider = create_venue_provider(venue, allocine_provider)
        venue_provider_price_rule = create_venue_provider_price_rule(venue_provider, price_rule=PriceRule.default, price=10)
        repository.save(venue_provider_price_rule)
        venue_provider_price_rule2 = create_venue_provider_price_rule(venue_provider, price_rule=PriceRule.default, price=12)

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
        venue_provider = create_venue_provider(venue, allocine_provider)
        price = 'wrong_price_format'
        venue_provider_price_rule = create_venue_provider_price_rule(venue_provider, price_rule=PriceRule.default, price=price)

        # When
        with pytest.raises(ApiErrors) as error:
            repository.save(venue_provider_price_rule)

        # Then
        assert error.value.errors == {'global': ["Le prix doit être un nombre décimal"]}
