from decimal import Decimal
from unittest.mock import MagicMock

from models import AllocineVenueProvider, AllocineVenueProviderPriceRule
from repository import repository
from tests.conftest import clean_database
from tests.model_creators.generic_creators import create_offerer, create_venue
from tests.model_creators.provider_creators import activate_provider
from use_cases.connect_provider_allocine_to_venue import connect_allocine_to_venue
from utils.human_ids import humanize


class ConnectAllocineToVenueTest:
    def setup_class(self):
        self.find_by_id = MagicMock()

    @clean_database
    def should_connect_venue_to_allocine_provider(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer)
        provider = activate_provider('AllocineStocks')

        repository.save(venue)

        self.find_by_id.return_value = \
 \
            self.find_by_id.return_value = venue

        venue_provider_payload = {
            'providerId': humanize(provider.id),
            'venueId': humanize(venue.id),
            'price': '9.99',
            'isDuo': True,
            'quantity': 50
        }

        # When
        connect_allocine_to_venue(venue_provider_payload, self.find_by_id)

        # Then
        allocine_venue_provider = AllocineVenueProvider.query.one()
        venue_provider_price_rule = AllocineVenueProviderPriceRule.query.one()

        assert allocine_venue_provider.venue == venue
        assert allocine_venue_provider.isDuo
        assert allocine_venue_provider.quantity == 50
        assert venue_provider_price_rule.price == Decimal('9.99')
