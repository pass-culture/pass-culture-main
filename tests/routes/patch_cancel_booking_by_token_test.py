from datetime import datetime, timedelta

from models import ApiKey, PcObject, EventType, Booking
from tests.conftest import clean_database, TestClient
from tests.test_utils import create_stock_with_thing_offer, \
    create_venue, create_offerer, \
    create_user, create_booking, create_offer_with_event_product, \
    create_event_occurrence, create_stock_from_event_occurrence, create_user_offerer, create_stock_with_event_offer, \
    create_stock, create_deposit
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
            pro_with_user = create_user(public_name='Mr Books', email='Mr Books@example.net')
            library = create_offerer(siren='793875030')
            user_offerer = create_user_offerer(pro_with_user, library)
            bookshop = create_venue(library)
            book_offer = create_offer_with_event_product(bookshop)
            stock = create_stock(offer=book_offer)

            user = create_user(public_name='J.F', email='j.f@example.net')
            deposit = create_deposit(user)
            booking = create_booking(user, stock, venue=bookshop)

            PcObject.save(booking, user_offerer)
            api_key = random_token(64)
            offerer_api_key = create_api_key_for_offerer(library, api_key)
            PcObject.save(offerer_api_key)

            # When
            response = TestClient(app.test_client()).patch(
                '/v2/bookings/cancel/token/{}'.format(booking.token),
                headers={
                    'Authorization': 'Bearer ' + api_key,
                    'Origin': 'http://localhost'
                })

            # Then
            assert response.status_code == 204

        @clean_database
        def test_should_mark_the_booking_as_cancelled(self, app):
            # Given
            pro_with_user = create_user(public_name='Mr Books', email='Mr Books@example.net')
            library = create_offerer(siren='793875030')
            user_offerer = create_user_offerer(pro_with_user, library)
            bookshop = create_venue(library)
            book_offer = create_offer_with_event_product(bookshop)
            stock = create_stock(offer=book_offer)

            user = create_user(public_name='J.F', email='j.f@example.net')
            deposit = create_deposit(user)
            booking = create_booking(user, stock, venue=bookshop)

            PcObject.save(booking, user_offerer)
            api_key = random_token(64)
            offerer_api_key = create_api_key_for_offerer(library, api_key)
            PcObject.save(offerer_api_key)

            # When
            TestClient(app.test_client()).patch(
                '/v2/bookings/cancel/token/{}'.format(booking.token),
                headers={
                    'Authorization': 'Bearer ' + api_key,
                    'Origin': 'http://localhost'
                })

            # Then
            updated_booking = Booking.query.first()
            assert updated_booking.isCancelled

    class Returns401:
        @clean_database
        def when_not_authenticated_used_api_key_or_login(self, app):
            # Given
            user = create_user(public_name='J.F', email='j.f@example.net')
            deposit = create_deposit(user)
            offerer = create_offerer()
            user_offerer = create_user_offerer(user, offerer)
            venue = create_venue(offerer)
            offer = create_offer_with_event_product(venue)
            stock = create_stock(offer=offer)
            booking = create_booking(user, stock, venue=venue)
            PcObject.save(user_offerer, booking)

            # When
            url = '/v2/bookings/cancel/token/{}'.format(booking.token)
            response = TestClient(app.test_client()).patch(url)

            # Then
            assert response.status_code == 401

        @clean_database
        def when_giving_an_api_key_that_does_not_exists(self, app):
            # Given
            user = create_user(public_name='J.F', email='j.f@example.net')
            deposit = create_deposit(user)
            offerer = create_offerer()
            user_offerer = create_user_offerer(user, offerer)
            venue = create_venue(offerer)
            offer = create_offer_with_event_product(venue)
            stock = create_stock(offer=offer)
            booking = create_booking(user, stock, venue=venue)
            PcObject.save(user_offerer, booking)

            # When
            url = '/v2/bookings/cancel/token/{}'.format(booking.token)
            response = TestClient(app.test_client()).patch(url, headers={
                'Authorization': 'Bearer WrongApiKey1234567',
                'Origin': 'http://localhost'
            })

            # Then
            # TODO Add an assert on payload message
            assert response.status_code == 401

    class Returns403:
        @clean_database
        def when_the_api_key_is_not_linked_to_the_right_offerer(self, app):
            # Given
            pro_with_user = create_user(public_name='Mr Books', email='Mr Books@example.net')
            library = create_offerer(siren='793875030')
            user_offerer = create_user_offerer(pro_with_user, library)
            bookshop = create_venue(library)
            book_offer = create_offer_with_event_product(bookshop)
            stock = create_stock(offer=book_offer)

            user = create_user(public_name='J.F', email='j.f@example.net')
            deposit = create_deposit(user)
            booking = create_booking(user, stock, venue=bookshop)

            PcObject.save(booking, user_offerer)

            offerer_with_api_key = create_offerer()
            PcObject.save(offerer_with_api_key)

            api_key = random_token(64)
            offerer_api_key = create_api_key_for_offerer(offerer_with_api_key, api_key)

            PcObject.save(offerer_api_key)

            # When
            response = TestClient(app.test_client()).patch(
                '/v2/bookings/cancel/token/{}'.format(booking.token),
                headers={
                    'Authorization': 'Bearer ' + api_key,
                    'Origin': 'http://localhost'
                })

            # Then
            assert response.status_code == 403
            assert response.json['global'] == ["Vous n'avez pas les droits suffisants pour éditer cette contremarque."]

        @clean_database
        def when_the_logged_user_has_not_rights_on_offerer(self, app):
            # Given
            pro_with_user = create_user(public_name='Mr Books', email='mr.book@example.net')
            library = create_offerer(siren='793875030')
            user_offerer = create_user_offerer(pro_with_user, library)
            bookshop = create_venue(library)
            book_offer = create_offer_with_event_product(bookshop)
            stock = create_stock(offer=book_offer)

            user = create_user(public_name='J.F', email='j.f@example.net')
            deposit = create_deposit(user)
            booking = create_booking(user, stock, venue=bookshop)

            PcObject.save(booking, user_offerer)

            offerer_with_api_key = create_offerer()
            PcObject.save(offerer_with_api_key)

            api_key = random_token(64)
            offerer_api_key = create_api_key_for_offerer(offerer_with_api_key, api_key)

            PcObject.save(offerer_api_key)

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
                pro_with_user = create_user(public_name='Mr Books', email='Mr Books@example.net')
                library = create_offerer(siren='793875030')
                user_offerer = create_user_offerer(pro_with_user, library)
                bookshop = create_venue(library)
                book_offer = create_offer_with_event_product(bookshop)
                stock = create_stock(offer=book_offer)

                user = create_user(public_name='J.F', email='j.f@example.net')
                deposit = create_deposit(user)
                booking = create_booking(user, stock, venue=bookshop, is_used=True)

                PcObject.save(booking, user_offerer)
                api_key = random_token(64)
                offerer_api_key = create_api_key_for_offerer(library, api_key)
                PcObject.save(offerer_api_key)

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
            user = create_user(public_name='J.F', email='j.f@example.net')
            deposit = create_deposit(user)
            offerer = create_offerer()
            user_offerer = create_user_offerer(user, offerer)
            venue = create_venue(offerer)
            offer = create_offer_with_event_product(venue)
            stock = create_stock(offer=offer)
            booking = create_booking(user, stock, venue=venue)
            PcObject.save(user_offerer, booking)

            api_key = random_token(64)
            offerer_api_key = create_api_key_for_offerer(offerer, api_key)
            PcObject.save(offerer_api_key)

            # When
            response = TestClient(app.test_client()).patch('/v2/bookings/cancel/token/FAKETOKEN',
                                                           headers={
                                                               'Authorization': api_key,
                                                               'Origin': 'http://localhost'
                                                           })

            # Then
            assert response.status_code == 404
            assert response.json['global'] == ["Cette contremarque n'a pas été trouvée"]

    class Returns410:
        @clean_database
        def test_cancel_a_booking_already_cancelled_returns_an_error(self, app):
            # Given
            pro_with_user = create_user(public_name='Mr Books', email='Mr Books@example.net')
            library = create_offerer(siren='793875030')
            user_offerer = create_user_offerer(pro_with_user, library)
            bookshop = create_venue(library)
            book_offer = create_offer_with_event_product(bookshop)
            stock = create_stock(offer=book_offer)

            user = create_user(public_name='J.F', email='j.f@example.net')
            deposit = create_deposit(user)
            booking = create_booking(user, stock, venue=bookshop, is_cancelled=True)

            PcObject.save(booking, user_offerer)
            api_key = random_token(64)
            offerer_api_key = create_api_key_for_offerer(library, api_key)
            PcObject.save(offerer_api_key)

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

# class Get:
#     class Returns200:
#         @clean_database
#         def when_user_has_rights_and_regular_offer(self, app):
#             # Given
#             user = create_user(public_name='John Doe', email='user@email.fr')
#             admin_user = create_user(email='admin@email.fr')
#             offerer = create_offerer()
#             user_offerer = create_user_offerer(admin_user, offerer)
#             venue = create_venue(offerer)
#             offer = create_offer_with_event_product(venue, event_name='Event Name', event_type=EventType.CINEMA)
#             event_occurrence = create_event_occurrence(offer)
#             stock = create_stock_from_event_occurrence(event_occurrence, price=0)
#             booking = create_booking(user, stock, venue=venue)
#
#             PcObject.save(user_offerer, booking)
#             url = 'v2/bookings/token/{}'.format(booking.token)
#
#             # When
#             response = TestClient(app.test_client()).with_auth('admin@email.fr').get(url)
#
#             # Then
#             assert response.headers['Content-type'] == 'application/json'
#             assert response.status_code == 200
#
#         @clean_database
#         def when_api_key_is_provided_and_rights_and_regular_offer(self, app):
#             # Given
#             user = create_user(public_name='John Doe', email='user@email.fr')
#             user2 = create_user(public_name='Jane Doe', email='user2@email.fr')
#             offerer = create_offerer()
#             user_offerer = create_user_offerer(user2, offerer)
#             offererApiKey = ApiKey()
#             venue = create_venue(offerer)
#             offer = create_offer_with_event_product(venue, event_name='Event Name', event_type=EventType.CINEMA)
#             event_occurrence = create_event_occurrence(offer)
#             stock = create_stock_from_event_occurrence(event_occurrence, price=0)
#             booking = create_booking(user, stock, venue=venue)
#
#             PcObject.save(user_offerer, booking)
#
#             offererApiKey.value = random_token(64)
#             offererApiKey.offererId = offerer.id
#
#             PcObject.save(offererApiKey)
#
#             user2ApiKey = 'Bearer ' + offererApiKey.value
#             booking_token = booking.token.lower()
#             url = 'v2/bookings/token/{}'.format(booking_token)
#
#             # When
#             response = TestClient(app.test_client()).get(
#                 url,
#                 headers={
#                     'Authorization': user2ApiKey,
#                     'Origin': 'http://localhost'}
#             )
#
#             # Then
#             assert response.status_code == 200
#
#
#         @clean_database
#         def when_user_has_rights_and_regular_offer_and_token_in_lower_case(self, app):
#             # Given
#             user = create_user(public_name='John Doe', email='user@email.fr')
#             admin_user = create_user(email='admin@email.fr')
#             offerer = create_offerer()
#             user_offerer = create_user_offerer(admin_user, offerer)
#             venue = create_venue(offerer)
#             offer = create_offer_with_event_product(venue, event_name='Event Name', event_type=EventType.CINEMA)
#             event_occurrence = create_event_occurrence(offer)
#             stock = create_stock_from_event_occurrence(event_occurrence, price=0)
#             booking = create_booking(user, stock, venue=venue)
#
#             PcObject.save(user_offerer, booking)
#
#             booking_token = booking.token.lower()
#             url = 'v2/bookings/token/{}'.format(booking_token)
#
#             # When
#             response = TestClient(app.test_client()).with_auth('admin@email.fr').get(url)
#
#             # Then
#             assert response.status_code == 200
#
#
#         @clean_database
#         def when_activation_event_and_user_has_rights(self, app):
#             # Given
#             user = create_user(email='user@email.fr', phone_number='0698765432', date_of_birth=datetime(2001, 2, 1))
#             admin_user = create_user(email='admin@email.fr', is_admin=True, can_book_free_offers=False)
#             offerer = create_offerer()
#             venue = create_venue(offerer)
#             offer = create_offer_with_event_product(venue, event_name='Offre d\'activation',
#                                                     event_type=EventType.ACTIVATION)
#             event_occurrence = create_event_occurrence(offer)
#             stock = create_stock_from_event_occurrence(event_occurrence, price=0)
#             booking = create_booking(user, stock, venue=venue)
#
#             PcObject.save(admin_user, booking)
#
#             # When
#             response = TestClient(app.test_client()) \
#                 .with_auth('admin@email.fr') \
#                 .get('v2/bookings/token/{}'.format(booking.token))
#
#             # Then
#             assert response.status_code == 200
#
#
#     class Returns401:
#         @clean_database
#         def when_user_not_logged_in_and_doesnt_give_api_key(self, app):
#             # Given
#             user = create_user(email='user@email.fr')
#             admin_user = create_user(email='admin@email.fr')
#             offerer = create_offerer()
#             venue = create_venue(offerer)
#             offer = create_offer_with_event_product(venue, event_name='Event Name')
#             event_occurrence = create_event_occurrence(offer)
#             stock = create_stock_from_event_occurrence(event_occurrence, price=0)
#             booking = create_booking(user, stock, venue=venue)
#
#             PcObject.save(admin_user, booking)
#
#             url = 'v2/bookings/token/{}'.format(booking.token)
#
#             # When
#             response = TestClient(app.test_client()).get(url)
#
#             # Then
#             assert response.status_code == 401
#
#         @clean_database
#         def when_user_not_logged_in_and_not_existing_api_key_given(self, app):
#             # Given
#             user = create_user(email='user@email.fr')
#             admin_user = create_user(email='admin@email.fr')
#             offerer = create_offerer()
#             venue = create_venue(offerer)
#             offer = create_offer_with_event_product(venue, event_name='Event Name')
#             event_occurrence = create_event_occurrence(offer)
#             stock = create_stock_from_event_occurrence(event_occurrence, price=0)
#             booking = create_booking(user, stock, venue=venue)
#
#             PcObject.save(admin_user, booking)
#
#             url = 'v2/bookings/token/{}'.format(booking.token)
#
#             # When
#             response = TestClient(app.test_client()).get(url, headers={
#                     'Authorization': 'Bearer WrongApiKey1234567',
#                     'Origin': 'http://localhost'})
#
#             # Then
#             assert response.status_code == 401
#
#
#     class Returns403:
#         @clean_database
#         def when_user_doesnt_have_rights_and_token_exists(self, app):
#             # Given
#             user = create_user(email='user@email.fr')
#             querying_user = create_user(email='querying@email.fr')
#             offerer = create_offerer()
#             venue = create_venue(offerer)
#             offer = create_offer_with_event_product(venue, event_name='Event Name')
#             event_occurrence = create_event_occurrence(offer)
#             stock = create_stock_from_event_occurrence(event_occurrence, price=0)
#             booking = create_booking(user, stock, venue=venue)
#
#             PcObject.save(querying_user, booking)
#
#             url = 'v2/bookings/token/{}'.format(booking.token)
#
#             # When
#             response = TestClient(app.test_client()).with_auth('querying@email.fr').get(url)
#
#             # Then
#             assert response.status_code == 403
#             assert response.json['user'] == ["Vous n'avez pas les droits suffisants pour éditer cette contremarque."]
#
#         @clean_database
#         def when_api_key_given_not_related_to_booking_offerer(self, app):
#             # Given
#             user = create_user(email='user@email.fr')
#             admin_user = create_user(email='admin@email.fr')
#             offerer = create_offerer()
#             offerer2 = create_offerer(siren='987654321')
#             user_offerer = create_user_offerer(admin_user, offerer)
#
#             offererApiKey = ApiKey()
#             venue = create_venue(offerer)
#             offer = create_offer_with_event_product(venue, event_name='Event Name')
#             event_occurrence = create_event_occurrence(offer)
#             stock = create_stock_from_event_occurrence(event_occurrence, price=0)
#             booking = create_booking(user, stock, venue=venue)
#
#             PcObject.save(admin_user, booking, user_offerer, offerer2)
#
#             offererApiKey.value = random_token(64)
#             offererApiKey.offererId = offerer2.id
#
#             PcObject.save(offererApiKey)
#
#             user2ApiKey = 'Bearer ' + offererApiKey.value
#             url = 'v2/bookings/token/{}'.format(booking.token)
#
#             # When
#             response = TestClient(app.test_client()).get(
#                 url,
#                 headers={
#                     'Authorization': user2ApiKey,
#                     'Origin': 'http://localhost'}
#             )
#
#             # Then
#             assert response.status_code == 403
#             assert response.json['user'] == ["Vous n'avez pas les droits suffisants pour éditer cette contremarque."]
#
#
#         @clean_database
#         def when_booking_is_on_stock_with_beginning_datetime_in_more_than_72_hours(self, app):
#             # Given
#             in_73_hours = datetime.utcnow() + timedelta(hours=73)
#             in_74_hours = datetime.utcnow() + timedelta(hours=74)
#             in_72_hours = datetime.utcnow() + timedelta(hours=72)
#             user = create_user(email='user@email.fr')
#             admin_user = create_user(email='admin@email.fr')
#             offerer = create_offerer()
#             venue = create_venue(offerer)
#             stock = create_stock_with_event_offer(offerer, venue, price=0, beginning_datetime=in_73_hours,
#             end_datetime=in_74_hours, booking_limit_datetime=in_72_hours)
#             booking = create_booking(user, stock, venue=venue)
#
#             PcObject.save(admin_user, booking)
#
#             url = 'v2/bookings/token/{}'.format(booking.token)
#
#             # When
#             response = TestClient(app.test_client()).with_auth('admin@email.fr').get(url)
#
#             # Then
#             assert response.status_code == 403
#             assert response.json['beginningDatetime'] == [
#             'Vous ne pouvez pas valider cette contremarque plus de 72h avant le début de l\'évènement']
#
#
#     class Returns404:
#         @clean_database
#         def when_token_user_has_rights_but_token_not_found(self, app):
#             # Given
#             admin_user = create_user(email='admin@email.fr')
#             PcObject.save(admin_user)
#
#             url = 'v2/bookings/token/{}'.format('12345')
#
#             # When
#             response = TestClient(app.test_client()).with_auth('admin@email.fr').get(url)
#
#             # Then
#             assert response.status_code == 404
#             assert response.json['global'] == ["Cette contremarque n'a pas été trouvée"]
#
#         @clean_database
#         def when_user_has_api_key_but_token_not_found(self, app):
#             # Given
#             user = create_user(email='user@email.fr')
#             admin_user = create_user(email='admin@email.fr')
#             offerer = create_offerer()
#             user_offerer = create_user_offerer(admin_user, offerer)
#
#             offererApiKey = ApiKey()
#             venue = create_venue(offerer)
#             offer = create_offer_with_event_product(venue, event_name='Event Name')
#             event_occurrence = create_event_occurrence(offer)
#             stock = create_stock_from_event_occurrence(event_occurrence, price=0)
#             booking = create_booking(user, stock, venue=venue)
#
#             PcObject.save(admin_user, booking, user_offerer)
#
#             offererApiKey.value = random_token(64)
#             offererApiKey.offererId = offerer.id
#
#             PcObject.save(offererApiKey)
#
#             user2ApiKey = 'Bearer ' + offererApiKey.value
#             url = 'v2/bookings/token/{}'.format('12345')
#
#             # When
#             response = TestClient(app.test_client()).get(
#                 url,
#                 headers={
#                     'Authorization': user2ApiKey,
#                     'Origin': 'http://localhost'}
#             )
#
#             # Then
#             assert response.status_code == 404
#             assert response.json['global'] == ["Cette contremarque n'a pas été trouvée"]
#
#     class Returns410:
#         @clean_database
#         def when_booking_is_already_validated(self, app):
#             # Given
#             user = create_user(email='user@email.fr')
#             admin_user = create_user(email='admin@email.fr')
#             offerer = create_offerer()
#             user_offerer = create_user_offerer(admin_user, offerer)
#             offererApiKey = ApiKey()
#             venue = create_venue(offerer)
#             stock = create_stock_with_thing_offer(offerer, venue, offer=None, price=0)
#             booking = create_booking(user, stock, venue=venue, is_used=True)
#
#             PcObject.save(admin_user, booking, user_offerer)
#
#             offererApiKey.value = random_token(64)
#             offererApiKey.offererId = offerer.id
#
#             PcObject.save(offererApiKey)
#
#             user2ApiKey = 'Bearer ' + offererApiKey.value
#             url = 'v2/bookings/token/{}'.format(booking.token)
#
#             # When
#             response = TestClient(app.test_client()).get(
#                 url,
#                 headers={
#                     'Authorization': user2ApiKey,
#                     'Origin': 'http://localhost'}
#             )
#
#             # Then
#             assert response.status_code == 410
#             assert response.json['booking'] == ['Cette réservation a déjà été validée']
#
#         @clean_database
#         def when_booking_is_cancelled(self, app):
#             # Given
#             user = create_user(email='user@email.fr')
#             admin_user = create_user(email='admin@email.fr')
#             offerer = create_offerer()
#             user_offerer = create_user_offerer(admin_user, offerer)
#             offererApiKey = ApiKey()
#             venue = create_venue(offerer)
#             stock = create_stock_with_thing_offer(offerer, venue, offer=None, price=0)
#             booking = create_booking(user, stock, venue=venue, is_cancelled=True)
#
#             PcObject.save(admin_user, booking, user_offerer)
#
#             offererApiKey.value = random_token(64)
#             offererApiKey.offererId = offerer.id
#
#             PcObject.save(offererApiKey)
#
#             user2ApiKey = 'Bearer ' + offererApiKey.value
#             url = 'v2/bookings/token/{}'.format(booking.token)
#
#             # When
#             response = TestClient(app.test_client()).get(
#                 url,
#                 headers={
#                     'Authorization': user2ApiKey,
#                     'Origin': 'http://localhost'}
#             )
#
#             # Then
#             assert response.status_code == 410
#             assert response.json['booking'] == ['Cette réservation a été annulée']
