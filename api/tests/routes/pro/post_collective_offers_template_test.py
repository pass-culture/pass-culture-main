from unittest.mock import patch

import pytest

from pcapi.core.categories import subcategories
import pcapi.core.educational.exceptions as educational_exceptions
import pcapi.core.educational.factories as educational_factories
from pcapi.core.educational.models import CollectiveOfferTemplate
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.users.factories as users_factories
from pcapi.utils.human_ids import dehumanize


base_collective_offer_payload = {
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
}


@pytest.mark.usefixtures("db_session")
class Returns200Test:
    def test_create_collective_offer_template(self, client):
        # Given
        venue = offerers_factories.VenueFactory()
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(offerer=offerer, user__email="user@example.com")
        educational_domain1 = educational_factories.EducationalDomainFactory()
        educational_domain2 = educational_factories.EducationalDomainFactory()

        # When
        data = {
            **base_collective_offer_payload,
            "venueId": venue.id,
            "domains": [educational_domain1.id, educational_domain1.id, educational_domain2.id],
            "subcategoryId": subcategories.SPECTACLE_REPRESENTATION.id,
            "offerVenue": {
                "addressType": "school",
                "venueId": venue.id,
                "otherAddress": "17 rue aléatoire",
            },
        }
        with patch("pcapi.core.offerers.api.can_offerer_create_educational_offer"):
            response = client.with_session_auth("user@example.com").post("/collective/offers-template", json=data)

        # Then

        assert response.status_code == 201
        offer_id = dehumanize(response.json["id"])
        offer = CollectiveOfferTemplate.query.get(offer_id)
        assert offer.bookingEmails == ["offer1@example.com", "offer2@example.com"]
        assert offer.subcategoryId == subcategories.SPECTACLE_REPRESENTATION.id
        assert offer.venue == venue
        assert offer.durationMinutes == 60
        assert offer.venue.managingOffererId == offerer.id
        assert offer.motorDisabilityCompliant == False
        assert offer.visualDisabilityCompliant == False
        assert offer.audioDisabilityCompliant == False
        assert offer.mentalDisabilityCompliant == True
        assert offer.mentalDisabilityCompliant == True
        assert offer.contactEmail == "pouet@example.com"
        assert offer.contactPhone == "01 99 00 25 68"
        assert offer.offerVenue == {
            "addressType": "school",
            "venueId": venue.id,
            "otherAddress": "17 rue aléatoire",
        }
        assert offer.interventionArea == ["75", "92", "93"]
        assert len(offer.students) == 2
        assert offer.students[0].value == "Lycée - Seconde"
        assert offer.students[1].value == "Lycée - Première"
        assert len(offer.domains) == 2
        assert set(offer.domains) == {educational_domain1, educational_domain2}
        assert offer.description == "Ma super description"
        assert offer.priceDetail == "Le détail ici"

    def test_create_collective_offer_template_empty_intervention_area(self, client):
        # Given
        venue = offerers_factories.VenueFactory()
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(offerer=offerer, user__email="user@example.com")
        educational_domain = educational_factories.EducationalDomainFactory()

        # When
        data = {
            **base_collective_offer_payload,
            "venueId": venue.id,
            "domains": [educational_domain.id],
            "subcategoryId": subcategories.SPECTACLE_REPRESENTATION.id,
            "offerVenue": {
                "addressType": "offererVenue",
                "otherAddress": "",
                "venueId": venue.id,
            },
            "interventionArea": [],
        }
        with patch("pcapi.core.offerers.api.can_offerer_create_educational_offer"):
            response = client.with_session_auth("user@example.com").post("/collective/offers-template", json=data)

        # Then
        assert response.status_code == 201


@pytest.mark.usefixtures("db_session")
class Returns403Test:
    def test_create_collective_offer_template_random_user(self, client):
        # Given
        user = users_factories.UserFactory()
        venue = offerers_factories.VenueFactory()
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(offerer=offerer, user__email="user@example.com")

        # When
        data = {
            **base_collective_offer_payload,
            "venueId": venue.id,
            "domains": [educational_factories.EducationalDomainFactory().id],
            "subcategoryId": subcategories.SPECTACLE_REPRESENTATION.id,
            "offerVenue": {
                "addressType": "school",
                "venueId": venue.id,
                "otherAddress": "17 rue aléatoire",
            },
        }
        with patch("pcapi.core.offerers.api.can_offerer_create_educational_offer"):
            response = client.with_session_auth(user.email).post("/collective/offers-template", json=data)

        # Then
        assert response.status_code == 403
        assert CollectiveOfferTemplate.query.count() == 0

    def test_create_collective_offer_template_no_adage_offerer(self, client):
        # Given
        def raise_ac(*args, **kwargs):
            raise educational_exceptions.CulturalPartnerNotFoundException("pouet")

        venue = offerers_factories.VenueFactory()
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(offerer=offerer, user__email="user@example.com")

        # When
        data = {
            **base_collective_offer_payload,
            "venueId": venue.id,
            "domains": [educational_factories.EducationalDomainFactory().id],
            "subcategoryId": subcategories.SPECTACLE_REPRESENTATION.id,
            "offerVenue": {
                "addressType": "school",
                "venueId": venue.id,
                "otherAddress": "17 rue aléatoire",
            },
        }
        with patch("pcapi.core.offerers.api.can_offerer_create_educational_offer", side_effect=raise_ac):
            response = client.with_session_auth("user@example.com").post("/collective/offers-template", json=data)

        # Then
        assert response.status_code == 403
        assert CollectiveOfferTemplate.query.count() == 0


@pytest.mark.usefixtures("db_session")
class Returns400Test:
    def test_create_collective_offer_template_unknown_category(self, client):
        # Given
        user = users_factories.UserFactory()
        venue = offerers_factories.VenueFactory()
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(offerer=offerer, user=user)

        # When
        data = {
            **base_collective_offer_payload,
            "venueId": venue.id,
            "offerVenue": {
                "addressType": "school",
                "venueId": 125,
                "otherAddress": "17 rue aléatoire",
            },
        }
        with patch("pcapi.core.offerers.api.can_offerer_create_educational_offer"):
            response = client.with_session_auth(user.email).post("/collective/offers-template", json=data)

        # Then
        assert response.status_code == 400
        assert CollectiveOfferTemplate.query.count() == 0

    def test_create_collective_offer_template_unselectable_category(self, client):
        # Given
        user = users_factories.UserFactory()
        venue = offerers_factories.VenueFactory()
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(offerer=offerer, user=user)

        # When
        data = {
            **base_collective_offer_payload,
            "venueId": venue.id,
            "subcategoryId": subcategories.OEUVRE_ART.id,
            "offerVenue": {
                "addressType": "school",
                "venueId": 125,
                "otherAddress": "17 rue aléatoire",
            },
        }
        with patch("pcapi.core.offerers.api.can_offerer_create_educational_offer"):
            response = client.with_session_auth(user.email).post("/collective/offers-template", json=data)

        # Then
        assert response.status_code == 400
        assert CollectiveOfferTemplate.query.count() == 0

    def test_create_collective_offer_template_no_collective_category(self, client):
        # Given
        user = users_factories.UserFactory()
        venue = offerers_factories.VenueFactory()
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(offerer=offerer, user=user)

        # When
        data = {
            **base_collective_offer_payload,
            "venueId": venue.id,
            "subcategoryId": subcategories.SUPPORT_PHYSIQUE_FILM.id,
            "offerVenue": {
                "addressType": "school",
                "venueId": 125,
                "otherAddress": "17 rue aléatoire",
            },
        }
        with patch("pcapi.core.offerers.api.can_offerer_create_educational_offer"):
            response = client.with_session_auth(user.email).post("/collective/offers-template", json=data)

        # Then
        assert response.status_code == 400
        assert CollectiveOfferTemplate.query.count() == 0

    def test_create_collective_offer_template_empty_domains(self, client):
        # Given
        user = users_factories.UserFactory()
        venue = offerers_factories.VenueFactory()
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(offerer=offerer, user=user)

        # When
        data = {
            **base_collective_offer_payload,
            "venueId": venue.id,
            "subcategoryId": subcategories.SPECTACLE_REPRESENTATION.id,
            "offerVenue": {
                "addressType": "school",
                "venueId": 125,
                "otherAddress": "17 rue aléatoire",
            },
        }
        with patch("pcapi.core.offerers.api.can_offerer_create_educational_offer"):
            response = client.with_session_auth(user.email).post("/collective/offers-template", json=data)

        # Then
        assert response.status_code == 400
        assert CollectiveOfferTemplate.query.count() == 0

    def test_create_collective_offer_template_too_long_price_details(self, client):
        user = users_factories.UserFactory()
        venue = offerers_factories.VenueFactory()
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(offerer=offerer, user=user)

        # When
        data = {
            **base_collective_offer_payload,
            "venueId": venue.id,
            "subcategoryId": subcategories.SPECTACLE_REPRESENTATION.id,
            "offerVenue": {
                "addressType": "school",
                "venueId": 125,
                "otherAddress": "17 rue aléatoire",
            },
            "priceDetail": "a" * 1001,
        }
        with patch("pcapi.core.offerers.api.can_offerer_create_educational_offer"):
            response = client.with_session_auth(user.email).post("/collective/offers-template", json=data)

        # Then
        assert response.status_code == 400
        assert CollectiveOfferTemplate.query.count() == 0


@pytest.mark.usefixtures("db_session")
class Returns404Test:
    def test_create_collective_offer_template_with_unknown_domain(self, client):
        # Given
        venue = offerers_factories.VenueFactory()
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(offerer=offerer, user__email="user@example.com")
        educational_domain1 = educational_factories.EducationalDomainFactory()
        educational_domain2 = educational_factories.EducationalDomainFactory()

        # When
        data = {
            **base_collective_offer_payload,
            "venueId": venue.id,
            "domains": [0, educational_domain1.id, educational_domain2.id],
            "subcategoryId": subcategories.SPECTACLE_REPRESENTATION.id,
            "offerVenue": {
                "addressType": "school",
                "venueId": venue.id,
                "otherAddress": "17 rue aléatoire",
            },
        }

        with patch("pcapi.core.offerers.api.can_offerer_create_educational_offer"):
            response = client.with_session_auth("user@example.com").post("/collective/offers-template", json=data)

        # Then
        assert response.status_code == 404
        assert response.json == {"code": "EDUCATIONAL_DOMAIN_NOT_FOUND"}
