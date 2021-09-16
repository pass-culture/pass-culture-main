import datetime
import decimal
import json

import pytest
from sqlalchemy.orm import joinedload

from pcapi.core.categories import subcategories
import pcapi.core.offerers.models as offerers_models
import pcapi.core.offers.factories as offers_factories
import pcapi.core.offers.models as offers_models
from pcapi.core.search.backends import appsearch
from pcapi.core.testing import assert_num_queries
from pcapi.utils.human_ids import humanize


pytestmark = pytest.mark.usefixtures("db_session")


def test_serialize_offer():
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
        subcategoryId=subcategories.LIVRE_PAPIER.id,
        venue__id=127,
        venue__name="La Moyenne Librairie SA",
        venue__publicName="La Moyenne Librairie",
        venue__managingOfferer__name="Les Librairies Associées",
    )
    stock = offers_factories.StockFactory(offer=offer, price=10)
    serialized = appsearch.AppSearchBackend().serialize_offer(offer)
    assert serialized == {
        "subcategory_label": "Livre",
        "artist": "Author Performer Speaker Stage Director",
        "category": "LIVRE",
        "date_created": offer.dateCreated,
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
        "search_group_name": subcategories.SearchGroups.LIVRE.name,
        "stocks_date_created": [stock.dateCreated],
        "offerer_name": "Les Librairies Associées",
        "venue_id": 127,
        "venue_department_code": "75",
        "venue_name": "La Moyenne Librairie SA",
        "venue_position": "48.87004,2.37850",
        "venue_public_name": "La Moyenne Librairie",
    }


def test_serialize_offer_artist_strip():
    offer = offers_factories.OfferFactory(extraData={"author": "Author"})
    serialized = appsearch.AppSearchBackend().serialize_offer(offer)
    assert serialized["artist"] == "Author"


def test_serialize_offer_artist_empty():
    offer = offers_factories.OfferFactory(extraData={})
    serialized = appsearch.AppSearchBackend().serialize_offer(offer)
    assert "artist" not in serialized


def test_serialize_offer_dates_and_times():
    offer = offers_factories.OfferFactory(subcategoryId=subcategories.SEANCE_CINE.id)
    dt = datetime.datetime(2032, 1, 1, 12, 15)
    offers_factories.EventStockFactory(offer=offer, beginningDatetime=dt)
    serialized = appsearch.AppSearchBackend().serialize_offer(offer)
    assert serialized["date_created"] == offer.dateCreated
    assert serialized["dates"] == [dt]
    assert serialized["times"] == [12 * 60 * 60 + 15 * 60]


def test_serialize_offer_group():
    offer = offers_factories.OfferFactory(extraData={})
    serialized = appsearch.AppSearchBackend().serialize_offer(offer)
    assert serialized["group"] == str(offer.id)
    offer.extraData["visa"] = "56070"
    serialized = appsearch.AppSearchBackend().serialize_offer(offer)
    assert serialized["group"] == "56070"

    offer.extraData["isbn"] = "123456789"
    serialized = appsearch.AppSearchBackend().serialize_offer(offer)
    assert serialized["group"] == "123456789"


def test_serialize_offer_tags():
    tag = offers_factories.OfferCriterionFactory(criterion__name="formidable")
    serialized = appsearch.AppSearchBackend().serialize_offer(tag.offer)
    assert serialized["tags"] == ["formidable"]


def test_serialize_offer_thumb_url():
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


def full_offer_factory():
    stock = offers_factories.EventStockFactory(
        offer__product__thumbCount=1,
        offer__extraData={"author": "Jane Doe"},
    )
    offers_factories.OfferCriterionFactory(offer=stock.offer)
    return stock.offer


def full_venue_factory():
    return offers_factories.VenueFactory(
        audioDisabilityCompliant=True,
        mentalDisabilityCompliant=True,
        motorDisabilityCompliant=True,
        visualDisabilityCompliant=True,
        contact__social_medias={
            "facebook": "https://example.com/facebook",
            "instagram": "https://example.com/instagram",
            "snapchat": "https://example.com/snapchat",
            "twitter": "https://twitter.com/my.venue",
        },
    )


@pytest.mark.parametrize(
    "factory,serializer,schema",
    [
        (full_offer_factory, appsearch.AppSearchBackend.serialize_offer, appsearch.OFFERS_SCHEMA),
        (full_venue_factory, appsearch.AppSearchBackend.serialize_venue, appsearch.VENUES_SCHEMA),
    ],
)
def test_schemas(factory, serializer, schema):
    obj = factory()
    serialized = serializer(obj)

    # Check that we send the same fields than defined in the schema,
    # nothing more, nothing less.
    assert set(schema.keys()) ^ set(serialized.keys()) == {"id"}

    # Check that we use the right types for all fields. It's a bit
    # rough but it shoud be good enough.
    for key, type_ in schema.items():
        if type_ == "text":
            expected_types = (str,)
        elif type_ == "number":
            expected_types = (decimal.Decimal, int)
        elif type_ == "geolocation":
            expected_types = (str,)
        elif type_ == "date":
            expected_types = (datetime.datetime,)

        value = serialized[key]
        assert value not in (None, [], "")  # empty values should not be indexed

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


def test_serialize_venue():
    venue = offers_factories.VenueFactory(
        venueTypeCode="VISUAL_ARTS",
        contact__email="some@email.com",
        contact__website=None,
        contact__phone_number=None,
        contact__social_medias={
            "facebook": None,
            "instagram": None,
            "snapchat": None,
            "twitter": "https://twitter.com/my.venue",
        },
    )

    serialized = appsearch.AppSearchBackend().serialize_venue(venue)
    assert serialized == {
        "id": venue.id,
        "name": venue.name,
        "offerer_name": venue.managingOfferer.name,
        "venue_type": venue.venueTypeCode.name,
        "position": f"{venue.latitude},{venue.longitude}",
        "description": venue.description,
        "email": "some@email.com",
        "twitter": "https://twitter.com/my.venue",
    }


def test_serialize_disability_related_fields():
    venue = offers_factories.VenueFactory(
        audioDisabilityCompliant=True,
        mentalDisabilityCompliant=False,
        motorDisabilityCompliant=None,
        visualDisabilityCompliant=True,
    )
    serialized = appsearch.AppSearchBackend().serialize_venue(venue)
    assert serialized["audio_disability"] == 1
    assert serialized["mental_disability"] == 0
    assert serialized["visual_disability"] == 1
    assert "motor_disability" not in serialized
