from datetime import datetime
from datetime import timedelta
from unittest.mock import patch

import pytest

from pcapi.core.categories import subcategories
import pcapi.core.educational.exceptions as educational_exceptions
import pcapi.core.educational.factories as educational_factories
from pcapi.core.educational.models import CollectiveOfferTemplate
import pcapi.core.offerers.factories as offerers_factories


START = datetime.utcnow()
END = START + timedelta(days=90)


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


@pytest.fixture(name="payload")
def payload_fixture(venue, domains, offer_venue):
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
        "start": START.isoformat(),
        "end": END.isoformat(),
        "offerVenue": offer_venue,
        "domains": [domain.id for domain in domains],
        "subcategoryId": subcategories.SPECTACLE_REPRESENTATION.id,
        "venueId": venue.id,
    }


class Returns200Test:
    def test_create_collective_offer_template(self, pro_client, offerer, venue, payload, domains, offer_venue):
        national_program = educational_factories.NationalProgramFactory()

        # When
        data = {**payload, "nationalProgramId": national_program.id}

        with patch("pcapi.core.offerers.api.can_offerer_create_educational_offer"):
            response = pro_client.post("/collective/offers-template", json=data)

        # Then
        assert response.status_code == 201

        offer_id = response.json["id"]
        offer = CollectiveOfferTemplate.query.get(offer_id)

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
        assert offer.start == START
        assert offer.end == END

    def test_empty_intervention_area(self, pro_client, payload, venue):
        data = {
            **payload,
            "offerVenue": {"addressType": "offererVenue", "otherAddress": "", "venueId": venue.id},
            "interventionArea": [],
        }

        with patch("pcapi.core.offerers.api.can_offerer_create_educational_offer"):
            response = pro_client.post("/collective/offers-template", json=data)

        assert response.status_code == 201

    def test_without_start_end_dates(self, pro_client, payload):
        data = {**payload, "start": None, "end": None}

        with patch("pcapi.core.offerers.api.can_offerer_create_educational_offer"):
            response = pro_client.post("/collective/offers-template", json=data)

        assert response.status_code == 201

        offer = CollectiveOfferTemplate.query.get(response.json["id"])
        assert not offer.start
        assert not offer.end


class Returns403Test:
    def test_random_user(self, client, payload):
        # Given
        user = offerers_factories.UserOffererFactory().user

        # When
        with patch("pcapi.core.offerers.api.can_offerer_create_educational_offer"):
            response = client.with_session_auth(user.email).post("/collective/offers-template", json=payload)

        # Then
        assert response.status_code == 403
        assert CollectiveOfferTemplate.query.count() == 0

    def test_no_adage_offerer(self, pro_client, payload):
        # Given
        def raise_ac(*args, **kwargs):
            raise educational_exceptions.CulturalPartnerNotFoundException("pouet")

        # When
        with patch("pcapi.core.offerers.api.can_offerer_create_educational_offer", side_effect=raise_ac):
            response = pro_client.post("/collective/offers-template", json=payload)

        # Then
        assert response.status_code == 403
        assert CollectiveOfferTemplate.query.count() == 0


class Returns400Test:
    def test_missing_category(self, pro_client, payload):
        # When
        del payload["subcategoryId"]

        with patch("pcapi.core.offerers.api.can_offerer_create_educational_offer"):
            response = pro_client.post("/collective/offers-template", json=payload)

        # Then
        assert response.status_code == 400
        assert CollectiveOfferTemplate.query.count() == 0

    def test_unselectable_category(self, pro_client, payload):
        # When
        data = {**payload, "subcategoryId": subcategories.OEUVRE_ART.id}

        with patch("pcapi.core.offerers.api.can_offerer_create_educational_offer"):
            response = pro_client.post("/collective/offers-template", json=data)

        # Then
        assert response.status_code == 400
        assert CollectiveOfferTemplate.query.count() == 0

    def test_no_collective_category(self, pro_client, payload):
        # When
        data = {**payload, "subcategoryId": subcategories.SUPPORT_PHYSIQUE_FILM.id}

        with patch("pcapi.core.offerers.api.can_offerer_create_educational_offer"):
            response = pro_client.post("/collective/offers-template", json=data)

        # Then
        assert response.status_code == 400
        assert CollectiveOfferTemplate.query.count() == 0

    def test_empty_domains(self, pro_client, payload):
        # When
        data = {**payload, "domains": []}

        with patch("pcapi.core.offerers.api.can_offerer_create_educational_offer"):
            response = pro_client.post("/collective/offers-template", json=data)

        # Then
        assert response.status_code == 400
        assert CollectiveOfferTemplate.query.count() == 0

    def test_too_long_price_details(self, pro_client, payload):
        # When
        data = {**payload, "priceDetail": "a" * 1001}

        with patch("pcapi.core.offerers.api.can_offerer_create_educational_offer"):
            response = pro_client.post("/collective/offers-template", json=data)

        # Then
        assert response.status_code == 400
        assert CollectiveOfferTemplate.query.count() == 0


class Returns404Test:
    def test_unknown_domain(self, pro_client, payload):
        # When
        data = {**payload, "domains": [0]}

        with patch("pcapi.core.offerers.api.can_offerer_create_educational_offer"):
            response = pro_client.post("/collective/offers-template", json=data)

        # Then
        assert response.status_code == 404
        assert response.json == {"code": "EDUCATIONAL_DOMAIN_NOT_FOUND"}

    def test_unknown_national_program(self, pro_client, payload):
        # When
        data = {**payload, "nationalProgramId": -1}

        with patch("pcapi.core.offerers.api.can_offerer_create_educational_offer"):
            response = pro_client.post("/collective/offers-template", json=data)

        assert response.status_code == 400
        assert response.json == {"code": "COLLECTIVE_OFFER_NATIONAL_PROGRAM_NOT_FOUND"}
