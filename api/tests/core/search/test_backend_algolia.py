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


@pytest.mark.parametrize(
    "enqueue_function_name, queue",
    [
        ("enqueue_offer_ids", algolia.REDIS_OFFER_IDS_NAME),
        ("enqueue_offer_ids_in_error", algolia.REDIS_OFFER_IDS_IN_ERROR_NAME),
        ("enqueue_collective_offer_ids", algolia.REDIS_COLLECTIVE_OFFER_IDS_TO_INDEX),
        (
            "enqueue_collective_offer_ids_in_error",
            algolia.REDIS_COLLECTIVE_OFFER_IDS_IN_ERROR_TO_INDEX,
        ),
        (
            "enqueue_collective_offer_template_ids",
            algolia.REDIS_COLLECTIVE_OFFER_TEMPLATE_IDS_TO_INDEX,
        ),
        (
            "enqueue_collective_offer_template_ids_in_error",
            algolia.REDIS_COLLECTIVE_OFFER_TEMPLATE_IDS_IN_ERROR_TO_INDEX,
        ),
        ("enqueue_venue_ids_for_offers", algolia.REDIS_VENUE_IDS_FOR_OFFERS_NAME),
        ("enqueue_venue_ids", algolia.REDIS_VENUE_IDS_TO_INDEX),
        ("enqueue_venue_ids_in_error", algolia.REDIS_VENUE_IDS_IN_ERROR_TO_INDEX),
    ],
)
def test_enqueue_functions(enqueue_function_name, queue):
    backend = get_backend()
    enqueue = getattr(backend, enqueue_function_name)
    enqueue([1])
    enqueue({2, 3})
    enqueue([])
    assert set(backend.redis_client.smembers(queue)) == {"1", "2", "3"}


@pytest.mark.parametrize(
    "pop_function_name, from_error_queue, queue",
    [
        ("pop_offer_ids_from_queue", False, algolia.REDIS_OFFER_IDS_NAME),
        ("pop_offer_ids_from_queue", True, algolia.REDIS_OFFER_IDS_IN_ERROR_NAME),
        ("pop_collective_offer_ids_from_queue", False, algolia.REDIS_COLLECTIVE_OFFER_IDS_TO_INDEX),
        (
            "pop_collective_offer_ids_from_queue",
            True,
            algolia.REDIS_COLLECTIVE_OFFER_IDS_IN_ERROR_TO_INDEX,
        ),
        (
            "pop_collective_offer_template_ids_from_queue",
            False,
            algolia.REDIS_COLLECTIVE_OFFER_TEMPLATE_IDS_TO_INDEX,
        ),
        (
            "pop_collective_offer_template_ids_from_queue",
            True,
            algolia.REDIS_COLLECTIVE_OFFER_TEMPLATE_IDS_IN_ERROR_TO_INDEX,
        ),
        (
            "pop_venue_ids_from_queue",
            False,
            algolia.REDIS_VENUE_IDS_TO_INDEX,
        ),
        (
            "pop_venue_ids_from_queue",
            True,
            algolia.REDIS_VENUE_IDS_IN_ERROR_TO_INDEX,
        ),
        (
            "pop_venue_ids_for_offers_from_queue",
            None,
            algolia.REDIS_VENUE_IDS_FOR_OFFERS_NAME,
        ),
    ],
)
def test_pop_functions(pop_function_name, from_error_queue, queue):
    # Handle `pop_venue_ids_for_offers_from_queue` that does not
    # have any error queue.
    if from_error_queue is None:
        kwargs = {}
    else:
        kwargs = {"from_error_queue": from_error_queue}

    backend = get_backend()
    backend.redis_client.sadd(queue, 1, 2, 3)
    pop = getattr(backend, pop_function_name)

    popped = set()
    ids = pop(count=2, **kwargs)
    popped |= ids
    assert len(ids) == 2
    assert ids.issubset({1, 2, 3})

    ids = pop(count=2, **kwargs)
    popped |= ids
    assert len(ids) == 1
    assert ids.issubset({1, 2, 3})
    assert popped == {1, 2, 3}

    ids = pop(count=2, **kwargs)
    assert ids == set()

    assert backend.redis_client.scard(queue) == 0


def test_count_offers_to_index_from_queue(app):
    backend = get_backend()
    assert backend.count_offers_to_index_from_queue() == 0

    app.redis_client.sadd("search:algolia:offer_ids", 1, 2, 3)
    assert backend.count_offers_to_index_from_queue() == 3


def test_count_offers_to_index_from_error_queue(app):
    backend = get_backend()
    assert backend.count_offers_to_index_from_queue(from_error_queue=True) == 0

    app.redis_client.sadd("search:algolia:offer_ids_in_error", 1, 2, 3)
    assert backend.count_offers_to_index_from_queue(from_error_queue=True) == 3


def test_check_offer_is_indexed(app):
    backend = get_backend()
    app.redis_client.hset("indexed_offers", "1", "")
    assert backend.check_offer_is_indexed(FakeOffer(id=1))
    assert not backend.check_offer_is_indexed(FakeOffer(id=2))


@pytest.mark.usefixtures("db_session")
def test_index_offers(app):
    backend = get_backend()
    offer = offers_factories.StockFactory().offer
    with requests_mock.Mocker() as mock:
        posted = mock.post("https://dummy-app-id.algolia.net/1/indexes/offers/batch", json={})
        backend.index_offers([offer], {offer.id: 0})
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
    venue = offerers_factories.VenueFactory()
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
    collective_stock_corsica_north = educational_factories.CollectiveStockFactory(
        collectiveOffer__venue__departementCode="20",
        collectiveOffer__venue__postalCode="20213",
    )
    collective_stock_corsica_south = educational_factories.CollectiveStockFactory(
        collectiveOffer__venue__departementCode="20",
        collectiveOffer__venue__postalCode="20113",
    )
    with requests_mock.Mocker() as mock:
        posted = mock.post("https://dummy-app-id.algolia.net/1/indexes/testing-collective-offers/batch", json={})
        backend.index_collective_offers(
            [
                collective_offer,
                collective_stock_corsica_north.collectiveOffer,
                collective_stock_corsica_south.collectiveOffer,
            ]
        )
        posted_json = posted.last_request.json()
        assert posted_json["requests"][0]["action"] == "updateObject"
        assert posted_json["requests"][0]["body"]["objectID"] == collective_offer.id
        assert posted_json["requests"][0]["body"]["venue"]["departmentCode"] == collective_offer.venue.departementCode
        assert posted_json["requests"][1]["body"]["venue"]["departmentCode"] == "2B"
        assert posted_json["requests"][2]["body"]["venue"]["departmentCode"] == "2A"


def test_unindex_collective_offer_ids():
    backend = get_backend()
    with requests_mock.Mocker() as mock:
        posted = mock.post("https://dummy-app-id.algolia.net/1/indexes/testing-collective-offers/batch", json={})
        backend.unindex_collective_offer_ids([1])
        posted_json = posted.last_request.json()
        assert posted_json["requests"][0]["action"] == "deleteObject"
        assert posted_json["requests"][0]["body"]["objectID"] == 1


def test_unindex_all_collective_offers_for_all_objects():
    backend = get_backend()
    with requests_mock.Mocker() as mock:
        posted = mock.post("https://dummy-app-id.algolia.net/1/indexes/testing-collective-offers/clear", json={})
        backend.unindex_all_collective_offers()
        assert posted.called


def test_unindex_all_collective_offers_only_for_template():
    backend = get_backend()
    with requests_mock.Mocker() as mock:
        posted = mock.post(
            "https://dummy-app-id.algolia.net/1/indexes/testing-collective-offers/deleteByQuery",
            json={"facetFilter": ["isTemplate:true"]},
        )
        backend.unindex_all_collective_offers(only_template=True)
        assert posted.called


def test_unindex_all_collective_offers():
    backend = get_backend()
    with requests_mock.Mocker() as mock:
        posted = mock.post(
            "https://dummy-app-id.algolia.net/1/indexes/testing-collective-offers/deleteByQuery",
            json={"facetFilter": ["isTemplate:false"]},
        )
        backend.unindex_all_collective_offers(only_non_template=True)
        assert posted.called


def test_index_collective_offers_templates():
    backend = get_backend()
    collective_offer_template = educational_factories.CollectiveOfferTemplateFactory.build()
    collective_offer_template_north_corsica = educational_factories.CollectiveOfferTemplateFactory(
        venue__departementCode=20,
        venue__postalCode="20213",
    )
    collective_offer_template_south_corsica = educational_factories.CollectiveOfferTemplateFactory(
        venue__departementCode=20,
        venue__postalCode="20113",
    )

    with requests_mock.Mocker() as mock:
        posted = mock.post("https://dummy-app-id.algolia.net/1/indexes/testing-collective-offers/batch", json={})
        backend.index_collective_offer_templates(
            [
                collective_offer_template,
                collective_offer_template_north_corsica,
                collective_offer_template_south_corsica,
            ]
        )
        posted_json = posted.last_request.json()
        assert posted_json["requests"][0]["action"] == "updateObject"
        assert posted_json["requests"][0]["body"]["objectID"] == f"T-{collective_offer_template.id}"
        assert (
            posted_json["requests"][0]["body"]["venue"]["departmentCode"]
            == collective_offer_template.venue.departementCode
        )
        assert posted_json["requests"][1]["body"]["venue"]["departmentCode"] == "2B"
        assert posted_json["requests"][2]["body"]["venue"]["departmentCode"] == "2A"


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
