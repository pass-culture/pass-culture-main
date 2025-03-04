from datetime import datetime
from datetime import timedelta
from unittest.mock import patch

import pytest

from pcapi.core.categories import subcategories
from pcapi.core.educational import exceptions as educational_exceptions
from pcapi.core.educational import factories as educational_factories
from pcapi.core.educational import models
from pcapi.core.educational import testing as educational_testing
from pcapi.core.offerers import factories as offerers_factories
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


@pytest.fixture(name="offer_venue")
def offer_venue_fixture(venue):
    return {
        "addressType": "school",
        "venueId": venue.id,
        "otherAddress": "17 rue aléatoire",
    }


@pytest.fixture(name="template_start", scope="module")
def template_start_fixture():
    return datetime.utcnow() + timedelta(days=1)


@pytest.fixture(name="template_end", scope="module")
def template_end_fixture():
    return datetime.utcnow() + timedelta(days=100)


@pytest.fixture(name="payload")
def payload_fixture(venue, domains, offer_venue, template_start, template_end):
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
        "offerVenue": offer_venue,
        "domains": [domain.id for domain in domains],
        "subcategoryId": subcategories.SPECTACLE_REPRESENTATION.id,
        "venueId": venue.id,
        "formats": [subcategories.EacFormat.CONCERT.value],
    }


class Returns200Test:
    def test_create_collective_offer_template(
        self,
        pro_client,
        payload,
        offerer,
        venue,
        offer_venue,
        domains,
        template_start,
        template_end,
        user,
    ):
        national_program = educational_factories.NationalProgramFactory()
        domains[0].nationalPrograms.append(national_program)

        # When
        data = {**payload, "nationalProgramId": national_program.id}

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = pro_client.post("/collective/offers-template", json=data)

        # Then
        assert response.status_code == 201

        offer_id = response.json["id"]
        offer = models.CollectiveOfferTemplate.query.get(offer_id)

        assert offer.bookingEmails == ["offer1@example.com", "offer2@example.com"]
        assert offer.subcategoryId == subcategories.SPECTACLE_REPRESENTATION.id
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
        assert offer.offerVenue == offer_venue
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

    def test_empty_email(self, pro_client, payload, venue):
        data = {
            **payload,
            "contactEmail": None,
        }

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = pro_client.post("/collective/offers-template", json=data)

        assert response.status_code == 201

        offer_id = response.json["id"]
        offer = models.CollectiveOfferTemplate.query.get(offer_id)

        assert offer.contactEmail is None
        assert offer.contactPhone == "01 99 00 25 68"

    def test_empty_intervention_area(self, pro_client, payload, venue):
        data = {
            **payload,
            "offerVenue": {"addressType": "offererVenue", "otherAddress": "", "venueId": venue.id},
            "interventionArea": [],
        }

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = pro_client.post("/collective/offers-template", json=data)

        assert response.status_code == 201

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
        now = datetime.utcnow()
        data = {**payload, "dates": {"start": format_into_utc_date(now), "end": format_into_utc_date(now)}}

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = pro_client.post("/collective/offers-template", json=data)

        assert response.status_code == 201
        offer = models.CollectiveOfferTemplate.query.filter_by(id=response.json["id"]).one()
        assert offer.dateRange.lower == now
        assert offer.dateRange.upper == now + timedelta(seconds=1)

    def test_offer_venue_offerer_venue(self, pro_client, payload, venue):
        data = {**payload, "offerVenue": {"addressType": "offererVenue", "otherAddress": "", "venueId": venue.id}}

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = pro_client.post("/collective/offers-template", json=data)

        assert response.status_code == 201
        offer = models.CollectiveOfferTemplate.query.filter_by(id=response.json["id"]).one()
        assert offer.offerVenue == data["offerVenue"]
        assert offer.interventionArea == []

        assert offer.offererAddressId == None
        assert offer.locationType == None
        assert offer.locationComment == None

    def test_offer_venue_school(self, pro_client, payload):
        data = {**payload, "offerVenue": {"addressType": "school", "otherAddress": "", "venueId": None}}

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = pro_client.post("/collective/offers-template", json=data)

        assert response.status_code == 201
        offer = models.CollectiveOfferTemplate.query.filter_by(id=response.json["id"]).one()
        assert offer.offerVenue == data["offerVenue"]
        assert len(offer.interventionArea) > 0

        assert offer.offererAddressId == None
        assert offer.locationType == None
        assert offer.locationComment == None

    def test_offer_venue_other(self, pro_client, payload):
        data = {**payload, "offerVenue": {"addressType": "other", "otherAddress": "In Paris", "venueId": None}}

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = pro_client.post("/collective/offers-template", json=data)

        assert response.status_code == 201
        offer = models.CollectiveOfferTemplate.query.filter_by(id=response.json["id"]).one()
        assert offer.offerVenue == data["offerVenue"]
        assert len(offer.interventionArea) > 0

        assert offer.offererAddressId == None
        assert offer.locationType == None
        assert offer.locationComment == None

    @pytest.mark.features(WIP_ENABLE_OFFER_ADDRESS_COLLECTIVE=True)
    def test_location_venue(self, pro_client, payload, venue):
        oa = venue.offererAddress
        data = {
            **payload,
            "offerVenue": None,
            "location": {
                "locationType": models.CollectiveLocationType.VENUE.value,
                "locationComment": None,
                "address": {
                    "isVenueAddress": True,
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
        offer = models.CollectiveOfferTemplate.query.filter_by(id=response.json["id"]).one()

        assert offer.offererAddressId == oa.id
        assert offer.locationType == models.CollectiveLocationType.VENUE
        assert offer.locationComment is None

        assert offer.offerVenue == {"addressType": "offererVenue", "otherAddress": "", "venueId": venue.id}

    @pytest.mark.features(WIP_ENABLE_OFFER_ADDRESS_COLLECTIVE=True)
    def test_location_school(self, pro_client, payload):
        data = {
            **payload,
            "offerVenue": None,
            "location": {
                "locationType": models.CollectiveLocationType.SCHOOL.value,
                "locationComment": None,
                "address": None,
            },
        }

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = pro_client.post("/collective/offers-template", json=data)

        assert response.status_code == 201
        offer = models.CollectiveOfferTemplate.query.filter_by(id=response.json["id"]).one()

        assert offer.offererAddressId is None
        assert offer.locationType == models.CollectiveLocationType.SCHOOL
        assert offer.locationComment is None

        assert offer.offerVenue == {"addressType": "school", "otherAddress": "", "venueId": None}

    @pytest.mark.features(WIP_ENABLE_OFFER_ADDRESS_COLLECTIVE=True)
    def test_location_address(self, pro_client, payload):
        data = {
            **payload,
            "offerVenue": None,
            "location": {
                "locationType": models.CollectiveLocationType.ADDRESS.value,
                "locationComment": None,
                "address": {
                    "isVenueAddress": False,
                    "isManualEdition": False,
                    "city": "Paris",
                    "label": "My address",
                    "latitude": "48.87171",
                    "longitude": "2.308289",
                    "postalCode": "75001",
                    "street": "3 Rue de Valois",
                },
            },
        }

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = pro_client.post("/collective/offers-template", json=data)

        assert response.status_code == 201
        offer = models.CollectiveOfferTemplate.query.filter_by(id=response.json["id"]).one()

        assert offer.offererAddress.label == "My address"
        assert offer.offererAddress.address.city == "Paris"
        assert offer.offererAddress.address.postalCode == "75001"
        assert offer.offererAddress.address.street == "3 Rue de Valois"
        assert offer.offererAddress.address.isManualEdition == False
        assert offer.locationType == models.CollectiveLocationType.ADDRESS
        assert offer.locationComment is None

        assert offer.offerVenue == {
            "addressType": "other",
            "otherAddress": "3 Rue de Valois 75001 Paris",
            "venueId": None,
        }

    @pytest.mark.features(WIP_ENABLE_OFFER_ADDRESS_COLLECTIVE=True)
    def test_location_to_be_defined(self, pro_client, payload):
        data = {
            **payload,
            "offerVenue": None,
            "location": {
                "locationType": models.CollectiveLocationType.TO_BE_DEFINED.value,
                "locationComment": "Right here",
                "address": None,
            },
        }

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = pro_client.post("/collective/offers-template", json=data)

        assert response.status_code == 201
        offer = models.CollectiveOfferTemplate.query.filter_by(id=response.json["id"]).one()

        assert offer.offererAddressId is None
        assert offer.locationType == models.CollectiveLocationType.TO_BE_DEFINED
        assert offer.locationComment == "Right here"

        assert offer.offerVenue == {"addressType": "other", "otherAddress": "Right here", "venueId": None}


class Returns403Test:
    def test_random_user(self, client, payload):
        user = offerers_factories.UserOffererFactory().user

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client.with_session_auth(user.email).post("/collective/offers-template", json=payload)

        assert response.status_code == 403
        assert models.CollectiveOfferTemplate.query.count() == 0

    def test_no_adage_offerer(self, pro_client, payload):
        def raise_ac(*args, **kwargs):
            raise educational_exceptions.CulturalPartnerNotFoundException("pouet")

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH, side_effect=raise_ac):
            response = pro_client.post("/collective/offers-template", json=payload)

        assert response.status_code == 403
        assert models.CollectiveOfferTemplate.query.count() == 0

    def test_offerer_address_venue_not_allowed(self, pro_client, payload):
        venue = offerers_factories.VenueFactory()
        data = {**payload, "offerVenue": {"addressType": "offererVenue", "otherAddress": "", "venueId": venue.id}}

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = pro_client.post("/collective/offers-template", json=data)

        assert response.status_code == 403
        assert response.json == {
            "global": ["Vous n'avez pas les droits d'accès suffisants pour accéder à cette information."]
        }


class Returns400Test:
    def test_unselectable_category(self, pro_client, payload):
        data = {**payload, "subcategoryId": subcategories.OEUVRE_ART.id}

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = pro_client.post("/collective/offers-template", json=data)

        assert response.status_code == 400
        assert response.json == {
            "subcategory": ["Une offre ne peut être créée ou éditée en utilisant cette sous-catégorie"]
        }

        assert models.CollectiveOfferTemplate.query.count() == 0

    def test_no_collective_category(self, pro_client, payload):
        data = {**payload, "subcategoryId": subcategories.SUPPORT_PHYSIQUE_FILM.id}

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = pro_client.post("/collective/offers-template", json=data)

        assert response.status_code == 400
        assert response.json == {"offer": ["Cette catégorie d'offre n'est pas éligible aux offres éducationnelles"]}

        assert models.CollectiveOfferTemplate.query.count() == 0

    def test_empty_domains(self, pro_client, payload):
        data = {**payload, "domains": []}

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = pro_client.post("/collective/offers-template", json=data)

        assert response.status_code == 400
        assert response.json == {"domains": ["domains must have at least one value"]}

        assert models.CollectiveOfferTemplate.query.count() == 0

    def test_too_long_price_details(self, pro_client, payload):
        data = {**payload, "priceDetail": "a" * 1001}

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = pro_client.post("/collective/offers-template", json=data)

        assert response.status_code == 400
        assert response.json == {"priceDetail": ["ensure this value has at most 1000 characters"]}

        assert models.CollectiveOfferTemplate.query.count() == 0

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
        assert response.json == {"code": "COLLECTIVE_OFFER_CONTACT_NOT_SET"}

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
        assert response.json == {"code": "COLLECTIVE_OFFER_URL_AND_FORM_BOTH_SET"}

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

    @pytest.mark.features(WIP_ENABLE_OFFER_ADDRESS_COLLECTIVE=True)
    def test_cannot_receive_offer_venue(self, pro_client, payload):
        data = {
            **payload,
            "location": {
                "locationType": models.CollectiveLocationType.SCHOOL.value,
                "locationComment": None,
                "address": None,
            },
        }
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = pro_client.post("/collective/offers-template", json=data)

        assert response.status_code == 400
        assert response.json == {"offerVenue": ["Cannot receive offerVenue, use location instead"]}
        assert models.CollectiveOfferTemplate.query.count() == 0

    @pytest.mark.features(WIP_ENABLE_OFFER_ADDRESS_COLLECTIVE=True)
    def test_must_receive_location(self, pro_client, payload):
        data = {**payload, "offerVenue": None, "location": None}
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = pro_client.post("/collective/offers-template", json=data)

        assert response.status_code == 400
        assert response.json == {"location": ["location must be provided"]}
        assert models.CollectiveOfferTemplate.query.count() == 0

    @pytest.mark.features(WIP_ENABLE_OFFER_ADDRESS_COLLECTIVE=False)
    def test_cannot_receive_location(self, pro_client, payload):
        data = {
            **payload,
            "location": {
                "locationType": models.CollectiveLocationType.SCHOOL.value,
                "locationComment": None,
                "address": None,
            },
        }
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = pro_client.post("/collective/offers-template", json=data)

        assert response.status_code == 400
        assert response.json == {"location": ["Cannot receive location, use offerVenue instead"]}
        assert models.CollectiveOfferTemplate.query.count() == 0

    @pytest.mark.features(WIP_ENABLE_OFFER_ADDRESS_COLLECTIVE=False)
    def test_must_receive_offer_venue(self, pro_client, payload):
        data = {**payload, "offerVenue": None, "location": None}
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = pro_client.post("/collective/offers-template", json=data)

        assert response.status_code == 400
        assert response.json == {"offerVenue": ["offerVenue must be provided"]}
        assert models.CollectiveOfferTemplate.query.count() == 0


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
        one_week_ago = datetime.utcnow() - timedelta(days=7)
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

    def test_unknown_venue_in_offer_venue(self, pro_client, payload):
        data = {**payload, "offerVenue": {"addressType": "offererVenue", "otherAddress": "", "venueId": -1}}

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = pro_client.post("/collective/offers-template", json=data)

        assert response.status_code == 404
        assert response.json == {"venueId": "The venue does not exist."}
