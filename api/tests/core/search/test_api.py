import datetime
import itertools
from unittest import mock

import pytest

from pcapi.core import search
from pcapi.core.bookings import factories as bookings_factories
from pcapi.core.bookings import models as bookings_models
from pcapi.core.offerers import models as offerers_models
import pcapi.core.offerers.factories as offerers_factories
from pcapi.core.offers import models as offers_models
import pcapi.core.offers.factories as offers_factories
from pcapi.core.search.backends import algolia
import pcapi.core.search.testing as search_testing
from pcapi.core.testing import assert_no_duplicated_queries
from pcapi.core.testing import assert_num_queries
from pcapi.core.testing import override_features
from pcapi.core.testing import override_settings


def make_bookable_offer() -> offers_models.Offer:
    return offers_factories.StockFactory().offer


def make_booked_offer() -> offers_models.Offer:
    offer = make_bookable_offer()
    offers_factories.StockFactory(offer=offer)
    now = datetime.datetime.utcnow()
    ago_30_days = now - datetime.timedelta(days=30, hours=-1)
    ago_31_days = now - datetime.timedelta(days=30, hours=1)
    bookings = []
    for stock, (status, date) in zip(
        itertools.cycle(offer.stocks),
        itertools.product(
            bookings_models.BookingStatus,
            (now, ago_30_days, ago_31_days),
        ),
    ):
        # This loop builds a booking for each possible couple of status and date,
        # shared across the existing stocks
        bookings.append(bookings_factories.BookingFactory(stock=stock, status=status, dateCreated=date))

    return offer


def make_unbookable_offer() -> offers_models.Offer:
    return offers_factories.OfferFactory()


def fail(*args, **kwargs):
    raise ValueError("It does not work")


def test_async_index_offer_ids(app):
    search.async_index_offer_ids({1, 2})
    assert app.redis_client.smembers("search:algolia:offer_ids") == {"1", "2"}


def test_async_index_offers_of_venue_ids(app):
    search.async_index_offers_of_venue_ids({1, 2})
    assert app.redis_client.smembers("search:algolia:venue_ids_for_offers") == {"1", "2"}


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
    queue = "search:algolia:venue_ids_for_offers"
    app.redis_client.sadd(queue, venue1.id, venue2.id)

    # `index_offers_of_venues_in_queue` pops 1 venue from the queue
    # (REDIS_VENUE_IDS_FOR_OFFERS_CHUNK_SIZE).
    search.index_offers_of_venues_in_queue()
    assert app.redis_client.scard(queue) == 1

    search.index_offers_of_venues_in_queue()
    assert app.redis_client.scard(queue) == 0

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

        with assert_no_duplicated_queries():
            search.reindex_offer_ids(offer_ids)

    def test_unindex_unbookable_offer(self, app):
        # given
        offer = make_unbookable_offer()
        search_testing.search_store["offers"][offer.id] = "dummy"
        app.redis_client.hset("indexed_offers", offer.id, "")

        # when
        search.reindex_offer_ids([offer.id])

        # then
        assert search_testing.search_store["offers"] == {}

    @mock.patch("pcapi.core.search.backends.testing.FakeClient.save_objects", fail)
    def test_handle_indexation_error(self, app):
        offer = make_bookable_offer()
        assert search_testing.search_store["offers"] == {}

        with override_settings(IS_RUNNING_TESTS=False):  # as on prod: don't catch errors
            search.reindex_offer_ids([offer.id])

        assert offer.id not in search_testing.search_store["offers"]
        assert app.redis_client.smembers("search:algolia:offer_ids_in_error") == {str(offer.id)}

    @mock.patch("pcapi.core.search.backends.testing.FakeClient.delete_objects", fail)
    def test_handle_unindexation_error(self, app):
        offer = make_unbookable_offer()
        search_testing.search_store["offers"][offer.id] = "dummy"
        app.redis_client.hset("indexed_offers", offer.id, "")
        with override_settings(IS_RUNNING_TESTS=False):  # as on prod: don't catch errors
            search.reindex_offer_ids([offer.id])

        assert offer.id in search_testing.search_store["offers"]
        assert app.redis_client.smembers("search:algolia:offer_ids_in_error") == {str(offer.id)}

    @override_features(ENABLE_VENUE_STRICT_SEARCH=True)
    def test_reindex_venues_after_reindexing_offers(self, app):
        offer = make_bookable_offer()
        assert search_testing.search_store["offers"] == {}

        search.reindex_offer_ids([offer.id])
        assert offer.id in search_testing.search_store["offers"]

        venue_ids = app.redis_client.smembers("search:algolia:venue-ids-to-index")
        venue_ids = {int(venue_id) for venue_id in venue_ids}
        assert venue_ids == {offer.venueId}

    @override_features(ALGOLIA_BOOKINGS_NUMBER_COMPUTATION=True)
    @override_settings(ALGOLIA_LAST_30_DAYS_BOOKINGS_RANGE_THRESHOLDS=[3, 6, 9, 12])
    def test_index_last_30_days_bookings(self, app):
        offer = make_booked_offer()
        assert search_testing.search_store["offers"] == {}
        search.reindex_offer_ids([offer.id])
        assert offer.id in search_testing.search_store["offers"]
        assert search_testing.search_store["offers"][offer.id]["offer"]["last30DaysBookings"] == 6
        assert (
            search_testing.search_store["offers"][offer.id]["offer"]["last30DaysBookingsRange"]
            == algolia.Last30DaysBookingsRange.MEDIUM.value
        )

    @override_features(ALGOLIA_BOOKINGS_NUMBER_COMPUTATION=False)
    @override_settings(ALGOLIA_LAST_30_DAYS_BOOKINGS_RANGE_THRESHOLDS=[3, 6, 9, 12])
    def test_last_30_days_bookings_computation_feature_toggle(self, app):
        offer = make_booked_offer()
        assert search_testing.search_store["offers"] == {}
        search.reindex_offer_ids([offer.id])
        assert offer.id in search_testing.search_store["offers"]
        assert search_testing.search_store["offers"][offer.id]["offer"]["last30DaysBookings"] == 0
        assert (
            search_testing.search_store["offers"][offer.id]["offer"]["last30DaysBookingsRange"]
            == algolia.Last30DaysBookingsRange.VERY_LOW.value
        )


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
        # TODO(atrancart): the query to find bookable offers is duplicated, we might want fix this N+1 problem
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
        offer_ids = list(range(1, 9))
        app.redis_client.sadd("search:algolia:offer_ids", *offer_ids)

        search.index_offers_in_queue()

        # First run pops and indexes 3 items. Second run pops and
        # indexes another set of 3 items. And stops because there are
        # less than REDIS_OFFER_IDS_CHUNK_SIZE items left in the
        # queue.
        assert mocked_reindex_offer_ids.call_count == 2

        assert app.redis_client.scard("search:algolia:offer_ids") == 2
        assert app.redis_client.smembers("search:algolia:offer_ids") <= {str(offer_id) for offer_id in offer_ids}

    def test_command_behaviour(self, mocked_reindex_offer_ids, app):
        items = list(range(1, 9))
        app.redis_client.sadd("search:algolia:offer_ids", *items)

        search.index_offers_in_queue(stop_only_when_empty=True)

        # First run pops and indexes 8, 7, 6. Second run pops and
        # indexes 5, 4, 3. Third run pops 2, 1 and stops because the
        # queue is empty.
        assert mocked_reindex_offer_ids.call_count == 3
        assert app.redis_client.scard("search:algolia:offer_ids") == 0


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
