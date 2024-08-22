import pytest

from pcapi.core.offerers.factories import VenueFactory
from pcapi.core.offers.factories import OfferFactory
from pcapi.core.offers.models import Offer
from pcapi.core.providers.factories import ProviderFactory
from pcapi.scripts.batch_offers_deactivation.main import run_task


pytestmark = pytest.mark.usefixtures("db_session")


def test_run(caplog):
    provider = ProviderFactory()
    other_provider = ProviderFactory()

    venue = VenueFactory()
    other_venue = VenueFactory()

    offers = OfferFactory.create_batch(3, venue=venue, lastProvider=provider, isActive=True)

    other_offers = OfferFactory.create_batch(
        3, venue=venue, lastProvider=other_provider, isActive=True
    ) + OfferFactory.create_batch(3, venue=other_venue, isActive=True)

    run_task(venue.id, provider.id)

    offer_ids = {o.id for o in offers}
    target_offers = Offer.query.filter(Offer.id.in_(offer_ids))

    assert all(not o.isActive for o in target_offers)

    other_offer_ids = {o.id for o in other_offers}
    other_target_offers = Offer.query.filter(Offer.id.in_(other_offer_ids))

    assert all(o.isActive for o in other_target_offers)
