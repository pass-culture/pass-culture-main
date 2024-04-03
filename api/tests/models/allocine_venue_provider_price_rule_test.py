import pytest

from pcapi.core.providers import factories as providers_factories
from pcapi.core.providers.models import AllocineVenueProviderPriceRule
from pcapi.domain.price_rule import PriceRule
from pcapi.models.api_errors import ApiErrors
from pcapi.repository import repository


class AllocineVenueProviderPriceRuleTest:

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
