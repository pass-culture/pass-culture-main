import datetime
import itertools
from unittest import mock

import pytest

import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
import pcapi.core.search.testing as search_testing
from pcapi.core import search
from pcapi.core.bookings import factories as bookings_factories
from pcapi.core.bookings import models as bookings_models
from pcapi.core.categories import subcategories
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import models as offers_models
from pcapi.core.search import redis_queues
from pcapi.core.search import serialization
from pcapi.core.testing import assert_no_duplicated_queries
from pcapi.core.testing import assert_num_queries


pytestmark = pytest.mark.usefixtures("db_session")


def make_bookable_offer(venue: offerers_models.Venue | None = None) -> offers_models.Offer:
    return offers_factories.StockFactory(offer__venue=venue or offerers_factories.VenueFactory()).offer


def make_fully_featured_offer(venue: offerers_models.Venue | None = None) -> offers_models.Offer:
    product = offers_factories.ProductFactory()
    offers_factories.ProductMediationFactory(product=product)
    offer = offers_factories.OfferFactory(product=product, venue=venue or offerers_factories.VenueFactory())
    offers_factories.StockFactory(offer=offer)
    return offer


def make_future_offer(venue: offerers_models.Venue | None = None) -> offers_models.Offer:
    publication_date = datetime.datetime.utcnow() - datetime.timedelta(days=1)
    booking_date = datetime.datetime.utcnow() + datetime.timedelta(days=30)
    return offers_factories.StockFactory(
        offer__venue=venue or offerers_factories.VenueFactory(),
        offer__publicationDatetime=publication_date,
        offer__bookingAllowedDatetime=booking_date,
    ).offer


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
    search.async_index_offer_ids({1, 2}, reason=search.IndexationReason.OFFER_UPDATE)
    queue = redis_queues.REDIS_OFFER_IDS_NAME
    assert app.redis_client.smembers(queue) == {"1", "2"}


def test_async_index_offers_of_venue_ids(app):
    search.async_index_offers_of_venue_ids({1, 2}, reason=search.IndexationReason.VENUE_UPDATE)
    queue = redis_queues.REDIS_VENUE_IDS_FOR_OFFERS_NAME
    assert app.redis_client.smembers(queue) == {"1", "2"}


def test_async_index_venue_ids(app):
    """
    Ensure that both permanent and non permanent venues are enqueues.
    The permanent/non-permanent filter comes after, during indexing.
    """
    permanent_venue = offerers_factories.VenueFactory(isPermanent=True)
    other_venue = offerers_factories.VenueFactory(isPermanent=False)

    search.async_index_venue_ids(
        [permanent_venue.id, other_venue.id],
        search.IndexationReason.VENUE_CREATION,
    )

    queue = redis_queues.REDIS_VENUE_IDS_TO_INDEX
    enqueued_ids = app.redis_client.smembers(queue)
    enqueued_ids = {int(venue_id) for venue_id in enqueued_ids}
    assert enqueued_ids == {permanent_venue.id, other_venue.id}


@pytest.mark.settings(REDIS_VENUE_IDS_FOR_OFFERS_CHUNK_SIZE=1)
def test_index_offers_of_venues_in_queue(app):
    bookable_offer = make_bookable_offer()
    venue1 = bookable_offer.venue
    unbookable_offer = make_unbookable_offer()
    venue2 = unbookable_offer.venue
    venue3 = offerers_factories.VenueFactory(managingOfferer=offerers_factories.ClosedOffererFactory())
    closed_offer = make_bookable_offer(venue3)
    queue = redis_queues.REDIS_VENUE_IDS_FOR_OFFERS_NAME
    app.redis_client.sadd(queue, venue1.id, venue2.id, venue3.id)

    # `index_offers_of_venues_in_queue` pops 1 venue from the queue
    # (REDIS_VENUE_IDS_FOR_OFFERS_CHUNK_SIZE).
    print(app.redis_client.smembers(queue))
    search.index_offers_of_venues_in_queue()
    print(app.redis_client.smembers(queue))
    assert app.redis_client.scard(queue) == 2

    search.index_offers_of_venues_in_queue()
    assert app.redis_client.scard(queue) == 1

    search.index_offers_of_venues_in_queue()
    assert app.redis_client.scard(queue) == 0

    assert bookable_offer.id in search_testing.search_store["offers"]
    assert unbookable_offer.id not in search_testing.search_store["offers"]
    assert closed_offer.id not in search_testing.search_store["offers"]


@pytest.mark.settings(REDIS_VENUE_IDS_CHUNK_SIZE=1)
def test_index_venues_in_queue(app):
    venue1 = offerers_factories.VenueFactory()
    venue2 = offerers_factories.VenueFactory()
    queue = redis_queues.REDIS_VENUE_IDS_TO_INDEX
    app.redis_client.sadd(queue, venue1.id, venue2.id)

    # `index_venues_in_queue` pops 1 venue from the queue (REDIS_VENUE_IDS_CHUNK_SIZE).
    search.index_venues_in_queue()
    assert app.redis_client.scard(queue) == 1

    search.index_venues_in_queue()
    assert app.redis_client.scard(queue) == 0


class ReindexOfferIdsTest:
    def test_index_new_offer(self):
        offer = make_bookable_offer()
        future_offer = make_future_offer()
        assert search_testing.search_store["offers"] == {}
        search.reindex_offer_ids([offer.id, future_offer.id])
        assert set(search_testing.search_store["offers"]) == {offer.id, future_offer.id}

    def test_no_unexpected_query_made(self):
        offer_ids = [make_bookable_offer().id for _ in range(3)]
        offer_ids.extend([make_future_offer().id for _ in range(3, 6)])

        with assert_no_duplicated_queries():
            search.reindex_offer_ids(offer_ids)

    def test_unindex_unbookable_offer(self, app):
        # given
        offer = make_unbookable_offer()
        search_testing.search_store["offers"][offer.id] = "dummy"
        app.redis_client.hset(redis_queues.REDIS_HASHMAP_INDEXED_OFFERS_NAME, offer.id, "")

        # when
        search.reindex_offer_ids([offer.id])

        # then
        assert search_testing.search_store["offers"] == {}

    def test_closed_offerer(self, app):
        offer = make_bookable_offer(
            offerers_factories.VenueFactory(managingOfferer=offerers_factories.ClosedOffererFactory())
        )
        search_testing.search_store["offers"][offer.id] = "dummy"
        app.redis_client.hset(redis_queues.REDIS_HASHMAP_INDEXED_OFFERS_NAME, offer.id, "")

        search.reindex_offer_ids([offer.id])

        assert search_testing.search_store["offers"] == {}

    def test_that_base_query_is_correct(self, app):
        # Make sure that `get_base_query_for_offer_indexation` loads
        # all offers and related data that is expected by
        # `reindex_offer_ids()`.
        unbookable = make_unbookable_offer()
        bookable = make_fully_featured_offer()
        future_offer = make_future_offer()
        past = datetime.datetime.utcnow() - datetime.timedelta(days=10)
        future = datetime.datetime.utcnow() + datetime.timedelta(days=10)
        multi_dates_unbookable = offers_factories.EventStockFactory(beginningDatetime=past).offer
        multi_dates_bookable = offers_factories.EventStockFactory(beginningDatetime=past).offer
        offers_factories.EventStockFactory(offer=multi_dates_bookable, beginningDatetime=future)
        offer_ids = {unbookable.id, bookable.id, future_offer.id, multi_dates_unbookable.id, multi_dates_bookable.id}
        for offer_id in offer_ids:
            search_testing.search_store["offers"][offer_id] = "dummy"
            app.redis_client.hset(redis_queues.REDIS_HASHMAP_INDEXED_OFFERS_NAME, offer_id, "")

        num_queries = 1  # base query for indexation
        num_queries += 1  # FF
        num_queries += 1  # last30DaysBookings

        num_queries += 1  # venues from offers
        with assert_num_queries(num_queries):
            with assert_no_duplicated_queries():
                search.reindex_offer_ids(offer_ids)

        assert set(search_testing.search_store["offers"]) == {bookable.id, future_offer.id, multi_dates_bookable.id}

    @mock.patch("pcapi.core.search.backends.testing.FakeClient.save_objects", fail)
    @pytest.mark.settings(CATCH_INDEXATION_EXCEPTIONS=True)  # as on prod: don't raise errors
    def test_handle_indexation_error(self, app):
        offer = make_bookable_offer()
        assert search_testing.search_store["offers"] == {}

        search.reindex_offer_ids([offer.id])

        assert offer.id not in search_testing.search_store["offers"]
        error_queue = redis_queues.REDIS_OFFER_IDS_IN_ERROR_NAME
        assert app.redis_client.smembers(error_queue) == {str(offer.id)}

    @mock.patch("pcapi.core.search.backends.testing.FakeClient.delete_objects", fail)
    @pytest.mark.settings(CATCH_INDEXATION_EXCEPTIONS=True)  # as on prod: don't raise errors
    def test_handle_unindexation_error(self, app):
        offer = make_unbookable_offer()
        search_testing.search_store["offers"][offer.id] = "dummy"
        app.redis_client.hset(redis_queues.REDIS_HASHMAP_INDEXED_OFFERS_NAME, offer.id, "")

        search.reindex_offer_ids([offer.id])

        assert offer.id in search_testing.search_store["offers"]
        error_queue = redis_queues.REDIS_OFFER_IDS_IN_ERROR_NAME
        assert app.redis_client.smembers(error_queue) == {str(offer.id)}

    @pytest.mark.features(ENABLE_VENUE_STRICT_SEARCH=True)
    def test_reindex_venues_after_reindexing_offers(self, app):
        offer = make_bookable_offer()
        assert search_testing.search_store["offers"] == {}

        search.reindex_offer_ids([offer.id])
        assert offer.id in search_testing.search_store["offers"]

        venue_queue = redis_queues.REDIS_VENUE_IDS_TO_INDEX
        venue_ids = app.redis_client.smembers(venue_queue)
        venue_ids = [int(venue_id) for venue_id in venue_ids]
        assert venue_ids == [offer.venueId]

    @pytest.mark.settings(ALGOLIA_LAST_30_DAYS_BOOKINGS_RANGE_THRESHOLDS=[3, 6, 9, 12])
    @pytest.mark.features(ALGOLIA_BOOKINGS_NUMBER_COMPUTATION=True)
    def test_index_last_30_days_bookings(self, app):
        offer = make_booked_offer()
        assert search_testing.search_store["offers"] == {}
        search.reindex_offer_ids([offer.id])
        assert offer.id in search_testing.search_store["offers"]
        assert search_testing.search_store["offers"][offer.id]["offer"]["last30DaysBookings"] == 6
        assert (
            search_testing.search_store["offers"][offer.id]["offer"]["last30DaysBookingsRange"]
            == serialization.Last30DaysBookingsRange.MEDIUM.value
        )

    @pytest.mark.settings(ALGOLIA_LAST_30_DAYS_BOOKINGS_RANGE_THRESHOLDS=[3, 6, 9, 12])
    @pytest.mark.features(ALGOLIA_BOOKINGS_NUMBER_COMPUTATION=False)
    def test_last_30_days_bookings_computation_feature_toggle(self, app):
        offer = make_booked_offer()
        assert search_testing.search_store["offers"] == {}
        search.reindex_offer_ids([offer.id])
        assert offer.id in search_testing.search_store["offers"]
        assert search_testing.search_store["offers"][offer.id]["offer"]["last30DaysBookings"] == 0
        assert (
            search_testing.search_store["offers"][offer.id]["offer"]["last30DaysBookingsRange"]
            == serialization.Last30DaysBookingsRange.VERY_LOW.value
        )


class ReindexVenueIdsTest:
    def test_index_new_venue(self):
        venue = offerers_factories.VenueFactory(isPermanent=True)
        offers_factories.OfferFactory(venue=venue)
        assert search_testing.search_store["venues"] == {}
        search.reindex_venue_ids([venue.id])
        assert venue.id in search_testing.search_store["venues"]

    def test_index_closed_venue(self):
        venue = offerers_factories.VenueFactory(
            isPermanent=True, managingOfferer=offerers_factories.ClosedOffererFactory()
        )
        assert search_testing.search_store["venues"] == {}
        search.reindex_venue_ids([venue.id])
        assert venue.id not in search_testing.search_store["venues"]

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
        offers_factories.OfferFactory(venue=indexable_venue)

        venue1 = offerers_factories.VenueFactory(isPermanent=False)
        venue2 = offerers_factories.VenueFactory(isPermanent=True, managingOfferer__isActive=False)
        venue3 = offerers_factories.VenueFactory(
            isPermanent=True, managingOfferer__isActive=True, venueTypeCode=offerers_models.VenueTypeCode.OTHER
        )

        search_testing.search_store["venues"][indexable_venue.id] = "dummy"
        search_testing.search_store["venues"][venue1.id] = "dummy"
        search_testing.search_store["venues"][venue2.id] = "dummy"
        search_testing.search_store["venues"][venue3.id] = "dummy"

        search.reindex_venue_ids([indexable_venue.id, venue1.id, venue2.id, venue3.id])
        assert search_testing.search_store["venues"].keys() == {indexable_venue.id}


@pytest.mark.settings(REDIS_OFFER_IDS_CHUNK_SIZE=3)
@mock.patch("pcapi.core.search.reindex_offer_ids")
class IndexOffersInQueueTest:
    def test_cron_behaviour(self, mocked_reindex_offer_ids, app):
        queue = redis_queues.REDIS_OFFER_IDS_NAME
        offer_ids = list(range(1, 9))
        app.redis_client.sadd(queue, *offer_ids)

        search.index_offers_in_queue()

        # First run pops and indexes 3 random ids.
        # Second run pops and indexes 3 other random ids,
        # Third run pops and indexes the last 2 items
        assert mocked_reindex_offer_ids.call_count == 3

        assert app.redis_client.scard(queue) == 0

    def test_command_behaviour_when_no_limit(self, mocked_reindex_offer_ids, app):
        queue = redis_queues.REDIS_OFFER_IDS_NAME
        items = list(range(1, 9))
        app.redis_client.sadd(queue, *items)

        search.index_offers_in_queue(max_batches_to_process=None)

        # First run pops and indexes 3 random ids.
        # Second run pops and indexes 3 other random ids,
        # Third run pops and indexes the last 2 items,
        # and stops because the queue is empty.
        assert mocked_reindex_offer_ids.call_count == 3
        assert app.redis_client.scard(queue) == 0

    def test_command_behaviour_when_limit_is_set(self, mocked_reindex_offer_ids, app):
        queue = redis_queues.REDIS_OFFER_IDS_NAME
        items = list(range(1, 9))
        app.redis_client.sadd(queue, *items)

        search.index_offers_in_queue(max_batches_to_process=2)

        # First run pops and indexes 3 random ids.
        # Second run pops and indexes 3 other random ids,
        # and stops because the maximum number of batches is reached
        assert mocked_reindex_offer_ids.call_count == 2
        assert app.redis_client.scard(queue) == 2
        assert app.redis_client.smembers(queue) <= set(str(id_) for id_ in items)


@pytest.mark.features(ENABLE_VENUE_STRICT_SEARCH=True)
def test_unindex_offer_ids(app):
    offer1 = make_bookable_offer()
    offer2 = make_bookable_offer()

    search_testing.search_store["offers"][offer1.id] = offer1
    search_testing.search_store["offers"][offer2.id] = offer2

    search.unindex_offer_ids([offer1.id, offer2.id])
    assert search_testing.search_store["offers"] == {}

    venue_ids = app.redis_client.smembers(redis_queues.REDIS_VENUE_IDS_TO_INDEX)
    venue_ids = {int(venue_id) for venue_id in venue_ids}
    assert venue_ids == {offer1.venueId, offer2.venueId}


def test_unindex_all_offers():
    search_testing.search_store["offers"][1] = "dummy"
    search_testing.search_store["offers"][2] = "dummy"

    search.unindex_all_offers()

    assert search_testing.search_store["offers"] == {}


class UpdateProductBookingCountTest:
    @mock.patch("pcapi.core.search.get_last_30_days_bookings_for_eans", return_value={})
    def test_booking_on_product_without_ean(self, _mock):
        product = offers_factories.ProductFactory()
        bookings_factories.BookingFactory(stock__offer__product=product)

        search.update_last_30_days_bookings_for_eans()

        assert product.last_30_days_booking is None

    @mock.patch("pcapi.core.search.get_last_30_days_bookings_for_eans")
    def test_no_unexpected_query_made(self, _mock):
        offers = [make_bookable_offer() for _ in range(3)]
        bookings_factories.BookingFactory.create_batch(3, stock__offer=offers[0])
        bookings_factories.BookingFactory.create_batch(3, stock__offer=offers[1])
        bookings_factories.BookingFactory.create_batch(3, stock__offer=offers[2])

        with assert_no_duplicated_queries():
            search.update_products_last_30_days_booking_count()

    @mock.patch("pcapi.core.search.update_booking_count_by_product")
    @mock.patch("pcapi.core.search.async_index_offer_ids")
    def test_all_offers_are_indexed(self, mock_async_index_offer_ids, mock_update_booking_count_by_product, app):
        product = offers_factories.ProductFactory()
        mock_update_booking_count_by_product.return_value = [product]
        offer1 = offers_factories.OfferFactory(product=product)
        offer2 = offers_factories.OfferFactory(product=product)

        search.update_products_last_30_days_booking_count(1)

        assert mock_async_index_offer_ids.call_count == 2
        mock_async_index_offer_ids.assert_any_call({offer1.id}, reason=search.IndexationReason.BOOKING_COUNT_CHANGE)
        mock_async_index_offer_ids.assert_any_call({offer2.id}, reason=search.IndexationReason.BOOKING_COUNT_CHANGE)


class ReadProductBookingCountTest:
    def test_is_reindexed(self):
        product = offers_factories.ProductFactory(last_30_days_booking=1)
        stock = offers_factories.StockFactory(offer__product=product)

        search.reindex_offer_ids([stock.offer.id])

        assert search_testing.search_store["offers"][stock.offer.id]["offer"].get("last30DaysBookings") == 1

    @mock.patch("pcapi.core.search.get_last_30_days_bookings_for_eans", return_value={"1234567890987": 1})
    def test_reindex_latest_computed_booking_count_only(self, _mock):
        product = offers_factories.ProductFactory(ean="1234567890987")
        offer = offers_factories.OfferFactory(product=product)
        bookings_factories.BookingFactory(stock__offer=offer)

        search.update_booking_count_by_product()
        bookings_factories.BookingFactory(stock__offer=offer)
        search.reindex_offer_ids([offer.id])

        assert search_testing.search_store["offers"][offer.id]["offer"].get("last30DaysBookings") == 1


@mock.patch("pcapi.core.search.update_last_30_days_bookings_for_eans", return_value=list(range(101)))
@mock.patch("pcapi.core.search.update_last_30_days_bookings_for_movies", return_value=list(range(101)))
def test_limit_products_to_reindex_depending_on_algolia_limit(_mock_eans, _mock_movies, settings):
    settings.ALGOLIA_OFFERS_INDEX_MAX_SIZE = -1
    items = search.update_booking_count_by_product()
    assert len(items) == 202

    settings.ALGOLIA_OFFERS_INDEX_MAX_SIZE = 1
    items = search.update_booking_count_by_product()
    assert len(items) == 200


def test_booking_count_for_movies():
    product = offers_factories.ProductFactory(subcategoryId=subcategories.SEANCE_CINE.id)
    offer = offers_factories.OfferFactory(product=product)
    bookings_factories.BookingFactory(
        stock__offer=offer,
        dateCreated=datetime.date.today(),
        status=bookings_models.BookingStatus.CONFIRMED,
    )

    search.update_last_30_days_bookings_for_movies()
    search.reindex_offer_ids([offer.id])

    assert search_testing.search_store["offers"][offer.id]["offer"].get("last30DaysBookings") == 1
