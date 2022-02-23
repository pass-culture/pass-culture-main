import pytest

from pcapi.core.providers import factories as providers_factories
from pcapi.core.providers.models import AllocineVenueProviderPriceRule
from pcapi.domain.price_rule import PriceRule
from pcapi.models.api_errors import ApiErrors
from pcapi.repository import repository


class AllocineVenueProviderPriceRuleTest:
    @pytest.mark.usefixtures("db_session")
    def test_should_add_price_rules_to_venue_provider(self, app):
        # Given
        allocine_venue_provider = providers_factories.AllocineVenueProviderFactory()
        providers_factories.AllocineVenueProviderPriceRuleFactory(
            allocineVenueProvider=allocine_venue_provider, priceRule=PriceRule.default, price=10
        )

        # Then
        assert len(allocine_venue_provider.priceRules) == 1

    @pytest.mark.usefixtures("db_session")
    def test_should_raise_error_when_price_is_negative(self, app):
        # Given
        allocine_venue_provider = providers_factories.AllocineVenueProviderFactory()

        allocine_venue_provider_price_rule = AllocineVenueProviderPriceRule()
        allocine_venue_provider_price_rule.allocineVenueProvider = allocine_venue_provider
        allocine_venue_provider_price_rule.priceRule = PriceRule.default
        allocine_venue_provider_price_rule.price = -4

        # When
        with pytest.raises(ApiErrors) as error:
            repository.save(allocine_venue_provider_price_rule)

        # Then
        assert error.value.errors["global"] == ["Vous ne pouvez renseigner un prix négatif"]

    @pytest.mark.usefixtures("db_session")
    def test_should_raise_error_when_saving_existing_rule_price(self, app):
        # Given
        allocine_venue_provider = providers_factories.AllocineVenueProviderFactory()

        providers_factories.AllocineVenueProviderPriceRuleFactory(
            allocineVenueProvider=allocine_venue_provider, priceRule=PriceRule.default, price=10
        )

        allocine_venue_provider_price_rule_2 = AllocineVenueProviderPriceRule()
        allocine_venue_provider_price_rule_2.allocineVenueProvider = allocine_venue_provider
        allocine_venue_provider_price_rule_2.priceRule = PriceRule.default
        allocine_venue_provider_price_rule_2.price = 12

        # When
        with pytest.raises(ApiErrors) as error:
            repository.save(allocine_venue_provider_price_rule_2)

        # Then
        assert error.value.errors["global"] == ["Vous ne pouvez avoir qu''un seul prix par catégorie"]

    @pytest.mark.usefixtures("db_session")
    def test_should_raise_error_when_saving_wrong_format_price(self, app):
        # Given
        allocine_venue_provider = providers_factories.AllocineVenueProviderFactory()

        allocine_venue_provider_price_rule = AllocineVenueProviderPriceRule()
        allocine_venue_provider_price_rule.allocineVenueProvider = allocine_venue_provider
        allocine_venue_provider_price_rule.priceRule = PriceRule.default
        allocine_venue_provider_price_rule.price = "wrong_price_format"

        # When
        with pytest.raises(ApiErrors) as error:
            repository.save(allocine_venue_provider_price_rule)

        # Then
        assert error.value.errors == {"global": ["Le prix doit être un nombre décimal"]}


class SaveAllocineVenueProviderPriceRuleTest:
    @pytest.mark.usefixtures("db_session")
    def test_should_not_save_new_venue_provider_price_rule(self, app):
        # Given
        allocine_venue_provider = providers_factories.AllocineVenueProviderFactory()

        venue_provider_price_rule = AllocineVenueProviderPriceRule()
        venue_provider_price_rule.allocineVenueProvider = allocine_venue_provider
        venue_provider_price_rule.priceRule = PriceRule.default
        venue_provider_price_rule.price = "wrong_price_format"

        # When
        with pytest.raises(ApiErrors):
            repository.save(venue_provider_price_rule)

        # Then
        assert AllocineVenueProviderPriceRule.query.count() == 0
