from datetime import timedelta
from unittest.mock import patch

import pytest

from pcapi.core.categories.models import EacFormat
from pcapi.core.educational import exceptions as educational_exceptions
from pcapi.core.educational import factories as educational_factories
from pcapi.core.educational import models
from pcapi.core.educational import testing as educational_testing
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offerers import models as offerers_models
from pcapi.models import db
from pcapi.utils import date as date_utils
from pcapi.utils.date import format_into_utc_date


pytestmark = pytest.mark.usefixtures("db_session")


@pytest.fixture(name="venue")
def venue_fixture():
    return offerers_factories.VenueFactory()


@pytest.fixture(name="user_offerer")
def user_offerer_fixture(venue):
    return offerers_factories.UserOffererFactory(offerer=venue.managingOfferer)


@pytest.fixture(name="user")
def user_fixture(user_offerer):
    return user_offerer.user


@pytest.fixture(name="offerer")
def offerer_fixture(user_offerer):
    return user_offerer.offerer


@pytest.fixture(name="pro_client")
def pro_client_fixture(client, user):
    return client.with_session_auth(user.email)


@pytest.fixture(name="domains")
def domains_fixture():
    return [educational_factories.EducationalDomainFactory(), educational_factories.EducationalDomainFactory()]


@pytest.fixture(name="template_start", scope="module")
def template_start_fixture():
    return date_utils.get_naive_utc_now() + timedelta(days=1)


@pytest.fixture(name="template_end", scope="module")
def template_end_fixture():
    return date_utils.get_naive_utc_now() + timedelta(days=100)


@pytest.fixture(name="payload")
def payload_fixture(venue, domains, template_start, template_end):
    return {
        "description": "Ma super description",
        "bookingEmails": ["offer1@example.com", "offer2@example.com"],
        "durationMinutes": 60,
        "name": "La pièce de théâtre",
        "contactEmail": "pouet@example.com",
        "contactPhone": "01 99 00 25 68",
        "students": ["Lycée - Seconde", "Lycée - Première"],
        "audioDisabilityCompliant": False,
        "mentalDisabilityCompliant": True,
        "motorDisabilityCompliant": False,
        "visualDisabilityCompliant": False,
        "interventionArea": ["75", "92", "93"],
        "templateId": None,
        "priceDetail": "Le détail ici",
        "dates": {"start": template_start.isoformat(), "end": template_end.isoformat()},
        "location": {
            "locationType": models.CollectiveLocationType.SCHOOL.value,
            "locationComment": None,
            "location": None,
        },
        "domains": [domain.id for domain in domains],
        "venueId": venue.id,
        "formats": [EacFormat.CONCERT.value],
    }


class Returns200Test:
    def test_create_collective_offer_template(
        self,
        pro_client,
        payload,
        offerer,
        venue,
        domains,
        template_start,
        template_end,
        user,
    ):
        national_program = educational_factories.NationalProgramFactory()
        domains[0].nationalPrograms.append(national_program)

        data = {**payload, "nationalProgramId": national_program.id}

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = pro_client.post("/collective/offers-template", json=data)

        assert response.status_code == 201

        offer_id = response.json["id"]
        offer = db.session.get(models.CollectiveOfferTemplate, offer_id)

        assert offer.bookingEmails == ["offer1@example.com", "offer2@example.com"]
        assert offer.venue == venue
        assert offer.durationMinutes == 60
        assert offer.venue.managingOffererId == offerer.id
        assert offer.motorDisabilityCompliant is False
        assert offer.visualDisabilityCompliant is False
        assert offer.audioDisabilityCompliant is False
        assert offer.mentalDisabilityCompliant is True
        assert offer.mentalDisabilityCompliant is True
        assert offer.contactEmail == "pouet@example.com"
        assert offer.contactPhone == "01 99 00 25 68"
        assert offer.interventionArea == ["75", "92", "93"]
        assert len(offer.students) == 2
        assert offer.students[0].value == "Lycée - Seconde"
        assert offer.students[1].value == "Lycée - Première"
        assert len(offer.domains) == 2
        assert set(offer.domains) == set(domains)
        assert offer.description == "Ma super description"
        assert offer.priceDetail == "Le détail ici"
        assert offer.nationalProgramId == national_program.id
        assert offer.start == template_start
        assert offer.end == template_end
        assert offer.author == user
        assert offer.formats == [EacFormat.CONCERT]

    def test_empty_email(self, pro_client, payload, venue):
        data = {
            **payload,
            "contactEmail": None,
        }

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = pro_client.post("/collective/offers-template", json=data)

        assert response.status_code == 201

        offer_id = response.json["id"]
        offer = db.session.get(models.CollectiveOfferTemplate, offer_id)

        assert offer.contactEmail is None
        assert offer.contactPhone == "01 99 00 25 68"

    def test_with_tz_aware_dates(self, pro_client, payload, template_start, template_end):
        data = {
            **payload,
            "dates": {
                "start": format_into_utc_date(template_start),
                "end": format_into_utc_date(template_end),
            },
        }

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = pro_client.post("/collective/offers-template", json=data)

        assert response.status_code == 201

    def test_with_start_and_end_equal(self, pro_client, payload):
        now = date_utils.get_naive_utc_now()
        data = {**payload, "dates": {"start": format_into_utc_date(now), "end": format_into_utc_date(now)}}

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = pro_client.post("/collective/offers-template", json=data)

        assert response.status_code == 201
        offer = db.session.query(models.CollectiveOfferTemplate).filter_by(id=response.json["id"]).one()
        assert offer.dateRange.lower == now
        assert offer.dateRange.upper == now + timedelta(seconds=1)

    def test_location_address_venue(self, pro_client, payload, venue):
        oa = venue.offererAddress
        data = {
            **payload,
            "interventionArea": None,
            "location": {
                "locationType": models.CollectiveLocationType.ADDRESS.value,
                "locationComment": None,
                "location": {
                    "isVenueLocation": True,
                    "isManualEdition": False,
                    "city": oa.address.city,
                    "latitude": oa.address.latitude,
                    "longitude": oa.address.longitude,
                    "postalCode": oa.address.postalCode,
                    "street": oa.address.street,
                },
            },
        }

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = pro_client.post("/collective/offers-template", json=data)

        assert response.status_code == 201
        offer = db.session.query(models.CollectiveOfferTemplate).filter_by(id=response.json["id"]).one()

        assert offer.offererAddress.type != offerers_models.LocationType.VENUE_LOCATION
        assert offer.offererAddress.addressId == oa.addressId
        assert offer.locationType == models.CollectiveLocationType.ADDRESS
        assert offer.locationComment is None

    def test_location_school(self, pro_client, payload):
        data = {
            **payload,
            "location": {
                "locationType": models.CollectiveLocationType.SCHOOL.value,
                "locationComment": None,
                "location": None,
            },
        }

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = pro_client.post("/collective/offers-template", json=data)

        assert response.status_code == 201
        offer = db.session.query(models.CollectiveOfferTemplate).filter_by(id=response.json["id"]).one()

        assert offer.offererAddressId is None
        assert offer.locationType == models.CollectiveLocationType.SCHOOL
        assert offer.locationComment is None

    def test_location_address(self, pro_client, payload):
        data = {
            **payload,
            "interventionArea": None,
            "location": {
                "locationType": models.CollectiveLocationType.ADDRESS.value,
                "locationComment": None,
                "location": educational_testing.ADDRESS_DICT,
            },
        }

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = pro_client.post("/collective/offers-template", json=data)

        assert response.status_code == 201
        offer = db.session.query(models.CollectiveOfferTemplate).filter_by(id=response.json["id"]).one()

        assert offer.offererAddress.label == "My address"
        assert offer.offererAddress.address.city == "Paris"
        assert offer.offererAddress.address.postalCode == "75001"
        assert offer.offererAddress.address.street == "3 Rue de Valois"
        assert offer.offererAddress.address.isManualEdition == False
        assert offer.locationType == models.CollectiveLocationType.ADDRESS
        assert offer.locationComment is None

    def test_location_venue_address(self, pro_client, venue, payload):
        data = {
            **payload,
            "interventionArea": None,
            "location": {
                "locationType": models.CollectiveLocationType.ADDRESS.value,
                "locationComment": None,
                "location": {
                    "banId": venue.offererAddress.address.banId,
                    "isVenueLocation": True,
                    "isManualEdition": venue.offererAddress.address.isManualEdition,
                    "inseeCode": venue.offererAddress.address.inseeCode,
                    "city": venue.offererAddress.address.city,
                    "label": "My address",
                    "latitude": str(venue.offererAddress.address.latitude),
                    "longitude": str(venue.offererAddress.address.longitude),
                    "postalCode": venue.offererAddress.address.postalCode,
                    "street": venue.offererAddress.address.street,
                },
            },
        }

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = pro_client.post("/collective/offers-template", json=data)

        assert response.status_code == 201
        offer = db.session.query(models.CollectiveOfferTemplate).filter_by(id=response.json["id"]).one()

        assert offer.offererAddress != venue.offererAddress
        assert offer.offererAddress.type is None  # TODO: soon to be OFFER_LOCATION
        assert offer.offererAddress.label == venue.common_name
        assert offer.offererAddress.address == venue.offererAddress.address
        assert offer.locationType == models.CollectiveLocationType.ADDRESS
        assert offer.locationComment is None

    def test_location_to_be_defined(self, pro_client, payload):
        data = {
            **payload,
            "location": {
                "locationType": models.CollectiveLocationType.TO_BE_DEFINED.value,
                "locationComment": "Right here",
                "location": None,
            },
        }

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = pro_client.post("/collective/offers-template", json=data)

        assert response.status_code == 201
        offer = db.session.query(models.CollectiveOfferTemplate).filter_by(id=response.json["id"]).one()

        assert offer.offererAddressId is None
        assert offer.locationType == models.CollectiveLocationType.TO_BE_DEFINED
        assert offer.locationComment == "Right here"


class Returns403Test:
    def test_random_user(self, client, payload):
        user = offerers_factories.UserOffererFactory().user

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client.with_session_auth(user.email).post("/collective/offers-template", json=payload)

        assert response.status_code == 403
        assert db.session.query(models.CollectiveOfferTemplate).count() == 0

    def test_no_adage_offerer(self, pro_client, payload):
        def raise_ac(*args, **kwargs):
            raise educational_exceptions.CulturalPartnerNotFoundException("pouet")

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH, side_effect=raise_ac):
            response = pro_client.post("/collective/offers-template", json=payload)

        assert response.status_code == 403
        assert db.session.query(models.CollectiveOfferTemplate).count() == 0


class Returns400Test:
    def test_empty_formats(self, pro_client, payload):
        data = {**payload, "formats": []}
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = pro_client.post("/collective/offers-template", json=data)

        assert response.status_code == 400
        assert response.json == {"formats": ["formats must have at least one value"]}
        assert db.session.query(models.CollectiveOffer).count() == 0

    def test_empty_domains(self, pro_client, payload):
        data = {**payload, "domains": []}

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = pro_client.post("/collective/offers-template", json=data)

        assert response.status_code == 400
        assert response.json == {"domains": ["domains must have at least one value"]}

        assert db.session.query(models.CollectiveOfferTemplate).count() == 0

    def test_too_long_price_details(self, pro_client, payload):
        data = {**payload, "priceDetail": "a" * 1001}

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = pro_client.post("/collective/offers-template", json=data)

        assert response.status_code == 400
        assert response.json == {"priceDetail": ["ensure this value has at most 1000 characters"]}

        assert db.session.query(models.CollectiveOfferTemplate).count() == 0

    def test_empty_contact(self, pro_client, payload, venue):
        data = {
            **payload,
            "contactEmail": None,
            "contactPhone": None,
            "contactUrl": None,
            "contactForm": None,
        }

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = pro_client.post("/collective/offers-template", json=data)

        assert response.status_code == 400
        assert response.json == {"contact[all]": "All contact information are null"}

    def test_both_contact_form_and_url(self, pro_client, payload, venue):
        data = {
            **payload,
            "contactEmail": None,
            "contactPhone": None,
            "contactUrl": "http://localhost/dir/something.html",
            "contactForm": "form",
        }

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = pro_client.post("/collective/offers-template", json=data)

        assert response.status_code == 400
        assert response.json == {"contact[url,form]": "Url and form can not both be used"}

    def test_booking_emails_invalid(self, pro_client, payload):
        data = {**payload, "bookingEmails": ["test@testmail.com", "test@test", "test"]}
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = pro_client.post("/collective/offers-template", json=data)

        assert response.status_code == 400
        assert response.json == {
            "bookingEmails.1": ["Le format d'email est incorrect."],
            "bookingEmails.2": ["Le format d'email est incorrect."],
        }

    def test_description_invalid(self, pro_client, payload):
        data = {**payload, "description": "too_long" * 200}
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = pro_client.post("/collective/offers-template", json=data)

        assert response.status_code == 400
        assert response.json == {"description": ["La description de l’offre doit faire au maximum 1500 caractères."]}

    def test_national_program_inactive(self, pro_client, payload, domains):
        national_program = educational_factories.NationalProgramFactory(isActive=False)
        domains[0].nationalPrograms.append(national_program)

        data = {**payload, "nationalProgramId": national_program.id}
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = pro_client.post("/collective/offers-template", json=data)

        assert response.status_code == 400
        assert response.json == {"code": "COLLECTIVE_OFFER_NATIONAL_PROGRAM_INACTIVE"}

    def test_national_program_invalid(self, pro_client, payload):
        national_program = educational_factories.NationalProgramFactory()

        data = {**payload, "nationalProgramId": national_program.id}
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = pro_client.post("/collective/offers-template", json=data)

        assert response.status_code == 400
        assert response.json == {"code": "COLLECTIVE_OFFER_NATIONAL_PROGRAM_INVALID"}

    def test_must_receive_location(self, pro_client, payload):
        data = {**payload, "location": None}
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = pro_client.post("/collective/offers-template", json=data)

        assert response.status_code == 400
        assert response.json == {"location": ["Ce champ ne peut pas être nul"]}
        assert db.session.query(models.CollectiveOfferTemplate).count() == 0

    def test_create_collective_offer_template_with_location_type_school_must_not_receive_location_comment(
        self, pro_client, payload
    ):
        data = {
            **payload,
            "location": {
                "locationType": models.CollectiveLocationType.SCHOOL.value,
                "locationComment": "FORBIDDEN COMMENT",
                "location": None,
            },
        }

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = pro_client.post("/collective/offers-template", json=data)

        assert response.status_code == 400
        assert response.json == {
            "location.locationComment": ["locationComment is not allowed for the provided locationType"]
        }
        assert db.session.query(models.CollectiveOfferTemplate).count() == 0

    def test_create_collective_offer_template_with_location_type_address_must_not_receive_location_comment(
        self, pro_client, payload
    ):
        data = {
            **payload,
            "location": {
                "locationType": models.CollectiveLocationType.ADDRESS.value,
                "locationComment": "FORBIDDEN COMMENT",
                "location": educational_testing.ADDRESS_DICT,
            },
        }

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = pro_client.post("/collective/offers-template", json=data)

        assert response.status_code == 400
        assert response.json == {
            "location.locationComment": ["locationComment is not allowed for the provided locationType"]
        }
        assert db.session.query(models.CollectiveOfferTemplate).count() == 0

    def test_create_collective_offer_template_with_location_type_school_must_provide_intervention_area(
        self, pro_client, payload
    ):
        data = {
            **payload,
            "interventionArea": None,
            "location": {
                "locationType": models.CollectiveLocationType.SCHOOL.value,
                "locationComment": None,
                "location": None,
            },
        }

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = pro_client.post("/collective/offers-template", json=data)

        assert response.status_code == 400
        assert response.json == {"interventionArea": ["intervention_area is required and must not be empty"]}
        assert db.session.query(models.CollectiveOfferTemplate).count() == 0

    def test_create_collective_offer_template_with_location_type_school_must_provide_correct_intervention_area(
        self, pro_client, payload
    ):
        data = {
            **payload,
            "interventionArea": ["75", "1234"],
            "location": {
                "locationType": models.CollectiveLocationType.SCHOOL.value,
                "locationComment": None,
                "location": None,
            },
        }

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = pro_client.post("/collective/offers-template", json=data)

        assert response.status_code == 400
        assert response.json == {"interventionArea": ["intervention_area must be a valid area"]}
        assert db.session.query(models.CollectiveOfferTemplate).count() == 0

    def test_create_collective_offer_template_with_location_type_address_must_provide_address(
        self, pro_client, payload
    ):
        data = {
            **payload,
            "location": {
                "locationType": models.CollectiveLocationType.ADDRESS.value,
                "locationComment": None,
                "location": None,
            },
        }

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = pro_client.post("/collective/offers-template", json=data)

        assert response.status_code == 400
        assert response.json == {"location.location": ["address is required for the provided locationType"]}
        assert db.session.query(models.CollectiveOfferTemplate).count() == 0

    @pytest.mark.parametrize(
        "location_type",
        (
            models.CollectiveLocationType.TO_BE_DEFINED.value,
            models.CollectiveLocationType.SCHOOL.value,
        ),
    )
    def test_create_collective_offer_template_with_location_type_when_address_must_not_be_provided(
        self, pro_client, payload, location_type
    ):
        venue = offerers_factories.VenueFactory()
        offerers_factories.UserOffererFactory(offerer=venue.managingOfferer, user__email="user@example.com")

        data = {
            **payload,
            "location": {
                "locationType": location_type,
                "locationComment": None,
                "location": educational_testing.ADDRESS_DICT,
            },
        }

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = pro_client.post("/collective/offers-template", json=data)

        assert response.status_code == 400
        assert response.json == {"location.location": ["address is not allowed for the provided locationType"]}
        assert db.session.query(models.CollectiveOfferTemplate).count() == 0


class InvalidDatesTest:
    def test_missing_start(self, pro_client, payload, template_end):
        response = self.send_request(pro_client, payload, {"end": template_end.isoformat()})
        assert response.status_code == 400
        assert "dates.start" in response.json

    def test_start_is_null(self, pro_client, payload, template_end):
        response = self.send_request(pro_client, payload, {"start": None, "end": template_end.isoformat()})
        assert response.status_code == 400
        assert "dates.start" in response.json

    def test_start_is_in_the_past(self, pro_client, payload, template_end):
        one_week_ago = date_utils.get_naive_utc_now() - timedelta(days=7)
        dates_extra = {"start": one_week_ago.isoformat(), "end": template_end.isoformat()}

        response = self.send_request(pro_client, payload, dates_extra)
        assert response.status_code == 400
        assert "dates.start" in response.json

    def test_start_is_after_end(self, pro_client, payload, template_end):
        dates_extra = {"start": (template_end + timedelta(days=1)).isoformat(), "end": template_end.isoformat()}
        response = self.send_request(pro_client, payload, dates_extra)
        assert response.status_code == 400
        assert "dates.__root__" in response.json

    def test_missing_end(self, pro_client, payload, template_start):
        response = self.send_request(pro_client, payload, {"start": template_start.isoformat()})
        assert response.status_code == 400
        assert "dates.end" in response.json

    def test_end_is_null(self, pro_client, payload, template_start):
        response = self.send_request(pro_client, payload, {"start": template_start.isoformat(), "end": None})
        assert response.status_code == 400
        assert "dates.end" in response.json

    def send_request(self, pro_client, payload, dates_extra):
        data = {**payload, "dates": {**dates_extra}}
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            return pro_client.post("/collective/offers-template", json=data)


class Returns404Test:
    def test_unknown_domain(self, pro_client, payload):
        data = {**payload, "domains": [0]}

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = pro_client.post("/collective/offers-template", json=data)

        assert response.status_code == 404
        assert response.json == {"code": "EDUCATIONAL_DOMAIN_NOT_FOUND"}

    def test_unknown_national_program(self, pro_client, payload):
        data = {**payload, "nationalProgramId": -1}

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = pro_client.post("/collective/offers-template", json=data)

        assert response.status_code == 400
        assert response.json == {"code": "COLLECTIVE_OFFER_NATIONAL_PROGRAM_NOT_FOUND"}

    def test_unknown_venue(self, pro_client, payload):
        data = {**payload, "venueId": -1}

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = pro_client.post("/collective/offers-template", json=data)

        assert response.status_code == 404
