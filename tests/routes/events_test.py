import pytest

from models import PcObject, EventType, Offer
from models.db import db
from tests.conftest import clean_database, TestClient
from utils.human_ids import humanize, dehumanize
from utils.test_utils import create_user, API_URL, create_venue, create_offerer, create_user_offerer, \
    create_event, create_event_offer


@pytest.mark.standalone
class Patch:
    class Returns200:
        @clean_database
        def when_updating_offer_booking_email(self, app):
            # Given
            user = create_user()
            event = create_event()
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_event_offer(venue, event, booking_email='old@email.com')

            PcObject.check_and_save(offer, user)

            json = {'bookingEmail': 'offer@email.com'}

            # When
            response = TestClient().with_auth(user.email, user.clearTextPassword).patch(
                f'{API_URL}/events/{humanize(event.id)}',
                json=json)

            # Then
            assert response.status_code == 200
            offer = Offer.query.filter_by(id=offer.id).first()
            assert offer.bookingEmail == 'offer@email.com'

        @clean_database
        def when_updating_thing_attributes(self, app):
            # Given
            user = create_user()
            event = create_event(event_name='Old name')

            PcObject.check_and_save(event, user)

            json = {'name': 'New name'}

            # When
            response = TestClient().with_auth(user.email, user.clearTextPassword).patch(
                f'{API_URL}/events/{humanize(event.id)}',
                json=json)

            # Then
            assert response.status_code == 200
            db.session.refresh(event)
            assert event.name == 'New name'


@pytest.mark.standalone
class Post:
    class Returns400:
        @clean_database
        def when_no_venue_id(self, app):
            # Given
            user = create_user(email='test@email.com', password='P@55w0rd')
            json = {'name': 'La pièce de théâtre', 'durationMinutes': 60}
            PcObject.check_and_save(user)

            # When
            request = TestClient().with_auth(user.email, user.clearTextPassword).post(
                f'{API_URL}/events/',
                json=json)

            # Then
            assert request.status_code == 400
            assert request.json()['venueId'] == ['Vous devez préciser un identifiant de lieu']

        @clean_database
        def when_no_venue_with_that_id(self, app):
            # Given
            user = create_user(email='test@email.com', password='P@55w0rd')
            json = {'name': 'La pièce de théâtre', 'durationMinutes': 60, 'venueId': humanize(123)}
            PcObject.check_and_save(user)

            # When
            request = TestClient().with_auth(user.email, user.clearTextPassword).post(
                f'{API_URL}/events/',
                json=json)

            # Then
            assert request.status_code == 400
            assert request.json()['venueId'] == [
                'Aucun objet ne correspond à cet identifiant dans notre base de données']

    class Returns201:
        @clean_database
        def when_creating_a_new_event(self, app):
            # Given
            user = create_user(email='test@email.com', password='P@55w0rd')
            offerer = create_offerer()
            venue = create_venue(offerer)
            PcObject.check_and_save(user, venue)

            json = {
                'name': 'La pièce de théâtre',
                'durationMinutes': 60,
                'venueId': humanize(venue.id),
                'type': str(EventType.SPECTACLE_VIVANT),
                'bookingEmail': 'offer@email.com'
            }

            # When
            request = TestClient().with_auth(user.email, user.clearTextPassword).post(
                f'{API_URL}/events/',
                json=json)

            # Then
            assert request.status_code == 201
            assert request.json()['durationMinutes'] == 60
            assert request.json()['name'] == 'La pièce de théâtre'
            assert request.json()['offerType'] == {
                'description': 'Suivre un géant de 12 mètres dans la ville ? '
                               'Rire aux éclats devant un stand up ? '
                               'Rêver le temps d’un opéra ou d’un spectacle de danse ? '
                               'Assister à une pièce de théâtre, '
                               'ou se laisser conter une histoire ?',
                'label': 'Spectacle vivant',
                'offlineOnly': True,
                'onlineOnly': False,
                'sublabel': 'Applaudir',
                'type': 'Event',
                'value': 'EventType.SPECTACLE_VIVANT'
            }
            event_id = dehumanize(request.json()['id'])
            offer = Offer.query.filter(Offer.eventId == event_id).first()
            assert offer.bookingEmail == 'offer@email.com'

        @clean_database
        def when_creating_a_new_event_without_booking_email(self, app):
            # Given
            user = create_user(email='test@email.com', password='P@55w0rd')
            offerer = create_offerer()
            venue = create_venue(offerer)
            PcObject.check_and_save(user, venue)

            json = {
                'name': 'La pièce de théâtre',
                'durationMinutes': 60,
                'venueId': humanize(venue.id),
                'type': str(EventType.SPECTACLE_VIVANT)
            }

            # When
            request = TestClient().with_auth(user.email, user.clearTextPassword).post(
                f'{API_URL}/events/',
                json=json)

            # Then
            assert request.status_code == 201
            event_id = dehumanize(request.json()['id'])
            offer = Offer.query.filter(Offer.eventId == event_id).first()
            assert offer.bookingEmail == None

        @clean_database
        def when_creating_a_new_activation_event_as_a_global_admin(self, app):
            # Given
            user = create_user(email='test@email.com', can_book_free_offers=False, password='P@55w0rd', is_admin=True)
            offerer = create_offerer()
            venue = create_venue(offerer)
            PcObject.check_and_save(user, venue)

            json = {
                'name': "Offre d'activation",
                'durationMinutes': 60,
                'venueId': humanize(venue.id),
                'type': str(EventType.ACTIVATION)
            }

            # When
            request = TestClient().with_auth(user.email, user.clearTextPassword).post(
                f'{API_URL}/events/',
                json=json)

            # Then
            assert request.status_code == 201

    class Returns403:
        @clean_database
        def when_creating_a_new_activation_event_as_an_offerer_editor(self, app):
            # Given
            user = create_user(email='test@email.com', password='P@55w0rd', is_admin=False)
            offerer = create_offerer()
            user_offerer = create_user_offerer(user, offerer, is_admin=False)
            venue = create_venue(offerer)
            PcObject.check_and_save(user_offerer, venue)

            json = {
                'name': "Offre d'activation",
                'durationMinutes': 60,
                'venueId': humanize(venue.id),
                'type': str(EventType.ACTIVATION)
            }

            # When
            request = TestClient().with_auth(user.email, user.clearTextPassword).post(
                f'{API_URL}/events/',
                json=json)

            # Then
            assert request.status_code == 403
            assert request.json()['type'] == [
                "Seuls les administrateurs du pass Culture peuvent créer des offres d'activation"]

        @clean_database
        @pytest.mark.standalone
        def when_creating_a_new_activation_event_as_an_offerer_admin(self, app):
            # Given
            user = create_user(email='test@email.com', password='P@55w0rd', is_admin=False)
            offerer = create_offerer()
            user_offerer = create_user_offerer(user, offerer, is_admin=True)
            venue = create_venue(offerer)
            PcObject.check_and_save(user_offerer, venue)

            json = {
                'name': "Offre d'activation",
                'durationMinutes': 60,
                'venueId': humanize(venue.id),
                'type': str(EventType.ACTIVATION)
            }

            # When
            request = TestClient().with_auth(user.email, user.clearTextPassword).post(
                f'{API_URL}/events/',
                json=json)

            # Then
            assert request.status_code == 403
            assert request.json()['type'] == [
                "Seuls les administrateurs du pass Culture peuvent créer des offres d'activation"]
