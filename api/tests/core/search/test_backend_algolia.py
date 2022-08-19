import dataclasses

import pytest
import requests_mock

import pcapi.core.educational.factories as educational_factories
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
from pcapi.core.search.backends import algolia


pytestmark = pytest.mark.usefixtures("db_session")


def get_backend():
    return algolia.AlgoliaBackend()


@dataclasses.dataclass
class FakeOffer:
    id: int


def test_enqueue_offer_ids(app):
    backend = get_backend()
    backend.enqueue_offer_ids([1])
    backend.enqueue_offer_ids({2, 3})
    backend.enqueue_offer_ids([])
    assert set(app.redis_client.lrange("offer_ids", 0, 5)) == {"1", "2", "3"}


def test_enqueue_offer_ids_in_error(app):
    backend = get_backend()
    backend.enqueue_offer_ids_in_error([1])
    backend.enqueue_offer_ids_in_error({2, 3})
    backend.enqueue_offer_ids_in_error([])
    assert set(app.redis_client.lrange("offer_ids_in_error", 0, 5)) == {"1", "2", "3"}


def test_enqueue_collective_offer_ids(app):
    backend = get_backend()
    backend.enqueue_collective_offer_ids([1])
    backend.enqueue_collective_offer_ids({2, 3})
    backend.enqueue_collective_offer_ids([])
    assert app.redis_client.smembers("search:algolia:collective-offer-ids-to-index") == {"1", "2", "3"}


def test_enqueue_collective_offer_ids_in_error(app):
    backend = get_backend()
    backend.enqueue_collective_offer_ids_in_error([1])
    backend.enqueue_collective_offer_ids_in_error({2, 3})
    backend.enqueue_collective_offer_ids_in_error([])
    assert app.redis_client.smembers("search:algolia:collective-offer-ids-in-error-to-index") == {
        "1",
        "2",
        "3",
    }


def test_enqueue_collective_offer_template_ids(app):
    backend = get_backend()
    backend.enqueue_collective_offer_template_ids([1])
    backend.enqueue_collective_offer_template_ids({2, 3})
    backend.enqueue_collective_offer_template_ids([])
    assert app.redis_client.smembers("search:algolia:collective-offer-template-ids-to-index") == {
        "1",
        "2",
        "3",
    }


def test_enqueue_collective_offer_template_ids_in_error(app):
    backend = get_backend()
    backend.enqueue_collective_offer_template_ids_in_error([1])
    backend.enqueue_collective_offer_template_ids_in_error({2, 3})
    backend.enqueue_collective_offer_template_ids_in_error([])
    assert app.redis_client.smembers("search:algolia:collective-offer-template-ids-in-error-to-index") == {
        "1",
        "2",
        "3",
    }


def test_enqueue_venue_ids_for_offers(app):
    backend = get_backend()
    backend.enqueue_venue_ids_for_offers([1])
    backend.enqueue_venue_ids_for_offers({2, 3})
    backend.enqueue_venue_ids_for_offers([])
    assert set(app.redis_client.lrange("venue_ids_for_offers", 0, 5)) == {"1", "2", "3"}


def test_pop_offer_ids_from_queue(app):
    backend = get_backend()
    app.redis_client.lpush("offer_ids", 1, 2, 3)

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
    app.redis_client.lpush("offer_ids_in_error", 1, 2, 3)

    offer_ids = backend.pop_offer_ids_from_queue(count=2, from_error_queue=True)
    assert offer_ids == {3, 2}

    offer_ids = backend.pop_offer_ids_from_queue(count=2, from_error_queue=True)
    assert offer_ids == {1}

    offer_ids = backend.pop_offer_ids_from_queue(count=2, from_error_queue=True)
    assert offer_ids == set()


def test_get_venue_ids_for_offers_from_queue(app):
    backend = get_backend()
    # The following pushes 1 to head, then 2 to head, etc. In the end,
    # we'll get `[3, 2, 1]` in that order.
    app.redis_client.lpush("venue_ids_for_offers", 1, 2, 3)

    venue_ids = backend.pop_venue_ids_for_offers_from_queue(count=2)
    assert venue_ids == {3, 2}

    venue_ids = backend.pop_venue_ids_for_offers_from_queue(count=1)
    assert venue_ids == {1}

    # Make sure we did pop values off the list.
    assert not set(app.redis_client.lrange("venue_ids_for_offers", 0, 5))


def test_count_offers_to_index_from_queue(app):
    backend = get_backend()
    assert backend.count_offers_to_index_from_queue() == 0
    app.redis_client.lpush("offer_ids", 1, 2, 3)
    assert backend.count_offers_to_index_from_queue() == 3


def test_count_offers_to_index_from_error_queue(app):
    backend = get_backend()
    assert backend.count_offers_to_index_from_queue(from_error_queue=True) == 0
    app.redis_client.lpush("offer_ids_in_error", 1, 2, 3)
    assert backend.count_offers_to_index_from_queue(from_error_queue=True) == 3


def test_check_offer_is_indexed(app):
    backend = get_backend()
    app.redis_client.hset("indexed_offers", "1", "")
    assert backend.check_offer_is_indexed(FakeOffer(id=1))
    assert not backend.check_offer_is_indexed(FakeOffer(id=2))


def test_enqueue_venue_ids(app):
    backend = get_backend()

    backend.enqueue_venue_ids([1])
    backend.enqueue_venue_ids({2, 3})
    backend.enqueue_venue_ids([])
    assert app.redis_client.smembers("search:algolia:venue-ids-to-index") == {"1", "2", "3"}


def test_enqueue_venue_ids_in_error(app):
    backend = get_backend()

    backend.enqueue_venue_ids_in_error([1])
    backend.enqueue_venue_ids_in_error({2, 3})
    backend.enqueue_venue_ids_in_error([])
    assert app.redis_client.smembers("search:algolia:venue-ids-in-error-to-index") == {"1", "2", "3"}


def test_pop_venue_ids_from_queue(app):
    backend = get_backend()
    app.redis_client.sadd("search:algolia:venue-ids-to-index", 1, 2, 3)

    popped = set()
    venue_ids = backend.pop_venue_ids_from_queue(count=2)
    popped |= venue_ids
    assert len(venue_ids) == 2
    assert venue_ids.issubset({1, 2, 3})

    venue_ids = backend.pop_venue_ids_from_queue(count=2)
    popped |= venue_ids
    assert len(venue_ids) == 1
    assert venue_ids.issubset({1, 2, 3})
    assert popped == {1, 2, 3}

    venue_ids = backend.pop_venue_ids_from_queue(count=2)
    assert venue_ids == set()


def test_pop_venue_ids_from_error_queue(app):
    backend = get_backend()
    app.redis_client.sadd("search:algolia:venue-ids-in-error-to-index", 1, 2, 3)

    popped = set()
    venue_ids = backend.pop_venue_ids_from_queue(count=2, from_error_queue=True)
    popped |= venue_ids
    assert len(venue_ids) == 2
    assert venue_ids.issubset({1, 2, 3})

    venue_ids = backend.pop_venue_ids_from_queue(count=2, from_error_queue=True)
    popped |= venue_ids
    assert len(venue_ids) == 1
    assert venue_ids.issubset({1, 2, 3})
    assert popped == {1, 2, 3}

    venue_ids = backend.pop_venue_ids_from_queue(count=2, from_error_queue=True)
    assert venue_ids == set()


def test_pop_collective_offer_ids_from_queue(app):
    backend = get_backend()
    app.redis_client.sadd("search:algolia:collective-offer-ids-to-index", 1, 2, 3)

    popped = set()
    collective_offer_ids = backend.pop_collective_offer_ids_from_queue(count=2)
    popped |= collective_offer_ids
    assert len(collective_offer_ids) == 2
    assert collective_offer_ids.issubset({1, 2, 3})

    collective_offer_ids = backend.pop_collective_offer_ids_from_queue(count=2)
    popped |= collective_offer_ids
    assert len(collective_offer_ids) == 1
    assert collective_offer_ids.issubset({1, 2, 3})
    assert popped == {1, 2, 3}

    collective_offer_ids = backend.pop_collective_offer_ids_from_queue(count=2)
    assert collective_offer_ids == set()


def test_pop_collective_offer_ids_from_error_queue(app):
    backend = get_backend()
    app.redis_client.sadd("search:algolia:collective-offer-ids-in-error-to-index", 1, 2, 3)

    popped = set()
    collective_offer_ids = backend.pop_collective_offer_ids_from_queue(count=2, from_error_queue=True)
    popped |= collective_offer_ids
    assert len(collective_offer_ids) == 2
    assert collective_offer_ids.issubset({1, 2, 3})

    collective_offer_ids = backend.pop_collective_offer_ids_from_queue(count=2, from_error_queue=True)
    popped |= collective_offer_ids
    assert len(collective_offer_ids) == 1
    assert collective_offer_ids.issubset({1, 2, 3})
    assert popped == {1, 2, 3}

    collective_offer_ids = backend.pop_collective_offer_ids_from_queue(count=2, from_error_queue=True)
    assert collective_offer_ids == set()


def test_pop_collective_offer_template_ids_from_queue(app):
    backend = get_backend()
    app.redis_client.sadd("search:algolia:collective-offer-template-ids-to-index", 1, 2, 3)

    popped = set()
    collective_offer_template_ids = backend.pop_collective_offer_template_ids_from_queue(count=2)
    popped |= collective_offer_template_ids
    assert len(collective_offer_template_ids) == 2
    assert collective_offer_template_ids.issubset({1, 2, 3})

    collective_offer_template_ids = backend.pop_collective_offer_template_ids_from_queue(count=2)
    popped |= collective_offer_template_ids
    assert len(collective_offer_template_ids) == 1
    assert collective_offer_template_ids.issubset({1, 2, 3})
    assert popped == {1, 2, 3}

    collective_offer_template_ids = backend.pop_collective_offer_template_ids_from_queue(count=2)
    assert collective_offer_template_ids == set()


def test_pop_collective_offer_template_ids_from_error_queue(app):
    backend = get_backend()
    app.redis_client.sadd("search:algolia:collective-offer-template-ids-in-error-to-index", 1, 2, 3)

    popped = set()
    collective_offer_template_ids = backend.pop_collective_offer_template_ids_from_queue(count=2, from_error_queue=True)
    popped |= collective_offer_template_ids
    assert len(collective_offer_template_ids) == 2
    assert collective_offer_template_ids.issubset({1, 2, 3})

    collective_offer_template_ids = backend.pop_collective_offer_template_ids_from_queue(count=2, from_error_queue=True)
    popped |= collective_offer_template_ids
    assert len(collective_offer_template_ids) == 1
    assert collective_offer_template_ids.issubset({1, 2, 3})
    assert popped == {1, 2, 3}

    collective_offer_template_ids = backend.pop_collective_offer_template_ids_from_queue(count=2, from_error_queue=True)
    assert collective_offer_template_ids == set()


@pytest.mark.usefixtures("db_session")
def test_index_offers(app):
    backend = get_backend()
    offer = offers_factories.StockFactory().offer
    with requests_mock.Mocker() as mock:
        posted = mock.post("https://dummy-app-id.algolia.net/1/indexes/offers/batch", json={})
        backend.index_offers([offer])
        posted_json = posted.last_request.json()
        assert posted_json["requests"][0]["action"] == "updateObject"
        assert posted_json["requests"][0]["body"]["objectID"] == offer.id
    assert backend.check_offer_is_indexed(offer)


def test_unindex_offer_ids(app):
    backend = get_backend()
    app.redis_client.hset("indexed_offers", "1", "")
    with requests_mock.Mocker() as mock:
        posted = mock.post("https://dummy-app-id.algolia.net/1/indexes/offers/batch", json={})
        backend.unindex_offer_ids([1])
        posted_json = posted.last_request.json()
        assert posted_json["requests"][0]["action"] == "deleteObject"
        assert posted_json["requests"][0]["body"]["objectID"] == 1
    assert not backend.check_offer_is_indexed(FakeOffer(id=1))


def test_unindex_all_offers(app):
    backend = get_backend()
    app.redis_client.hset("indexed_offers", "1", "")
    with requests_mock.Mocker() as mock:
        posted = mock.post("https://dummy-app-id.algolia.net/1/indexes/offers/clear", json={})
        backend.unindex_all_offers()
        assert posted.called
    assert not backend.check_offer_is_indexed(FakeOffer(id=1))


def test_index_venues(app):
    backend = get_backend()
    venue = offerers_factories.VenueFactory.build()
    with requests_mock.Mocker() as mock:
        posted = mock.post("https://dummy-app-id.algolia.net/1/indexes/venues/batch", json={})
        backend.index_venues([venue])
        posted_json = posted.last_request.json()
        assert posted_json["requests"][0]["action"] == "updateObject"
        assert posted_json["requests"][0]["body"]["objectID"] == venue.id


def test_unindex_venue_ids(app):
    backend = get_backend()
    with requests_mock.Mocker() as mock:
        posted = mock.post("https://dummy-app-id.algolia.net/1/indexes/venues/batch", json={})
        backend.unindex_venue_ids([1])
        posted_json = posted.last_request.json()
        assert posted_json["requests"][0]["action"] == "deleteObject"
        assert posted_json["requests"][0]["body"]["objectID"] == 1


def test_index_collective_offers():
    backend = get_backend()
    collective_offer = educational_factories.CollectiveStockFactory.build().collectiveOffer
    with requests_mock.Mocker() as mock:
        posted = mock.post("https://dummy-app-id.algolia.net/1/indexes/testing-collective-offers/batch", json={})
        backend.index_collective_offers([collective_offer])
        posted_json = posted.last_request.json()
        assert posted_json["requests"][0]["action"] == "updateObject"
        assert posted_json["requests"][0]["body"]["objectID"] == collective_offer.id


def test_unindex_collective_offer_ids():
    backend = get_backend()
    with requests_mock.Mocker() as mock:
        posted = mock.post("https://dummy-app-id.algolia.net/1/indexes/testing-collective-offers/batch", json={})
        backend.unindex_collective_offer_ids([1])
        posted_json = posted.last_request.json()
        assert posted_json["requests"][0]["action"] == "deleteObject"
        assert posted_json["requests"][0]["body"]["objectID"] == 1


def test_unindex_all_collective_offers():
    backend = get_backend()
    with requests_mock.Mocker() as mock:
        posted = mock.post("https://dummy-app-id.algolia.net/1/indexes/testing-collective-offers/clear", json={})
        backend.unindex_all_collective_offers()
        assert posted.called


def test_index_collective_offers_templates():
    backend = get_backend()
    collective_offer_template = educational_factories.CollectiveOfferTemplateFactory.build()
    with requests_mock.Mocker() as mock:
        posted = mock.post("https://dummy-app-id.algolia.net/1/indexes/testing-collective-offers/batch", json={})
        backend.index_collective_offer_templates([collective_offer_template])
        posted_json = posted.last_request.json()
        assert posted_json["requests"][0]["action"] == "updateObject"
        assert posted_json["requests"][0]["body"]["objectID"] == f"T-{collective_offer_template.id}"


def test_unindex_collective_offer__templatesids():
    backend = get_backend()
    with requests_mock.Mocker() as mock:
        posted = mock.post("https://dummy-app-id.algolia.net/1/indexes/testing-collective-offers/batch", json={})
        backend.unindex_collective_offer_template_ids([1])
        posted_json = posted.last_request.json()
        assert posted_json["requests"][0]["action"] == "deleteObject"
        assert posted_json["requests"][0]["body"]["objectID"] == "T-1"


def test_unindex_all_collective_offers_templates():
    backend = get_backend()
    with requests_mock.Mocker() as mock:
        posted = mock.post("https://dummy-app-id.algolia.net/1/indexes/testing-collective-offers/clear", json={})
        backend.unindex_all_collective_offers_templates()
        assert posted.called


def test_remove_stopwords():
    description = "Il était une fois, dans la ville de Foix. Voilà Foix !"
    expected = "fois ville foix voilà foix"
    assert algolia.remove_stopwords(description) == expected
