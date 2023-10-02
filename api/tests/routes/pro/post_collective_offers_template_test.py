from datetime import datetime
from datetime import timedelta
from unittest.mock import patch

import pytest

from pcapi.core.categories import subcategories
import pcapi.core.educational.exceptions as educational_exceptions
import pcapi.core.educational.factories as educational_factories
import pcapi.core.educational.models as educational_models
from pcapi.core.educational.models import CollectiveOfferTemplate
import pcapi.core.offerers.factories as offerers_factories


pytestmark = pytest.mark.usefixtures("db_session")


PATCH_CAN_CREATE_OFFER_PATH = "pcapi.core.offerers.api.can_offerer_create_educational_offer"


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


@pytest.fixture(name="payload")
def payload_fixture(venue, domains, offer_venue, template_start):
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
        "dates": [{"start": template_start.isoformat()}],
        "offerVenue": offer_venue,
        "domains": [domain.id for domain in domains],
        "subcategoryId": subcategories.SPECTACLE_REPRESENTATION.id,
        "venueId": venue.id,
    }


class Returns200Test:
    def test_create_collective_offer_template(
        self, pro_client, payload, offerer, venue, offer_venue, domains, template_start
    ):
        national_program = educational_factories.NationalProgramFactory()

        # When
        data = {
            **payload,
            "nationalProgramId": national_program.id,
            "dates": [{"start": template_start.isoformat()}],
        }

        with patch(PATCH_CAN_CREATE_OFFER_PATH):
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

        assert offer.startEndDates

        start_end_dates = offer.startEndDates

        assert len(start_end_dates) == 1
        assert start_end_dates[0].start == template_start
        assert not start_end_dates[0].end

    def test_empty_intervention_area(self, pro_client, payload, venue):
        data = {
            **payload,
            "offerVenue": {"addressType": "offererVenue", "otherAddress": "", "venueId": venue.id},
            "interventionArea": [],
        }

        with patch(PATCH_CAN_CREATE_OFFER_PATH):
            response = pro_client.post("/collective/offers-template", json=data)

        assert response.status_code == 201


class Returns403Test:
    def test_random_user(self, client, payload):
        user = offerers_factories.UserOffererFactory().user

        with patch(PATCH_CAN_CREATE_OFFER_PATH):
            response = client.with_session_auth(user.email).post("/collective/offers-template", json=payload)

        assert response.status_code == 403
        assert CollectiveOfferTemplate.query.count() == 0

    def test_no_adage_offerer(self, pro_client, payload):
        def raise_ac(*args, **kwargs):
            raise educational_exceptions.CulturalPartnerNotFoundException("pouet")

        with patch(PATCH_CAN_CREATE_OFFER_PATH, side_effect=raise_ac):
            response = pro_client.post("/collective/offers-template", json=payload)

        assert response.status_code == 403
        assert CollectiveOfferTemplate.query.count() == 0


class Returns400Test:
    def test_missing_category(self, pro_client, payload):
        del payload["subcategoryId"]

        with patch(PATCH_CAN_CREATE_OFFER_PATH):
            response = pro_client.post("/collective/offers-template", json=payload)

        assert response.status_code == 400
        assert response.json == {"subcategoryId": ["Ce champ est obligatoire"]}

        assert CollectiveOfferTemplate.query.count() == 0

    def test_unselectable_category(self, pro_client, payload):
        data = {**payload, "subcategoryId": subcategories.OEUVRE_ART.id}

        with patch(PATCH_CAN_CREATE_OFFER_PATH):
            response = pro_client.post("/collective/offers-template", json=data)

        assert response.status_code == 400
        assert response.json == {
            "subcategory": ["Une offre ne peut être créée ou éditée en utilisant cette sous-catégorie"]
        }

        assert CollectiveOfferTemplate.query.count() == 0

    def test_no_collective_category(self, pro_client, payload):
        data = {**payload, "subcategoryId": subcategories.SUPPORT_PHYSIQUE_FILM.id}

        with patch(PATCH_CAN_CREATE_OFFER_PATH):
            response = pro_client.post("/collective/offers-template", json=data)

        assert response.status_code == 400
        assert response.json == {"offer": ["Cette catégorie d'offre n'est pas éligible aux offres éducationnelles"]}

        assert CollectiveOfferTemplate.query.count() == 0

    def test_empty_domains(self, pro_client, payload):
        data = {**payload, "domains": []}

        with patch(PATCH_CAN_CREATE_OFFER_PATH):
            response = pro_client.post("/collective/offers-template", json=data)

        assert response.status_code == 400
        assert response.json == {"__root__": ["domains must have at least one value"]}

        assert CollectiveOfferTemplate.query.count() == 0

    def test_too_long_price_details(self, pro_client, payload):
        data = {**payload, "priceDetail": "a" * 1001}

        with patch(PATCH_CAN_CREATE_OFFER_PATH):
            response = pro_client.post("/collective/offers-template", json=data)

        assert response.status_code == 400
        assert response.json == {"priceDetail": ["ensure this value has at most 1000 characters"]}

        assert CollectiveOfferTemplate.query.count() == 0

    def test_cannot_set_too_many_start_end_dates(self, pro_client, payload):
        start = datetime.utcnow() + timedelta(days=1)
        limit = educational_models.TemplateStartEndDates.MAX_DATES_PER_TEMPLATE
        dates = [_build_start_end_dates_from(start, n) for n in range(limit + 1)]

        data = {**payload, "dates": dates}

        with patch(PATCH_CAN_CREATE_OFFER_PATH):
            response = pro_client.post("/collective/offers-template", json=data)

        assert response.status_code == 400
        assert response.json == {"dates": [f"Une offre vitrine ne peut avoir plus de {limit} dates"]}
        assert CollectiveOfferTemplate.query.count() == 0


class Returns404Test:
    def test_unknown_domain(self, pro_client, payload):
        data = {**payload, "domains": [0]}

        with patch(PATCH_CAN_CREATE_OFFER_PATH):
            response = pro_client.post("/collective/offers-template", json=data)

        assert response.status_code == 404
        assert response.json == {"code": "EDUCATIONAL_DOMAIN_NOT_FOUND"}

    def test_unknown_national_program(self, pro_client, payload):
        data = {**payload, "nationalProgramId": -1}

        with patch(PATCH_CAN_CREATE_OFFER_PATH):
            response = pro_client.post("/collective/offers-template", json=data)

        assert response.status_code == 400
        assert response.json == {"code": "COLLECTIVE_OFFER_NATIONAL_PROGRAM_NOT_FOUND"}


def _build_start_end_dates_from(start: datetime, offset: int) -> dict[str, str]:
    return {
        "start": (start + timedelta(days=offset)).isoformat(),
        "end": (start + timedelta(days=offset + 1)).isoformat(),
    }
