from unittest import mock

import pytest

from pcapi.core import search
from pcapi.core.offerers import models as offerers_models
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
import pcapi.core.search.testing as search_testing
from pcapi.core.testing import assert_num_queries
from pcapi.core.testing import override_features
from pcapi.core.testing import override_settings


pytestmark = pytest.mark.usefixtures("db_session")


def make_bookable_offer():
    return offers_factories.StockFactory().offer


def make_unbookable_offer():
    return offers_factories.OfferFactory()


def fail(*args, **kwargs):
    raise ValueError("It does not work")


def test_async_index_offer_ids(app):
    search.async_index_offer_ids({1, 2})
    assert app.redis_client.lrange("offer_ids", 0, 5) == ["1", "2"]


def test_async_index_offers_of_venue_ids(app):
    search.async_index_offers_of_venue_ids({1, 2})
    assert app.redis_client.lrange("venue_ids_for_offers", 0, 5) == ["1", "2"]


def test_async_index_venue_ids(app):
    """
    Ensure that both permanent and non permanent venues are enqueues.
    The permanent/non-permanent filter comes after, during indexing.
    """
    permanent_venue = offerers_factories.VenueFactory(isPermanent=True)
    other_venue = offerers_factories.VenueFactory(isPermanent=False)

    search.async_index_venue_ids([permanent_venue.id, other_venue.id])

    enqueued_ids = app.redis_client.smembers("search:algolia:venue-ids-to-index")
    enqueued_ids = {int(venue_id) for venue_id in enqueued_ids}
    assert enqueued_ids == {permanent_venue.id, other_venue.id}


@override_settings(REDIS_VENUE_IDS_FOR_OFFERS_CHUNK_SIZE=1)
def test_index_offers_of_venues_in_queue(app):
    bookable_offer = make_bookable_offer()
    venue1 = bookable_offer.venue
    unbookable_offer = make_unbookable_offer()
    venue2 = unbookable_offer.venue
    queue = "venue_ids_for_offers"
    app.redis_client.lpush(queue, venue1.id, venue2.id)

    # `index_offers_of_venues_in_queue` pops 1 venue from the queue
    # (REDIS_VENUE_IDS_FOR_OFFERS_CHUNK_SIZE).
    search.index_offers_of_venues_in_queue()
    assert app.redis_client.llen(queue) == 1

    search.index_offers_of_venues_in_queue()
    assert app.redis_client.llen(queue) == 0

    assert bookable_offer.id in search_testing.search_store["offers"]
    assert unbookable_offer.id not in search_testing.search_store["offers"]


@override_settings(REDIS_VENUE_IDS_CHUNK_SIZE=1)
def test_index_venues_in_queue(app):
    venue1 = offerers_factories.VenueFactory()
    venue2 = offerers_factories.VenueFactory()
    queue = "search:algolia:venue-ids-to-index"
    app.redis_client.sadd(queue, venue1.id, venue2.id)

    # `index_venues_in_queue` pops 1 venue from the queue (REDIS_VENUE_IDS_CHUNK_SIZE).
    search.index_venues_in_queue()
    assert app.redis_client.scard(queue) == 1

    search.index_venues_in_queue()
    assert app.redis_client.scard(queue) == 0


class ReindexOfferIdsTest:
    def test_index_new_offer(self):
        offer = make_bookable_offer()
        assert search_testing.search_store["offers"] == {}
        search.reindex_offer_ids([offer.id])
        assert offer.id in search_testing.search_store["offers"]

    def test_no_unexpected_query_made(self):
        offer_ids = [make_bookable_offer().id for _ in range(3)]

        # 1: get offers
        # 2. get FF
        # 3. get the offers's venue id
        with assert_num_queries(3):
            search.reindex_offer_ids(offer_ids)

    def test_unindex_unbookable_offer(self, app):
        offer = make_unbookable_offer()
        search_testing.search_store["offers"][offer.id] = "dummy"
        app.redis_client.hset("indexed_offers", offer.id, "")
        search.reindex_offer_ids([offer.id])
        assert search_testing.search_store["offers"] == {}

    @mock.patch("pcapi.core.search.backends.testing.FakeClient.save_objects", fail)
    def test_handle_indexation_error(self, app):
        offer = make_bookable_offer()
        assert search_testing.search_store["offers"] == {}
        with override_settings(IS_RUNNING_TESTS=False):  # as on prod: don't catch errors
            search.reindex_offer_ids([offer.id])
        assert offer.id not in search_testing.search_store["offers"]
        assert app.redis_client.lrange("offer_ids_in_error", 0, 5) == [str(offer.id)]

    @mock.patch("pcapi.core.search.backends.testing.FakeClient.delete_objects", fail)
    def test_handle_unindexation_error(self, app):
        offer = make_unbookable_offer()
        search_testing.search_store["offers"][offer.id] = "dummy"
        app.redis_client.hset("indexed_offers", offer.id, "")
        with override_settings(IS_RUNNING_TESTS=False):  # as on prod: don't catch errors
            search.reindex_offer_ids([offer.id])
        assert offer.id in search_testing.search_store["offers"]
        assert app.redis_client.lrange("offer_ids_in_error", 0, 5) == [str(offer.id)]

    @override_features(ENABLE_VENUE_STRICT_SEARCH=True)
    def test_reindex_venues_after_reindexing_offers(self, app):
        offer = make_bookable_offer()
        assert search_testing.search_store["offers"] == {}

        search.reindex_offer_ids([offer.id])
        assert offer.id in search_testing.search_store["offers"]

        venue_ids = app.redis_client.smembers("search:algolia:venue-ids-to-index")
        venue_ids = {int(venue_id) for venue_id in venue_ids}
        assert venue_ids == {offer.venueId}


class ReindexVenueIdsTest:
    def test_index_new_venue(self):
        venue = offerers_factories.VenueFactory(isPermanent=True)
        assert search_testing.search_store["venues"] == {}
        search.reindex_venue_ids([venue.id])
        assert venue.id in search_testing.search_store["venues"]

    def test_no_unexpected_query_made(self):
        venues = offerers_factories.VenueFactory.create_batch(3, isPermanent=True)
        venue_ids = [venue.id for venue in venues]

        assert search_testing.search_store["venues"] == {}

        # load venues (1 query)
        # load FF (1 query)
        # find whether venue has at least one bookable offer (1 query per venue)
        with assert_num_queries(5):
            search.reindex_venue_ids(venue_ids)

    def test_unindex_ineligible_venues(self):
        indexable_venue = offerers_factories.VenueFactory(
            isPermanent=True, managingOfferer__isActive=True, venueTypeCode=offerers_models.VenueTypeCode.BOOKSTORE
        )

        venue1 = offerers_factories.VenueFactory(isPermanent=False)
        venue2 = offerers_factories.VenueFactory(isPermanent=True, managingOfferer__isActive=False)
        venue3 = offerers_factories.VenueFactory(
            isPermanent=True, managingOfferer__isActive=True, venueTypeCode=offerers_models.VenueTypeCode.ADMINISTRATIVE
        )

        search_testing.search_store["venues"][indexable_venue.id] = "dummy"
        search_testing.search_store["venues"][venue1.id] = "dummy"
        search_testing.search_store["venues"][venue2.id] = "dummy"
        search_testing.search_store["venues"][venue3.id] = "dummy"

        search.reindex_venue_ids([indexable_venue.id, venue1.id, venue2.id, venue3.id])
        assert search_testing.search_store["venues"].keys() == {indexable_venue.id}


@override_settings(REDIS_OFFER_IDS_CHUNK_SIZE=3)
@mock.patch("pcapi.core.search.reindex_offer_ids")
class IndexOffersInQueueTest:
    def test_cron_behaviour(self, mocked_reindex_offer_ids, app):
        items = range(1, 9)  # 8 items: 1..8
        app.redis_client.lpush("offer_ids", *items)

        search.index_offers_in_queue()

        # First run pops and indexes 3 items. Second run pops and
        # indexes another set of 3 items. And stops because there are
        # less than REDIS_OFFER_IDS_CHUNK_SIZE items left in the
        # queue.
        assert mocked_reindex_offer_ids.mock_calls == [
            mock.call({8, 7, 6}),
            mock.call({5, 4, 3}),
        ]

        assert app.redis_client.lrange("offer_ids", 0, 5) == ["2", "1"]

    def test_command_behaviour(self, mocked_reindex_offer_ids, app):
        items = range(1, 9)  # 8 items: 1..8
        app.redis_client.lpush("offer_ids", *items)

        search.index_offers_in_queue(stop_only_when_empty=True)

        # First run pops and indexes 8, 7, 6. Second run pops and
        # indexes 5, 4, 3. Third run pops 2, 1 and stops because the
        # queue is empty.
        assert mocked_reindex_offer_ids.mock_calls == [
            mock.call({8, 7, 6}),
            mock.call({5, 4, 3}),
            mock.call({2, 1}),
        ]

        assert app.redis_client.llen("offer_ids") == 0


@override_features(ENABLE_VENUE_STRICT_SEARCH=True)
def test_unindex_offer_ids(app):
    offer1 = make_bookable_offer()
    offer2 = make_bookable_offer()

    search_testing.search_store["offers"][offer1.id] = offer1
    search_testing.search_store["offers"][offer2.id] = offer2

    search.unindex_offer_ids([offer1.id, offer2.id])
    assert search_testing.search_store["offers"] == {}

    venue_ids = app.redis_client.smembers("search:algolia:venue-ids-to-index")
    venue_ids = {int(venue_id) for venue_id in venue_ids}
    assert venue_ids == {offer1.venueId, offer2.venueId}


def test_unindex_all_offers():
    search_testing.search_store["offers"][1] = "dummy"
    search_testing.search_store["offers"][2] = "dummy"

    search.unindex_all_offers()

    assert search_testing.search_store["offers"] == {}
