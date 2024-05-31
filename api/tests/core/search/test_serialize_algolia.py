import datetime
import decimal

import pytest

from pcapi.core.categories import subcategories_v2 as subcategories
import pcapi.core.criteria.factories as criteria_factories
import pcapi.core.educational.factories as educational_factories
from pcapi.core.educational.models import StudentLevels
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offerers.models as offerers_models
import pcapi.core.offers.factories as offers_factories
import pcapi.core.offers.models as offers_models
from pcapi.core.search.backends import algolia
from pcapi.core.testing import override_settings
from pcapi.routes.adage_iframe.serialization.offers import OfferAddressType
from pcapi.utils.human_ids import humanize


pytestmark = pytest.mark.usefixtures("db_session")


@override_settings(ALGOLIA_LAST_30_DAYS_BOOKINGS_RANGE_THRESHOLDS=[1, 2, 3, 4])
def test_serialize_offer():
    rayon = "Policier / Thriller format poche"  # fetched from provider

    # known values (inserted using a migration)
    # note: some might contain trailing whitespaces. Also sections are
    # usually lowercase whilst sections from providers might be
    # capitalized.
    book_macro_section = offers_models.BookMacroSection.query.filter_by(
        section="policier / thriller format poche"
    ).one()
    macro_section = book_macro_section.macroSection.strip()

    offer = offers_factories.OfferFactory(
        dateCreated=datetime.datetime(2022, 1, 1, 10, 0, 0),
        name="Titre formidable",
        description="Un LIVRE qu'il est bien pour le lire",
        extraData={
            "author": "Author",
            "ean": "2221001648",
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
        venue__managingOfferer__name="Les Librairies Associées",
    )
    offers_factories.StockFactory(offer=offer, price=10)
    serialized = algolia.AlgoliaBackend().serialize_offer(offer, 0)
    assert serialized == {
        "distinct": "2221001648",
        "objectID": offer.id,
        "offer": {
            "artist": "Author Performer Speaker Stage Director",
            "bookMacroSection": macro_section,
            "dateCreated": offer.dateCreated.timestamp(),
            "dates": [],
            "description": "livre bien lire",
            "ean": "2221001648",
            "isDigital": False,
            "isDuo": False,
            "isEducational": False,
            "isEvent": False,
            "isForbiddenToUnderage": offer.is_forbidden_to_underage,
            "isThing": True,
            "last30DaysBookings": 0,
            "last30DaysBookingsRange": algolia.Last30DaysBookingsRange.VERY_LOW.value,
            "name": "Titre formidable",
            "nativeCategoryId": offer.subcategory.native_category_id,
            "prices": [decimal.Decimal("10.00")],
            "rankingWeight": 2,
            "searchGroupName": "LIVRES",
            "searchGroupNamev2": "LIVRES",
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
            "city": offer.venue.city,
            "departmentCode": "86",
            "id": offer.venueId,
            "isAudioDisabilityCompliant": False,
            "isMentalDisabilityCompliant": False,
            "isMotorDisabilityCompliant": False,
            "isVisualDisabilityCompliant": False,
            "name": "La Moyenne Librairie SA",
            "postalCode": offer.venue.postalCode,
            "publicName": "La Moyenne Librairie",
        },
        "_geoloc": {"lat": 48.87004, "lng": 2.3785},
    }


@pytest.mark.parametrize(
    "extra_data, expected_music_style, expected_show_type, expected_movie_genres, expected_macro_section",
    (
        ({"musicType": "501"}, "Jazz", None, None, None),
        ({"musicType": "600"}, "Classique", None, None, None),
        ({"musicType": "-1"}, "Autre", None, None, None),
        ({"musicType": " "}, None, None, None, None),
        ({"showType": "100"}, None, "Arts de la rue", None, None),
        ({"showType": "1200"}, None, "Spectacle Jeunesse", None, None),
        ({"showType": "-1"}, None, "Autre", None, None),
        ({"showType": " "}, None, None, None, None),
        ({"genres": ["DRAMA"]}, None, None, ["DRAMA"], None),
        ({"genres": ["ADVENTURE", "DRAMA", "FAMILY"]}, None, None, ["ADVENTURE", "DRAMA", "FAMILY"], None),
        ({"genres": []}, None, None, [], None),
        ({"genres": None}, None, None, None, None),
        ({"rayon": "documentaire jeunesse histoire"}, None, None, None, "Jeunesse"),
        ({"rayon": "petits prix"}, None, None, None, "Littérature française"),
        ({"rayon": "ce rayon n'existe pas"}, None, None, None, None),
        ({"rayon": None}, None, None, None, None),
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


@override_settings(ALGOLIA_LAST_30_DAYS_BOOKINGS_RANGE_THRESHOLDS=[1, 2, 3, 4])
@pytest.mark.parametrize(
    "bookings_count, expected_range",
    (
        (0, algolia.Last30DaysBookingsRange.VERY_LOW.value),
        (1, algolia.Last30DaysBookingsRange.LOW.value),
        (2, algolia.Last30DaysBookingsRange.MEDIUM.value),
        (3, algolia.Last30DaysBookingsRange.HIGH.value),
        (4, algolia.Last30DaysBookingsRange.VERY_HIGH.value),
        (5, algolia.Last30DaysBookingsRange.VERY_HIGH.value),
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
    "extra_data,expected_distinct",
    (
        [{}, "1"],
        [{"allocineId": 12345, "visa": "56070"}, "12345"],
        [{"visa": "56070"}, "56070"],
        [{"visa": "56070", "diffusionVersion": "VO"}, "56070VO"],
        [{"visa": "56070", "diffusionVersion": "VF"}, "56070VF"],
        [{"ean": "12345678"}, "12345678"],
    ),
)
def test_serialize_offer_distinct(extra_data, expected_distinct):
    offer = offers_factories.OfferFactory(id=1, extraData=extra_data)
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
        "lat": algolia.DEFAULT_LATITUDE,
        "lng": algolia.DEFAULT_LONGITUDE,
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


def test_serialize_offer_visa():
    offer = offers_factories.OfferFactory(
        extraData={"visa": "2607019901"},
    )
    serialized = algolia.AlgoliaBackend().serialize_offer(offer, 0)
    assert serialized["offer"]["visa"] == "2607019901"


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
        "city": venue.city,
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
        "_geoloc": {"lng": float(venue.longitude), "lat": float(venue.latitude)},
        "has_at_least_one_bookable_offer": False,
        "date_created": venue.dateCreated.timestamp(),
        "postalCode": venue.postalCode,
        "adress": venue.street,
    }


def test_serialize_venue_with_one_bookable_offer():
    venue = offerers_factories.VenueFactory(isPermanent=True)

    serialized = algolia.AlgoliaBackend().serialize_venue(venue)
    assert not serialized["has_at_least_one_bookable_offer"]

    offers_factories.EventStockFactory(offer__venue=venue)
    serialized = algolia.AlgoliaBackend().serialize_venue(venue)
    assert serialized["has_at_least_one_bookable_offer"]


def test_serialize_collective_offer_template():
    domain1 = educational_factories.EducationalDomainFactory(name="Danse")
    domain2 = educational_factories.EducationalDomainFactory(name="Architecture")
    venue = offerers_factories.VenueFactory(latitude=algolia.DEFAULT_LATITUDE, longitude=algolia.DEFAULT_LONGITUDE)

    collective_offer_template = educational_factories.CollectiveOfferTemplateFactory(
        dateCreated=datetime.datetime(2022, 1, 1, 10, 0, 0),
        name="Titre formidable",
        description="description formidable",
        students=[StudentLevels.CAP1, StudentLevels.CAP2],
        subcategoryId=subcategories.CONCERT.id,
        venue__postalCode="86140",
        venue__name="La Moyenne Librairie SA",
        venue__publicName="La Moyenne Librairie",
        venue__managingOfferer__name="Les Librairies Associées",
        venue__departementCode="86",
        venue__adageId="123456",
        educational_domains=[domain1, domain2],
        interventionArea=None,
        offerVenue={"addressType": OfferAddressType.OFFERER_VENUE, "venueId": venue.id, "otherAddress": ""},
    )

    serialized = algolia.AlgoliaBackend().serialize_collective_offer_template(collective_offer_template)
    assert serialized == {
        "objectID": f"T-{collective_offer_template.id}",
        "offer": {
            "dateCreated": 1641031200.0,
            "name": "Titre formidable",
            "students": ["CAP - 1re année", "CAP - 2e année"],
            "subcategoryId": subcategories.CONCERT.id,
            "domains": [domain1.id, domain2.id],
            "educationalInstitutionUAICode": "all",
            "interventionArea": [],
            "schoolInterventionArea": None,
            "eventAddressType": OfferAddressType.OFFERER_VENUE.value,
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
            "lat": float(venue.latitude),
            "lng": float(venue.longitude),
        },
        "isTemplate": True,
        "formats": [fmt.value for fmt in subcategories.CONCERT.formats],
    }
