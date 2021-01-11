import pytest

import pcapi.core.offers.factories as offers_factories
import pcapi.core.users.factories as users_factories
from pcapi.models import EventType
from pcapi.models import Offer
from pcapi.models import ThingType
from pcapi.utils.human_ids import dehumanize
from pcapi.utils.human_ids import humanize

from tests.conftest import TestClient


@pytest.mark.usefixtures("db_session")
class Returns200:
    def test_create_event_offer(self, app):
        # Given
        venue = offers_factories.VenueFactory()
        offerer = venue.managingOfferer
        offers_factories.UserOffererFactory(offerer=offerer, user__email="user@example.com")

        # When
        data = {
            "venueId": humanize(venue.id),
            "bookingEmail": "offer@example.com",
            "durationMinutes": 60,
            "name": "La pièce de théâtre",
            "type": str(EventType.SPECTACLE_VIVANT),
            "extraData": {"toto": "text"},
        }
        client = TestClient(app.test_client()).with_auth("user@example.com")
        response = client.post("/offers", json=data)

        # Then
        assert response.status_code == 201
        offer_id = dehumanize(response.json["id"])
        offer = Offer.query.get(offer_id)
        assert offer.bookingEmail == "offer@example.com"
        assert offer.type == str(EventType.SPECTACLE_VIVANT)
        assert offer.extraData == {"toto": "text"}
        assert offer.venue == venue
        assert offer.product.durationMinutes == 60
        assert offer.product.owningOfferer == offerer

    def when_creating_new_thing_offer(self, app):
        # Given
        venue = offers_factories.VirtualVenueFactory()
        offerer = venue.managingOfferer
        offers_factories.UserOffererFactory(offerer=offerer, user__email="user@example.com")

        # When
        client = TestClient(app.test_client()).with_auth("user@example.com")
        data = {
            "venueId": humanize(venue.id),
            "bookingEmail": "offer@example.com",
            "mediaUrls": ["http://example.com/media"],
            "name": "Les lièvres pas malins",
            "type": "ThingType.JEUX_VIDEO",
            "url": "http://example.com/offer",
        }
        response = client.post("/offers", json=data)

        # Then
        assert response.status_code == 201
        offer_id = dehumanize(response.json["id"])
        offer = Offer.query.get(offer_id)
        assert offer.bookingEmail == "offer@example.com"
        assert offer.type == str(ThingType.JEUX_VIDEO)
        assert offer.venue == venue
        assert offer.product.name == "Les lièvres pas malins"
        assert offer.product.url == "http://example.com/offer"
        assert offer.url == "http://example.com/offer"
        assert offer.isDigital
        assert offer.isNational
        assert offer.product.isNational
        assert offer.product.owningOfferer == offerer


@pytest.mark.usefixtures("db_session")
class Returns400:
    def test_fail_if_venue_is_not_found(self, app):
        # Given
        offers_factories.UserOffererFactory(user__email="user@example.com")

        # When
        client = TestClient(app.test_client()).with_auth("user@example.com")
        data = {
            "venueId": humanize(1),
            "bookingEmail": "offer@example.com",
            "mediaUrls": ["http://example.com/media"],
            "name": "Les lièvres pas malins",
            "type": "ThingType.JEUX_VIDEO",
            "url": "http://example.com/offer",
        }
        response = client.post("/offers", json=data)

        # Then
        assert response.status_code == 400
        assert response.json["global"] == ["Aucun objet ne correspond à cet identifiant dans notre base de données"]

    def test_fail_if_name_too_long(self, app):
        # Given
        venue = offers_factories.VenueFactory()
        offerer = venue.managingOfferer
        offers_factories.UserOffererFactory(offerer=offerer, user__email="user@example.com")

        # When
        data = {
            "venueId": humanize(venue.id),
            "name": "too long" * 30,
            "type": str(EventType.SPECTACLE_VIVANT),
        }
        client = TestClient(app.test_client()).with_auth("user@example.com")
        response = client.post("/offers", json=data)

        # Then
        assert response.status_code == 400
        assert response.json["name"] == ["Le titre de l’offre doit faire au maximum 90 caractères."]

    def test_fail_if_unknown_type(self, app):
        # Given
        venue = offers_factories.VenueFactory()
        offerer = venue.managingOfferer
        offers_factories.UserOffererFactory(offerer=offerer, user__email="user@example.com")

        # When
        data = {
            "venueId": humanize(venue.id),
            "name": "An unacceptable name",
            "type": "unknown type",
        }
        client = TestClient(app.test_client()).with_auth("user@example.com")
        response = client.post("/offers", json=data)

        # Then
        assert response.status_code == 400
        assert response.json["type"] == ["Le type de cette offre est inconnu"]

    def test_fail_if_incoherent_input(self, app):
        # Given
        venue = offers_factories.VirtualVenueFactory()
        offerer = venue.managingOfferer
        offers_factories.UserOffererFactory(offerer=offerer, user__email="user@example.com")

        # When
        data = {
            "type": "ThingType.JEUX",
            "name": "Le grand jeu",
            "url": "http://legrandj.eu",
            "mediaUrls": ["http://media.url"],
            "venueId": humanize(venue.id),
        }
        client = TestClient(app.test_client()).with_auth("user@example.com")
        response = client.post("/offers", json=data)

        # Then
        assert response.status_code == 400
        assert response.json["url"] == ["Une offre de type Jeux (support physique) ne peut pas être numérique"]

    def should_fail_when_url_is_not_properly_formatted(self, app):
        # Given
        venue = offers_factories.VirtualVenueFactory()
        offerer = venue.managingOfferer
        offers_factories.UserOffererFactory(offerer=offerer, user__email="user@example.com")

        # When
        client = TestClient(app.test_client()).with_auth("user@example.com")
        data = {
            "venueId": humanize(venue.id),
            "name": "Les lièvres pas malins",
            "type": "ThingType.JEUX_VIDEO",
            "url": "missing.something",
        }
        response = client.post("/offers", json=data)

        # Then
        assert response.status_code == 400
        assert response.json["url"] == ['L\'URL doit commencer par "http://" ou "https://"']


@pytest.mark.usefixtures("db_session")
class Returns403:
    def when_user_is_not_attached_to_offerer(self, app):
        # Given
        users_factories.UserFactory(email="user@example.com")
        venue = offers_factories.VirtualVenueFactory()

        # When
        client = TestClient(app.test_client()).with_auth("user@example.com")
        data = {
            "venueId": humanize(venue.id),
        }
        response = client.post("/offers", json=data)

        # Then
        assert response.status_code == 403
        assert response.json["global"] == [
            "Vous n'avez pas les droits d'accès suffisant pour accéder à cette information."
        ]
