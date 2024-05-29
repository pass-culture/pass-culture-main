from datetime import datetime
from datetime import timedelta
from unittest.mock import patch

import pytest

from pcapi.core.categories import subcategories_v2 as subcategories
import pcapi.core.educational.exceptions as educational_exceptions
import pcapi.core.educational.factories as educational_factories
from pcapi.core.educational.models import CollectiveOfferTemplate
import pcapi.core.offerers.factories as offerers_factories
from pcapi.utils.date import format_into_utc_date


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

        # When
        data = {**payload, "nationalProgramId": national_program.id}

        with patch(PATCH_CAN_CREATE_OFFER_PATH):
            response = pro_client.post("/collective/offers-template", json=data)

        # Then
        assert response.status_code == 201

        offer_id = response.json["id"]
        offer = CollectiveOfferTemplate.query.filter_by(id=offer_id).one()

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

        with patch(PATCH_CAN_CREATE_OFFER_PATH):
            response = pro_client.post("/collective/offers-template", json=data)

        assert response.status_code == 201

        offer_id = response.json["id"]
        offer = CollectiveOfferTemplate.query.filter_by(id=offer_id).one()

        assert offer.contactEmail is None
        assert offer.contactPhone == "01 99 00 25 68"

    def test_empty_intervention_area(self, pro_client, payload, venue):
        data = {
            **payload,
            "offerVenue": {"addressType": "offererVenue", "otherAddress": "", "venueId": venue.id},
            "interventionArea": [],
        }

        with patch(PATCH_CAN_CREATE_OFFER_PATH):
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

    def test_empty_contact(self, pro_client, payload, venue):
        data = {
            **payload,
            "contactEmail": None,
            "contactPhone": None,
            "contactUrl": None,
            "contactForm": None,
        }

        with patch(PATCH_CAN_CREATE_OFFER_PATH):
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

        with patch(PATCH_CAN_CREATE_OFFER_PATH):
            response = pro_client.post("/collective/offers-template", json=data)

        assert response.status_code == 400
        assert response.json == {"code": "COLLECTIVE_OFFER_URL_AND_FORM_BOTH_SET"}


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
        with patch(PATCH_CAN_CREATE_OFFER_PATH):
            return pro_client.post("/collective/offers-template", json=data)


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
