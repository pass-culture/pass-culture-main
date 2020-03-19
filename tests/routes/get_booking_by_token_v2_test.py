from datetime import datetime, timedelta

from freezegun import freeze_time

from models import EventType
from repository import repository
from tests.conftest import clean_database, TestClient
from tests.model_creators.generic_creators import create_booking, create_user, create_offerer, create_venue, \
    create_deposit, \
    create_user_offerer, create_api_key
from tests.model_creators.specific_creators import create_stock_with_event_offer, create_stock_from_event_occurrence, \
    create_stock_with_thing_offer, create_offer_with_event_product, create_event_occurrence

API_KEY_VALUE = 'A_MOCKED_API_KEY'


class Get:
    class Returns200:
        @freeze_time('2019-11-26 18:29:20.891028')
        @clean_database
        def when_user_has_rights_and_regular_offer(self, app):
            # Given
            user = create_user(email='user@example.com', public_name='John Doe')
            create_deposit(user)
            admin_user = create_user(email='admin@example.com')
            offerer = create_offerer()
            create_user_offerer(admin_user, offerer)
            venue = create_venue(offerer, name='Venue name', address='Venue address')
            offer = create_offer_with_event_product(venue=venue, event_name='Event Name', event_type=EventType.CINEMA)
            event_occurrence = create_event_occurrence(offer, beginning_datetime=datetime.utcnow())
            stock = create_stock_from_event_occurrence(event_occurrence, price=12)
            booking = create_booking(user=user, quantity=3, stock=stock, venue=venue)
            repository.save(booking)
            url = f'/v2/bookings/token/{booking.token}'

            # When
            response = TestClient(app.test_client()) \
                .with_auth('admin@example.com') \
                .get(url)

            # Then
            assert response.headers['Content-type'] == 'application/json'
            assert response.status_code == 200

        @clean_database
        def when_api_key_is_provided_and_rights_and_regular_offer(self, app):
            # Given
            user = create_user(email='user@example.com', public_name='John Doe')
            user2 = create_user(email='user2@example.com', public_name='Jane Doe')
            offerer = create_offerer()
            user_offerer = create_user_offerer(user2, offerer)
            venue = create_venue(offerer)
            offer = create_offer_with_event_product(venue, event_name='Event Name', event_type=EventType.CINEMA)
            event_occurrence = create_event_occurrence(offer)
            stock = create_stock_from_event_occurrence(event_occurrence, price=0)
            booking = create_booking(user=user, stock=stock, venue=venue)
            repository.save(user_offerer, booking)
            offererApiKey = create_api_key(offerer_id=offerer.id)
            repository.save(offererApiKey)
            user2ApiKey = f'Bearer {offererApiKey.value}'
            booking_token = booking.token.lower()
            url = f'/v2/bookings/token/{booking_token}'

            # When
            response = TestClient(app.test_client()) \
                .get(
                    url,
                    headers={
                        'Authorization': user2ApiKey,
                        'Origin': 'http://localhost'
                    }
                )

            # Then
            assert response.status_code == 200

        @clean_database
        def when_user_has_rights_and_regular_offer_and_token_in_lower_case(self, app):
            # Given
            user = create_user(email='user@example.com', public_name='John Doe')
            admin_user = create_user(email='admin@example.com')
            offerer = create_offerer()
            user_offerer = create_user_offerer(admin_user, offerer)
            venue = create_venue(offerer)
            offer = create_offer_with_event_product(venue, event_name='Event Name', event_type=EventType.CINEMA)
            event_occurrence = create_event_occurrence(offer)
            stock = create_stock_from_event_occurrence(event_occurrence, price=0)
            booking = create_booking(user=user, stock=stock, venue=venue)
            repository.save(user_offerer, booking)
            booking_token = booking.token.lower()
            url = f'/v2/bookings/token/{booking_token}'

            # When
            response = TestClient(app.test_client()) \
                .with_auth('admin@example.com') \
                .get(url)

            # Then
            assert response.status_code == 200

        @clean_database
        def when_non_standard_origin_header(self, app):
            # Given
            user = create_user()
            admin_user = create_user(email='admin@example.com')
            offerer = create_offerer()
            user_offerer = create_user_offerer(admin_user, offerer)
            venue = create_venue(offerer)
            stock = create_stock_with_event_offer(offerer, venue, price=0)
            booking = create_booking(user=user, stock=stock, venue=venue)
            repository.save(booking, user_offerer)
            url = f'/v2/bookings/token/{booking.token}'

            # When
            response = TestClient(app.test_client()) \
                .with_auth('admin@example.com') \
                .get(
                    url,
                    headers={
                        'origin': 'http://random_header.fr'
                    }
                )

            # Then
            assert response.status_code == 200

        @clean_database
        def when_activation_event_and_user_has_rights(self, app):
            # Given
            user = create_user(date_of_birth=datetime(2001, 2, 1), email='user@example.com',
                               phone_number='0698765432')
            admin_user = create_user(can_book_free_offers=False, email='admin@example.com', is_admin=True)
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_offer_with_event_product(venue, event_name="Offre d'activation", event_type=EventType.ACTIVATION)
            event_occurrence = create_event_occurrence(offer)
            stock = create_stock_from_event_occurrence(event_occurrence, price=0)
            booking = create_booking(user=user, stock=stock, venue=venue)
            repository.save(admin_user, booking)
            url = f'/v2/bookings/token/{booking.token}'

            # When
            response = TestClient(app.test_client()) \
                .with_auth('admin@example.com') \
                .get(url)

            # Then
            assert response.status_code == 200

    class Returns401:
        def when_user_not_logged_in_and_doesnt_give_api_key(self, app):
            # Given
            url = '/v2/bookings/token/MOCKED_TOKEN'

            # When
            response = TestClient(app.test_client()) \
                .get(url)

            # Then
            assert response.status_code == 401

        def when_user_not_logged_in_and_given_api_key_does_not_exist(self, app):
            # Given
            url = '/v2/bookings/token/FAKETOKEN'

            # When
            response = TestClient(app.test_client()) \
                .get(
                    url,
                    headers={
                        'Authorization': 'Bearer WrongApiKey1234567',
                        'Origin': 'http://localhost'
                    }
                )

            # Then
            assert response.status_code == 401

        @clean_database
        def when_user_not_logged_in_and_existing_api_key_given_with_no_bearer_prefix(self, app):
            # Given
            pro = create_user(email='offerer@example.com')
            offerer = create_offerer()
            user_offerer = create_user_offerer(pro, offerer)
            repository.save(user_offerer)
            offerer_api_key = create_api_key(offerer_id=offerer.id)
            repository.save(offerer_api_key)
            url = f'/v2/bookings/token/FAKETOKEN'

            # When
            response = TestClient(app.test_client()) \
                .get(
                    url,
                    headers={
                        'Authorization': API_KEY_VALUE,
                        'Origin': 'http://localhost'
                    }
                )

            # Then
            assert response.status_code == 401

    class Returns403:
        @clean_database
        def when_user_doesnt_have_rights_and_token_exists(self, app):
            # Given
            user = create_user(email='user@example.com')
            querying_user = create_user(email='querying@example.com')
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_offer_with_event_product(venue, event_name='Event Name')
            event_occurrence = create_event_occurrence(offer)
            stock = create_stock_from_event_occurrence(event_occurrence, price=0)
            booking = create_booking(user=user, stock=stock, venue=venue)
            repository.save(querying_user, booking)
            url = f'/v2/bookings/token/{booking.token}'

            # When
            response = TestClient(app.test_client()) \
                .with_auth('querying@example.com') \
                .get(url)

            # Then
            assert response.status_code == 403
            assert response.json['user'] == ["Vous n'avez pas les droits suffisants pour valider cette contremarque."]

        @clean_database
        def when_given_api_key_not_related_to_booking_offerer(self, app):
            # Given
            user = create_user(email='user@example.com')
            admin_user = create_user(email='admin@example.com')
            offerer = create_offerer()
            offerer2 = create_offerer(siren='987654321')
            user_offerer = create_user_offerer(admin_user, offerer)
            venue = create_venue(offerer)
            offer = create_offer_with_event_product(venue, event_name='Event Name')
            event_occurrence = create_event_occurrence(offer)
            stock = create_stock_from_event_occurrence(event_occurrence, price=0)
            booking = create_booking(user=user, stock=stock, venue=venue)
            repository.save(admin_user, booking, user_offerer, offerer2)
            offerer2ApiKey = create_api_key(offerer_id=offerer2.id)
            repository.save(offerer2ApiKey)
            user2ApiKey = f'Bearer {offerer2ApiKey.value}'
            url = f'/v2/bookings/token/{booking.token}'

            # When
            response = TestClient(app.test_client()) \
                .get(
                    url,
                    headers={
                        'Authorization': user2ApiKey,
                        'Origin': 'http://localhost'
                    }
                )

            # Then
            assert response.status_code == 403
            assert response.json['user'] == ["Vous n'avez pas les droits suffisants pour valider cette contremarque."]

        @clean_database
        def when_booking_is_on_stock_with_beginning_datetime_in_more_than_72_hours(self, app):
            # Given
            in_73_hours = datetime.utcnow() + timedelta(hours=73)
            in_74_hours = datetime.utcnow() + timedelta(hours=74)
            in_72_hours = datetime.utcnow() + timedelta(hours=72)
            user = create_user(email='user@example.com')
            admin_user = create_user(email='admin@example.com')
            offerer = create_offerer()
            user_offerer = create_user_offerer(admin_user, offerer)
            venue = create_venue(offerer)
            stock = create_stock_with_event_offer(offerer, venue, price=0, beginning_datetime=in_73_hours,
                                                  end_datetime=in_74_hours, booking_limit_datetime=in_72_hours)
            booking = create_booking(user=user, stock=stock, venue=venue)
            repository.save(admin_user, booking, user_offerer)
            url = f'/v2/bookings/token/{booking.token}'

            # When
            response = TestClient(app.test_client()) \
                .with_auth('admin@example.com') \
                .get(url)

            # Then
            assert response.status_code == 403
            assert response.json['beginningDatetime'] == ["Vous ne pouvez pas valider cette contremarque plus de 72h avant le début de l'évènement"]

    class Returns404:
        @clean_database
        def when_booking_is_not_provided_at_all(self, app):
            # Given
            user = create_user(email='user@example.com')
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_offer_with_event_product(venue, event_name='Event Name')
            event_occurrence = create_event_occurrence(offer)
            stock = create_stock_from_event_occurrence(event_occurrence, price=0)
            booking = create_booking(user=user, stock=stock, venue=venue)
            repository.save(booking)
            url = '/v2/bookings/token/'

            # When
            response = TestClient(app.test_client()) \
                .get(url)

            # Then
            assert response.status_code == 404

        @clean_database
        def when_token_user_has_rights_but_token_not_found(self, app):
            # Given
            admin_user = create_user(email='admin@example.com')
            repository.save(admin_user)
            url = '/v2/bookings/token/12345'

            # When
            response = TestClient(app.test_client()) \
                .with_auth('admin@example.com') \
                .get(url)

            # Then
            assert response.status_code == 404
            assert response.json['global'] == ["Cette contremarque n'a pas été trouvée"]

        @clean_database
        def when_user_has_api_key_but_token_not_found(self, app):
            # Given
            user = create_user(email='user@example.com')
            admin_user = create_user(email='admin@example.com')
            offerer = create_offerer()
            user_offerer = create_user_offerer(admin_user, offerer)
            venue = create_venue(offerer)
            offer = create_offer_with_event_product(venue, event_name='Event Name')
            event_occurrence = create_event_occurrence(offer)
            stock = create_stock_from_event_occurrence(event_occurrence, price=0)
            booking = create_booking(user=user, stock=stock, venue=venue)
            repository.save(admin_user, booking, user_offerer)
            offererApiKey = create_api_key(offerer_id=offerer.id)
            repository.save(offererApiKey)
            user2ApiKey = f'Bearer {offererApiKey.value}'
            url = '/v2/bookings/token/12345'

            # When
            response = TestClient(app.test_client()) \
                .get(
                    url,
                    headers={
                        'Authorization': user2ApiKey,
                        'Origin': 'http://localhost'
                    }
                )

            # Then
            assert response.status_code == 404
            assert response.json['global'] == ["Cette contremarque n'a pas été trouvée"]

    class Returns410:
        @clean_database
        def when_booking_is_already_validated(self, app):
            # Given
            user = create_user(email='user@example.com')
            admin_user = create_user(email='admin@example.com')
            offerer = create_offerer()
            user_offerer = create_user_offerer(admin_user, offerer)
            venue = create_venue(offerer)
            stock = create_stock_with_thing_offer(offerer, venue, offer=None, price=0)
            booking = create_booking(user=user, stock=stock, is_used=True, venue=venue)
            repository.save(admin_user, booking, user_offerer)
            offererApiKey = create_api_key(offerer_id=offerer.id)
            repository.save(offererApiKey)
            user2ApiKey = f'Bearer {offererApiKey.value}'
            url = f'/v2/bookings/token/{booking.token}'

            # When
            response = TestClient(app.test_client()) \
                .get(
                    url,
                    headers={
                        'Authorization': user2ApiKey,
                        'Origin': 'http://localhost'
                    }
                )

            # Then
            assert response.status_code == 410
            assert response.json['booking'] == ['Cette réservation a déjà été validée']

        @clean_database
        def when_booking_is_cancelled(self, app):
            # Given
            user = create_user(email='user@example.com')
            admin_user = create_user(email='admin@example.com')
            offerer = create_offerer()
            user_offerer = create_user_offerer(admin_user, offerer)
            venue = create_venue(offerer)
            stock = create_stock_with_thing_offer(offerer, venue, offer=None, price=0)
            booking = create_booking(user=user, stock=stock, is_cancelled=True, venue=venue)
            repository.save(admin_user, booking, user_offerer)
            offererApiKey = create_api_key(offerer_id=offerer.id)
            repository.save(offererApiKey)
            user2ApiKey = f'Bearer {offererApiKey.value}'
            url = f'/v2/bookings/token/{booking.token}'

            # When
            response = TestClient(app.test_client()) \
                .get(
                    url,
                    headers={
                        'Authorization': user2ApiKey,
                        'Origin': 'http://localhost'
                    }
                )

            # Then
            assert response.status_code == 410
            assert response.json['booking'] == ['Cette réservation a été annulée']
