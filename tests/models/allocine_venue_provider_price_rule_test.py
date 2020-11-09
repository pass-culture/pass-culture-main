import pytest

from pcapi.domain.price_rule import PriceRule
from pcapi.model_creators.generic_creators import create_allocine_venue_provider
from pcapi.model_creators.generic_creators import create_allocine_venue_provider_price_rule
from pcapi.model_creators.generic_creators import create_offerer
from pcapi.model_creators.generic_creators import create_venue
from pcapi.model_creators.provider_creators import activate_provider
from pcapi.models import AllocineVenueProviderPriceRule
from pcapi.models import ApiErrors
from pcapi.repository import repository
from pcapi.repository.provider_queries import get_provider_by_local_class


class AllocineVenueProviderPriceRuleTest:
    @pytest.mark.usefixtures("db_session")
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

    @pytest.mark.usefixtures("db_session")
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

    @pytest.mark.usefixtures("db_session")
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

    @pytest.mark.usefixtures("db_session")
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
    @pytest.mark.usefixtures("db_session")
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
