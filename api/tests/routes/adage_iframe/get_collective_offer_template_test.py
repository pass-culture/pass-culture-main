import datetime
from operator import attrgetter
from operator import itemgetter

import pytest
from flask import url_for

from pcapi.core.educational import factories as educational_factories
from pcapi.core.educational import models as educational_models
from pcapi.core.educational.models import StudentLevels
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.testing import assert_num_queries
from pcapi.models import offer_mixin
from pcapi.utils import date as date_utils
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
        start=date_utils.get_naive_utc_now() - datetime.timedelta(days=7),
        end=date_utils.get_naive_utc_now() - datetime.timedelta(days=1),
    )
    return offer_range


def expected_serialized_offer(offer, redactor, offer_venue=None):
    national_program = offer.nationalProgram
    is_favorite = offer.id in {offer.id for offer in redactor.favoriteCollectiveOfferTemplates}
    venue_address = offer.venue.offererAddress.address
    coordinates = {
        "longitude": float(venue_address.longitude),
        "latitude": float(venue_address.latitude),
    }
    oa = offer.offererAddress
    address = oa.address if oa else None

    return {
        "description": offer.description,
        "id": offer.id,
        "name": offer.name,
        "venue": {
            "adageId": offer.venue.adageId,
            "address": venue_address.street,
            "city": venue_address.city,
            "coordinates": coordinates,
            "id": offer.venue.id,
            "imgUrl": offer.venue.bannerUrl,
            "managingOfferer": {"name": offer.venue.managingOfferer.name},
            "name": offer.venue.name,
            "postalCode": venue_address.postalCode,
            "departmentCode": venue_address.departmentCode,
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
        "location": {
            "locationType": offer.locationType.value,
            "locationComment": offer.locationComment,
            "location": {
                "banId": address.banId,
                "city": address.city,
                "departmentCode": address.departmentCode,
                "id": address.id,
                "inseeCode": address.inseeCode,
                "isManualEdition": address.isManualEdition,
                "label": oa.label,
                "latitude": float(address.latitude),
                "longitude": float(address.longitude),
                "postalCode": address.postalCode,
                "street": address.street,
                "isVenueLocation": False,
            }
            if address
            else None,
        },
        "students": [student.value for student in offer.students],
        "educationalPriceDetail": offer.priceDetail,
        "domains": [{"id": domain.id, "name": domain.name} for domain in offer.domains],
        "imageUrl": offer.imageUrl,
        "nationalProgram": {"id": national_program.id, "name": national_program.name} if national_program else None,
        "isFavorite": is_favorite,
        "dates": {
            "start": format_into_utc_date(offer.start) if offer.start else None,
            "end": format_into_utc_date(offer.end) if offer.end else None,
        },
        "formats": [format.value for format in offer.formats],
        "isTemplate": isinstance(offer, educational_models.CollectiveOfferTemplate),
    }


class CollectiveOfferTemplateTest:
    num_queries = 1  # fetch collective offer and related data
    num_queries += 1  # fetch redactor
    num_queries += 1  # check if offer is favorite

    def test_get_collective_offer_template(self, eac_client, redactor):
        venue = offerers_factories.VenueFactory()
        offer = educational_factories.CollectiveOfferTemplateFactory(
            venue__bannerUrl=IMG_URL,
            name="offer name",
            description="offer description",
            priceDetail="détail du prix",
            students=[StudentLevels.GENERAL2],
            locationType=educational_models.CollectiveLocationType.ADDRESS,
            offererAddress=offerers_factories.get_offerer_address_with_label_from_venue(venue),
            nationalProgramId=educational_factories.NationalProgramFactory().id,
        )

        url = url_for("adage_iframe.get_collective_offer_template", offer_id=offer.id)

        with assert_num_queries(self.num_queries):
            response = eac_client.get(url)

        assert response.status_code == 200
        assert offer.displayedStatus == educational_models.CollectiveOfferDisplayedStatus.PUBLISHED
        assert response.json == expected_serialized_offer(offer, redactor, venue)

    def test_get_collective_offer_template_if_inactive(self, eac_client, redactor):
        offer = educational_factories.CollectiveOfferTemplateFactory(
            dateCreated=date_utils.get_naive_utc_now() - datetime.timedelta(days=9),
            dateRange=db_utils.make_timerange(
                start=date_utils.get_naive_utc_now() - datetime.timedelta(days=7),
                end=date_utils.get_naive_utc_now() - datetime.timedelta(days=1),
            ),
        )

        url = url_for("adage_iframe.get_collective_offer_template", offer_id=offer.id)

        with assert_num_queries(self.num_queries):
            response = eac_client.get(url)

        assert response.status_code == 200
        assert offer.displayedStatus == educational_models.CollectiveOfferDisplayedStatus.ENDED

    def test_get_collective_offer_template_without_date_range(self, eac_client, redactor):
        offer = educational_factories.CollectiveOfferTemplateFactory(
            dateCreated=date_utils.get_naive_utc_now() - datetime.timedelta(days=9),
            dateRange=None,
        )

        url = url_for("adage_iframe.get_collective_offer_template", offer_id=offer.id)

        with assert_num_queries(self.num_queries):
            response = eac_client.get(url)

        assert response.status_code == 200
        assert offer.displayedStatus == educational_models.CollectiveOfferDisplayedStatus.PUBLISHED

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

    def test_location_address_venue(self, eac_client, redactor):
        venue = offerers_factories.VenueFactory()
        offer = educational_factories.CollectiveOfferTemplateFactory(
            venue=venue,
            locationType=educational_models.CollectiveLocationType.ADDRESS,
            locationComment=None,
            offererAddressId=venue.offererAddress.id,
            interventionArea=None,
        )

        dst = url_for("adage_iframe.get_collective_offer_template", offer_id=offer.id)
        with assert_num_queries(self.num_queries):
            response = eac_client.get(dst)

        assert response.status_code == 200
        response_location = response.json["location"]
        assert response_location["locationType"] == "ADDRESS"
        assert response_location["locationComment"] is None
        assert response_location["location"] is not None
        assert response_location["location"]["isVenueLocation"] is True
        assert response_location["location"]["banId"] == venue.offererAddress.address.banId

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

    # 1. fetch collective offer and related data
    # 2. fetch redactor
    # 3. check if offer is favorite
    expected_num_queries = 3

    def test_one_template_id(self, eac_client, redactor):
        offer = educational_factories.CollectiveOfferTemplateFactory()
        url = url_for(self.endpoint, ids=[offer.id])

        with assert_num_queries(self.expected_num_queries):
            response = eac_client.get(url)

        assert response.status_code == 200
        assert response.json["collectiveOffers"] == [expected_serialized_offer(offer, redactor)]

    def test_get_many_templates(self, eac_client, redactor):
        venues = offerers_factories.VenueFactory.create_batch(3)
        venues = sorted(venues, key=attrgetter("id"))

        venues_from_offer_ids = {}

        offers = []
        for venue in venues:
            offer = educational_factories.CollectiveOfferTemplateFactory(
                locationType=educational_models.CollectiveLocationType.ADDRESS,
                offererAddress=offerers_factories.get_offerer_address_with_label_from_venue(venue),
            )

            offers.append(offer)
            venues_from_offer_ids[offer.id] = venue

        url = url_for(self.endpoint, ids=[offer.id for offer in offers])

        with assert_num_queries(self.expected_num_queries):
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

        with assert_num_queries(self.expected_num_queries):
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
        archived_offer = educational_factories.CollectiveOfferTemplateFactory(
            isActive=False, dateArchived=date_utils.get_naive_utc_now()
        )

        url = url_for(self.endpoint, ids=[offer.id, archived_offer.id])

        with assert_num_queries(self.expected_num_queries):
            response = eac_client.get(url)

        assert response.status_code == 200
        assert len(response.json["collectiveOffers"]) == 1
        assert response.json["collectiveOffers"][0]["id"] == offer.id

    def test_one_template_id_with_one_inactive_template(self, eac_client, redactor):
        offer = educational_factories.CollectiveOfferTemplateFactory()
        inactive_offer = educational_factories.CollectiveOfferTemplateFactory(isActive=False)

        url = url_for(self.endpoint, ids=[offer.id, inactive_offer.id])

        with assert_num_queries(self.expected_num_queries):
            response = eac_client.get(url)

        assert response.status_code == 200
        assert len(response.json["collectiveOffers"]) == 1
        assert response.json["collectiveOffers"][0]["id"] == offer.id

    def test_one_template_id_without_date_range(self, eac_client, redactor):
        offer = educational_factories.CollectiveOfferTemplateFactory(dateRange=None)
        url = url_for(self.endpoint, ids=[offer.id])

        with assert_num_queries(self.expected_num_queries):
            response = eac_client.get(url)

        assert response.status_code == 200
        assert len(response.json["collectiveOffers"]) == 1
        assert response.json["collectiveOffers"][0]["id"] == offer.id

    def test_get_one_template(self, eac_client, redactor):
        venue = offerers_factories.VenueFactory()

        offer = educational_factories.CollectiveOfferTemplateFactory(
            locationType=educational_models.CollectiveLocationType.ADDRESS,
            offererAddress=offerers_factories.get_offerer_address_with_label_from_venue(venue),
        )

        url = url_for(self.endpoint, ids=offer.id)

        with assert_num_queries(self.expected_num_queries):
            response = eac_client.get(url)

        assert response.status_code == 200
        assert response.json["collectiveOffers"] == [expected_serialized_offer(offer, redactor, venue)]

    def test_location_address_venue(self, eac_client, redactor):
        venue = offerers_factories.VenueFactory()
        offer = educational_factories.CollectiveOfferTemplateFactory(
            venue=venue,
            locationType=educational_models.CollectiveLocationType.ADDRESS,
            locationComment=None,
            offererAddressId=venue.offererAddress.id,
            interventionArea=None,
        )

        url = url_for(self.endpoint, ids=offer.id)
        with assert_num_queries(self.expected_num_queries):
            response = eac_client.get(url)

        assert response.status_code == 200
        [result] = response.json["collectiveOffers"]
        response_location = result["location"]
        assert response_location["locationType"] == "ADDRESS"
        assert response_location["locationComment"] is None
        assert response_location["location"] is not None
        assert response_location["location"]["isVenueLocation"] is True
        assert response_location["location"]["banId"] == venue.offererAddress.address.banId

    def test_location_school(self, eac_client, redactor):
        offer = educational_factories.CollectiveOfferTemplateFactory(
            locationType=educational_models.CollectiveLocationType.SCHOOL,
            locationComment=None,
            offererAddressId=None,
            interventionArea=["33", "75", "93"],
        )

        url = url_for(self.endpoint, ids=offer.id)
        with assert_num_queries(self.expected_num_queries):
            response = eac_client.get(url)

        assert response.status_code == 200
        [result] = response.json["collectiveOffers"]
        response_location = result["location"]
        assert response_location["locationType"] == "SCHOOL"
        assert response_location["locationComment"] is None
        assert response_location["location"] is None

    def test_location_address(self, eac_client, redactor):
        venue = offerers_factories.VenueFactory()
        oa = offerers_factories.OffererAddressFactory(offerer=venue.managingOfferer)
        offer = educational_factories.CollectiveOfferTemplateFactory(
            locationType=educational_models.CollectiveLocationType.ADDRESS,
            locationComment=None,
            offererAddress=oa,
            interventionArea=None,
            venue=venue,
        )

        url = url_for(self.endpoint, ids=offer.id)
        with assert_num_queries(self.expected_num_queries):
            response = eac_client.get(url)

        assert response.status_code == 200
        [result] = response.json["collectiveOffers"]
        response_location = result["location"]
        assert response_location["locationType"] == "ADDRESS"
        assert response_location["locationComment"] is None
        assert response_location["location"] is not None
        assert response_location["location"]["isVenueLocation"] is False
        assert response_location["location"]["banId"] == oa.address.banId

    def test_location_to_be_defined(self, eac_client, redactor):
        offer = educational_factories.CollectiveOfferTemplateFactory(
            locationType=educational_models.CollectiveLocationType.TO_BE_DEFINED,
            locationComment="In space",
            offererAddressId=None,
            interventionArea=["33", "75", "93"],
        )

        url = url_for(self.endpoint, ids=offer.id)
        with assert_num_queries(self.expected_num_queries):
            response = eac_client.get(url)

        assert response.status_code == 200
        [result] = response.json["collectiveOffers"]
        response_location = result["location"]
        assert response_location["locationType"] == "TO_BE_DEFINED"
        assert response_location["locationComment"] == "In space"
        assert response_location["location"] is None

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
