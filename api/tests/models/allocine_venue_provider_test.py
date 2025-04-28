import pytest

import pcapi.core.providers.factories as providers_factories
import pcapi.core.providers.models as providers_models
from pcapi.models import db


@pytest.mark.usefixtures("db_session")
def test_allocine_venue_provider_inheritance():
    venue_provider = providers_factories.AllocineVenueProviderFactory(isDuo=True)
    allocine = venue_provider.provider
    other_provider = providers_factories.ProviderFactory(localClass="Other")
    providers_factories.VenueProviderFactory(provider=other_provider)

    assert db.session.query(providers_models.VenueProvider).count() == 2
    assert db.session.query(providers_models.AllocineVenueProvider).count() == 1
    allocine_vp = db.session.query(providers_models.VenueProvider).filter_by(provider=allocine).one()
    assert isinstance(allocine_vp, providers_models.AllocineVenueProvider)
    assert allocine_vp.isDuo
    assert allocine_vp.isFromAllocineProvider
    other_vp = db.session.query(providers_models.VenueProvider).filter_by(provider=other_provider).one()
    assert isinstance(other_vp, providers_models.VenueProvider)
    assert not other_vp.isFromAllocineProvider
