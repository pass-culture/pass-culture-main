import datetime
import decimal
import json

import pytest
from sqlalchemy.orm import joinedload

import pcapi.core.offerers.models as offerers_models
import pcapi.core.offers.factories as offers_factories
import pcapi.core.offers.models as offers_models
from pcapi.core.search.backends import appsearch
from pcapi.core.testing import assert_num_queries
from pcapi.utils.human_ids import humanize


pytestmark = pytest.mark.usefixtures("db_session")


def test_serialize():
    offer = offers_factories.OfferFactory(
        name="Titre formidable",
        description="Un livre qu'il est bien pour le lire",
        extraData={
            "author": "Author",
            "isbn": "2221001648",
            "performer": "Performer",
            "speaker": "Speaker",
            "stageDirector": "Stage Director",
        },
        rankingWeight=2,
        type="ThingType.LIVRE_EDITION",
        venue__id=127,
        venue__name="La Moyenne Librairie SA",
        venue__publicName="La Moyenne Librairie",
        venue__managingOfferer__name="Les Librairies Associées",
    )
    stock = offers_factories.StockFactory(offer=offer, price=10)
    serialized = appsearch.AppSearchBackend().serialize_offer(offer)
    assert serialized == {
        "artist": "Author Performer Speaker Stage Director",
        "category": "LIVRE",
        "date_created": offer.dateCreated,
        "dates": [],
        "description": "Un livre qu'il est bien pour le lire",
        "group": "2221001648",
        "is_digital": 0,
        "is_duo": 0,
        "is_educational": 0,
        "is_event": 0,
        "is_thing": 1,
        "label": "Livre ou carte lecture",
        "name": "Titre formidable",
        "id": offer.id,
        "prices": [1000],
        "ranking_weight": 2,
        "stocks_date_created": [stock.dateCreated],
        "tags": [],
        "times": [],
        "thumb_url": None,
        "offerer_name": "Les Librairies Associées",
        "venue_id": 127,
        "venue_department_code": "75",
        "venue_name": "La Moyenne Librairie SA",
        "venue_position": "48.87004,2.37850",
        "venue_public_name": "La Moyenne Librairie",
    }


def test_serialize_artist_strip():
    offer = offers_factories.OfferFactory(extraData={"author": "Author"})
    serialized = appsearch.AppSearchBackend().serialize_offer(offer)
    assert serialized["artist"] == "Author"


def test_serialize_artist_empty():
    offer = offers_factories.OfferFactory(extraData={})
    serialized = appsearch.AppSearchBackend().serialize_offer(offer)
    assert serialized["artist"] is None


def test_serialize_dates_and_times():
    offer = offers_factories.OfferFactory(type="EventType.CINEMA")
    dt = datetime.datetime(2032, 1, 1, 12, 15)
    offers_factories.EventStockFactory(offer=offer, beginningDatetime=dt)
    serialized = appsearch.AppSearchBackend().serialize_offer(offer)
    assert serialized["date_created"] == offer.dateCreated
    assert serialized["dates"] == [dt]
    assert serialized["times"] == [12 * 60 * 60 + 15 * 60]


def test_serialize_group():
    offer = offers_factories.OfferFactory(extraData={})
    serialized = appsearch.AppSearchBackend().serialize_offer(offer)
    assert serialized["group"] == str(offer.id)
    offer.extraData["visa"] = "56070"
    serialized = appsearch.AppSearchBackend().serialize_offer(offer)
    assert serialized["group"] == "56070"

    offer.extraData["isbn"] = "123456789"
    serialized = appsearch.AppSearchBackend().serialize_offer(offer)
    assert serialized["group"] == "123456789"


def test_serialize_tags():
    tag = offers_factories.OfferCriterionFactory(criterion__name="formidable")
    serialized = appsearch.AppSearchBackend().serialize_offer(tag.offer)
    assert serialized["tags"] == ["formidable"]


def test_serialize_thumb_url():
    offer = offers_factories.OfferFactory(product__thumbCount=1)
    serialized = appsearch.AppSearchBackend().serialize_offer(offer)
    assert serialized["thumb_url"] == f"/storage/thumbs/products/{humanize(offer.productId)}"


def test_app_search_json_encoder_dates():
    dt = datetime.datetime(2032, 1, 1, 12, 15)
    data = json.dumps({"date_created": dt}, cls=appsearch.AppSearchJsonEncoder)
    assert data == '{"date_created": "2032-01-01T12:15:00Z"}'

    data = json.dumps({"dates": [dt]}, cls=appsearch.AppSearchJsonEncoder)
    assert data == '{"dates": ["2032-01-01T12:15:00Z"]}'


def test_check_number_of_sql_queries():
    offer = offers_factories.OfferFactory()
    # FIXME (dbaty, 2021-07-05): we should put these `joinedload` in a
    # function, and call that function from `_reindex_offer_ids()`
    # where we fetch offers.
    offer = (
        offers_models.Offer.query.options(
            joinedload(offers_models.Offer.venue).joinedload(offerers_models.Venue.managingOfferer)
        )
        .options(joinedload(offers_models.Offer.criteria))
        .options(joinedload(offers_models.Offer.mediations))
        .options(joinedload(offers_models.Offer.product))
        .options(joinedload(offers_models.Offer.stocks))
        .one()
    )

    # Make sure that the JOINs above are enough to avoid any extra SQL
    # query below where serializing an offer.
    with assert_num_queries(0):
        appsearch.AppSearchBackend().serialize_offer(offer)


def test_schema():
    offer = offers_factories.OfferFactory()
    serialized = appsearch.AppSearchBackend().serialize_offer(offer)

    # Check that we send the same fields than defined in the schema,
    # nothing more, nothing less.
    assert set(appsearch.SCHEMA.keys()) ^ set(serialized.keys()) == {"id"}

    # Check that we use the right types for all fields. It's a bit
    # rough but it shoud be good enough.
    for key, type_ in appsearch.SCHEMA.items():
        if type_ == "text":
            expected_types = (str,)
        elif type_ == "number":
            expected_types = (decimal.Decimal, int)
        elif type_ == "geolocation":
            expected_types = (str,)
        elif type_ == "date":
            expected_types = (datetime.datetime,)
        value = serialized[key]
        if value in (None, []):  # valid for all field types
            continue
        if isinstance(value, list):
            value = value[0]  # check the first item only
        assert isinstance(value, expected_types), f"Type of {key} should be {expected_types}, got {value}"


def test_do_no_return_booleans():
    # If the backend's `serialize()` method returned boolean values,
    # they would be left as booleans when JSON-encoded, and the App
    # Search API would reject them (because it does not support this
    # data type).
    offer = offers_factories.OfferFactory()
    serialized = appsearch.AppSearchBackend().serialize_offer(offer)
    for key, value in serialized.items():
        assert not isinstance(value, bool), f"Key {key}should not be a boolean"


@pytest.mark.parametrize(
    "url,expected",
    [
        ("https://example.com/foo/bar", "/foo/bar"),
        ("https://example.com/foo/bar?baz=1", "/foo/bar?baz=1"),
        ("https://example.com/foo/bar?baz=1#quuz", "/foo/bar?baz=1#quuz"),
    ],
)
def test_url_path(url, expected):
    assert appsearch.url_path(url) == expected
