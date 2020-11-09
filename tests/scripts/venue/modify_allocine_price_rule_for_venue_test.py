from decimal import Decimal

import pytest

from pcapi.domain.price_rule import PriceRule
from pcapi.model_creators.generic_creators import create_allocine_venue_provider
from pcapi.model_creators.generic_creators import create_allocine_venue_provider_price_rule
from pcapi.model_creators.generic_creators import create_offerer
from pcapi.model_creators.generic_creators import create_provider
from pcapi.model_creators.generic_creators import create_venue
from pcapi.models import AllocineVenueProviderPriceRule
from pcapi.repository import repository
from pcapi.scripts.venue.modify_allocine_price_rule_for_venue import modify_allocine_price_rule_for_venue_by_id
from pcapi.scripts.venue.modify_allocine_price_rule_for_venue import modify_allocine_price_rule_for_venue_by_siret


class ModifyAllocinePriceRuleForVenueTest:
    @pytest.mark.usefixtures("db_session")
    def should_update_allocine_price_rule_for_venue_with_given_id(self, app):
        # Given
        initial_price = Decimal(7.5)
        new_price = Decimal(8)
        offerer = create_offerer()
        venue = create_venue(offerer)
        allocine_provider = create_provider(local_class='TestLocalProvider')
        allocine_venue_provider = create_allocine_venue_provider(venue, allocine_provider)
        allocine_venue_provider_price_rule = create_allocine_venue_provider_price_rule(allocine_venue_provider,
                                                                                       price_rule=PriceRule.default,
                                                                                       price=initial_price)

        repository.save(allocine_venue_provider_price_rule)

        # When
        modify_allocine_price_rule_for_venue_by_id(venue.id, new_price)

        # Then
        assert allocine_venue_provider_price_rule.price == new_price

    @pytest.mark.usefixtures("db_session")
    def should_update_allocine_price_rule_for_venue_with_given_siret(self, app):
        # Given
        initial_price = Decimal(7.5)
        new_price = Decimal(8)
        offerer = create_offerer()
        venue = create_venue(offerer)
        allocine_provider = create_provider(local_class='TestLocalProvider')
        allocine_venue_provider = create_allocine_venue_provider(venue, allocine_provider)
        allocine_venue_provider_price_rule = create_allocine_venue_provider_price_rule(allocine_venue_provider,
                                                                                       price_rule=PriceRule.default,
                                                                                       price=initial_price)

        repository.save(allocine_venue_provider_price_rule)

        # When
        modify_allocine_price_rule_for_venue_by_siret(venue.siret, new_price)

        # Then
        assert allocine_venue_provider_price_rule.price == new_price

    @pytest.mark.usefixtures("db_session")
    def should_not_update_allocine_price_rule_when_there_is_no_venue_provider_associated_to_the_venue(self, app):
        # Given
        new_price = Decimal(8)
        offerer = create_offerer()
        venue = create_venue(offerer)

        repository.save(venue)

        # When
        modify_allocine_price_rule_for_venue_by_siret(venue.siret, new_price)

        # Then
        assert AllocineVenueProviderPriceRule.query.count() == 0

    @pytest.mark.usefixtures("db_session")
    def should_not_update_allocine_price_rule_when_there_is_no_allocine_price_rule_associated_to_the_venue(self, app):
        # Given
        new_price = Decimal(8)
        offerer = create_offerer()
        venue = create_venue(offerer)
        allocine_provider = create_provider(local_class='TestLocalProvider')
        allocine_venue_provider = create_allocine_venue_provider(venue, allocine_provider)

        repository.save(allocine_venue_provider)

        # When
        modify_allocine_price_rule_for_venue_by_siret(venue.siret, new_price)

        # Then
        assert AllocineVenueProviderPriceRule.query.count() == 0
