from decimal import Decimal

from pcapi.core.offers.factories import VenueFactory
from pcapi.core.providers.factories import AllocinePivotFactory
from pcapi.core.providers.models import AllocineVenueProvider
from pcapi.core.providers.models import AllocineVenueProviderPriceRule
from pcapi.core.providers.models import VenueProviderCreationPayload
from pcapi.model_creators.provider_creators import activate_provider
from pcapi.use_cases.connect_venue_to_allocine import connect_venue_to_allocine


class ConnectAllocineToVenueTest:
    def should_connect_venue_to_allocine_provider(self, app, db_session):
        # Given
        venue = VenueFactory()
        provider = activate_provider("AllocineStocks")
        AllocinePivotFactory(
            siret=venue.siret,
            internalId="PXXXXXX",
            theaterId="123VHJ==",
        )

        # When
        connect_venue_to_allocine(
            venue, provider.id, VenueProviderCreationPayload(price="9.99", isDuo=True, quantity=50)
        )

        # Then
        allocine_venue_provider = AllocineVenueProvider.query.one()
        venue_provider_price_rule = AllocineVenueProviderPriceRule.query.one()

        assert allocine_venue_provider.venue == venue
        assert allocine_venue_provider.isDuo
        assert allocine_venue_provider.quantity == 50
        assert allocine_venue_provider.internalId == "PXXXXXX"
        assert allocine_venue_provider.venueIdAtOfferProvider == "123VHJ=="
        assert venue_provider_price_rule.price == Decimal("9.99")
