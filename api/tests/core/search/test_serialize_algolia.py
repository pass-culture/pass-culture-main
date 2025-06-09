import datetime
import decimal
import logging

import pytest
import time_machine
from dateutil.relativedelta import relativedelta

from pcapi.core.artist import factories as artists_factories
from pcapi.core.artist import models as artists_models
from pcapi.core.categories import subcategories
from pcapi.core.criteria import factories as criteria_factories
from pcapi.core.educational import factories as educational_factories
from pcapi.core.educational import models as educational_models
from pcapi.core.geography import factories as geography_factories
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offerers.schemas import VenueTypeCode
from pcapi.core.offers import factories as offers_factories
from pcapi.core.offers import models as offers_models
from pcapi.core.providers.constants import BookFormat
from pcapi.core.reactions import factories as reactions_factories
from pcapi.core.reactions.models import ReactionTypeEnum
from pcapi.core.search import get_base_query_for_offer_indexation
from pcapi.core.search.backends import algolia
from pcapi.core.search.backends import serialization
from pcapi.models import db
from pcapi.utils.human_ids import humanize


pytestmark = pytest.mark.usefixtures("db_session")


@pytest.mark.settings(ALGOLIA_LAST_30_DAYS_BOOKINGS_RANGE_THRESHOLDS=[1, 2, 3, 4])
@time_machine.travel("2024-01-01T00:00:00", tick=False)
def test_serialize_offer():
    rayon = "Policier / Thriller format poche"  # fetched from provider

    # known values (inserted using a migration)
    # note: some might contain trailing whitespaces. Also sections are
    # usually lowercase whilst sections from providers might be
    # capitalized.
    book_macro_section = (
        db.session.query(offers_models.BookMacroSection).filter_by(section="policier / thriller format poche").one()
    )
    macro_section = book_macro_section.macroSection.strip()

    venue_offerer_address = offerers_factories.OffererAddressFactory(
        address__departmentCode="75",
        address__postalCode="75001",
        address__latitude=geography_factories.DEFAULT_LATITUDE,
        address__longitude=geography_factories.DEFAULT_TRUNCATED_LONGITUDE,
    )

    offer_offerer_address = offerers_factories.OffererAddressFactory(
        address__departmentCode="86",
        address__postalCode="86140",
        address__city="Cernay",
        address__latitude=-5.01,
        address__longitude=-6.02,
    )

    offer = offers_factories.OfferFactory(
        dateCreated=datetime.datetime(2022, 1, 1, 10, 0, 0),
        name="Titre formidable",
        description="Un LIVRE qu'il est bien pour le lire",
        ean="2221001648999",
        extraData={
            "author": "Author",
            "performer": "Performer",
            "speaker": "Speaker",
            "stageDirector": "Stage Director",
            "rayon": rayon,
        },
        rankingWeight=2,
        subcategoryId=subcategories.LIVRE_PAPIER.id,
        offererAddress=offer_offerer_address,
        venue__id=127,
        venue__offererAddress=venue_offerer_address,
        venue__name="La Moyenne Librairie SA",
        venue__publicName="La Moyenne Librairie",
        venue__venueTypeCode=VenueTypeCode.LIBRARY,
        venue__managingOfferer__name="Les Librairies Associées",
    )
    offers_factories.StockFactory(offer=offer, price=10)
    serialized = algolia.AlgoliaBackend().serialize_offer(offer, 0)
    assert serialized == {
        "distinct": "2221001648999",
        "objectID": offer.id,
        "offer": {
            "artist": "Author Performer Speaker Stage Director",
            "bookMacroSection": macro_section,
            "dateCreated": offer.dateCreated.timestamp(),
            "dates": [],
            "description": "livre bien lire",
            "ean": "2221001648999",
            "indexedAt": "2024-01-01T00:00:00",
            "isDigital": False,
            "isDuo": False,
            "isEducational": False,
            "isEvent": False,
            "isForbiddenToUnderage": offer.is_forbidden_to_underage,
            "isPermanent": offer.isPermanent,
            "isThing": True,
            "last30DaysBookings": 0,
            "last30DaysBookingsRange": serialization.Last30DaysBookingsRange.VERY_LOW.value,
            "musicType": [],
            "name": "Titre formidable",
            "nativeCategoryId": ["LIVRES_PAPIER"],
            "prices": [decimal.Decimal("10.00")],
            "rankingWeight": 2,
            "searchGroups": ["LIVRES"],
            "searchGroupNamev2": ["LIVRES"],
            "students": [],
            "subcategoryId": offer.subcategory.id,
            "tags": [],
            "times": [],
        },
        "offerer": {
            "name": "Les Librairies Associées",
        },
        "venue": {
            "banner_url": offer.venue.bannerUrl,
            "address": offer.offererAddress.address.street,
            "city": offer.offererAddress.address.city,
            "departmentCode": "86",
            "postalCode": offer.offererAddress.address.postalCode,
            "id": offer.venueId,
            "isAudioDisabilityCompliant": False,
            "isMentalDisabilityCompliant": False,
            "isMotorDisabilityCompliant": False,
            "isVisualDisabilityCompliant": False,
            "name": "La Moyenne Librairie",
            "publicName": "La Moyenne Librairie",
            "venue_type": VenueTypeCode.LIBRARY.name,
            "isPermanent": True,
        },
        "_geoloc": {
            "lat": -5.01,
            "lng": -6.02,
        },
    }


@pytest.mark.settings(ALGOLIA_LAST_30_DAYS_BOOKINGS_RANGE_THRESHOLDS=[1, 2, 3, 4])
@time_machine.travel("2024-01-01T00:00:00", tick=False)
def test_serialize_offer_legacy():
    rayon = "Policier / Thriller format poche"  # fetched from provider

    # known values (inserted using a migration)
    # note: some might contain trailing whitespaces. Also sections are
    # usually lowercase whilst sections from providers might be
    # capitalized.
    book_macro_section = (
        db.session.query(offers_models.BookMacroSection).filter_by(section="policier / thriller format poche").one()
    )
    macro_section = book_macro_section.macroSection.strip()

    offer = offers_factories.OfferFactory(
        dateCreated=datetime.datetime(2022, 1, 1, 10, 0, 0),
        name="Titre formidable",
        description="Un LIVRE qu'il est bien pour le lire",
        ean="2221001648999",
        extraData={
            "author": "Author",
            "performer": "Performer",
            "speaker": "Speaker",
            "stageDirector": "Stage Director",
            "rayon": rayon,
        },
        rankingWeight=2,
        subcategoryId=subcategories.LIVRE_PAPIER.id,
        venue__id=127,
        venue__postalCode="86140",
        venue__name="La Moyenne Librairie SA",
        venue__publicName="La Moyenne Librairie",
        venue__venueTypeCode=VenueTypeCode.LIBRARY,
        venue__managingOfferer__name="Les Librairies Associées",
    )
    offers_factories.StockFactory(offer=offer, price=10)
    serialized = algolia.AlgoliaBackend().serialize_offer(offer, 0)
    assert serialized == {
        "distinct": "2221001648999",
        "objectID": offer.id,
        "offer": {
            "artist": "Author Performer Speaker Stage Director",
            "bookMacroSection": macro_section,
            "dateCreated": offer.dateCreated.timestamp(),
            "dates": [],
            "description": "livre bien lire",
            "ean": "2221001648999",
            "indexedAt": "2024-01-01T00:00:00",
            "isDigital": False,
            "isDuo": False,
            "isEducational": False,
            "isEvent": False,
            "isForbiddenToUnderage": offer.is_forbidden_to_underage,
            "isPermanent": offer.isPermanent,
            "isThing": True,
            "last30DaysBookings": 0,
            "last30DaysBookingsRange": serialization.Last30DaysBookingsRange.VERY_LOW.value,
            "musicType": [],
            "name": "Titre formidable",
            "nativeCategoryId": ["LIVRES_PAPIER"],
            "prices": [decimal.Decimal("10.00")],
            "rankingWeight": 2,
            "searchGroups": ["LIVRES"],
            "searchGroupNamev2": ["LIVRES"],
            "students": [],
            "subcategoryId": offer.subcategory.id,
            "tags": [],
            "times": [],
        },
        "offerer": {
            "name": "Les Librairies Associées",
        },
        "venue": {
            "address": offer.venue.street,
            "banner_url": offer.venue.bannerUrl,
            "city": offer.venue.city,
            "departmentCode": "86",
            "id": offer.venueId,
            "isAudioDisabilityCompliant": False,
            "isMentalDisabilityCompliant": False,
            "isMotorDisabilityCompliant": False,
            "isVisualDisabilityCompliant": False,
            "name": "La Moyenne Librairie",
            "postalCode": offer.venue.postalCode,
            "publicName": "La Moyenne Librairie",
            "venue_type": VenueTypeCode.LIBRARY.name,
            "isPermanent": True,
        },
        "_geoloc": {"lat": 48.87004, "lng": 2.3785},
    }


@pytest.mark.parametrize(
    "extra_data, expected_music_style, expected_show_type, expected_movie_genres, expected_macro_section",
    (
        ({"musicType": "501"}, ["Jazz"], None, None, None),
        ({"musicType": "600"}, ["Classique"], None, None, None),
        ({"musicType": "-1"}, ["Autre"], None, None, None),
        ({"musicType": " "}, [], None, None, None),
        ({"gtl_id": "04000000", "musicType": "880"}, ["ELECTRO", "Electro"], None, None, None),
        ({"showType": "100"}, [], "Arts de la rue", None, None),
        ({"showType": "1200"}, [], "Spectacle Jeunesse", None, None),
        ({"showType": "-1"}, [], "Autre", None, None),
        ({"showType": " "}, [], None, None, None),
        ({"genres": ["DRAMA"]}, [], None, ["DRAMA"], None),
        ({"genres": ["ADVENTURE", "DRAMA", "FAMILY"]}, [], None, ["ADVENTURE", "DRAMA", "FAMILY"], None),
        ({"genres": []}, [], None, [], None),
        ({"genres": None}, [], None, None, None),
        ({"rayon": "documentaire jeunesse histoire"}, [], None, None, "Jeunesse"),
        ({"rayon": "petits prix"}, [], None, None, "Littérature française"),
        ({"rayon": "ce rayon n'existe pas"}, [], None, None, None),
        ({"rayon": None}, [], None, None, None),
    ),
)
def test_serialize_offer_extra_data(
    extra_data, expected_music_style, expected_show_type, expected_movie_genres, expected_macro_section
):
    # given
    offer = offers_factories.OfferFactory(extraData=extra_data)

    # when
    serialized = algolia.AlgoliaBackend().serialize_offer(offer, 0)

    # then
    assert serialized["offer"].get("musicType") == expected_music_style
    assert serialized["offer"].get("showType") == expected_show_type
    assert serialized["offer"].get("movieGenres") == expected_movie_genres
    assert serialized["offer"].get("bookMacroSection") == expected_macro_section


@pytest.mark.settings(ALGOLIA_LAST_30_DAYS_BOOKINGS_RANGE_THRESHOLDS=[1, 2, 3, 4])
@pytest.mark.parametrize(
    "bookings_count, expected_range",
    (
        (0, serialization.Last30DaysBookingsRange.VERY_LOW.value),
        (1, serialization.Last30DaysBookingsRange.LOW.value),
        (2, serialization.Last30DaysBookingsRange.MEDIUM.value),
        (3, serialization.Last30DaysBookingsRange.HIGH.value),
        (4, serialization.Last30DaysBookingsRange.VERY_HIGH.value),
        (5, serialization.Last30DaysBookingsRange.VERY_HIGH.value),
    ),
)
def test_index_last_30_days_bookings(app, bookings_count, expected_range):
    # given
    offer = offers_factories.StockFactory().offer

    # when
    serialized = algolia.AlgoliaBackend().serialize_offer(offer, bookings_count)

    # then
    assert serialized["offer"]["last30DaysBookings"] == bookings_count
    assert serialized["offer"]["last30DaysBookingsRange"] == expected_range


def test_serialize_offer_event():
    offer = offers_factories.OfferFactory(subcategoryId=subcategories.SEANCE_CINE.id)
    dt1 = datetime.datetime(2032, 1, 4, 12, 15)
    offers_factories.EventStockFactory(offer=offer, beginningDatetime=dt1)
    dt2 = datetime.datetime(2032, 1, 1, 16, 30)
    offers_factories.EventStockFactory(offer=offer, beginningDatetime=dt2)
    serialized = algolia.AlgoliaBackend().serialize_offer(offer, 0)
    # Dates are ordered, but times are not. I don't know why we order dates.
    assert serialized["offer"]["dates"] == [dt2.timestamp(), dt1.timestamp()]
    assert set(serialized["offer"]["times"]) == {12 * 60 * 60 + 15 * 60, 16 * 60 * 60 + 30 * 60}


@pytest.mark.parametrize(
    "extra_data,ean,expected_distinct",
    (
        [{}, None, "1"],
        [{"allocineId": 12345, "visa": "56070"}, None, "12345"],
        [{"visa": "56070"}, None, "56070"],
        [{}, "1234567890999", "1234567890999"],
    ),
)
def test_serialize_offer_distinct(extra_data, ean, expected_distinct):
    product = offers_factories.ProductFactory(extraData=extra_data, ean=ean)
    offer = offers_factories.OfferFactory(id=1, product=product)
    serialized = algolia.AlgoliaBackend().serialize_offer(offer, 0)
    assert serialized["distinct"] == expected_distinct


def test_serialize_offer_tags():
    criterion = criteria_factories.CriterionFactory(name="formidable")
    offer = offers_factories.OfferFactory(criteria=[criterion])
    serialized = algolia.AlgoliaBackend().serialize_offer(offer, 0)
    assert serialized["offer"]["tags"] == ["formidable"]


def test_serialize_default_position():
    offer = offers_factories.DigitalOfferFactory()
    serialized = algolia.AlgoliaBackend().serialize_offer(offer, 0)
    assert serialized["_geoloc"] == {
        "lat": serialization.DEFAULT_LATITUDE,
        "lng": serialization.DEFAULT_LONGITUDE,
    }


def test_serialize_offer_thumb_url():
    product = offers_factories.ProductFactory(thumbCount=1)
    offer = offers_factories.OfferFactory(product=product)
    serialized = algolia.AlgoliaBackend().serialize_offer(offer, 0)
    assert serialized["offer"]["thumbUrl"] == f"/storage/thumbs/products/{humanize(offer.productId)}"


def test_serialize_offer_gtl():
    product = offers_factories.ProductFactory(extraData={"gtl_id": "01030100"})
    offer = offers_factories.OfferFactory(
        product=product,
        subcategoryId=subcategories.LIVRE_PAPIER.id,
    )
    serialized = algolia.AlgoliaBackend().serialize_offer(offer, 0)
    assert serialized["offer"]["gtl_level1"] == "Littérature"
    assert serialized["offer"]["gtl_level2"] == "Œuvres classiques"
    assert serialized["offer"]["gtl_level3"] == "Antiquité"
    assert "gtl_level4" not in serialized["offer"]
    assert serialized["offer"]["gtlCodeLevel1"] == "01000000"
    assert serialized["offer"]["gtlCodeLevel2"] == "01030000"
    assert serialized["offer"]["gtlCodeLevel3"] == "01030100"
    assert serialized["offer"]["gtlCodeLevel4"] == "01030100"


def test_use_titelive_music_type_if_offer_is_music():
    product = offers_factories.ProductFactory(
        extraData={"gtl_id": "01000000"}, subcategoryId=subcategories.SUPPORT_PHYSIQUE_MUSIQUE_CD.id
    )
    offer = offers_factories.OfferFactory(product=product)
    serialized = algolia.AlgoliaBackend().serialize_offer(offer, 0)
    assert serialized["offer"]["gtl_level1"] == "Musique Classique"
    assert "gtl_level2" not in serialized["offer"]
    assert "gtl_level3" not in serialized["offer"]
    assert "gtl_level4" not in serialized["offer"]
    assert serialized["offer"]["gtlCodeLevel1"] == "01000000"
    assert serialized["offer"]["gtlCodeLevel2"] == "01000000"
    assert serialized["offer"]["gtlCodeLevel3"] == "01000000"
    assert serialized["offer"]["gtlCodeLevel4"] == "01000000"


def test_serialize_offer_visa():
    offer = offers_factories.OfferFactory(
        extraData={"visa": "2607019901"},
    )
    serialized = algolia.AlgoliaBackend().serialize_offer(offer, 0)
    assert serialized["offer"]["visa"] == "2607019901"


def test_serialize_offer_release_date():
    product = offers_factories.ProductFactory(extraData={"releaseDate": "2024-01-01"})
    offer = offers_factories.OfferFactory(product=product)
    serialized = algolia.AlgoliaBackend().serialize_offer(offer, 0)
    assert serialized["offer"]["releaseDate"] == 1704067200


def test_serialize_offer_book_format():
    product = offers_factories.ProductFactory(extraData={"bookFormat": BookFormat.BEAUX_LIVRES.name})
    offer = offers_factories.OfferFactory(product=product)
    serialized = algolia.AlgoliaBackend().serialize_offer(offer, 0)
    assert serialized["offer"]["bookFormat"] == "Beaux livres"


def test_serialize_offer_forever_headline():
    headline_offer = offers_factories.HeadlineOfferFactory()
    serialized = algolia.AlgoliaBackend().serialize_offer(headline_offer.offer, 0)
    assert serialized["offer"]["isHeadline"] is True
    assert "isHeadlineUntil" not in serialized["offer"]


@time_machine.travel("2025-01-01")
def test_serialize_offer_temporarily_headline():
    now = datetime.datetime.utcnow()
    headline_offer = offers_factories.HeadlineOfferFactory(timespan=(now, now + relativedelta(days=1)))
    serialized = algolia.AlgoliaBackend().serialize_offer(headline_offer.offer, 0)
    assert serialized["offer"]["isHeadline"] is True
    assert serialized["offer"]["isHeadlineUntil"] == 1735776000


def test_serialize_offer_artists():
    artist = artists_factories.ArtistFactory()
    product = offers_factories.ProductFactory()
    offer = offers_factories.OfferFactory(product=product)
    artists_factories.ArtistProductLinkFactory(
        artist_id=artist.id, product_id=product.id, artist_type=artists_models.ArtistType.AUTHOR
    )

    serialized = algolia.AlgoliaBackend().serialize_offer(offer, 0)
    assert serialized["artists"] == [{"id": artist.id, "name": artist.name, "image": artist.image}]


def test_serialize_offer_artists_without_image():
    artist = artists_factories.ArtistFactory(image=None)
    product = offers_factories.ProductFactory()
    offers_factories.ProductMediationFactory(product=product)
    offer = offers_factories.OfferFactory(product=product)
    artists_factories.ArtistProductLinkFactory(
        artist_id=artist.id, product_id=product.id, artist_type=artists_models.ArtistType.AUTHOR
    )

    serialized = algolia.AlgoliaBackend().serialize_offer(offer, 0)
    assert serialized["artists"][0]["image"] == offer.thumbUrl


def test_filter_artists():
    offer = offers_factories.OfferFactory(
        extraData={
            "author": "collectifs",
            "performer": "Collectif",
            "speaker": "Artiste1, Artiste2",
            "stageDirector": "Artiste1;Artiste2",
        }
    )
    serialized = algolia.AlgoliaBackend().serialize_offer(offer, 0)
    assert "artist" not in serialized["offer"]


def test_filter_on_empty_artist():
    offer = offers_factories.OfferFactory(
        extraData={
            "author": None,
            "performer": "",
            "speaker": "Artiste1",
            "stageDirector": "Artiste2",
        }
    )
    serialized = algolia.AlgoliaBackend().serialize_offer(offer, 0)
    assert serialized["offer"]["artist"] == "Artiste1 Artiste2"


def test_serialize_offer_likes_count():
    offer = offers_factories.OfferFactory()
    reactions_factories.ReactionFactory(reactionType=ReactionTypeEnum.LIKE, offer=offer)
    reactions_factories.ReactionFactory(reactionType=ReactionTypeEnum.DISLIKE, offer=offer)
    reactions_factories.ReactionFactory(reactionType=ReactionTypeEnum.NO_REACTION, offer=offer)

    offer = get_base_query_for_offer_indexation().filter(offers_models.Offer.id == offer.id).one()
    serialized = algolia.AlgoliaBackend().serialize_offer(offer, 0)
    assert serialized["offer"]["likes"] == 1


def test_serialize_venue():
    venue = offerers_factories.VenueFactory(
        venueTypeCode=offerers_models.VenueTypeCode.VISUAL_ARTS,
        audioDisabilityCompliant=True,
        contact__email="venue@example.com",
        contact__website="http://venue.example.com",
        contact__phone_number="+33.123456",
        contact__social_medias={
            "facebook": None,
            "instagram": None,
            "snapchat": None,
            "twitter": "https://twitter.com/my.venue",
        },
    )

    serialized = algolia.AlgoliaBackend().serialize_venue(venue)
    assert serialized == {
        "objectID": venue.id,
        "city": venue.offererAddress.address.city,
        "name": venue.name,
        "offerer_name": venue.managingOfferer.name,
        "venue_type": venue.venueTypeCode.name,
        "description": venue.description,
        "audio_disability": True,
        "mental_disability": False,
        "motor_disability": False,
        "visual_disability": False,
        "email": "venue@example.com",
        "phone_number": "+33.123456",
        "website": "http://venue.example.com",
        "facebook": None,
        "instagram": None,
        "snapchat": None,
        "twitter": "https://twitter.com/my.venue",
        "tags": [],
        "banner_url": venue.bannerUrl,
        "_geoloc": {
            "lng": float(venue.offererAddress.address.longitude),
            "lat": float(venue.offererAddress.address.latitude),
        },
        "has_at_least_one_bookable_offer": False,
        "date_created": venue.dateCreated.timestamp(),
        "postalCode": venue.offererAddress.address.postalCode,
        "adress": venue.offererAddress.address.street,
    }


def test_serialize_venue_with_one_bookable_offer():
    venue = offerers_factories.VenueFactory(isPermanent=True)

    serialized = algolia.AlgoliaBackend().serialize_venue(venue)
    assert not serialized["has_at_least_one_bookable_offer"]

    offers_factories.EventStockFactory(offer__venue=venue)
    serialized = algolia.AlgoliaBackend().serialize_venue(venue)
    assert serialized["has_at_least_one_bookable_offer"]


def test_serialize_future_offer():
    offer_1 = offers_factories.OfferFactory(isActive=False, subcategoryId=subcategories.FESTIVAL_MUSIQUE.id)
    offer_2 = offers_factories.OfferFactory(isActive=True)
    publication_date = datetime.datetime.utcnow() + datetime.timedelta(days=30)
    offers_factories.FutureOfferFactory(offer=offer_1, publicationDate=publication_date)
    offers_factories.FutureOfferFactory(offer=offer_2, publicationDate=publication_date)
    beginning_date = datetime.datetime(2032, 1, 4, 12, 15)
    offers_factories.EventStockFactory(offer=offer_1, price=10, beginningDatetime=beginning_date)
    offers_factories.StockFactory(offer=offer_2, price=8.50)

    serialized = algolia.AlgoliaBackend().serialize_offer(offer_1, 0)
    assert serialized["offer"]["publicationDate"] == publication_date.timestamp()
    assert serialized["offer"]["prices"] == [decimal.Decimal("10.00")]
    assert serialized["offer"]["dates"] == [beginning_date.timestamp()]
    assert serialized["offer"]["times"] == [12 * 60 * 60 + 15 * 60]
    assert serialized["_tags"] == ["is_future"]

    serialized = algolia.AlgoliaBackend().serialize_offer(offer_2, 0)
    assert "publicationDate" not in serialized["offer"]
    assert serialized["offer"]["prices"] == [decimal.Decimal("8.50")]
    assert serialized["offer"]["dates"] == []
    assert serialized["offer"]["times"] == []
    assert "_tags" not in serialized


def test_serialize_collective_offer_template_offerer_venue():
    domain1 = educational_factories.EducationalDomainFactory(name="Danse")
    domain2 = educational_factories.EducationalDomainFactory(name="Architecture")

    # offer.offerVenue
    offer_venue_offerer_address = offerers_factories.OffererAddressFactory(address__latitude=45, address__longitude=3)
    offer_venue = offerers_factories.VenueFactory(offererAddress=offer_venue_offerer_address)

    # offer.venue
    venue_offerer_address = offerers_factories.OffererAddressFactory(
        address__postalCode="86140", address__departmentCode="86", address__latitude=44, address__longitude=2
    )

    collective_offer_template = educational_factories.CollectiveOfferTemplateFactory(
        dateCreated=datetime.datetime(2022, 1, 1, 10, 0, 0),
        name="Titre formidable",
        description="description formidable",
        students=[educational_models.StudentLevels.CAP1, educational_models.StudentLevels.CAP2],
        venue__offererAddress=venue_offerer_address,
        venue__name="La Moyenne Librairie SA",
        venue__publicName="La Moyenne Librairie",
        venue__managingOfferer__name="Les Librairies Associées",
        venue__adageId="123456",
        educational_domains=[domain1, domain2],
        interventionArea=None,
        offerVenue={
            "addressType": educational_models.OfferAddressType.OFFERER_VENUE,
            "venueId": offer_venue.id,
            "otherAddress": "",
        },
        locationType=educational_models.CollectiveLocationType.ADDRESS,
    )

    serialized = algolia.AlgoliaBackend().serialize_collective_offer_template(collective_offer_template)
    assert serialized == {
        "objectID": f"T-{collective_offer_template.id}",
        "offer": {
            "dateCreated": 1641031200.0,
            "name": "Titre formidable",
            "students": ["CAP - 1re année", "CAP - 2e année"],
            "domains": [domain1.id, domain2.id],
            "interventionArea": [],
            "schoolInterventionArea": None,
            "eventAddressType": educational_models.OfferAddressType.OFFERER_VENUE.value,
            "locationType": educational_models.CollectiveLocationType.ADDRESS.value,
            "beginningDatetime": 1641031200.0,
            "description": collective_offer_template.description,
        },
        "offerer": {
            "name": "Les Librairies Associées",
        },
        "venue": {
            "academy": "Poitiers",
            "departmentCode": "86",
            "id": collective_offer_template.venue.id,
            "name": "La Moyenne Librairie SA",
            "publicName": "La Moyenne Librairie",
            "adageId": collective_offer_template.venue.adageId,
        },
        "_geoloc": {"lat": 45, "lng": 3},  # values are extracted from offer.offerVenue (and not offer.venue)
        "isTemplate": True,
        "formats": [format.value for format in collective_offer_template.formats],
    }


def test_serialize_collective_offer_template_school():
    venue_offerer_address = offerers_factories.OffererAddressFactory(address__latitude=45, address__longitude=3)

    collective_offer_template = educational_factories.CollectiveOfferTemplateFactory(
        venue__offererAddress=venue_offerer_address,
        offerVenue={
            "addressType": educational_models.OfferAddressType.SCHOOL,
            "venueId": None,
            "otherAddress": "",
        },
    )

    serialized = algolia.AlgoliaBackend().serialize_collective_offer_template(collective_offer_template)
    assert serialized["offer"]["eventAddressType"] == "school"
    assert serialized["_geoloc"] == {"lat": 45, "lng": 3}


def test_serialize_collective_offer_template_other():
    venue_offerer_address = offerers_factories.OffererAddressFactory(address__latitude=45, address__longitude=3)

    collective_offer_template = educational_factories.CollectiveOfferTemplateFactory(
        venue__offererAddress=venue_offerer_address,
        offerVenue={
            "addressType": educational_models.OfferAddressType.OTHER,
            "venueId": None,
            "otherAddress": "Here",
        },
    )

    serialized = algolia.AlgoliaBackend().serialize_collective_offer_template(collective_offer_template)
    assert serialized["offer"]["eventAddressType"] == "other"
    assert serialized["_geoloc"] == {"lat": 45, "lng": 3}


@pytest.mark.features(WIP_ENABLE_OFFER_ADDRESS_COLLECTIVE=True)
def test_serialize_collective_offer_template_school_with_ff():
    venue_offerer_address = offerers_factories.OffererAddressFactory(address__latitude=45, address__longitude=3)
    collective_offer_template = educational_factories.CollectiveOfferTemplateFactory(
        venue__offererAddress=venue_offerer_address,
        locationType=educational_models.CollectiveLocationType.SCHOOL,
        offererAddress=None,
    )

    serialized = algolia.AlgoliaBackend().serialize_collective_offer_template(collective_offer_template)
    assert serialized["offer"]["locationType"] == "SCHOOL"
    assert serialized["_geoloc"] == {"lat": 45, "lng": 3}


@pytest.mark.features(WIP_ENABLE_OFFER_ADDRESS_COLLECTIVE=True)
def test_serialize_collective_offer_template_address_with_ff():
    offerer_address = offerers_factories.OffererAddressFactory(address__latitude=45, address__longitude=3)
    collective_offer_template = educational_factories.CollectiveOfferTemplateFactory(
        locationType=educational_models.CollectiveLocationType.ADDRESS, offererAddress=offerer_address
    )

    serialized = algolia.AlgoliaBackend().serialize_collective_offer_template(collective_offer_template)
    assert serialized["offer"]["locationType"] == "ADDRESS"
    assert serialized["_geoloc"] == {"lat": 45, "lng": 3}


@pytest.mark.features(WIP_ENABLE_OFFER_ADDRESS_COLLECTIVE=True)
def test_serialize_collective_offer_template_to_be_defined_with_ff():
    venue_offerer_address = offerers_factories.OffererAddressFactory(address__latitude=45, address__longitude=3)
    collective_offer_template = educational_factories.CollectiveOfferTemplateFactory(
        venue__offererAddress=venue_offerer_address,
        locationType=educational_models.CollectiveLocationType.TO_BE_DEFINED,
        locationComment="Here",
    )

    serialized = algolia.AlgoliaBackend().serialize_collective_offer_template(collective_offer_template)
    assert serialized["offer"]["locationType"] == "TO_BE_DEFINED"
    assert serialized["_geoloc"] == {"lat": 45, "lng": 3}


@pytest.mark.features(WIP_ENABLE_OFFER_ADDRESS_COLLECTIVE=True)
def test_serialize_collective_offer_template_no_location_with_ff(caplog):
    venue_offerer_address = offerers_factories.OffererAddressFactory(address__latitude=45, address__longitude=3)
    collective_offer_template = educational_factories.CollectiveOfferTemplateFactory(
        venue__offererAddress=venue_offerer_address,
        locationType=None,
    )

    with caplog.at_level(logging.ERROR):
        serialized = algolia.AlgoliaBackend().serialize_collective_offer_template(collective_offer_template)

    serialized["offer"]["locationType"] is None
    assert serialized["_geoloc"] == {"lat": 45, "lng": 3}

    [log] = caplog.records
    assert log.message == f"Invalid locationType for collective offer template {collective_offer_template.id}"


def test_serialize_collective_offer_template_virtual_venue():
    # this should not happen, collective offers should be linked to physical venues
    collective_offer_template = educational_factories.CollectiveOfferTemplateFactory(
        venue__offererAddress=None, venue__isVirtual=True, venue__siret=None, venue__comment=None
    )

    serialized = algolia.AlgoliaBackend().serialize_collective_offer_template(collective_offer_template)
    assert serialized["venue"]["departmentCode"] is None
    assert serialized["venue"]["academy"] is None
    assert serialized["_geoloc"] == {"lat": serialization.DEFAULT_LATITUDE, "lng": serialization.DEFAULT_LONGITUDE}


def test_serialize_collective_offer_template_legacy():
    # Same as test_serialize_collective_offer_template
    domain1 = educational_factories.EducationalDomainFactory(name="Danse")
    domain2 = educational_factories.EducationalDomainFactory(name="Architecture")
    venue = offerers_factories.VenueFactory()

    collective_offer_template = educational_factories.CollectiveOfferTemplateFactory(
        dateCreated=datetime.datetime(2022, 1, 1, 10, 0, 0),
        name="Titre formidable",
        description="description formidable",
        students=[educational_models.StudentLevels.CAP1, educational_models.StudentLevels.CAP2],
        venue__street="Place de la mairie",
        venue__postalCode="86140",
        venue__name="La Moyenne Librairie SA",
        venue__publicName="La Moyenne Librairie",
        venue__managingOfferer__name="Les Librairies Associées",
        venue__departementCode="86",
        venue__adageId="123456",
        educational_domains=[domain1, domain2],
        interventionArea=None,
        offerVenue={
            "addressType": educational_models.OfferAddressType.OFFERER_VENUE,
            "venueId": venue.id,
            "otherAddress": "",
        },
        locationType=None,
        offererAddress=None,
    )

    serialized = algolia.AlgoliaBackend().serialize_collective_offer_template(collective_offer_template)
    assert serialized == {
        "objectID": f"T-{collective_offer_template.id}",
        "offer": {
            "dateCreated": 1641031200.0,
            "name": "Titre formidable",
            "students": ["CAP - 1re année", "CAP - 2e année"],
            "domains": [domain1.id, domain2.id],
            "interventionArea": [],
            "schoolInterventionArea": None,
            "eventAddressType": educational_models.OfferAddressType.OFFERER_VENUE.value,
            "locationType": None,
            "beginningDatetime": 1641031200.0,
            "description": collective_offer_template.description,
        },
        "offerer": {
            "name": "Les Librairies Associées",
        },
        "venue": {
            "academy": "Poitiers",
            "departmentCode": "86",
            "id": collective_offer_template.venue.id,
            "name": "La Moyenne Librairie SA",
            "publicName": "La Moyenne Librairie",
            "adageId": collective_offer_template.venue.adageId,
        },
        "_geoloc": {
            "lat": float(collective_offer_template.venue.offererAddress.address.latitude),
            "lng": float(collective_offer_template.venue.offererAddress.address.longitude),
        },
        "isTemplate": True,
        "formats": [format.value for format in collective_offer_template.formats],
    }
