import pytest

from models import PcObject, Offer
from models.db import db
from tests.conftest import clean_database, TestClient
from tests.test_utils import create_user, API_URL, create_venue, create_offerer, \
    create_user_offerer, create_thing, create_thing_offer
from utils.human_ids import humanize, dehumanize


@pytest.mark.standalone
class Patch:
    class Returns200:
        @clean_database
        def when_updating_offer_booking_email(self, app):
            # Given
            user = create_user()
            thing = create_thing()
            offerer = create_offerer()
            user_offerer = create_user_offerer(user, offerer)
            venue = create_venue(offerer)
            offer = create_thing_offer(venue, thing, booking_email='old@email.com')

            PcObject.check_and_save(offer, user, user_offerer)

            json = {
                'bookingEmail': 'offer@email.com',
                'venueId': humanize(venue.id)
            }

            # When
            response = TestClient().with_auth(user.email, user.clearTextPassword).patch(
                f'{API_URL}/things/{humanize(thing.id)}',
                json=json)

            # Then
            assert response.status_code == 200
            offer = Offer.query.filter_by(id=offer.id).first()
            assert offer.bookingEmail == 'offer@email.com'

        @clean_database
        def when_updating_thing_attributes(self, app):
            # Given
            user = create_user()
            offerer = create_offerer()
            thing = create_thing()
            user_offerer = create_user_offerer(user, offerer)
            venue = create_venue(offerer)

            PcObject.check_and_save(thing, user, user_offerer)

            json = {
                'name': 'New name',
                'venueId': humanize(venue.id)
            }

            # When
            response = TestClient().with_auth(user.email, user.clearTextPassword).patch(
                f'{API_URL}/things/{humanize(thing.id)}',
                json=json)

            # Then
            assert response.status_code == 200
            db.session.refresh(thing)
            assert thing.name == 'New name'

    class Returns400:
        @clean_database
        def when_thing_with_invalid_url(self, app):
            # Given
            user = create_user(email='test@email.com', password='P@55W0rd!')
            offerer = create_offerer()
            user_offerer = create_user_offerer(user, offerer)
            venue = create_venue(offerer, is_virtual=True, siret=None)
            thing = create_thing()
            PcObject.check_and_save(user, venue, thing, user_offerer)
            json = {
                'url': 'ftp://invalid.url',
                'venueId': humanize(venue.id)
            }

            # When
            response = TestClient().with_auth(user.email, user.clearTextPassword).patch(
                f'{API_URL}/things/{humanize(thing.id)}',
                json=json)

            # Then
            assert response.status_code == 400
            assert response.json()['url'] == ["L'URL doit commencer par \"http://\" ou \"https://\""]

    class Returns403:
        @clean_database
        def when_user_is_not_rattached_to_offerer(self, app):
            # Given
            user = create_user()
            thing = create_thing()
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_thing_offer(venue, thing, booking_email='old@email.com')

            PcObject.check_and_save(offer, user)

            json = {
                'bookingEmail': 'offer@email.com',
                'venueId': humanize(venue.id)
            }

            # When
            response = TestClient().with_auth(user.email, user.clearTextPassword).patch(
                f'{API_URL}/things/{humanize(thing.id)}',
                json=json)

            # Then
            assert response.status_code == 403
            assert response.json()['global'] == ["Cette structure n'est pas enregistrée chez cet utilisateur."]


@pytest.mark.standalone
class Post:
    class Returns400:
        @clean_database
        def when_thing_with_urls_and_type_offline_only(self, app):
            # Given
            user = create_user(email='test@email.com', password='P@55W0rd!')
            offerer = create_offerer()
            user_offerer = create_user_offerer(user, offerer)
            venue = create_venue(offerer, is_virtual=True, siret=None)
            PcObject.check_and_save(user, venue, user_offerer)
            json = {'thumbCount': 0, 'type': 'ThingType.JEUX_ABO', 'name': 'Le grand jeu',
                    'mediaUrls': 'http://media.url',
                    'url': 'http://jeux_abo.fr/offre', 'isNational': False, 'venueId': humanize(venue.id)}

            # When
            response = TestClient().with_auth(user.email, user.clearTextPassword).post(
                f'{API_URL}/things/',
                json=json)

            # Then
            assert response.status_code == 400
            assert response.json()['url'] == ['Une offre de type Jeux (Abonnements) ne peut pas être numérique']

        @clean_database
        def when_thing_with_invalid_url(self, app):
            # Given
            user = create_user(email='test@email.com', password='P@55W0rd!')
            offerer = create_offerer()
            user_offerer = create_user_offerer(user, offerer)
            venue = create_venue(offerer, is_virtual=True, siret=None)
            PcObject.check_and_save(user, venue, user_offerer)
            json = {'thumbCount': 0, 'type': 'ThingType.JEUX_ABO', 'name': 'Le grand jeu',
                    'mediaUrls': 'http://media.url',
                    'url': 'ftp://invalid.url', 'isNational': False, 'venueId': humanize(venue.id)}

            # When
            response = TestClient().with_auth(user.email, user.clearTextPassword).post(
                f'{API_URL}/things/',
                json=json)

            # Then
            assert response.status_code == 400
            assert response.json()['url'] == ["L'URL doit commencer par \"http://\" ou \"https://\""]

        @clean_database
        def when_thing_with_url_and_physical_venue(self, app):
            # Given
            user = create_user(email='test@email.com', password='P@55W0rd!')
            offerer = create_offerer()
            user_offerer = create_user_offerer(user, offerer)
            venue = create_venue(offerer, is_virtual=False)
            PcObject.check_and_save(user, venue, user_offerer)
            json = {'thumbCount': 0, 'type': 'ThingType.JEUX_VIDEO', 'name': 'Les lapins crétins',
                    'mediaUrls': 'http://media.url',
                    'url': 'http://jeux.fr/offre', 'isNational': False, 'venueId': humanize(venue.id)}

            # When
            response = TestClient().with_auth(user.email, user.clearTextPassword).post(
                f'{API_URL}/things/',
                json=json)

            # Then
            assert response.status_code == 400
            assert response.json()['venue'] == [
                'Une offre numérique doit obligatoirement être associée au lieu "Offre en ligne"']

    class Returns201:

        @clean_database
        def when_creating_new_thing(self, app):
            # Given
            user = create_user(email='test@email.com', password='P@55W0rd!')
            offerer = create_offerer()
            user_offerer = create_user_offerer(user, offerer)
            venue = create_venue(offerer, is_virtual=True, siret=None)
            thing = create_thing()
            PcObject.check_and_save(user, venue, thing, user_offerer)
            json = {'thumbCount': 0,
                    'type': 'ThingType.JEUX_VIDEO',
                    'name': 'Les lapins crétins',
                    'mediaUrls': 'http://media.url',
                    'url': 'http://jeux.fr/offre',
                    'isNational': False,
                    'venueId': humanize(venue.id),
                    'bookingEmail': 'offer@email.com'
                    }

            # When
            response = TestClient().with_auth(user.email, user.clearTextPassword).post(
                f'{API_URL}/things/',
                json=json)

            # Then
            assert response.status_code == 201
            thing_id = dehumanize(response.json()['id'])
            offer = Offer.query.filter(Offer.thingId == thing_id).first()
            assert offer.bookingEmail == 'offer@email.com'

        @clean_database
        def when_creating_new_thing_without_booking_email(self, app):
            # Given
            user = create_user(email='test@email.com', password='P@55W0rd!')
            offerer = create_offerer()
            user_offerer = create_user_offerer(user, offerer)
            venue = create_venue(offerer, is_virtual=True, siret=None)
            thing = create_thing()
            PcObject.check_and_save(user, venue, thing, user_offerer)
            json = {'thumbCount': 0,
                    'type': 'ThingType.JEUX_VIDEO',
                    'name': 'Les lapins crétins',
                    'mediaUrls': 'http://media.url',
                    'url': 'http://jeux.fr/offre',
                    'isNational': False,
                    'venueId': humanize(venue.id)
                    }

            # When
            response = TestClient().with_auth(user.email, 'P@55W0rd!').post(
                f'{API_URL}/things/',
                json=json)

            # Then
            assert response.status_code == 201
            thing_id = dehumanize(response.json()['id'])
            offer = Offer.query.filter(Offer.thingId == thing_id).first()
            assert offer.bookingEmail == None

    class Returns403:
        @clean_database
        def when_user_is_not_rattached_to_offerer(self, app):
            # Given
            user = create_user(email='test@email.com', password='P@55W0rd!')
            offerer = create_offerer()
            venue = create_venue(offerer, is_virtual=True, siret=None)
            thing = create_thing()
            PcObject.check_and_save(user, venue, thing)
            json = {'thumbCount': 0,
                    'type': 'ThingType.JEUX_VIDEO',
                    'name': 'Les lapins crétins',
                    'mediaUrls': 'http://media.url',
                    'url': 'http://jeux.fr/offre',
                    'isNational': False,
                    'venueId': humanize(venue.id),
                    'bookingEmail': 'offer@email.com'
                    }

            # When
            response = TestClient().with_auth(user.email, user.clearTextPassword).post(
                f'{API_URL}/things/',
                json=json)

            # Then
            assert response.status_code == 403
            assert response.json()['global'] == ["Cette structure n'est pas enregistrée chez cet utilisateur."]
