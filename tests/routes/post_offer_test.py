import pytest

from models import PcObject, EventType, Offer, Thing, Event, ThingType
from tests.conftest import clean_database, TestClient
from tests.test_utils import create_user, API_URL, create_offerer, create_venue, create_user_offerer, create_thing, \
    create_event
from utils.human_ids import humanize, dehumanize


@pytest.mark.standalone
class Post:
    class Returns400:
        @clean_database
        def when_no_venue_id(self, app):
            # Given
            user = create_user(email='test@email.com')
            json = {
                'bookingEmail': 'offer@email.com',
                'thing':
                    {
                        'name': 'La pièce de théâtre',
                        'durationMinutes': 60,
                        'type': str(EventType.SPECTACLE_VIVANT),
                    }

            }
            PcObject.check_and_save(user)

            # When
            request = TestClient().with_auth(user.email).post(
                f'{API_URL}/offers/',
                json=json)

            # Then
            assert request.status_code == 400
            assert request.json()['venueId'] == ['Vous devez préciser un identifiant de lieu']

        @clean_database
        def when_no_venue_with_that_id(self, app):
            # Given
            user = create_user(email='test@email.com')
            json = {
                'venueId': humanize(123),
                'thing':
                    {
                        'name': 'La pièce de théâtre',
                        'durationMinutes': 60
                    }
            }
            PcObject.check_and_save(user)

            # When
            request = TestClient().with_auth(user.email).post(
                f'{API_URL}/offers/',
                json=json)

            # Then
            assert request.status_code == 400
            assert request.json()['global'] == [
                'Aucun objet ne correspond à cet identifiant dans notre base de données']

        @clean_database
        def when_offer_with_urls_and_type_offline_only(self, app):
            # Given
            user = create_user(email='test@email.com')
            offerer = create_offerer()
            user_offerer = create_user_offerer(user, offerer)
            venue = create_venue(offerer, is_virtual=True, siret=None)
            PcObject.check_and_save(user, venue, user_offerer)
            json = {
                'thing':
                    {
                        'type': 'ThingType.JEUX_ABO',
                        'name': 'Le grand jeu',
                        "url": 'http://legrandj.eu',
                        'mediaUrls': ['http://media.url']
                    },
                'venueId': humanize(venue.id)
            }

            # When
            response = TestClient().with_auth(user.email).post(
                f'{API_URL}/offers/',
                json=json)

            # Then
            assert response.status_code == 400
            assert response.json()['url'] == ['Une offre de type Jeux (Abonnements) ne peut pas être numérique']

        @clean_database
        def when_offer_thing_with_invalid_url(self, app):
            # Given
            user = create_user(email='test@email.com')
            offerer = create_offerer()
            user_offerer = create_user_offerer(user, offerer)
            venue = create_venue(offerer, is_virtual=True, siret=None)
            PcObject.check_and_save(user, venue, user_offerer)
            json = {
                'thing': {
                    'type': 'ThingType.JEUX_VIDEO',
                    'name': 'Les Lapins Crétins',
                    'mediaUrls': ['http://media.url'],
                    'url': 'ftp://invalid.url'
                },
                'venueId': humanize(venue.id)}

            # When
            response = TestClient().with_auth(user.email).post(
                f'{API_URL}/offers/',
                json=json)

            # Then
            assert response.status_code == 400
            assert response.json()['url'] == ["L'URL doit commencer par \"http://\" ou \"https://\""]

        @clean_database
        def when_thing_offer_with_url_and_physical_venue(self, app):
            # Given
            user = create_user(email='test@email.com')
            offerer = create_offerer()
            user_offerer = create_user_offerer(user, offerer)
            venue = create_venue(offerer, is_virtual=False)
            PcObject.check_and_save(user, venue, user_offerer)
            json = {
                'thing': {
                    'type': 'ThingType.JEUX_VIDEO',
                    'name': 'Les Lapins Crétins',
                    'mediaUrls': ['http://media.url'],
                    'url': 'http://lapins-cretins.fr'
                },
                'venueId': humanize(venue.id)}

            # When
            response = TestClient().with_auth(user.email).post(
                f'{API_URL}/offers/',
                json=json)

            # Then
            assert response.status_code == 400
            assert response.json()['venue'] == [
                'Une offre numérique doit obligatoirement être associée au lieu "Offre en ligne"']

        @clean_database
        def when_existing_thing_is_physical_and_venue_is_virtual(self, app):
            # given
            user = create_user(email='user@test.com')
            offerer = create_offerer()
            user_offerer = create_user_offerer(user, offerer)
            venue = create_venue(offerer, is_virtual=True, siret=None)
            thing = create_thing(url=None)
            PcObject.check_and_save(user_offerer, venue, thing)

            data = {
                'venueId': humanize(venue.id),
                'thingId': humanize(thing.id)
            }
            auth_request = TestClient().with_auth(email='user@test.com')

            # when
            response = auth_request.post(API_URL + '/offers', json=data)

            # then
            assert response.status_code == 400
            assert response.json()['venue'] == ['Une offre physique ne peut être associée au lieu "Offre en ligne"']

    class Returns201:
        @clean_database
        def when_creating_a_new_event_offer(self, app):
            # Given
            user = create_user(email='test@email.com')
            offerer = create_offerer()
            venue = create_venue(offerer)
            user_offerer = create_user_offerer(user, offerer)
            PcObject.check_and_save(user, user_offerer, venue)

            json = {
                'venueId': humanize(venue.id),
                'bookingEmail': 'offer@email.com',
                'event':
                    {
                        'name': 'La pièce de théâtre',
                        'durationMinutes': 60,
                        'type': str(EventType.SPECTACLE_VIVANT)
                    }
            }

            # When
            response = TestClient().with_auth(user.email).post(
                f'{API_URL}/offers/',
                json=json)

            # Then
            assert response.status_code == 201
            assert response.json()['event']['offerType'] == {
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

            offer_id = dehumanize(response.json()['id'])
            offer = Offer.query.filter_by(id=offer_id).first()
            assert offer.bookingEmail == 'offer@email.com'
            assert offer.venueId == venue.id
            event_id = dehumanize(response.json()['event']['id'])
            event = Event.query.filter_by(id=event_id).first()
            assert event.durationMinutes == 60
            assert event.name == 'La pièce de théâtre'
            assert offer.type == str(EventType.SPECTACLE_VIVANT)

        @clean_database
        def when_creating_a_new_event_offer_without_booking_email(self, app):
            # Given
            user = create_user(email='test@email.com')
            offerer = create_offerer()
            venue = create_venue(offerer)
            user_offerer = create_user_offerer(user, offerer)
            PcObject.check_and_save(user, user_offerer, venue)

            json = {
                'venueId': humanize(venue.id),
                'event':
                    {
                        'name': 'La pièce de théâtre',
                        'durationMinutes': 60,
                        'type': str(EventType.SPECTACLE_VIVANT)
                    }
            }

            # When
            response = TestClient().with_auth(user.email).post(
                f'{API_URL}/offers/',
                json=json)

            # Then
            offer_id = dehumanize(response.json()['id'])
            offer = Offer.query.filter_by(id=offer_id).first()
            assert response.status_code == 201
            assert offer.bookingEmail == None

        @clean_database
        def when_creating_new_thing_offer(self, app):
            # Given
            user = create_user(email='test@email.com')
            offerer = create_offerer()
            user_offerer = create_user_offerer(user, offerer)
            venue = create_venue(offerer, is_virtual=True, siret=None)
            thing = create_thing()
            PcObject.check_and_save(user, venue, thing, user_offerer)
            json = {
                'thing':
                    {
                        'type': 'ThingType.JEUX_VIDEO',
                        'name': 'Les lapins crétins',
                        'mediaUrls': ['http://media.url'],
                        'url': 'http://jeux.fr/offre',
                    },
                'venueId': humanize(venue.id),
                'bookingEmail': 'offer@email.com'
            }

            # When
            response = TestClient().with_auth(user.email).post(
                f'{API_URL}/offers/',
                json=json)

            # Then
            assert response.status_code == 201
            offer_id = dehumanize(response.json()['id'])
            offer = Offer.query.filter_by(id=offer_id).first()
            assert offer.bookingEmail == 'offer@email.com'
            assert response.json()['thing']['offerType'] == {
                'description': 'Résoudre l’énigme d’un jeu de piste dans votre ville ? '
                               'Jouer en ligne entre amis ? '
                               'Découvrir cet univers étrange avec une manette ?',
                'label': 'Jeux Vidéo',
                'offlineOnly': False,
                'onlineOnly': True,
                'sublabel': 'Jouer',
                'type': 'Thing',
                'value': 'ThingType.JEUX_VIDEO'
            }
            offer_id = dehumanize(response.json()['id'])
            offer = Offer.query.filter_by(id=offer_id).first()
            assert offer.bookingEmail == 'offer@email.com'
            assert offer.venueId == venue.id
            thing_id = dehumanize(response.json()['thing']['id'])
            thing = Thing.query.filter_by(id=thing_id).first()
            assert thing.name == 'Les lapins crétins'
            assert offer.type == str(ThingType.JEUX_VIDEO)
            assert thing.url == 'http://jeux.fr/offre'
            assert offer.url == 'http://jeux.fr/offre'
            assert offer.isDigital
            assert offer.isNational
            assert thing.isNational

        @clean_database
        def when_creating_a_new_offer_from_an_existing_thing(self, app):
            # given
            user = create_user(email='user@test.com')
            offerer = create_offerer()
            user_offerer = create_user_offerer(user, offerer)
            venue = create_venue(offerer)
            thing = create_thing()
            PcObject.check_and_save(user_offerer, venue, thing)

            data = {
                'venueId': humanize(venue.id),
                'thingId': humanize(thing.id)
            }
            auth_request = TestClient().with_auth(email='user@test.com')

            # when
            response = auth_request.post(API_URL + '/offers', json=data)

            # then
            assert response.status_code == 201

        @clean_database
        def when_creating_a_new_offer_from_an_existing_event(self, app):
            # given
            user = create_user(email='user@test.com')
            offerer = create_offerer()
            user_offerer = create_user_offerer(user, offerer)
            venue = create_venue(offerer)
            event = create_event()
            PcObject.check_and_save(user_offerer, venue, event)

            data = {
                'venueId': humanize(venue.id),
                'eventId': humanize(event.id)
            }
            auth_request = TestClient().with_auth(email='user@test.com')

            # when
            response = auth_request.post(API_URL + '/offers', json=data)

            # then
            assert response.status_code == 201

        @clean_database
        def when_creating_a_new_activation_event_offer_as_a_global_admin(self, app):
            # Given
            user = create_user(email='test@email.com', can_book_free_offers=False, is_admin=True)
            offerer = create_offerer()
            venue = create_venue(offerer)
            PcObject.check_and_save(user, venue)

            json = {
                'event':
                    {
                        'name': "Offre d'activation",
                        'durationMinutes': 60,
                        'type': str(EventType.ACTIVATION)
                    },
                'venueId': humanize(venue.id),
            }

            # When
            request = TestClient().with_auth(user.email).post(
                f'{API_URL}/offers/',
                json=json)

            # Then
            assert request.status_code == 201

    class Returns403:
        @clean_database
        def when_creating_a_new_activation_event_offer_as_an_offerer_editor(self, app):
            # Given
            user = create_user(email='test@email.com', is_admin=False)
            offerer = create_offerer()
            user_offerer = create_user_offerer(user, offerer, is_admin=False)
            venue = create_venue(offerer)
            PcObject.check_and_save(user_offerer, venue)

            json = {
                'event':
                    {
                        'name': "Offre d'activation",
                        'durationMinutes': 60,
                        'type': str(EventType.ACTIVATION)
                    },
                'venueId': humanize(venue.id),
            }

            # When
            request = TestClient().with_auth(user.email).post(
                f'{API_URL}/offers/',
                json=json)

            # Then
            assert request.status_code == 403
            assert request.json()['type'] == [
                "Seuls les administrateurs du pass Culture peuvent créer des offres d'activation"]

        @clean_database
        @pytest.mark.standalone
        def when_creating_a_new_activation_event_offer_as_an_offerer_admin(self, app):
            # Given
            user = create_user(email='test@email.com', is_admin=False)
            offerer = create_offerer()
            user_offerer = create_user_offerer(user, offerer, is_admin=True)
            venue = create_venue(offerer)
            PcObject.check_and_save(user_offerer, venue)

            json = {
                'event':
                    {
                        'name': "Offre d'activation",
                        'durationMinutes': 60,
                        'type': str(EventType.ACTIVATION)
                    },
                'venueId': humanize(venue.id),
            }

            # When
            request = TestClient().with_auth(user.email).post(
                f'{API_URL}/offers/',
                json=json)

            # Then
            assert request.status_code == 403
            assert request.json()['type'] == [
                "Seuls les administrateurs du pass Culture peuvent créer des offres d'activation"]

        @clean_database
        def when_user_is_not_attached_to_offerer(self, app):
            # Given
            user = create_user(email='test@email.com')
            offerer = create_offerer()
            venue = create_venue(offerer)
            PcObject.check_and_save(user, venue)

            json = {
                'event': {
                    'name': 'La pièce de théâtre',
                    'durationMinutes': 60,
                    'type': str(EventType.SPECTACLE_VIVANT)
                },
                'venueId': humanize(venue.id),
                'bookingEmail': 'offer@email.com'
            }

            # When
            request = TestClient().with_auth(user.email).post(
                f'{API_URL}/offers/',
                json=json)

            # Then
            assert request.status_code == 403
            assert request.json()['global'] == ["Cette structure n'est pas enregistrée chez cet utilisateur."]
