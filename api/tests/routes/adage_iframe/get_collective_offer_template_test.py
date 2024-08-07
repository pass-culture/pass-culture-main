import datetime
from operator import attrgetter
from operator import itemgetter

from flask import url_for
import pytest

from pcapi.core.categories import subcategories_v2 as subcategories
from pcapi.core.educational import factories as educational_factories
from pcapi.core.educational import models as educational_models
from pcapi.core.educational.models import StudentLevels
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.testing import assert_num_queries
from pcapi.models import offer_mixin
from pcapi.utils import db as db_utils
from pcapi.utils.date import format_into_utc_date


pytestmark = pytest.mark.usefixtures("db_session")

EMAIL = "toto@mail.com"
IMG_URL = "http://localhost/some/picture.png"


@pytest.fixture(name="eac_client")
def eac_client_fixture(client):
    return client.with_adage_token(email=EMAIL, uai="1234UAI")


@pytest.fixture(name="redactor")
def redactor_fixture():
    return educational_factories.EducationalRedactorFactory(email=EMAIL)


@pytest.fixture(name="offer")
def offer_fixture():
    offer_range = educational_factories.DateRangeFactory(
        start=datetime.datetime.utcnow() - datetime.timedelta(days=7),
        end=datetime.datetime.utcnow() - datetime.timedelta(days=1),
    )
    return offer_range


def expected_serialized_offer(offer, redactor, offer_venue=None):
    national_program = offer.nationalProgram
    is_favorite = offer.id in {offer.id for offer in redactor.favoriteCollectiveOfferTemplates}
    coordinates = {
        "longitude": float(offer.venue.longitude),
        "latitude": float(offer.venue.latitude),
    }

    if offer.formats:
        formats = [fmt.value for fmt in offer.formats]
    elif offer.subcategoryId:
        formats = [fmt.value for fmt in offer.subcategory.formats]
    else:
        formats = []

    return {
        "description": offer.description,
        "id": offer.id,
        "isExpired": offer.hasBookingLimitDatetimesPassed,
        "isSoldOut": False,
        "name": offer.name,
        "venue": {
            "adageId": offer.venue.adageId,
            "address": offer.venue.street,
            "city": offer.venue.city,
            "coordinates": coordinates,
            "distance": None,
            "id": offer.venue.id,
            "imgUrl": offer.venue.bannerUrl,
            "managingOfferer": {"name": offer.venue.managingOfferer.name},
            "name": offer.venue.name,
            "postalCode": offer.venue.postalCode,
            "departmentCode": offer.venue.departementCode,
            "publicName": offer.venue.publicName,
        },
        "interventionArea": offer.interventionArea,
        "audioDisabilityCompliant": offer.audioDisabilityCompliant,
        "mentalDisabilityCompliant": offer.mentalDisabilityCompliant,
        "motorDisabilityCompliant": offer.motorDisabilityCompliant,
        "visualDisabilityCompliant": offer.visualDisabilityCompliant,
        "durationMinutes": offer.durationMinutes,
        "contactEmail": offer.contactEmail,
        "contactPhone": offer.contactPhone,
        "contactForm": offer.contactForm.value,
        "contactUrl": offer.contactUrl,
        "offerVenue": {
            "addressType": offer.offerVenue["addressType"],
            "venueId": offer.offerVenue["venueId"],
            "otherAddress": offer.offerVenue["otherAddress"],
            "address": offer_venue.street if offer_venue else None,
            "city": offer_venue.city if offer_venue else None,
            "distance": None,
            "name": offer_venue.name if offer_venue else None,
            "postalCode": offer_venue.postalCode if offer_venue else None,
            "publicName": offer_venue.publicName if offer_venue else None,
        },
        "students": [student.value for student in offer.students],
        "offerId": offer.offerId,
        "educationalPriceDetail": offer.priceDetail,
        "domains": [{"id": domain.id, "name": domain.name} for domain in offer.domains],
        "imageUrl": offer.imageUrl,
        "imageCredit": offer.imageCredit,
        "nationalProgram": {"id": national_program.id, "name": national_program.name} if national_program else None,
        "isFavorite": is_favorite,
        "dates": {
            "start": format_into_utc_date(offer.start) if offer.start else None,
            "end": format_into_utc_date(offer.end) if offer.end else None,
        },
        "formats": formats,
        "isTemplate": isinstance(offer, educational_models.CollectiveOfferTemplate),
    }


class CollectiveOfferTemplateTest:
    def test_get_collective_offer_template(self, eac_client, redactor):
        venue = offerers_factories.VenueFactory()
        offer = educational_factories.CollectiveOfferTemplateFactory(
            subcategoryId=subcategories.SEANCE_CINE.id,
            venue__bannerUrl=IMG_URL,
            name="offer name",
            description="offer description",
            priceDetail="détail du prix",
            students=[StudentLevels.GENERAL2],
            offerVenue={
                "venueId": venue.id,
                "addressType": "offererVenue",
                "otherAddress": "",
            },
            nationalProgramId=educational_factories.NationalProgramFactory().id,
        )

        url = url_for("adage_iframe.get_collective_offer_template", offer_id=offer.id)

        # 1. fetch redactor
        # 2. fetch collective offer and related data
        # 3. fetch the offerVenue's details (Venue)
        # 4. find out if its a redactor's favorite
        with assert_num_queries(4):
            response = eac_client.get(url)

        assert response.status_code == 200
        assert offer.status == "ACTIVE"
        assert response.json == expected_serialized_offer(offer, redactor, venue)

    def test_get_collective_offer_template_if_inactive(self, eac_client, redactor):
        venue = offerers_factories.VenueFactory()
        offer = educational_factories.CollectiveOfferTemplateFactory(
            subcategoryId=subcategories.SEANCE_CINE.id,
            name="offer name",
            description="offer description",
            priceDetail="détail du prix",
            students=[StudentLevels.GENERAL2],
            offerVenue={
                "venueId": venue.id,
                "addressType": "offererVenue",
                "otherAddress": "",
            },
            nationalProgramId=educational_factories.NationalProgramFactory().id,
            dateCreated=datetime.datetime.utcnow() - datetime.timedelta(days=9),
            dateRange=db_utils.make_timerange(
                start=datetime.datetime.utcnow() - datetime.timedelta(days=7),
                end=datetime.datetime.utcnow() - datetime.timedelta(days=1),
            ),
        )

        url = url_for("adage_iframe.get_collective_offer_template", offer_id=offer.id)

        # 1. fetch collective offer and related data
        # 2. fetch redactor
        # 3. find out if its a redactor's favorite
        # 4. fetch the venue
        with assert_num_queries(4):
            response = eac_client.get(url)

        assert response.status_code == 200
        assert offer.status == offer_mixin.CollectiveOfferStatus.INACTIVE.value

    def test_get_collective_offer_template_without_date_range(self, eac_client, redactor):
        venue = offerers_factories.VenueFactory()
        offer = educational_factories.CollectiveOfferTemplateFactory(
            subcategoryId=subcategories.SEANCE_CINE.id,
            name="offer name",
            description="offer description",
            priceDetail="détail du prix",
            students=[StudentLevels.GENERAL2],
            offerVenue={
                "venueId": venue.id,
                "addressType": "offererVenue",
                "otherAddress": "",
            },
            nationalProgramId=educational_factories.NationalProgramFactory().id,
            dateCreated=datetime.datetime.utcnow() - datetime.timedelta(days=9),
            dateRange=None,
        )

        url = url_for("adage_iframe.get_collective_offer_template", offer_id=offer.id)

        # 1. fetch collective offer and related data
        # 2. fetch redactor
        # 4. find out if its a redactor's favorite
        # 4. fetch the venue
        with assert_num_queries(4):
            response = eac_client.get(url)

        assert response.status_code == 200
        assert offer.status == offer_mixin.CollectiveOfferStatus.ACTIVE.value

    def test_is_a_redactors_favorite(self, eac_client):
        """Ensure that the isFavorite field is true only if the
        redactor added it to its favorites.
        """
        offer = educational_factories.CollectiveOfferTemplateFactory()
        educational_factories.EducationalRedactorFactory(email=EMAIL, favoriteCollectiveOfferTemplates=[offer])

        dst = url_for("adage_iframe.get_collective_offer_template", offer_id=offer.id)

        # 1. fetch collective offer template and related data
        # 2. fetch redactor
        # 3. find out if its a redactor's favorite
        with assert_num_queries(3):
            response = eac_client.get(dst)

        assert response.status_code == 200
        assert response.json["isFavorite"]

    def test_should_return_404_when_no_collective_offer_template(self, eac_client, redactor):
        response = eac_client.get("/adage-iframe/collective/offers-template/0")
        assert response.status_code == 404

    @pytest.mark.parametrize(
        "validation",
        [
            offer_mixin.OfferValidationStatus.DRAFT,
            offer_mixin.OfferValidationStatus.PENDING,
            offer_mixin.OfferValidationStatus.REJECTED,
        ],
    )
    def test_should_return_404_when_collective_offer_template_is_not_approved(self, eac_client, redactor, validation):
        offer = educational_factories.CollectiveOfferTemplateFactory(validation=validation)
        response = eac_client.get(f"/adage-iframe/collective/offers-template/{offer.id}")
        assert response.status_code == 404

    def test_non_redactor_is_ok(self, eac_client):
        """Ensure that an authenticated user that is a not an
        educational redactor can still fetch offers informations.
        """
        offer = educational_factories.CollectiveOfferTemplateFactory()
        dst = url_for("adage_iframe.get_collective_offer_template", offer_id=offer.id)

        # 1. fetch redactor
        # 2. fetch collective offer and related data
        with assert_num_queries(2):
            response = eac_client.get(dst)

        assert response.status_code == 200


class GetCollectiveOfferTemplatesTest:
    endpoint = "adage_iframe.get_collective_offer_templates"

    def test_one_template_id(self, eac_client, redactor):
        offer = educational_factories.CollectiveOfferTemplateFactory()
        url = url_for(self.endpoint, ids=[offer.id])

        # 1. fetch redactor
        # 2. fetch collective offer and related data
        # 3. fetch the venue
        # 4. fetch the venue's images
        with assert_num_queries(4):
            response = eac_client.get(url)

        assert response.status_code == 200
        assert response.json["collectiveOffers"] == [expected_serialized_offer(offer, redactor)]

    def test_get_many_templates(self, eac_client, redactor):
        venues = offerers_factories.VenueFactory.create_batch(3)
        venues = sorted(venues, key=attrgetter("id"))

        venues_from_offer_ids = {}

        offers = []
        for venue in venues:
            offer_venue = {"addressType": "offererVenue", "otherAddress": "", "venueId": venue.id}
            offer = educational_factories.CollectiveOfferTemplateFactory(offerVenue=offer_venue)

            offers.append(offer)
            venues_from_offer_ids[offer.id] = venue

        url = url_for(self.endpoint, ids=[offer.id for offer in offers])

        # 1. fetch redactor
        # 2. fetch collective offers and related data
        # 3. fetch the venue
        # 4. fetch the venues's images
        with assert_num_queries(4):
            response = eac_client.get(url)

        assert response.status_code == 200

        found_offers = sorted(response.json["collectiveOffers"], key=itemgetter("id"))
        offers = sorted(offers, key=attrgetter("id"))

        assert found_offers == [
            expected_serialized_offer(offers[0], redactor, venues_from_offer_ids[offers[0].id]),
            expected_serialized_offer(offers[1], redactor, venues_from_offer_ids[offers[1].id]),
            expected_serialized_offer(offers[2], redactor, venues_from_offer_ids[offers[2].id]),
        ]

    def test_get_many_templates_with_some_unknown_ids(self, eac_client, redactor):
        offers = educational_factories.CollectiveOfferTemplateFactory.create_batch(2)
        url = url_for(self.endpoint, ids=[offer.id for offer in offers] + [-1, -2, -3])

        # 1. fetch redactor
        # 2. fetch collective offers and related data
        # 3. fetch the venue
        # 4. fetch the venues's images
        with assert_num_queries(4):
            response = eac_client.get(url)

        assert response.status_code == 200

        found_offers = sorted(response.json["collectiveOffers"], key=itemgetter("id"))
        offers = sorted(offers, key=attrgetter("id"))

        assert found_offers == [
            expected_serialized_offer(offers[0], redactor),
            expected_serialized_offer(offers[1], redactor),
        ]

    def test_one_template_id_with_one_archived_template(self, eac_client, redactor):
        offer = educational_factories.CollectiveOfferTemplateFactory()
        archived_offer = educational_factories.CollectiveOfferTemplateFactory(dateArchived=datetime.datetime.utcnow())

        url = url_for(self.endpoint, ids=[offer.id, archived_offer.id])

        # 1. fetch redactor
        # 2. fetch collective offer and related data
        # 3. fetch the venue
        # 4. fetch the venue's images
        with assert_num_queries(4):
            response = eac_client.get(url)

            assert response.status_code == 200
            assert len(response.json["collectiveOffers"]) == 1

            assert response.json["collectiveOffers"][0]["id"] != archived_offer.id

    def test_one_template_id_with_one_inactive_template(self, eac_client, redactor):
        offer = educational_factories.CollectiveOfferTemplateFactory()
        inactive_offer = educational_factories.CollectiveOfferTemplateFactory(isActive=False)

        url = url_for(self.endpoint, ids=[offer.id, inactive_offer.id])

        # 1. fetch redactor
        # 2. fetch collective offer and related data
        # 3. fetch the venue
        # 4. fetch the venue's images
        with assert_num_queries(4):
            response = eac_client.get(url)

            assert response.status_code == 200
            assert len(response.json["collectiveOffers"]) == 1

            assert response.json["collectiveOffers"][0]["id"] != inactive_offer.id

    def test_get_one_template(self, eac_client, redactor):
        venue = offerers_factories.VenueFactory()

        offer_venue = {"addressType": "offererVenue", "otherAddress": "", "venueId": venue.id}
        offer = educational_factories.CollectiveOfferTemplateFactory(offerVenue=offer_venue)

        url = url_for(self.endpoint, ids=offer.id)

        # 1. fetch redactor
        # 2. fetch collective offer and related data
        # 3. fetch the venue
        # 4. fetch the venue's images
        with assert_num_queries(4):
            response = eac_client.get(url)

        assert response.status_code == 200
        assert response.json["collectiveOffers"] == [expected_serialized_offer(offer, redactor, venue)]

    def test_unknown_ids(self, eac_client, redactor):
        offers = educational_factories.CollectiveOfferTemplateFactory.create_batch(3)
        self.assert_one_query_and_empty_response(eac_client, [o.id + 100 for o in offers])

    def test_no_templates_to_fetch(self, eac_client, redactor):
        self.assert_one_query_and_empty_response(eac_client, [1, 2])

    def test_missing_ids_parameter(self, eac_client, redactor):
        with assert_num_queries(0):
            assert eac_client.get(url_for(self.endpoint)).status_code == 400

    def test_no_templates_ids(self, eac_client, redactor):
        self.assert_no_queries_and_error_code(eac_client, [], "ids")

    def test_ids_is_null(self, eac_client, redactor):
        self.assert_no_queries_and_error_code(eac_client, None, "ids")

    def test_ids_is_not_a_list_of_ids(self, eac_client, redactor):
        self.assert_no_queries_and_error_code(eac_client, ["not an id", "oops"], "ids.0", "ids.1")

    def test_unauthenticated(self, client):
        url = url_for(self.endpoint, ids=[1, 2, 3])
        assert client.get(url).status_code == 401

    def assert_one_query_and_empty_response(self, client, ids):
        url = url_for(self.endpoint, ids=ids)

        # 1. (try to) fetch collective offers and related data
        with assert_num_queries(1):
            response = client.get(url)

        assert response.status_code == 200
        assert not response.json["collectiveOffers"]

    def assert_no_queries_and_error_code(self, client, ids, *keys):
        url = url_for(self.endpoint, ids=ids)

        with assert_num_queries(0):
            response = client.get(url)

        assert response.status_code == 400

        for key in keys:
            assert key in response.json
