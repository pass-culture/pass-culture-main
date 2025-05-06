from datetime import datetime
from datetime import timedelta
from datetime import timezone
import decimal
from pathlib import Path
from unittest.mock import patch

import pytest
import time_machine

from pcapi import settings
from pcapi.core.categories.models import EacFormat
from pcapi.core.educational import exceptions as educational_exceptions
from pcapi.core.educational import factories as educational_factories
from pcapi.core.educational import models as educational_models
from pcapi.core.educational import testing as educational_testing
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.providers import factories as provider_factories
from pcapi.core.providers import models as providers_models
from pcapi.core.testing import assert_num_queries
from pcapi.models import db

import tests
from tests.routes import image_data
from tests.routes.public.helpers import PublicAPIEndpointBaseHelper


IMAGES_DIR = Path(tests.__path__[0]) / "files"
UPLOAD_FOLDER = settings.LOCAL_STORAGE_DIR / educational_models.CollectiveOffer.FOLDER

time_travel_str = "2021-10-01 15:00:00"


@pytest.fixture(name="venue_provider")
def venue_provider_fixture():
    return provider_factories.VenueProviderFactory()


@pytest.fixture(name="api_key")
def api_key_fixture(venue_provider):
    return offerers_factories.ApiKeyFactory(provider=venue_provider.provider)


@pytest.fixture(name="venue")
def venue_fixture(venue_provider):
    return venue_provider.venue


@pytest.fixture(name="national_program")
def national_program_fixture():
    return educational_factories.NationalProgramFactory()


@pytest.fixture(name="domain")
def domain_fixture(national_program):
    return educational_factories.EducationalDomainFactory(nationalPrograms=[national_program])


@pytest.fixture(name="institution")
def institution_fixture():
    return educational_factories.EducationalInstitutionFactory()


@pytest.fixture(name="payload")
def payload_fixture(minimal_payload, venue_provider, domain, institution, national_program, venue):
    return {
        **minimal_payload,
        "name": "Some offer",
        "description": "une description d'offre",
        "durationMinutes": 183,
        "audioDisabilityCompliant": True,
        "mentalDisabilityCompliant": True,
        "motorDisabilityCompliant": False,
        "visualDisabilityCompliant": False,
        "nationalProgramId": national_program.id,
        "educationalPriceDetail": "Justification du prix",
        "imageCredit": "pouet",
        "imageFile": image_data.GOOD_IMAGE,
        "endDatetime": minimal_payload["startDatetime"],
    }


@pytest.fixture(name="minimal_payload")
@time_machine.travel(time_travel_str)
def minimal_payload_fixture(domain, institution, venue):
    educational_factories.EducationalCurrentYearFactory()

    booking_beginning = datetime.now(timezone.utc) + timedelta(days=10)
    booking_limit = booking_beginning - timedelta(days=2)

    return {
        "venueId": venue.id,
        "name": "Some offer with minimal payload",
        "description": "description",
        "formats": [EacFormat.CONCERT.value],
        "bookingEmails": ["offerer-email@example.com", "offerer-email2@example.com"],
        "contactEmail": "offerer-contact@example.com",
        "contactPhone": "+33100992798",
        "domains": [domain.id],
        "students": [educational_models.StudentLevels.COLLEGE4.name],
        "offerVenue": {
            "venueId": venue.id,
            "addressType": "offererVenue",
            "otherAddress": "",
        },
        "isActive": True,
        "startDatetime": booking_beginning.isoformat(timespec="seconds"),
        "bookingLimitDatetime": booking_limit.isoformat(timespec="seconds"),
        "totalPrice": 600,
        "numberOfTickets": 30,
        "educationalInstitutionId": institution.id,
    }


@pytest.fixture(name="public_client")
def public_client_fixture(client, api_key):
    return client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY)


@pytest.mark.usefixtures("db_session")
class CollectiveOffersPublicPostOfferTest(PublicAPIEndpointBaseHelper):
    endpoint_url = "/v2/collective/offers/"
    endpoint_method = "post"

    def teardown_method(self, *args):
        """clear images after each tests"""
        storage_folder = UPLOAD_FOLDER / educational_models.CollectiveOffer.__name__.lower()
        if storage_folder.exists():
            for child in storage_folder.iterdir():
                if not child.is_file():
                    continue
                child.unlink()

    def test_should_raise_401_because_api_key_not_linked_to_provider(self, client):
        num_queries = 2  # Select API key + rollback
        super().test_should_raise_401_because_api_key_not_linked_to_provider(client, num_queries=num_queries)

    @time_machine.travel(time_travel_str)
    def test_post_offers(self, public_client, payload, venue_provider, domain, institution, national_program, venue):
        num_queries = 1  # fetch api key
        num_queries += 1  # fetch feature flag
        num_queries += 1  # fetch venue
        num_queries += 1  # check if offerer has at least one venue with an adage id
        num_queries += 1  # fetch venue's managing offerer's siren
        num_queries += 1  # fetch educational domain
        num_queries += 1  # fetch educational institution
        num_queries += 1  # fetch educational year
        num_queries += 1  # fetch venue for location

        num_queries += 1  # insert collective offer
        num_queries += 1  # insert collective offer domain
        num_queries += 1  # insert collective stock

        num_queries += 1  # fetch offer for validation
        num_queries += 1  # fetch offer validation rule
        num_queries += 1  # update collective offer validation

        num_queries += 1  # fetch collective offer
        num_queries += 1  # update collective offer image
        num_queries += 1  # fetch collective offer for serialization

        with assert_num_queries(num_queries):
            with patch("pcapi.core.educational.adage_backends.get_adage_offerer") as mock:
                mock.return_value = ["anything", "it does not matter"]
                response = public_client.post("/v2/collective/offers/", json=payload)

            assert response.status_code == 200

        offer = db.session.query(educational_models.CollectiveOffer).filter_by(id=response.json["id"]).one()
        assert offer.students == [educational_models.StudentLevels.COLLEGE4]
        assert offer.venueId == venue.id
        assert offer.name == payload["name"]
        assert offer.domains == [domain]
        assert offer.institutionId == institution.id
        assert offer.interventionArea == []
        assert offer.offerVenue == {
            "venueId": venue.id,
            "addressType": "offererVenue",
            "otherAddress": "",
        }
        assert offer.providerId == venue_provider.providerId
        assert offer.hasImage is True
        assert offer.isPublicApi
        assert offer.nationalProgramId == national_program.id
        assert (UPLOAD_FOLDER / offer._get_image_storage_id()).exists()
        assert offer.formats == [EacFormat.CONCERT]

        # stock data
        assert offer.collectiveStock.startDatetime == datetime.fromisoformat(payload["startDatetime"]).replace(
            tzinfo=None
        )
        assert offer.collectiveStock.endDatetime == datetime.fromisoformat(payload["endDatetime"]).replace(tzinfo=None)
        assert offer.collectiveStock.bookingLimitDatetime == datetime.fromisoformat(
            payload["bookingLimitDatetime"]
        ).replace(tzinfo=None)
        assert offer.collectiveStock.price == decimal.Decimal(payload["totalPrice"])
        assert offer.collectiveStock.priceDetail == payload["educationalPriceDetail"]

        json = response.json
        assert json["name"] == "Some offer"
        assert "location" in json

    @time_machine.travel(time_travel_str)
    def test_post_offers_without_end_datetime(self, public_client, payload):
        del payload["endDatetime"]

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = public_client.post("/v2/collective/offers/", json=payload)

        assert response.status_code == 200
        offer = db.session.query(educational_models.CollectiveOffer).filter_by(id=response.json["id"]).one()
        assert offer.collectiveStock.startDatetime == datetime.fromisoformat(payload["startDatetime"]).replace(
            tzinfo=None
        )
        assert offer.collectiveStock.endDatetime == datetime.fromisoformat(payload["startDatetime"]).replace(
            tzinfo=None
        )

    @time_machine.travel(time_travel_str)
    def test_post_offers_with_uai(self, public_client, payload, venue_provider, domain, institution, venue):
        payload["educationalInstitution"] = institution.institutionId
        del payload["educationalInstitutionId"]

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = public_client.post("/v2/collective/offers/", json=payload)

        assert response.status_code == 200

        offer = db.session.query(educational_models.CollectiveOffer).filter_by(id=response.json["id"]).one()
        assert offer.students == [educational_models.StudentLevels.COLLEGE4]
        assert offer.venueId == venue.id
        assert offer.name == payload["name"]
        assert offer.domains == [domain]
        assert offer.institutionId == institution.id
        assert offer.interventionArea == []
        assert offer.offerVenue == {
            "venueId": venue.id,
            "addressType": "offererVenue",
            "otherAddress": "",
        }
        assert offer.providerId == venue_provider.providerId
        assert offer.hasImage is True
        assert offer.isPublicApi
        assert (UPLOAD_FOLDER / offer._get_image_storage_id()).exists()

    @time_machine.travel(time_travel_str)
    def test_post_offers_offer_venue_offerer_venue(self, public_client, minimal_payload, venue):
        payload = {
            **minimal_payload,
            "offerVenue": {"addressType": "offererVenue", "otherAddress": "", "venueId": venue.id},
        }

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = public_client.post("/v2/collective/offers/", json=payload)

        offer = db.session.query(educational_models.CollectiveOffer).filter_by(id=response.json["id"]).one()
        assert response.status_code == 200
        assert offer.offerVenue == payload["offerVenue"]

        assert offer.offererAddressId == venue.offererAddressId
        assert offer.locationType == educational_models.CollectiveLocationType.ADDRESS
        assert offer.locationComment is None

    @time_machine.travel(time_travel_str)
    def test_post_offers_offer_venue_offerer_venue_other_venue(
        self, public_client, minimal_payload, venue_provider, venue
    ):
        other_venue = offerers_factories.VenueFactory(managingOfferer=venue.managingOfferer)
        other_venue.venueProviders.append(
            providers_models.VenueProvider(venue=other_venue, provider=venue_provider.provider)
        )
        db.session.flush()

        payload = {
            **minimal_payload,
            "offerVenue": {"addressType": "offererVenue", "otherAddress": "", "venueId": other_venue.id},
        }

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = public_client.post("/v2/collective/offers/", json=payload)

        offer = db.session.query(educational_models.CollectiveOffer).filter_by(id=response.json["id"]).one()
        assert response.status_code == 200
        assert offer.offerVenue == payload["offerVenue"]

        assert offer.offererAddressId == other_venue.offererAddressId
        assert offer.locationType == educational_models.CollectiveLocationType.ADDRESS
        assert offer.locationComment is None

    @time_machine.travel(time_travel_str)
    def test_post_offers_offer_venue_school(self, public_client, minimal_payload):
        payload = {**minimal_payload, "offerVenue": {"addressType": "school", "otherAddress": "", "venueId": None}}

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = public_client.post("/v2/collective/offers/", json=payload)

        offer = db.session.query(educational_models.CollectiveOffer).filter_by(id=response.json["id"]).one()
        assert response.status_code == 200
        assert offer.offerVenue == payload["offerVenue"]

        assert offer.offererAddressId is None
        assert offer.locationType == educational_models.CollectiveLocationType.SCHOOL
        assert offer.locationComment is None

    @time_machine.travel(time_travel_str)
    def test_post_offers_offer_venue_other(self, public_client, minimal_payload, venue):
        payload = {
            **minimal_payload,
            "offerVenue": {"addressType": "other", "otherAddress": "In Paris", "venueId": None},
        }

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = public_client.post("/v2/collective/offers/", json=payload)

        offer = db.session.query(educational_models.CollectiveOffer).filter_by(id=response.json["id"]).one()
        assert response.status_code == 200
        assert offer.offerVenue == payload["offerVenue"]

        assert offer.offererAddressId is None
        assert offer.locationType == educational_models.CollectiveLocationType.TO_BE_DEFINED
        assert offer.locationComment == "In Paris"

    @time_machine.travel(time_travel_str)
    def test_post_offers_with_uai_and_institution_id(self, public_client, payload, institution):
        payload["educationalInstitution"] = institution.institutionId
        payload["educationalInstitutionId"] = institution.id

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = public_client.post("/v2/collective/offers/", json=payload)

        assert response.status_code == 400
        assert "__root__" in response.json

    @time_machine.travel(time_travel_str)
    def test_invalid_api_key(self, client, payload):
        public_client = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY)
        response = public_client.post("/v2/collective/offers/", json=payload)
        assert response.status_code == 401

    @time_machine.travel(time_travel_str)
    def test_user_cannot_create_collective_offer(self, public_client, payload):
        with patch(
            educational_testing.PATCH_CAN_CREATE_OFFER_PATH,
            side_effect=educational_exceptions.CulturalPartnerNotFoundException,
        ):
            response = public_client.post("/v2/collective/offers/", json=payload)

        assert response.status_code == 403

    @time_machine.travel(time_travel_str)
    def test_bad_educational_institution(self, public_client, payload):
        payload["educationalInstitutionId"] = -1

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = public_client.post("/v2/collective/offers/", json=payload)

        assert response.status_code == 404

    @time_machine.travel(time_travel_str)
    def test_unlinked_venue_in_offer_venue(self, public_client, minimal_payload):
        other_venue = offerers_factories.VenueFactory()
        payload = {
            **minimal_payload,
            "offerVenue": {"addressType": "offererVenue", "otherAddress": "", "venueId": other_venue.id},
        }

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = public_client.post("/v2/collective/offers/", json=payload)

        assert response.status_code == 404
        assert response.json == {"venueId": ["Ce lieu n'à pas été trouvé."]}

    @time_machine.travel(time_travel_str)
    def test_venue_id_not_found_in_offer_venue(self, public_client, minimal_payload):
        payload = {**minimal_payload, "offerVenue": {"addressType": "offererVenue", "otherAddress": "", "venueId": -1}}

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = public_client.post("/v2/collective/offers/", json=payload)

        assert response.status_code == 404
        assert response.json == {"venueId": ["Ce lieu n'à pas été trouvé."]}

    @time_machine.travel(time_travel_str)
    def test_unlinked_venue(self, public_client, payload):
        payload["venueId"] = offerers_factories.VenueFactory().id

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = public_client.post("/v2/collective/offers/", json=payload)

        assert response.status_code == 404
        assert response.json == {"venueId": ["Ce lieu n'à pas été trouvé."]}

    @time_machine.travel(time_travel_str)
    def test_venue_id_not_found(self, public_client, payload):
        payload["venueId"] = 0

        response = public_client.post("/v2/collective/offers/", json=payload)
        assert response.status_code == 404
        assert response.json == {"venueId": ["Ce lieu n'à pas été trouvé."]}

    @time_machine.travel(time_travel_str)
    def test_invalid_image_size(self, public_client, payload):
        payload["imageFile"] = image_data.WRONG_IMAGE_SIZE

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = public_client.post("/v2/collective/offers/", json=payload)

        assert response.status_code == 400
        assert "imageFile" in response.json

    @time_machine.travel(time_travel_str)
    def test_invalid_image_type(self, public_client, payload):
        payload["imageFile"] = image_data.WRONG_IMAGE_TYPE

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = public_client.post("/v2/collective/offers/", json=payload)

        assert response.status_code == 400
        assert "imageFile" in response.json

    @time_machine.travel(time_travel_str)
    def test_should_raise_400_because_startDatetime_is_after_endDatetime(self, public_client, payload):
        start_datetime = datetime.now(timezone.utc) + timedelta(days=10)
        end_datetime = start_datetime - timedelta(days=1)
        payload["startDatetime"] = start_datetime.isoformat(timespec="seconds")
        payload["endDatetime"] = end_datetime.isoformat(timespec="seconds")

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = public_client.post("/v2/collective/offers/", json=payload)

        assert response.status_code == 400
        assert response.json == {"endDatetime": ["La date de fin de l'évènement ne peut précéder la date de début."]}

    @time_machine.travel(time_travel_str)
    def test_post_offers_institution_not_active(self, public_client, payload):
        institution = educational_factories.EducationalInstitutionFactory(isActive=False)
        payload["educationalInstitutionId"] = institution.id

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = public_client.post("/v2/collective/offers/", json=payload)

        assert response.status_code == 403

    @time_machine.travel(time_travel_str)
    def test_post_offers_invalid_domain(self, public_client, payload):
        payload["nationalProgramId"] = None
        payload["domains"] = [-1]

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = public_client.post("/v2/collective/offers/", json=payload)

        assert response.status_code == 404
        assert response.json == {"domains": ["Domaine scolaire non trouvé."]}

    @time_machine.travel(time_travel_str)
    def test_post_offers_unknown_national_program(self, public_client, payload):
        payload["nationalProgramId"] = -1

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = public_client.post("/v2/collective/offers/", json=payload)

        assert response.status_code == 404
        assert response.json == {"nationalProgramId": ["Dispositif national non trouvé."]}

    @time_machine.travel(time_travel_str)
    def test_national_program_not_linked_to_domains(self, public_client, payload):
        payload["nationalProgramId"] = educational_factories.NationalProgramFactory().id

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = public_client.post("/v2/collective/offers/", json=payload)

        assert response.status_code == 400
        assert response.json == {"nationalProgramId": ["Dispositif national non valide."]}

    @time_machine.travel(time_travel_str)
    def test_national_program_inactive(self, public_client, payload):
        payload["nationalProgramId"] = educational_factories.NationalProgramFactory(isActive=False).id

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = public_client.post("/v2/collective/offers/", json=payload)

        assert response.status_code == 400
        assert response.json == {"nationalProgramId": ["Dispositif national inactif."]}

    @time_machine.travel(time_travel_str)
    def test_invalid_offer_venue(self, public_client, payload, venue):
        payload["offerVenue"] = {
            "venueId": venue.id,
            "addressType": "other",
            "otherAddress": "",
        }

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = public_client.post("/v2/collective/offers/", json=payload)

        assert response.status_code == 404
        assert "offerVenue.otherAddress" in response.json

    @time_machine.travel(time_travel_str)
    def test_missing_formats(self, public_client, payload):
        del payload["formats"]

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = public_client.post("/v2/collective/offers/", json=payload)

        assert response.status_code == 400
        assert response.json == {"formats": ["field required"]}

    @time_machine.travel(time_travel_str)
    def test_description_invalid(self, public_client, payload):
        payload["description"] = "too_long" * 200

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = public_client.post("/v2/collective/offers/", json=payload)

        assert response.status_code == 400
        assert response.json == {"description": ["La description de l’offre doit faire au maximum 1500 caractères."]}

    @time_machine.travel(time_travel_str)
    def test_missing_start_datetime(self, public_client, payload):
        del payload["startDatetime"]

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = public_client.post("/v2/collective/offers/", json=payload)

        assert response.status_code == 400
        assert response.json == {"startDatetime": ["field required"]}

    @time_machine.travel(time_travel_str)
    def test_booking_limit_after_start(self, public_client, payload):
        payload["bookingLimitDatetime"] = (
            datetime.fromisoformat(payload["startDatetime"]) + timedelta(days=1)
        ).isoformat(timespec="seconds")

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = public_client.post("/v2/collective/offers/", json=payload)

        assert response.status_code == 400
        assert response.json == {
            "bookingLimitDatetime": [
                "La date limite de réservation ne peut être postérieure à la date de début de l'évènement"
            ]
        }

    @time_machine.travel(time_travel_str)
    def test_different_educational_years(self, public_client, minimal_payload):
        start = datetime.fromisoformat(minimal_payload["startDatetime"])
        end = start.replace(year=start.year + 1)
        educational_factories.create_educational_year(end)

        minimal_payload["endDatetime"] = end.isoformat()

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = public_client.post("/v2/collective/offers/", json=minimal_payload)

        assert response.status_code == 400
        assert response.json == {"global": ["Les dates de début et de fin ne sont pas sur la même année scolaire."]}

    @time_machine.travel(time_travel_str)
    def test_educational_year_missing_start(self, public_client, minimal_payload):
        start = datetime.fromisoformat(minimal_payload["startDatetime"])
        minimal_payload["startDatetime"] = start.replace(year=start.year + 1).isoformat()

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = public_client.post("/v2/collective/offers/", json=minimal_payload)

        assert response.status_code == 400
        assert response.json == {"startDatetime": ["Année scolaire manquante pour la date de début."]}

    @time_machine.travel(time_travel_str)
    def test_educational_year_missing_end(self, public_client, minimal_payload):
        start = datetime.fromisoformat(minimal_payload["startDatetime"])
        minimal_payload["endDatetime"] = start.replace(year=start.year + 1).isoformat()

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = public_client.post("/v2/collective/offers/", json=minimal_payload)

        assert response.status_code == 400
        assert response.json == {"endDatetime": ["Année scolaire manquante pour la date de fin."]}


@pytest.mark.usefixtures("db_session")
class CollectiveOffersPublicPostOfferMinimalTest:
    @time_machine.travel(time_travel_str)
    def test_mandatory_information_only(self, public_client, minimal_payload):
        self.assert_expected_offer_is_created(public_client, minimal_payload)

    @time_machine.travel(time_travel_str)
    def test_institution_instead_of_institution_id(self, public_client, minimal_payload, institution):
        del minimal_payload["educationalInstitutionId"]

        minimal_payload["name"] = "Some offer with minimal payload (institution)"
        minimal_payload["educationalInstitution"] = institution.institutionId

        self.assert_expected_offer_is_created(public_client, minimal_payload)

    @time_machine.travel(time_travel_str)
    def test_missing_field(self, public_client, minimal_payload):
        for key in minimal_payload:
            payload = {k: v for k, v in minimal_payload.items() if k != key}

            with patch("pcapi.core.educational.adage_backends.get_adage_offerer") as mock:
                mock.return_value = ["anything", "it does not matter"]
                response = public_client.post("/v2/collective/offers/", json=payload)

            assert response.status_code == 400
            assert key in response.json or "__root__" in response.json

    def assert_expected_offer_is_created(self, public_client, payload):
        with patch("pcapi.core.educational.adage_backends.get_adage_offerer") as mock:
            mock.return_value = ["anything", "it does not matter"]
            response = public_client.post("/v2/collective/offers/", json=payload)

        assert response.status_code == 200

        offer = db.session.query(educational_models.CollectiveOffer).filter_by(id=response.json["id"]).one()
        assert offer.name == payload["name"]
