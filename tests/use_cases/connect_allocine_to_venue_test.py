from decimal import Decimal
from unittest.mock import MagicMock

import pytest

from pcapi.model_creators.generic_creators import create_allocine_pivot
from pcapi.model_creators.generic_creators import create_offerer
from pcapi.model_creators.generic_creators import create_venue
from pcapi.model_creators.provider_creators import activate_provider
from pcapi.models import AllocineVenueProvider
from pcapi.models import AllocineVenueProviderPriceRule
from pcapi.repository import repository
from pcapi.use_cases.connect_venue_to_allocine import connect_venue_to_allocine
from pcapi.utils.human_ids import humanize


class ConnectAllocineToVenueTest:
    def setup_class(self):
        self.find_by_id = MagicMock()
        self.get_theaterid_for_venue = MagicMock()

    @pytest.mark.usefixtures("db_session")
    def should_connect_venue_to_allocine_provider(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer)
        provider = activate_provider("AllocineStocks")
        allocine_pivot = create_allocine_pivot(siret=venue.siret)

        repository.save(venue, allocine_pivot)

        self.find_by_id.return_value = venue
        self.get_theaterid_for_venue.return_value = allocine_pivot.theaterId

        venue_provider_payload = {
            "providerId": humanize(provider.id),
            "venueId": humanize(venue.id),
            "price": "9.99",
            "isDuo": True,
            "quantity": 50,
        }

        # When
        connect_venue_to_allocine(venue_provider_payload, self.find_by_id, self.get_theaterid_for_venue)

        # Then
        allocine_venue_provider = AllocineVenueProvider.query.one()
        venue_provider_price_rule = AllocineVenueProviderPriceRule.query.one()

        assert allocine_venue_provider.venue == venue
        assert allocine_venue_provider.isDuo
        assert allocine_venue_provider.quantity == 50
        assert venue_provider_price_rule.price == Decimal("9.99")
