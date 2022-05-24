from decimal import Decimal

import pytest

import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.providers.factories as providers_factories
import pcapi.core.providers.models as providers_models
from pcapi.use_cases.connect_venue_to_allocine import connect_venue_to_allocine


@pytest.mark.usefixtures("db_session")
def test_connect_venue_to_allocine_provider():
    # Given
    venue = offerers_factories.VenueFactory()
    allocine_provider = providers_factories.AllocineProviderFactory()
    providers_factories.AllocineTheaterFactory(
        siret=venue.siret,
        internalId="PXXXXXX",
        theaterId="123VHJ==",
    )

    # When
    connect_venue_to_allocine(
        venue,
        allocine_provider.id,
        providers_models.VenueProviderCreationPayload(
            price="9.99",
            isDuo=True,
            quantity=50,
        ),
    )

    # Then
    allocine_venue_provider = providers_models.AllocineVenueProvider.query.one()
    allocine_pivot = providers_models.AllocinePivot.query.one()
    venue_provider_price_rule = providers_models.AllocineVenueProviderPriceRule.query.one()

    assert allocine_venue_provider.venue == venue
    assert allocine_venue_provider.isDuo
    assert allocine_venue_provider.quantity == 50
    assert allocine_venue_provider.internalId == "PXXXXXX"
    assert allocine_venue_provider.venueIdAtOfferProvider == "123VHJ=="
    assert venue_provider_price_rule.price == Decimal("9.99")
    assert allocine_pivot.venueId == venue.id
