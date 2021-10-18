from unittest import mock

import pytest

from pcapi.core import search
import pcapi.core.offers.factories as offers_factories
import pcapi.core.search.testing as search_testing
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
    assert app.redis_client.smembers("search:appsearch:offer-ids-to-index") == {"1", "2"}


def test_async_index_offers_of_venue_ids(app):
    search.async_index_offers_of_venue_ids({1, 2})
    assert app.redis_client.smembers("search:appsearch:venue-ids-for-offers-to-index") == {"1", "2"}


def test_async_index_venue_ids(app):
    """
    Ensure that both permanent and non permanent venues are enqueues.
    The permanent/non-permanent filter comes after, during indexing.
    """
    permanent_venue = offers_factories.VenueFactory(isPermanent=True)
    other_venue = offers_factories.VenueFactory(isPermanent=False)

    search.async_index_venue_ids([permanent_venue.id, other_venue.id])

    enqueued_ids = app.redis_client.smembers("search:appsearch:venue-ids-new-to-index")
    enqueued_ids = {int(venue_id) for venue_id in enqueued_ids}
    assert enqueued_ids == {permanent_venue.id, other_venue.id}


@override_settings(REDIS_VENUE_IDS_CHUNK_SIZE=1)
def test_index_offers_of_venues_in_queue(app):
    bookable_offer = make_bookable_offer()
    venue1 = bookable_offer.venue
    unbookable_offer = make_unbookable_offer()
    venue2 = unbookable_offer.venue
    queue = "search:appsearch:venue-ids-for-offers-to-index"
    app.redis_client.sadd(queue, venue1.id, venue2.id)

    # `index_offers_of_venues_in_queue` pops 1 venue from the queue
    # (REDIS_VENUE_IDS_FOR_OFFERS_TO_INDEX).
    search.index_offers_of_venues_in_queue()
    assert app.redis_client.scard(queue) == 1

    search.index_offers_of_venues_in_queue()
    assert app.redis_client.scard(queue) == 0

    assert bookable_offer.id in search_testing.search_store["offers"]
    assert unbookable_offer.id not in search_testing.search_store["offers"]


@override_settings(REDIS_VENUE_IDS_CHUNK_SIZE=1)
def test_index_venues_in_queue(app):
    venue1 = offers_factories.VenueFactory()
    venue2 = offers_factories.VenueFactory()
    queue = "search:appsearch:venue-ids-new-to-index"
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

    def test_unindex_unbookable_offer(self, app):
        offer = make_unbookable_offer()
        search_testing.search_store["offers"][offer.id] = "dummy"
        search.reindex_offer_ids([offer.id])
        assert search_testing.search_store["offers"] == {}

    @mock.patch("pcapi.core.search.backends.testing.FakeClient.create_or_update_documents", fail)
    def test_handle_indexation_error(self, app):
        offer = make_bookable_offer()
        assert search_testing.search_store["offers"] == {}
        with override_settings(IS_RUNNING_TESTS=False):  # as on prod: don't catch errors
            search.reindex_offer_ids([offer.id])
        assert offer.id not in search_testing.search_store["offers"]
        assert app.redis_client.smembers("search:appsearch:offer-ids-in-error-to-index") == {str(offer.id)}

    @mock.patch("pcapi.core.search.backends.testing.FakeClient.delete_documents", fail)
    def test_handle_unindexation_error(self, app):
        offer = make_unbookable_offer()
        search_testing.search_store["offers"][offer.id] = "dummy"
        with override_settings(IS_RUNNING_TESTS=False):  # as on prod: don't catch errors
            search.reindex_offer_ids([offer.id])
        assert offer.id in search_testing.search_store["offers"]
        assert app.redis_client.smembers("search:appsearch:offer-ids-in-error-to-index") == {str(offer.id)}


class ReindexVenueIdsTest:
    def test_index_new_venue(self):
        venue = offers_factories.VenueFactory(isPermanent=True)
        assert search_testing.search_store["venues"] == {}
        search.reindex_venue_ids([venue.id])
        assert venue.id in search_testing.search_store["venues"]

    def test_unindex_ineligible_venues(self):
        venue1 = offers_factories.VenueFactory(isPermanent=False)
        venue2 = offers_factories.VenueFactory(isPermanent=True, managingOfferer__isActive=False)
        search_testing.search_store["venues"][venue1.id] = "dummy"
        search_testing.search_store["venues"][venue2.id] = "dummy"
        search.reindex_venue_ids([venue1.id, venue2.id])
        assert search_testing.search_store["venues"] == {}


@override_settings(REDIS_OFFER_IDS_CHUNK_SIZE=3)
@mock.patch("pcapi.core.search._reindex_offer_ids")
class IndexOffersInQueueTest:
    def test_cron_behaviour(self, mocked_reindex_offer_ids, app):
        items = set(range(1, 9))  # 8 items: 1..8
        app.redis_client.sadd("search:appsearch:offer-ids-to-index", *items)

        search.index_offers_in_queue()

        # First run pops and indexes 3 items. Second run pops and
        # indexes another set of 3 items. And stops because there are
        # less than REDIS_OFFER_IDS_CHUNK_SIZE items left in the
        # queue.
        calls = mocked_reindex_offer_ids.mock_calls
        assert len(calls) == 2

        assert calls[0].args[1].issubset(items)
        assert len(calls[0].args[1]) == 3

        assert calls[1].args[1].issubset(items)
        assert len(calls[1].args[1]) == 3

        assert app.redis_client.scard("search:appsearch:offer-ids-to-index") == 2

    def test_command_behaviour(self, mocked_reindex_offer_ids, app):
        # Put 8 items in the queue, in that order: 1..8
        items = set(range(1, 9))  # 8 items: 1..8
        app.redis_client.sadd("search:appsearch:offer-ids-to-index", *items)

        search.index_offers_in_queue(stop_only_when_empty=True)

        # First run pops and indexes 1, 2, 3. Second run pops and
        # indexes 4, 5, 6. Third run pops 7, 8 and stops because the
        # queue is empty.
        calls = mocked_reindex_offer_ids.mock_calls
        assert len(calls) == 3

        assert calls[0].args[1].issubset(items)
        assert len(calls[0].args[1]) == 3

        assert calls[1].args[1].issubset(items)
        assert len(calls[1].args[1]) == 3

        assert calls[2].args[1].issubset(items)
        assert len(calls[2].args[1]) == 2

        assert app.redis_client.llen("search:appsearch:offer-ids-to-index") == 0


def test_unindex_offer_ids():
    search_testing.search_store["offers"][1] = "dummy"
    search_testing.search_store["offers"][2] = "dummy"

    search.unindex_offer_ids([1, 2])

    assert search_testing.search_store["offers"] == {}


def test_unindex_all_offers():
    search_testing.search_store["offers"][1] = "dummy"
    search_testing.search_store["offers"][2] = "dummy"

    search.unindex_all_offers()

    assert search_testing.search_store["offers"] == {}
