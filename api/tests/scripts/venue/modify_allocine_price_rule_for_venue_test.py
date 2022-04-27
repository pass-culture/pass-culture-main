from decimal import Decimal

import pytest

import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.providers.factories as providers_factories
from pcapi.core.providers.models import AllocineVenueProviderPriceRule
from pcapi.domain.price_rule import PriceRule
from pcapi.scripts.venue.modify_allocine_price_rule_for_venue import modify_allocine_price_rule_for_venue_by_id
from pcapi.scripts.venue.modify_allocine_price_rule_for_venue import modify_allocine_price_rule_for_venue_by_siret


class ModifyAllocinePriceRuleForVenueTest:
    @pytest.mark.usefixtures("db_session")
    def should_update_allocine_price_rule_for_venue_with_given_id(self, app):
        # Given
        initial_price = Decimal(7.5)
        new_price = Decimal(8)
        allocine_venue_provider_price_rule = providers_factories.AllocineVenueProviderPriceRuleFactory(
            priceRule=PriceRule.default, price=initial_price
        )
        venue = allocine_venue_provider_price_rule.allocineVenueProvider.venue

        # When
        modify_allocine_price_rule_for_venue_by_id(venue.id, new_price)

        # Then
        assert allocine_venue_provider_price_rule.price == new_price

    @pytest.mark.usefixtures("db_session")
    def should_update_allocine_price_rule_for_venue_with_given_siret(self, app):
        # Given
        initial_price = Decimal(7.5)
        new_price = Decimal(8)
        allocine_venue_provider_price_rule = providers_factories.AllocineVenueProviderPriceRuleFactory(
            priceRule=PriceRule.default, price=initial_price
        )
        venue = allocine_venue_provider_price_rule.allocineVenueProvider.venue

        # When
        modify_allocine_price_rule_for_venue_by_siret(venue.siret, new_price)

        # Then
        assert allocine_venue_provider_price_rule.price == new_price

    @pytest.mark.usefixtures("db_session")
    def should_not_update_allocine_price_rule_when_there_is_no_venue_provider_associated_to_the_venue(self, app):
        # Given
        new_price = Decimal(8)
        venue = offerers_factories.VenueFactory()

        # When
        modify_allocine_price_rule_for_venue_by_siret(venue.siret, new_price)

        # Then
        assert AllocineVenueProviderPriceRule.query.count() == 0

    @pytest.mark.usefixtures("db_session")
    def should_not_update_allocine_price_rule_when_there_is_no_allocine_price_rule_associated_to_the_venue(self, app):
        # Given
        new_price = Decimal(8)
        venue = offerers_factories.VenueFactory()
        providers_factories.AllocineVenueProviderFactory(venue=venue)

        # When
        modify_allocine_price_rule_for_venue_by_siret(venue.siret, new_price)

        # Then
        assert AllocineVenueProviderPriceRule.query.count() == 0
