from datetime import datetime

from pcapi.model_creators.generic_creators import API_URL
from pcapi.model_creators.generic_creators import create_offerer
from pcapi.model_creators.generic_creators import create_user
from pcapi.model_creators.generic_creators import create_user_offerer
from pcapi.model_creators.generic_creators import create_venue
from pcapi.model_creators.specific_creators import create_product_with_event_type
from pcapi.model_creators.specific_creators import create_product_with_thing_type
from pcapi.models import EventType
from pcapi.models import Offer
from pcapi.models import Offerer
from pcapi.models import Product
from pcapi.models import ThingType
from pcapi.repository import repository
from pcapi.utils.human_ids import dehumanize
from pcapi.utils.human_ids import humanize

from tests.conftest import TestClient


class Returns400:
    def when_venue_id_is_not_received(self, app, db_session):
        # Given
        user = create_user(email="test@email.com")
        json = {
            "bookingEmail": "offer@email.com",
            "name": "La pièce de théâtre",
            "durationMinutes": 60,
            "type": str(ThingType.AUDIOVISUEL),
        }
        repository.save(user)

        # When
        request = TestClient(app.test_client()).with_auth(user.email).post(f"{API_URL}/offers", json=json)

        # Then
        assert request.status_code == 400
        assert request.json["venueId"] == ["Ce champ est obligatoire"]

    def when_no_duration_given_for_an_event(self, app, db_session):
        # Given
        user = create_user(email="test@email.com")
        offerer = create_offerer()
        venue = create_venue(offerer)
        user_offerer = create_user_offerer(user, offerer)
        repository.save(user, user_offerer, venue)

        json = {
            "bookingEmail": "offer@email.com",
            "name": "Le concert de Mallory Knox",
            "type": str(EventType.SPECTACLE_VIVANT),
            "venueId": humanize(venue.id),
        }

        # When
        request = TestClient(app.test_client()).with_auth(user.email).post(f"{API_URL}/offers", json=json)

        # Then
        assert request.status_code == 201

    def when_venue_is_not_found(self, app, db_session):
        # Given
        user = create_user(email="test@email.com")
        json = {
            "venueId": humanize(123),
            "name": "La pièce de théâtre",
            "durationMinutes": 60,
        }
        repository.save(user)

        # When
        request = TestClient(app.test_client()).with_auth(user.email).post(f"{API_URL}/offers", json=json)

        # Then
        assert request.status_code == 400
        assert request.json["global"] == ["Aucun objet ne correspond à cet identifiant dans notre base de données"]

    def when_new_offer_has_errors(self, app, db_session):
        # Given
        user = create_user(email="test@email.com")
        offerer = create_offerer()
        user_offerer = create_user_offerer(user, offerer)
        venue = create_venue(offerer, is_virtual=True, siret=None)
        repository.save(user, venue, user_offerer)
        json = {
            "type": "ThingType.JEUX",
            "name": "Le grand jeu",
            "url": "http://legrandj.eu",
            "mediaUrls": ["http://media.url"],
            "venueId": humanize(venue.id),
        }

        # When
        response = TestClient(app.test_client()).with_auth(user.email).post(f"{API_URL}/offers", json=json)

        # Then
        assert response.status_code == 400
        assert response.json["url"] == ["Une offre de type Jeux (support physique) ne peut pas être numérique"]

    def when_offer_type_is_unknown(self, app, db_session):
        # Given
        user = create_user(email="test@email.com")
        offerer = create_offerer()
        user_offerer = create_user_offerer(user, offerer)
        venue = create_venue(offerer, is_virtual=False)
        event_product = create_product_with_event_type()
        repository.save(user, venue, event_product, user_offerer)
        json = {
            "type": "",
            "name": "Les lapins crétins",
            "mediaUrls": ["http://media.url"],
            "durationMinutes": 200,
            "venueId": humanize(venue.id),
            "bookingEmail": "offer@email.com",
        }

        # When
        response = TestClient(app.test_client()).with_auth(user.email).post(f"{API_URL}/offers", json=json)

        # Then
        assert response.status_code == 400
        assert response.json["type"] == ["Le type de cette offre est inconnu"]

    def when_offer_name_is_too_long(self, app, db_session):
        # Given
        user = create_user(email="test@email.com")
        offerer = create_offerer()
        user_offerer = create_user_offerer(user, offerer)
        venue = create_venue(offerer, is_virtual=False)
        event_product = create_product_with_event_type()
        repository.save(user, venue, event_product, user_offerer)
        json = {
            "type": str(EventType.ACTIVATION),
            "name": "Nom vraiment très long excédant la taille maximale (nom de plus de quatre-vingt-dix caractères)",
            "mediaUrls": ["http://media.url"],
            "durationMinutes": 200,
            "venueId": humanize(venue.id),
            "bookingEmail": "offer@email.com",
        }

        # When
        response = TestClient(app.test_client()).with_auth(user.email).post(f"{API_URL}/offers", json=json)

        # Then
        assert response.status_code == 400
        assert response.json["name"] == ["Le titre de l’offre doit faire au maximum 90 caractères."]


class Returns201:
    def when_creating_a_new_event_offer(self, app, db_session):
        # Given
        user = create_user(email="test@email.com")
        offerer = create_offerer()
        venue = create_venue(offerer)
        user_offerer = create_user_offerer(user, offerer)
        repository.save(user, user_offerer, venue)
        offerer_id = offerer.id

        json = {
            "venueId": humanize(venue.id),
            "bookingEmail": "offer@email.com",
            "name": "La pièce de théâtre",
            "durationMinutes": 60,
            "type": str(EventType.SPECTACLE_VIVANT),
        }

        # When
        response = TestClient(app.test_client()).with_auth(user.email).post(f"{API_URL}/offers", json=json)

        # Then
        assert response.status_code == 201

        offer_id = dehumanize(response.json["id"])
        offer = Offer.query.filter_by(id=offer_id).first()
        assert offer.bookingEmail == "offer@email.com"
        assert offer.venueId == venue.id
        assert offer.isEvent == True
        assert offer.isThing == False
        event_product = offer.product
        assert event_product.durationMinutes == 60
        assert event_product.name == "La pièce de théâtre"
        assert offer.type == str(EventType.SPECTACLE_VIVANT)
        assert offer.product.owningOfferer == Offerer.query.get(offerer_id)

    def when_creating_a_new_event_offer_without_booking_email(self, app, db_session):
        # Given
        user = create_user(email="test@email.com")
        offerer = create_offerer()
        venue = create_venue(offerer)
        user_offerer = create_user_offerer(user, offerer)
        repository.save(user, user_offerer, venue)

        json = {
            "venueId": humanize(venue.id),
            "name": "La pièce de théâtre",
            "durationMinutes": 60,
            "type": str(EventType.SPECTACLE_VIVANT),
        }

        # When
        response = TestClient(app.test_client()).with_auth(user.email).post(f"{API_URL}/offers", json=json)

        # Then
        offer_id = dehumanize(response.json["id"])
        offer = Offer.query.filter_by(id=offer_id).first()
        assert response.status_code == 201
        assert offer.bookingEmail == None

    def when_creating_new_thing_offer(self, app, db_session):
        # Given
        user = create_user(email="test@email.com")
        offerer = create_offerer()
        user_offerer = create_user_offerer(user, offerer)
        venue = create_venue(offerer, is_virtual=True, siret=None)
        repository.save(user, venue, user_offerer)
        offerer_id = offerer.id
        json = {
            "type": "ThingType.JEUX_VIDEO",
            "name": "Les lapins crétins",
            "mediaUrls": ["http://media.url"],
            "url": "http://jeux.fr/offre",
            "venueId": humanize(venue.id),
            "bookingEmail": "offer@email.com",
        }

        # When
        response = TestClient(app.test_client()).with_auth(user.email).post(f"{API_URL}/offers", json=json)

        # Then
        assert response.status_code == 201
        offer_id = dehumanize(response.json["id"])
        offer = Offer.query.filter_by(id=offer_id).first()
        assert offer.bookingEmail == "offer@email.com"
        offer_id = dehumanize(response.json["id"])
        offer = Offer.query.filter_by(id=offer_id).first()
        assert offer.bookingEmail == "offer@email.com"
        assert offer.venueId == venue.id
        thing_id = offer.product.id
        thing_product = Product.query.filter_by(id=thing_id).first()
        assert thing_product.name == "Les lapins crétins"
        assert offer.type == str(ThingType.JEUX_VIDEO)
        assert thing_product.url == "http://jeux.fr/offre"
        assert offer.url == "http://jeux.fr/offre"
        assert offer.isDigital
        assert offer.isNational
        assert thing_product.isNational
        assert offer.product.owningOfferer == Offerer.query.get(offerer_id)

    def when_creating_a_new_offer_from_an_existing_thing(self, app, db_session):
        # given
        date_now = datetime(2020, 10, 15)

        user = create_user(email="user@test.com")
        offerer = create_offerer(date_created=date_now, date_modified_at_last_provider=date_now)
        user_offerer = create_user_offerer(user, offerer)
        venue = create_venue(offerer, date_created=date_now, date_modified_at_last_provider=date_now)
        thing_product = create_product_with_thing_type(
            date_modified_at_last_provider=date_now, id_at_providers="1234567891"
        )
        repository.save(user_offerer, venue, thing_product)

        data = {"venueId": humanize(venue.id), "productId": humanize(thing_product.id)}
        auth_request = TestClient(app.test_client()).with_auth(email="user@test.com")

        # when
        response = auth_request.post("/offers", json=data)

        # then
        assert response.status_code == 201
        offer_id = response.json["id"]
        assert type(offer_id) == str
        assert offer_id != "" and not offer_id.isspace()
        assert response.json == {"id": offer_id}

    def when_creating_a_new_offer_from_an_existing_event(self, app, db_session):
        # given
        user = create_user(email="user@test.com")
        offerer = create_offerer()
        user_offerer = create_user_offerer(user, offerer)
        venue = create_venue(offerer)
        event_product = create_product_with_event_type()
        repository.save(user_offerer, venue, event_product)

        data = {"venueId": humanize(venue.id), "productId": humanize(event_product.id)}
        auth_request = TestClient(app.test_client()).with_auth(email="user@test.com")

        # when
        response = auth_request.post("/offers", json=data)

        # then
        assert response.status_code == 201

    def when_creating_a_new_activation_event_offer_as_a_global_admin(self, app, db_session):
        # Given
        user = create_user(can_book_free_offers=False, email="test@email.com", is_admin=True)
        offerer = create_offerer()
        venue = create_venue(offerer)
        repository.save(user, venue)

        json = {
            "name": "Offre d'activation",
            "durationMinutes": 60,
            "type": str(EventType.ACTIVATION),
            "venueId": humanize(venue.id),
        }

        # When
        request = TestClient(app.test_client()).with_auth(user.email).post(f"{API_URL}/offers", json=json)

        # Then
        assert request.status_code == 201


class Returns403:
    def when_creating_a_new_activation_event_offer_as_an_offerer_editor(self, app, db_session):
        # Given
        user = create_user(email="test@email.com", is_admin=False)
        offerer = create_offerer()
        user_offerer = create_user_offerer(user, offerer, is_admin=False)
        venue = create_venue(offerer)
        repository.save(user_offerer, venue)

        json = {
            "name": "Offre d'activation",
            "durationMinutes": 60,
            "type": str(EventType.ACTIVATION),
            "venueId": humanize(venue.id),
        }

        # When
        request = TestClient(app.test_client()).with_auth(user.email).post(f"{API_URL}/offers", json=json)

        # Then
        assert request.status_code == 403
        assert request.json["type"] == [
            "Seuls les administrateurs du pass Culture peuvent créer des offres d'activation"
        ]

    def when_creating_a_new_activation_event_offer_as_an_offerer_admin(self, app, db_session):
        # Given
        user = create_user(email="test@email.com", is_admin=False)
        offerer = create_offerer()
        user_offerer = create_user_offerer(user, offerer, is_admin=True)
        venue = create_venue(offerer)
        repository.save(user_offerer, venue)

        json = {
            "name": "Offre d'activation",
            "durationMinutes": 60,
            "type": str(EventType.ACTIVATION),
            "venueId": humanize(venue.id),
        }

        # When
        request = TestClient(app.test_client()).with_auth(user.email).post(f"{API_URL}/offers", json=json)

        # Then
        assert request.status_code == 403
        assert request.json["type"] == [
            "Seuls les administrateurs du pass Culture peuvent créer des offres d'activation"
        ]

    def when_user_is_not_attached_to_offerer(self, app, db_session):
        # Given
        user = create_user(email="test@email.com")
        offerer = create_offerer()
        venue = create_venue(offerer)
        repository.save(user, venue)

        json = {
            "name": "La pièce de théâtre",
            "durationMinutes": 60,
            "type": str(EventType.SPECTACLE_VIVANT),
            "venueId": humanize(venue.id),
            "bookingEmail": "offer@email.com",
        }

        # When
        request = TestClient(app.test_client()).with_auth(user.email).post(f"{API_URL}/offers", json=json)

        # Then
        assert request.status_code == 403
        assert request.json["global"] == [
            "Vous n'avez pas les droits d'accès suffisant pour accéder à cette information."
        ]
