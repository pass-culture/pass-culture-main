import dataclasses

import pytest
import requests_mock

import pcapi.core.offers.factories as offers_factories
from pcapi.core.search.backends import appsearch
from pcapi.core.testing import override_settings


@override_settings(APPSEARCH_HOST="https://appsearch.example.com/", APPSEARCH_API_KEY="fake-key")
def get_backend():
    return appsearch.AppSearchBackend()


@dataclasses.dataclass
class FakeOffer:
    id: int


def test_enqueue_offer_ids(app):
    backend = get_backend()
    backend.enqueue_offer_ids([1])
    backend.enqueue_offer_ids({2, 3})
    backend.enqueue_offer_ids([])

    in_queue = app.redis_client.smembers("search:appsearch:offer-ids-to-index")
    assert in_queue == {"1", "2", "3"}


def test_enqueue_offer_ids_in_error(app):
    backend = get_backend()
    backend.enqueue_offer_ids_in_error([1])
    backend.enqueue_offer_ids_in_error({2, 3})
    backend.enqueue_offer_ids_in_error([])

    in_queue = app.redis_client.smembers("search:appsearch:offer-ids-in-error-to-index")
    assert in_queue == {"1", "2", "3"}


def test_enqueue_venue_ids_for_offers(app):
    backend = get_backend()
    backend.enqueue_venue_ids_for_offers([1])
    backend.enqueue_venue_ids_for_offers({2, 3})
    backend.enqueue_venue_ids_for_offers([])

    in_queue = app.redis_client.smembers("search:appsearch:venue-ids-for-offers-to-index")
    assert in_queue == {"1", "2", "3"}


def test_pop_offer_ids_from_queue(app):
    backend = get_backend()
    app.redis_client.sadd("search:appsearch:offer-ids-to-index", 1, 2, 3)

    popped = set()
    offer_ids = backend.pop_offer_ids_from_queue(count=2)
    popped |= offer_ids
    assert len(offer_ids) == 2
    assert offer_ids.issubset({1, 2, 3})

    offer_ids = backend.pop_offer_ids_from_queue(count=2)
    popped |= offer_ids
    assert len(offer_ids) == 1
    assert offer_ids.issubset({1, 2, 3})
    assert popped == {1, 2, 3}

    offer_ids = backend.pop_offer_ids_from_queue(count=2)
    assert offer_ids == set()


def test_pop_offer_ids_from_error_queue(app):
    backend = get_backend()
    app.redis_client.sadd("search:appsearch:offer-ids-in-error-to-index", 1, 2, 3)

    popped = set()
    offer_ids = backend.pop_offer_ids_from_queue(count=2, from_error_queue=True)
    popped |= offer_ids
    assert len(offer_ids) == 2
    assert offer_ids.issubset({1, 2, 3})

    offer_ids = backend.pop_offer_ids_from_queue(count=2, from_error_queue=True)
    popped |= offer_ids
    assert len(offer_ids) == 1
    assert offer_ids.issubset({1, 2, 3})
    assert popped == {1, 2, 3}

    offer_ids = backend.pop_offer_ids_from_queue(count=2, from_error_queue=True)
    assert offer_ids == set()


def test_pop_venue_ids_for_offers_from_queue(app):
    backend = get_backend()
    app.redis_client.sadd("search:appsearch:venue-ids-for-offers-to-index", 1, 2, 3)

    venue_ids = backend.pop_venue_ids_for_offers_from_queue(count=2)
    assert len(venue_ids) == 2
    assert venue_ids <= {1, 2, 3}

    # Make sure we did not pop all values off the list.
    in_queue = app.redis_client.smembers("search:appsearch:venue-ids-for-offers-to-index")
    assert len(in_queue) == 1
    assert in_queue <= {"1", "2", "3"}


def test_count_offers_to_index_from_queue(app):
    backend = get_backend()
    assert backend.count_offers_to_index_from_queue() == 0
    app.redis_client.sadd("search:appsearch:offer-ids-to-index", 1, 2, 3)
    assert backend.count_offers_to_index_from_queue() == 3


def test_count_offers_to_index_from_error_queue(app):
    backend = get_backend()
    assert backend.count_offers_to_index_from_queue(from_error_queue=True) == 0
    app.redis_client.sadd("search:appsearch:offer-ids-in-error-to-index", 1, 2, 3)
    assert backend.count_offers_to_index_from_queue(from_error_queue=True) == 3


def test_check_offer_is_indexed(app):
    backend = get_backend()
    assert backend.check_offer_is_indexed("whatever")


def test_get_batches():
    documents = list(range(1, 24))
    engine_selector = lambda document_id: f"engine-{document_id % 6}"
    batches = list(appsearch.get_batches(documents, engine_selector, size=2))
    assert batches == [
        ("engine-1", [1, 7]),
        ("engine-2", [2, 8]),
        ("engine-3", [3, 9]),
        ("engine-4", [4, 10]),
        ("engine-5", [5, 11]),
        ("engine-0", [6, 12]),
        ("engine-1", [13, 19]),
        ("engine-2", [14, 20]),
        ("engine-3", [15, 21]),
        ("engine-4", [16, 22]),
        ("engine-5", [17, 23]),
        ("engine-0", [18]),
    ]


@pytest.mark.usefixtures("db_session")
def test_index_offers(app):
    backend = get_backend()
    offers = [stock.offer for stock in offers_factories.StockFactory.create_batch(18)]
    with requests_mock.Mocker() as mock:
        posted_by_engine = {
            i: mock.post(f"https://appsearch.example.com/api/as/v1/engines/offers-{i}/documents", json=[{"errors": []}])
            for i in range(len(appsearch.OFFERS_ENGINE_NAMES))
        }
        backend.index_offers(offers)
        for i in range(6):
            assert posted_by_engine[i].call_count == 1
            posted_json = posted_by_engine[i].last_request.json()
            assert len(posted_json) == 3
            for item in posted_json:
                assert item["id"] % 6 == i


def test_unindex_offer_ids(app):
    backend = get_backend()
    app.redis_client.sadd("search:appsearch:indexed-offer-ids", "1")
    with requests_mock.Mocker() as mock:
        deleted = mock.delete("https://appsearch.example.com/api/as/v1/engines/offers-1/documents")
        deleted_educational = mock.delete(
            "https://appsearch.example.com/api/as/v1/engines/offers-educational/documents"
        )
        backend.unindex_offer_ids([1])
        deleted_json = deleted.last_request.json()
        deleted_educational_json = deleted_educational.last_request.json()
        assert deleted_json == [1]
        assert deleted_educational_json == [1]


def test_unindex_all_offers(app):
    pass  # FIXME (dbaty): this feature is not implemented yet.


@pytest.mark.usefixtures("db_session")
def test_index_venues(app):
    backend = get_backend()
    venue = offers_factories.StockFactory().offer.venue
    with requests_mock.Mocker() as mock:
        posted = mock.post(
            "https://appsearch.example.com/api/as/v1/engines/venues/documents", json=[{"item": venue.id, "errors": []}]
        )
        backend.index_venues([venue])
        posted_json = posted.last_request.json()
        assert posted_json[0]["id"] == venue.id
        assert posted_json[0]["name"] == venue.name


def test_unindex_venue_ids(app):
    backend = get_backend()
    app.redis_client.sadd("search:appsearch:indexed-venue-ids", "1")
    with requests_mock.Mocker() as mock:
        deleted = mock.delete("https://appsearch.example.com/api/as/v1/engines/venues/documents")
        backend.unindex_venue_ids([1])
        deleted_json = deleted.last_request.json()
        assert deleted_json == [1]


def test_remove_stopwords():
    description = "Il était une fois, dans la ville de Foix. Voilà Foix !"
    expected = "fois ville foix voilà foix"
    assert appsearch.remove_stopwords(description) == expected
