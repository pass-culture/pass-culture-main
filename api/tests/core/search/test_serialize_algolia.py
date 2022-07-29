import datetime
import decimal

import pytest

from pcapi.core.categories import subcategories
import pcapi.core.criteria.factories as criteria_factories
import pcapi.core.educational.factories as educational_factories
from pcapi.core.educational.models import StudentLevels
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offerers.models as offerers_models
import pcapi.core.offers.factories as offers_factories
from pcapi.core.search.backends import algolia
from pcapi.utils.human_ids import humanize


pytestmark = pytest.mark.usefixtures("db_session")


def test_serialize_offer():
    offer = offers_factories.OfferFactory(
        dateCreated=datetime.datetime(2022, 1, 1, 10, 0, 0),
        name="Titre formidable",
        description="Un LIVRE qu'il est bien pour le lire",
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
        venue__postalCode="86140",
        venue__name="La Moyenne Librairie SA",
        venue__publicName="La Moyenne Librairie",
        venue__managingOfferer__name="Les Librairies Associées",
    )
    stock = offers_factories.StockFactory(offer=offer, price=10)
    serialized = algolia.AlgoliaBackend().serialize_offer(offer)
    assert serialized == {
        "distinct": "2221001648",
        "objectID": offer.id,
        "offer": {
            "artist": "Author Performer Speaker Stage Director",
            "rankingWeight": 2,
            "dateCreated": offer.dateCreated.timestamp(),
            "dates": [],
            "description": "livre bien lire",
            "isDigital": False,
            "isDuo": False,
            "isEducational": False,
            "isEvent": False,
            "isForbiddenToUnderage": offer.is_forbidden_to_underage,
            "isThing": True,
            "name": "Titre formidable",
            "prices": [decimal.Decimal("10.00")],
            "searchGroupName": "LIVRE",
            "stocksDateCreated": [stock.dateCreated.timestamp()],
            "students": [],
            "subcategoryId": offer.subcategory.id,
            "thumbUrl": None,
            "tags": [],
            "times": [],
        },
        "offerer": {
            "name": "Les Librairies Associées",
        },
        "venue": {
            "departmentCode": "86",
            "id": offer.venueId,
            "name": "La Moyenne Librairie SA",
            "publicName": "La Moyenne Librairie",
        },
        "_geoloc": {"lat": 48.87004, "lng": 2.3785},
    }


def test_serialize_offer_event():
    offer = offers_factories.OfferFactory(subcategoryId=subcategories.SEANCE_CINE.id)
    dt1 = datetime.datetime(2032, 1, 4, 12, 15)
    offers_factories.EventStockFactory(offer=offer, beginningDatetime=dt1)
    dt2 = datetime.datetime(2032, 1, 1, 16, 30)
    offers_factories.EventStockFactory(offer=offer, beginningDatetime=dt2)
    serialized = algolia.AlgoliaBackend().serialize_offer(offer)
    # Dates are ordered, but times are not. I don't know why we order dates.
    assert serialized["offer"]["dates"] == [dt2.timestamp(), dt1.timestamp()]
    assert set(serialized["offer"]["times"]) == {12 * 60 * 60 + 15 * 60, 16 * 60 * 60 + 30 * 60}


@pytest.mark.parametrize(
    "extra_data,expected_distinct",
    (
        [{}, "1"],
        [{"visa": "56070"}, "56070"],
        [{"isbn": "123456789"}, "123456789"],
        [{"visa": "56070", "diffusionVersion": "VO"}, "56070VO"],
        [{"visa": "56070", "diffusionVersion": "VF"}, "56070VF"],
    ),
)
def test_serialize_offer_distinct(extra_data, expected_distinct):
    offer = offers_factories.OfferFactory(id=1, extraData=extra_data)
    serialized = algolia.AlgoliaBackend().serialize_offer(offer)
    assert serialized["distinct"] == expected_distinct


def test_serialize_offer_tags():
    criterion = criteria_factories.CriterionFactory(name="formidable")
    offer = offers_factories.OfferFactory(criteria=[criterion])
    serialized = algolia.AlgoliaBackend().serialize_offer(offer)
    assert serialized["offer"]["tags"] == ["formidable"]


def test_serialize_default_position():
    offer = offers_factories.DigitalOfferFactory()
    serialized = algolia.AlgoliaBackend().serialize_offer(offer)
    assert serialized["_geoloc"] == {
        "lat": algolia.DEFAULT_LATITUDE,
        "lng": algolia.DEFAULT_LONGITUDE,
    }


def test_serialize_offer_thumb_url():
    offer = offers_factories.OfferFactory(product__thumbCount=1)
    serialized = algolia.AlgoliaBackend().serialize_offer(offer)
    assert serialized["offer"]["thumbUrl"] == f"/storage/thumbs/products/{humanize(offer.productId)}"


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
        "is_eligible_for_strict_search": False,
        "has_at_least_one_bookable_offer": False,
    }


def test_serialize_venue_with_one_bookable_offer():
    venue = offerers_factories.VenueFactory(isPermanent=True)
    offers_factories.EventStockFactory(offer__venue=venue)

    serialized = algolia.AlgoliaBackend().serialize_venue(venue)
    assert serialized["is_eligible_for_strict_search"]
    assert serialized["has_at_least_one_bookable_offer"]


def test_serialize_collective_offer():
    domain1 = educational_factories.EducationalDomainFactory(name="Danse")
    domain2 = educational_factories.EducationalDomainFactory(name="Architecture")
    educational_institution = educational_factories.EducationalInstitutionFactory()
    collective_offer = educational_factories.CollectiveOfferFactory(
        dateCreated=datetime.datetime(2022, 1, 1, 10, 0, 0),
        name="Titre formidable",
        students=[StudentLevels.CAP1, StudentLevels.CAP2],
        subcategoryId=subcategories.LIVRE_PAPIER.id,
        venue__postalCode="86140",
        venue__name="La Moyenne Librairie SA",
        venue__publicName="La Moyenne Librairie",
        venue__managingOfferer__name="Les Librairies Associées",
        venue__departementCode="86",
        educational_domains=[domain1, domain2],
        institution=educational_institution,
        interventionArea=["1", "90", "94"],
    )

    serialized = algolia.AlgoliaBackend().serialize_collective_offer(collective_offer)
    assert serialized == {
        "objectID": collective_offer.id,
        "offer": {
            "dateCreated": 1641031200.0,
            "name": "Titre formidable",
            "students": ["CAP - 1re année", "CAP - 2e année"],
            "subcategoryId": subcategories.LIVRE_PAPIER.id,
            "domains": [domain1.id, domain2.id],
            "educationalInstitutionUAICode": educational_institution.institutionId,
            "interventionArea": ["1", "90", "94"],
        },
        "offerer": {
            "name": "Les Librairies Associées",
        },
        "venue": {
            "departmentCode": "86",
            "id": collective_offer.venue.id,
            "name": "La Moyenne Librairie SA",
            "publicName": "La Moyenne Librairie",
        },
        "isTemplate": False,
    }


def test_serialize_collective_offer_without_institution():
    collective_offer = educational_factories.CollectiveOfferFactory()
    serialized = algolia.AlgoliaBackend().serialize_collective_offer(collective_offer)
    assert serialized["offer"]["educationalInstitutionUAICode"] == "all"


def test_serialize_collective_offer_template():
    domain1 = educational_factories.EducationalDomainFactory(name="Danse")
    domain2 = educational_factories.EducationalDomainFactory(name="Architecture")
    collective_offer_template = educational_factories.CollectiveOfferTemplateFactory(
        dateCreated=datetime.datetime(2022, 1, 1, 10, 0, 0),
        name="Titre formidable",
        students=[StudentLevels.CAP1, StudentLevels.CAP2],
        subcategoryId=subcategories.LIVRE_PAPIER.id,
        venue__postalCode="86140",
        venue__name="La Moyenne Librairie SA",
        venue__publicName="La Moyenne Librairie",
        venue__managingOfferer__name="Les Librairies Associées",
        venue__departementCode="86",
        educational_domains=[domain1, domain2],
        interventionArea=["1", "90", "94"],
    )

    serialized = algolia.AlgoliaBackend().serialize_collective_offer_template(collective_offer_template)
    assert serialized == {
        "objectID": f"T-{collective_offer_template.id}",
        "offer": {
            "dateCreated": 1641031200.0,
            "name": "Titre formidable",
            "students": ["CAP - 1re année", "CAP - 2e année"],
            "subcategoryId": subcategories.LIVRE_PAPIER.id,
            "domains": [domain1.id, domain2.id],
            "educationalInstitutionUAICode": "all",
            "interventionArea": ["1", "90", "94"],
        },
        "offerer": {
            "name": "Les Librairies Associées",
        },
        "venue": {
            "departmentCode": "86",
            "id": collective_offer_template.venue.id,
            "name": "La Moyenne Librairie SA",
            "publicName": "La Moyenne Librairie",
        },
        "isTemplate": True,
    }
