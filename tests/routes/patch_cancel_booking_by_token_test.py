from models import ApiKey, Booking
from repository import repository
from tests.conftest import clean_database, TestClient
from tests.model_creators.generic_creators import create_booking, create_user, create_stock, create_offerer, create_venue, \
    create_deposit, create_user_offerer
from tests.model_creators.specific_creators import create_offer_with_thing_product, create_offer_with_event_product
from utils.token import random_token


def create_api_key_for_offerer(offerer, token):
    offerer_api_key = ApiKey()
    offerer_api_key.value = token
    offerer_api_key.offererId = offerer.id
    return offerer_api_key


class Patch:
    class Returns204:
        @clean_database
        def test_should_returns_204_with_cancellation_allowed(self, app):
            # Given
            pro_user = create_user(email='Mr Books@example.net', public_name='Mr Books')
            offerer = create_offerer(siren='793875030')
            user_offerer = create_user_offerer(pro_user, offerer)
            venue = create_venue(offerer)
            book_offer = create_offer_with_event_product(venue)
            stock = create_stock(offer=book_offer)

            user = create_user(email='j.f@example.net', public_name='J.F')
            create_deposit(user)
            booking = create_booking(user=user, stock=stock, venue=venue)

            repository.save(booking, user_offerer)
            api_key = random_token(64)
            offerer_api_key = create_api_key_for_offerer(offerer, api_key)
            repository.save(offerer_api_key)

            # When
            response = TestClient(app.test_client()).patch(
                '/v2/bookings/cancel/token/{}'.format(booking.token),
                headers={
                    'Authorization': 'Bearer ' + api_key,
                    'Origin': 'http://localhost'
                })

            # Then
            assert response.status_code == 204
            updated_booking = Booking.query.first()
            assert updated_booking.isCancelled

        @clean_database
        def test_should_returns_204_with_lowercase_token(self, app):
            # Given
            pro_user = create_user(email='Mr Books@example.net', public_name='Mr Books')
            offerer = create_offerer(siren='793875030')
            user_offerer = create_user_offerer(pro_user, offerer)
            venue = create_venue(offerer)
            book_offer = create_offer_with_event_product(venue)
            stock = create_stock(offer=book_offer)

            user = create_user(email='j.f@example.net', public_name='J.F')
            create_deposit(user)
            booking = create_booking(user=user, stock=stock, venue=venue)

            repository.save(booking, user_offerer)
            api_key = random_token(64)
            offerer_api_key = create_api_key_for_offerer(offerer, api_key)
            repository.save(offerer_api_key)

            # When
            token = booking.token.lower()
            response = TestClient(app.test_client()).patch(
                '/v2/bookings/cancel/token/{}'.format(token),
                headers={
                    'Authorization': 'Bearer ' + api_key,
                    'Origin': 'http://localhost'
                })

            # Then
            assert response.status_code == 204
            updated_booking = Booking.query.first()
            assert updated_booking.isCancelled

    class Returns401:
        @clean_database
        def when_not_authenticated_used_api_key_or_login(self, app):
            # Given
            user = create_user(email='j.f@example.net', public_name='J.F')
            create_deposit(user)
            offerer = create_offerer()
            user_offerer = create_user_offerer(user, offerer)
            venue = create_venue(offerer)
            offer = create_offer_with_event_product(venue)
            stock = create_stock(offer=offer)
            booking = create_booking(user=user, stock=stock, venue=venue)
            repository.save(user_offerer, booking)

            # When
            url = '/v2/bookings/cancel/token/{}'.format(booking.token)
            response = TestClient(app.test_client()).patch(url)

            # Then
            assert response.status_code == 401

        @clean_database
        def when_giving_an_api_key_that_does_not_exists(self, app):
            # Given
            user = create_user(email='j.f@example.net', public_name='J.F')
            create_deposit(user)
            offerer = create_offerer()
            user_offerer = create_user_offerer(user, offerer)
            venue = create_venue(offerer)
            offer = create_offer_with_event_product(venue)
            stock = create_stock(offer=offer)
            booking = create_booking(user=user, stock=stock, venue=venue)
            repository.save(user_offerer, booking)

            # When
            url = '/v2/bookings/cancel/token/{}'.format(booking.token)
            wrong_api_key = 'Bearer WrongApiKey1234567'
            response = TestClient(app.test_client()).patch(url, headers={
                'Authorization': wrong_api_key,
                'Origin': 'http://localhost'
            })

            assert response.status_code == 401

    class Returns403:
        @clean_database
        def when_the_api_key_is_not_linked_to_the_right_offerer(self, app):
            # Given
            pro_user = create_user(email='Mr Books@example.net', public_name='Mr Books')
            offerer = create_offerer(siren='793875030')
            user_offerer = create_user_offerer(pro_user, offerer)
            venue = create_venue(offerer)
            book_offer = create_offer_with_event_product(venue)
            stock = create_stock(offer=book_offer)

            user = create_user(email='j.f@example.net', public_name='J.F')
            create_deposit(user)
            booking = create_booking(user=user, stock=stock, venue=venue)

            repository.save(booking, user_offerer)

            offerer_with_api_key = create_offerer()
            repository.save(offerer_with_api_key)

            api_key = random_token(64)
            offerer_api_key = create_api_key_for_offerer(offerer_with_api_key, api_key)

            repository.save(offerer_api_key)

            # When
            response = TestClient(app.test_client()).patch(
                '/v2/bookings/cancel/token/{}'.format(booking.token),
                headers={
                    'Authorization': 'Bearer ' + api_key,
                    'Origin': 'http://localhost'
                })

            # Then
            assert response.status_code == 403
            assert response.json['user'] == ["Vous n'avez pas les droits suffisants pour annuler cette réservation."]

        @clean_database
        def when_the_logged_user_has_not_rights_on_offerer(self, app):
            # Given
            pro_user = create_user(email='mr.book@example.net', public_name='Mr Books')
            offerer = create_offerer(siren='793875030')
            user_offerer = create_user_offerer(pro_user, offerer)
            venue = create_venue(offerer)
            book_offer = create_offer_with_event_product(venue)
            stock = create_stock(offer=book_offer)

            user = create_user(email='j.f@example.net', public_name='J.F')
            create_deposit(user)
            booking = create_booking(user=user, stock=stock, venue=venue)

            repository.save(booking, user_offerer)

            offerer_with_api_key = create_offerer()
            repository.save(offerer_with_api_key)

            api_key = random_token(64)
            offerer_api_key = create_api_key_for_offerer(offerer_with_api_key, api_key)

            repository.save(offerer_api_key)

            # When
            response = TestClient(app.test_client())\
                .with_auth('j.f@example.net')\
                .patch('/v2/bookings/cancel/token/{}'.format(booking.token))

            # Then
            assert response.status_code == 403
            assert response.json['global'] == ["Vous n'avez pas les droits d'accès suffisant pour accéder à cette information."]

        class WhenTheBookingIsUsed:
            @clean_database
            def test_should_prevent_a_used_booking_from_being_cancelled(self, app):
                # Given
                pro_user = create_user(email='Mr Books@example.net', public_name='Mr Books')
                offerer = create_offerer(siren='793875030')
                user_offerer = create_user_offerer(pro_user, offerer)
                venue = create_venue(offerer)
                book_offer = create_offer_with_event_product(venue)
                stock = create_stock(offer=book_offer)

                user = create_user(email='j.f@example.net', public_name='J.F')
                create_deposit(user)
                booking = create_booking(user=user, stock=stock, is_used=True, venue=venue)

                repository.save(booking, user_offerer)
                api_key = random_token(64)
                offerer_api_key = create_api_key_for_offerer(offerer, api_key)
                repository.save(offerer_api_key)

                # When
                response = TestClient(app.test_client()).patch(
                    '/v2/bookings/cancel/token/{}'.format(booking.token),
                    headers={
                        'Authorization': 'Bearer ' + api_key,
                        'Origin': 'http://localhost'
                    })

                # Then
                assert response.status_code == 403
                assert response.json['global'] == ["Impossible d\'annuler une réservation consommée"]
                updated_booking = Booking.query.first()
                assert updated_booking.isUsed
                assert updated_booking.isCancelled is False

    class Returns404:
        @clean_database
        def when_the_booking_does_not_exists(self, app):
            # Given
            user = create_user()
            create_deposit(user)
            offerer = create_offerer()
            user_offerer = create_user_offerer(user, offerer)
            venue = create_venue(offerer)
            offer = create_offer_with_event_product(venue)
            stock = create_stock(offer=offer)
            booking = create_booking(user=user, stock=stock, venue=venue)
            repository.save(user_offerer, booking)

            api_key = 'A_MOCKED_API_KEY'
            offerer_api_key = create_api_key_for_offerer(offerer, api_key)
            repository.save(offerer_api_key)

            # When
            response = TestClient(app.test_client()).patch('/v2/bookings/cancel/token/FAKETOKEN',
                                                           headers={
                                                               'Authorization': f'Bearer {api_key}',
                                                               'Origin': 'http://localhost'
                                                           })

            # Then
            assert response.status_code == 404
            assert response.json['global'] == ["Cette contremarque n'a pas été trouvée"]

    class Returns410:
        @clean_database
        def test_cancel_a_booking_already_cancelled(self, app):
            # Given
            pro_user = create_user(email='Mr Books@example.net', public_name='Mr Books')
            offerer = create_offerer(siren='793875030')
            user_offerer = create_user_offerer(pro_user, offerer)
            venue = create_venue(offerer)
            book_offer = create_offer_with_thing_product(venue)
            stock = create_stock(offer=book_offer)

            user = create_user(email='j.f@example.net', public_name='J.F')
            create_deposit(user)
            booking = create_booking(user=user, stock=stock, is_cancelled=True, venue=venue)

            repository.save(booking, user_offerer)
            api_key = random_token(64)
            offerer_api_key = create_api_key_for_offerer(offerer, api_key)
            repository.save(offerer_api_key)

            # When
            response = TestClient(app.test_client()).patch(
                '/v2/bookings/cancel/token/{}'.format(booking.token),
                headers={
                    'Authorization': 'Bearer ' + api_key,
                    'Origin': 'http://localhost'
                })

            # Then
            assert response.status_code == 410
            assert response.json['global'] == ["Cette contremarque a déjà été annulée"]
