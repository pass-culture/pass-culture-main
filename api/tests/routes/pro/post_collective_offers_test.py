from unittest.mock import patch

import pytest

from pcapi.core.categories import subcategories
import pcapi.core.educational.exceptions as educational_exceptions
import pcapi.core.educational.factories as educational_factories
from pcapi.core.educational.models import CollectiveOffer
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.users.factories as users_factories
from pcapi.utils.human_ids import dehumanize
from pcapi.utils.human_ids import humanize


@pytest.mark.usefixtures("db_session")
class Returns200Test:
    def test_create_collective_offer(self, client):
        # Given
        venue = offerers_factories.VenueFactory()
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(offerer=offerer, user__email="user@example.com")
        educational_domain1 = educational_factories.EducationalDomainFactory()
        educational_domain2 = educational_factories.EducationalDomainFactory()

        # When
        data = {
            "venueId": humanize(venue.id),
            "bookingEmail": "offer@example.com",
            "domains": [educational_domain1.id, educational_domain1.id, educational_domain2.id],
            "durationMinutes": 60,
            "name": "La pièce de théâtre",
            "subcategoryId": subcategories.SPECTACLE_REPRESENTATION.id,
            "contactEmail": "pouet@example.com",
            "contactPhone": "01 99 00 25 68",
            "offerVenue": {
                "addressType": "school",
                "venueId": humanize(venue.id),
                "otherAddress": "17 rue aléatoire",
            },
            "students": ["Lycée - Seconde", "Lycée - Première"],
            "offererId": humanize(offerer.id),
            "audioDisabilityCompliant": False,
            "mentalDisabilityCompliant": True,
            "motorDisabilityCompliant": False,
            "visualDisabilityCompliant": False,
            "interventionArea": ["75", "92", "93"],
        }
        with patch("pcapi.core.offerers.api.can_offerer_create_educational_offer"):
            response = client.with_session_auth("user@example.com").post("/collective/offers", json=data)

        # Then
        assert response.status_code == 201
        offer_id = dehumanize(response.json["id"])
        offer = CollectiveOffer.query.get(offer_id)
        assert offer.bookingEmail == "offer@example.com"
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
            "venueId": humanize(venue.id),
            "otherAddress": "17 rue aléatoire",
        }
        assert offer.interventionArea == ["75", "92", "93"]
        assert len(offer.students) == 2
        assert offer.students[0].value == "Lycée - Seconde"
        assert offer.students[1].value == "Lycée - Première"
        assert len(offer.domains) == 2
        assert set(offer.domains) == {educational_domain1, educational_domain2}


@pytest.mark.usefixtures("db_session")
class Returns403Test:
    def test_create_collective_offer_random_user(self, client):
        # Given
        user = users_factories.UserFactory()
        venue = offerers_factories.VenueFactory()
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(offerer=offerer, user__email="user@example.com")

        # When
        data = {
            "venueId": humanize(venue.id),
            "bookingEmail": "offer@example.com",
            "durationMinutes": 60,
            "name": "La pièce de théâtre",
            "subcategoryId": subcategories.SPECTACLE_REPRESENTATION.id,
            "contactEmail": "pouet@example.com",
            "contactPhone": "01 99 00 25 68",
            "offerVenue": {
                "addressType": "school",
                "venueId": humanize(venue.id),
                "otherAddress": "17 rue aléatoire",
            },
            "students": ["Lycée - Seconde", "Lycée - Première"],
            "offererId": humanize(offerer.id),
            "audioDisabilityCompliant": False,
            "mentalDisabilityCompliant": True,
            "motorDisabilityCompliant": False,
            "visualDisabilityCompliant": False,
            "interventionArea": ["75", "92", "93"],
        }
        with patch("pcapi.core.offerers.api.can_offerer_create_educational_offer"):
            response = client.with_session_auth(user.email).post("/collective/offers", json=data)

        # Then
        assert response.status_code == 403
        assert CollectiveOffer.query.count() == 0

    def test_create_collective_offer_no_adage_offerer(self, client):
        # Given
        def raise_ac(*args, **kwargs):
            raise educational_exceptions.CulturalPartnerNotFoundException("pouet")

        venue = offerers_factories.VenueFactory()
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(offerer=offerer, user__email="user@example.com")

        # When
        data = {
            "venueId": humanize(venue.id),
            "bookingEmail": "offer@example.com",
            "durationMinutes": 60,
            "name": "La pièce de théâtre",
            "subcategoryId": subcategories.SPECTACLE_REPRESENTATION.id,
            "contactEmail": "pouet@example.com",
            "contactPhone": "01 99 00 25 68",
            "offerVenue": {
                "addressType": "school",
                "venueId": humanize(venue.id),
                "otherAddress": "17 rue aléatoire",
            },
            "students": ["Lycée - Seconde", "Lycée - Première"],
            "offererId": humanize(offerer.id),
            "audioDisabilityCompliant": False,
            "mentalDisabilityCompliant": True,
            "motorDisabilityCompliant": False,
            "visualDisabilityCompliant": False,
            "interventionArea": ["75", "92", "93"],
        }
        with patch("pcapi.core.offerers.api.can_offerer_create_educational_offer", side_effect=raise_ac):
            response = client.with_session_auth("user@example.com").post("/collective/offers", json=data)

        # Then
        assert response.status_code == 403
        assert CollectiveOffer.query.count() == 0


@pytest.mark.usefixtures("db_session")
class Returns400Test:
    def test_create_collective_offer_unknown_category(self, client):
        # Given
        user = users_factories.UserFactory()
        venue = offerers_factories.VenueFactory()
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(offerer=offerer, user=user)

        # When
        data = {
            "venueId": humanize(venue.id),
            "bookingEmail": "offer@example.com",
            "durationMinutes": 60,
            "name": "La pièce de théâtre",
            "subcategoryId": "Pouet",
            "contactEmail": "pouet@example.com",
            "contactPhone": "01 99 00 25 68",
            "offerVenue": {
                "addressType": "school",
                "venueId": humanize(125),
                "otherAddress": "17 rue aléatoire",
            },
            "students": ["Lycée - Seconde", "Lycée - Première"],
            "offererId": humanize(offerer.id),
            "audioDisabilityCompliant": False,
            "mentalDisabilityCompliant": True,
            "motorDisabilityCompliant": False,
            "visualDisabilityCompliant": False,
            "interventionArea": ["75", "92", "93"],
        }
        with patch("pcapi.core.offerers.api.can_offerer_create_educational_offer"):
            response = client.with_session_auth(user.email).post("/collective/offers", json=data)

        # Then
        assert response.status_code == 400
        assert CollectiveOffer.query.count() == 0

    def test_create_collective_offer_unselectable_category(self, client):
        # Given
        user = users_factories.UserFactory()
        venue = offerers_factories.VenueFactory()
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(offerer=offerer, user=user)

        # When
        data = {
            "venueId": humanize(venue.id),
            "bookingEmail": "offer@example.com",
            "durationMinutes": 60,
            "name": "La pièce de théâtre",
            "subcategoryId": subcategories.OEUVRE_ART.id,
            "contactEmail": "pouet@example.com",
            "contactPhone": "01 99 00 25 68",
            "offerVenue": {
                "addressType": "school",
                "venueId": humanize(125),
                "otherAddress": "17 rue aléatoire",
            },
            "students": ["Lycée - Seconde", "Lycée - Première"],
            "offererId": humanize(offerer.id),
            "audioDisabilityCompliant": False,
            "mentalDisabilityCompliant": True,
            "motorDisabilityCompliant": False,
            "visualDisabilityCompliant": False,
            "interventionArea": ["75", "92", "93"],
        }
        with patch("pcapi.core.offerers.api.can_offerer_create_educational_offer"):
            response = client.with_session_auth(user.email).post("/collective/offers", json=data)

        # Then
        assert response.status_code == 400
        assert CollectiveOffer.query.count() == 0

    def test_create_collective_offer_no_collective__category(self, client):
        # Given
        user = users_factories.UserFactory()
        venue = offerers_factories.VenueFactory()
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(offerer=offerer, user=user)

        # When
        data = {
            "venueId": humanize(venue.id),
            "bookingEmail": "offer@example.com",
            "durationMinutes": 60,
            "name": "La pièce de théâtre",
            "subcategoryId": subcategories.SUPPORT_PHYSIQUE_FILM.id,
            "contactEmail": "pouet@example.com",
            "contactPhone": "01 99 00 25 68",
            "offerVenue": {
                "addressType": "school",
                "venueId": humanize(125),
                "otherAddress": "17 rue aléatoire",
            },
            "students": ["Lycée - Seconde", "Lycée - Première"],
            "offererId": humanize(offerer.id),
            "audioDisabilityCompliant": False,
            "mentalDisabilityCompliant": True,
            "motorDisabilityCompliant": False,
            "visualDisabilityCompliant": False,
            "interventionArea": ["75", "92", "93"],
        }
        with patch("pcapi.core.offerers.api.can_offerer_create_educational_offer"):
            response = client.with_session_auth(user.email).post("/collective/offers", json=data)

        # Then
        assert response.status_code == 400
        assert CollectiveOffer.query.count() == 0

    def test_create_collective_offer_empty_domains(self, client):
        # Given
        user = users_factories.UserFactory()
        venue = offerers_factories.VenueFactory()
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(offerer=offerer, user=user)

        # When
        data = {
            "venueId": humanize(venue.id),
            "bookingEmail": "offer@example.com",
            "durationMinutes": 60,
            "domains": [],
            "name": "La pièce de théâtre",
            "subcategoryId": subcategories.SPECTACLE_REPRESENTATION.id,
            "contactEmail": "pouet@example.com",
            "contactPhone": "01 99 00 25 68",
            "offerVenue": {
                "addressType": "school",
                "venueId": humanize(125),
                "otherAddress": "17 rue aléatoire",
            },
            "students": ["Lycée - Seconde", "Lycée - Première"],
            "offererId": humanize(offerer.id),
            "audioDisabilityCompliant": False,
            "mentalDisabilityCompliant": True,
            "motorDisabilityCompliant": False,
            "visualDisabilityCompliant": False,
            "interventionArea": ["75", "92", "93"],
        }
        with patch("pcapi.core.offerers.api.can_offerer_create_educational_offer"):
            response = client.with_session_auth(user.email).post("/collective/offers", json=data)

        # Then
        assert response.status_code == 400
        assert CollectiveOffer.query.count() == 0


@pytest.mark.usefixtures("db_session")
class Returns404Test:
    def test_create_collective_offer_with_uknown_domain(self, client):
        # Given
        venue = offerers_factories.VenueFactory()
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(offerer=offerer, user__email="user@example.com")
        educational_domain1 = educational_factories.EducationalDomainFactory()
        educational_domain2 = educational_factories.EducationalDomainFactory()

        # When
        data = {
            "venueId": humanize(venue.id),
            "bookingEmail": "offer@example.com",
            "domains": [0, educational_domain1.id, educational_domain2.id],
            "durationMinutes": 60,
            "name": "La pièce de théâtre",
            "subcategoryId": subcategories.SPECTACLE_REPRESENTATION.id,
            "contactEmail": "pouet@example.com",
            "contactPhone": "01 99 00 25 68",
            "offerVenue": {
                "addressType": "school",
                "venueId": humanize(venue.id),
                "otherAddress": "17 rue aléatoire",
            },
            "students": ["Lycée - Seconde", "Lycée - Première"],
            "offererId": humanize(offerer.id),
            "audioDisabilityCompliant": False,
            "mentalDisabilityCompliant": True,
            "motorDisabilityCompliant": False,
            "visualDisabilityCompliant": False,
            "interventionArea": ["75", "92", "93"],
        }

        with patch("pcapi.core.offerers.api.can_offerer_create_educational_offer"):
            response = client.with_session_auth("user@example.com").post("/collective/offers", json=data)

        # Then
        assert response.status_code == 404
        assert response.json == {"code": "EDUCATIONAL_DOMAIN_NOT_FOUND"}
