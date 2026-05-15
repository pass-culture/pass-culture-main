from contextlib import contextmanager

import pytest
from flask import current_app as app

from pcapi.core import search
from pcapi.core.offerers import factories
from pcapi.core.offerers.venues.api import close as api
from pcapi.core.offers import factories as offers_factories
from pcapi.core.providers import factories as providers_factories
from pcapi.core.search import redis_queues
from pcapi.models import db


pytestmark = pytest.mark.usefixtures("db_session")


@contextmanager
def assert_no_active_offers_no_indexed_offers_no_syncs(venue):
    db.session.refresh(venue)

    assert all([not o.publicationDatetime for o in venue.offers])
    assert not app.redis_client.hgetall(redis_queues.REDIS_HASHMAP_INDEXED_OFFERS_NAME)

    assert not venue.cinemaProviderPivot
    assert not venue.allocinePivot


class PutVenueOffersToHaltTest:
    def test_venue_without_offers_nor_syncs_updates_nothing(self):
        venue = factories.VenueFactory()

        api.put_venue_offers_to_halt(venue)
        assert_no_active_offers_no_indexed_offers_no_syncs(venue)

    def test_venue_with_only_non_synced_deactivated_offers(self):
        venue = factories.VenueFactory()
        offers_factories.OfferFactory.create_batch(3, publicationDatetime=None, venue=venue)

        api.put_venue_offers_to_halt(venue)
        assert_no_active_offers_no_indexed_offers_no_syncs(venue)

    def test_venue_with_active_and_synced_offers_halts_everything(self):
        venue = factories.VenueFactory()
        boost_pivot = providers_factories.BoostCinemaProviderPivotFactory(venue=venue)

        offers = [
            offers_factories.OfferFactory(venue=venue),
            offers_factories.OfferFactory(venue=venue, lastProviderId=boost_pivot.providerId),
        ]

        search.reindex_offer_ids(o.id for o in offers)

        api.put_venue_offers_to_halt(venue)
        assert_no_active_offers_no_indexed_offers_no_syncs(venue)
