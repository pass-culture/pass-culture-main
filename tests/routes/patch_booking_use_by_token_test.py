from unittest.mock import patch, Mock

from domain.user_emails import send_activation_email
from models import PcObject, EventType, Deposit, Booking, User
from tests.conftest import clean_database, TestClient
from tests.test_utils import create_deposit, create_venue, create_offerer, \
    create_user, create_booking, \
    create_user_offerer, create_stock, \
    create_offer_with_thing_product
from tests.test_utils import create_api_key, create_stock_with_event_offer
from utils.token import random_token

API_KEY_VALUE = random_token(64)


class Patch:
    class Returns204:
        class WithApiKeyAuthTest:
            @clean_database
            def when_api_key_is_provided_and_rights_and_regular_offer(self, app):
                # Given
                user = create_user()
                offerer = create_offerer()
                venue = create_venue(offerer)
                stock = create_stock_with_event_offer(offerer, venue, price=0)
                booking = create_booking(user, stock, venue=venue)
                PcObject.save(booking, offerer)
                booking_id = booking.id

                offerer_api_key = create_api_key(offerer, API_KEY_VALUE)
                PcObject.save(offerer_api_key)
                user2ApiKey = 'Bearer ' + offerer_api_key.value

                # When
                url = '/v2/bookings/use/token/{}'.format(booking.token)
                response = TestClient(app.test_client()).patch(
                    url,
                    headers={
                        'Authorization': user2ApiKey,
                        'Origin': 'http://localhost'
                    }
                )

                # Then
                assert response.status_code == 204
                assert Booking.query.get(booking_id).isUsed is True

            @clean_database
            def expect_booking_to_be_used_with_non_standard_origin_header(self, app):
                # Given
                user = create_user()
                pro_user = create_user(email='pro@email.fr')
                offerer = create_offerer()
                user_offerer = create_user_offerer(pro_user, offerer)
                venue = create_venue(offerer)
                stock = create_stock_with_event_offer(offerer, venue, price=0)
                booking = create_booking(user, stock, venue=venue)
                PcObject.save(booking, user_offerer)
                booking_id = booking.id

                offerer_api_key = create_api_key(offerer, API_KEY_VALUE)
                PcObject.save(offerer_api_key)
                user2ApiKey = 'Bearer ' + offerer_api_key.value

                # When
                url = '/v2/bookings/use/token/{}'.format(booking.token)
                response = TestClient(app.test_client()).patch(
                    url,
                    headers={
                        'Authorization': user2ApiKey,
                        'Origin': 'http://random_header.fr'
                    }
                )

                # Then
                assert response.status_code == 204
                assert Booking.query.get(booking_id).isUsed is True

        class WithBasicAuthTest:
            @clean_database
            def when_user_is_logged_in_and_regular_offer(self, app):
                # Given
                user = create_user()
                pro_user = create_user(email='pro@email.fr')
                offerer = create_offerer()
                user_offerer = create_user_offerer(pro_user, offerer)
                venue = create_venue(offerer)
                stock = create_stock_with_event_offer(offerer, venue, price=0)
                booking = create_booking(user, stock, venue=venue)
                PcObject.save(booking, user_offerer)
                booking_id = booking.id

                # When
                url = '/v2/bookings/use/token/{}'.format(booking.token)
                response = TestClient(app.test_client()).with_auth(
                    'pro@email.fr').patch(url)

                # Then
                assert response.status_code == 204
                assert Booking.query.get(booking_id).isUsed is True

            @clean_database
            def when_user_is_logged_in_expect_booking_with_token_in_lower_case_to_be_used(self, app):
                # Given
                user = create_user()
                pro_user = create_user(email='pro@email.fr')
                offerer = create_offerer()
                user_offerer = create_user_offerer(pro_user, offerer)
                venue = create_venue(offerer)
                stock = create_stock_with_event_offer(offerer, venue, price=0)
                booking = create_booking(user, stock, venue=venue)
                PcObject.save(booking, user_offerer)
                booking_id = booking.id
                booking_token = booking.token.lower()

                # When
                url = '/v2/bookings/use/token/{}'.format(booking_token)
                response = TestClient(app.test_client()).with_auth(
                    'pro@email.fr').patch(url)

                # Then
                assert response.status_code == 204
                assert Booking.query.get(booking_id).isUsed is True

            @clean_database
            def when_admin_user_is_logged_in_expect_activation_booking_to_be_used_and_linked_user_to_be_able_to_book(self, app):
                # Given
                user = create_user(can_book_free_offers=False, is_admin=False)
                admin_user = create_user(
                    email='pro@email.fr', can_book_free_offers=False, is_admin=True)
                offerer = create_offerer()
                user_offerer = create_user_offerer(admin_user, offerer)
                venue = create_venue(offerer)
                stock = create_stock_with_event_offer(
                    offerer, venue, price=0, event_type=EventType.ACTIVATION)
                booking = create_booking(user, stock, venue=venue)
                PcObject.save(booking, user_offerer)
                user_id = user.id

                # When
                url = '/v2/bookings/use/token/{}'.format(booking.token)
                response = TestClient(app.test_client()).with_auth(
                    'pro@email.fr').patch(url)

                # Then
                user = User.query.get(user_id)
                assert response.status_code == 204
                assert user.canBookFreeOffers is True
                assert user.deposits[0].amount == 500

            @clean_database
            def when_admin_user_is_logged_in_expect_to_send_notification_email(self, app):
                # Given
                user = create_user(email='user@email.fr')
                admin_user = create_user(
                    email='pro@email.fr', can_book_free_offers=False, is_admin=True)
                offerer = create_offerer()
                user_offerer = create_user_offerer(admin_user, offerer)
                venue = create_venue(offerer)
                stock = create_stock_with_event_offer(
                    offerer, venue, price=0, event_type=EventType.ACTIVATION)
                booking = create_booking(user, stock, venue=venue)
                PcObject.save(booking, user_offerer)
                user_id = user.id

                mocked_send_email = Mock()
                return_value = Mock()
                mocked_send_email.return_value = return_value

                # When
                url = '/v2/bookings/use/token/{}'.format(booking.token)
                with patch('utils.mailing.feature_send_mail_to_users_enabled', return_value=True):
                    send_activation_email(user, mocked_send_email)
                response = TestClient(app.test_client()).with_auth(
                    'pro@email.fr').patch(url)

                # Then
                user = User.query.get(user_id)
                assert response.status_code == 204
                assert user.canBookFreeOffers is True
                assert user.deposits[0].amount == 500
                mocked_send_email.assert_called_once()
                args = mocked_send_email.call_args

    class Returns400:
        @clean_database
        def when_there_is_not_enough_available_stock_to_validate_a_booking(self, app):
            # Given
            user = create_user()
            pro_user = create_user(email='pro@email.fr', is_admin=False)
            offerer = create_offerer()
            user_offerer = create_user_offerer(pro_user, offerer)
            venue = create_venue(offerer)
            stock = create_stock_with_event_offer(offerer, venue, price=0)
            booking = create_booking(user, stock, venue=venue)
            PcObject.save(booking, user_offerer)

            stock.available = 0
            PcObject.save(stock)

            # When
            url = '/v2/bookings/use/token/{}'.format(booking.token)
            response = TestClient(app.test_client()).with_auth(
                'pro@email.fr').patch(url)

            # Then
            assert response.status_code == 400
            assert response.json['global'] == [
                "La quantité disponible pour cette offre est atteinte."]

    class Returns401:
        @clean_database
        def when_user_not_logged_in_and_doesnt_give_api_key(self, app):
            # Given
            user = create_user(email='user@email.fr')
            offerer = create_offerer()
            venue = create_venue(offerer)
            stock = create_stock_with_event_offer(offerer, venue, price=0)
            booking = create_booking(user, stock, venue=venue)

            PcObject.save(booking)

            # When
            url = '/v2/bookings/use/token/{}'.format(booking.token)
            response = TestClient(app.test_client()).patch(url)

            # Then
            assert response.status_code == 401

        @clean_database
        def when_user_not_logged_in_and_not_existing_api_key_given(self, app):
            # Given
            user = create_user(email='user@email.fr')
            pro_user = create_user(email='pro@email.fr')
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_offer_with_thing_product(venue)
            stock = create_stock(offer=offer, price=0)
            booking = create_booking(user, stock, venue=venue)

            PcObject.save(pro_user, booking)

            # When
            url = '/v2/bookings/use/token/{}'.format(booking.token)
            response = TestClient(app.test_client()).patch(url, headers={
                'Authorization': 'Bearer WrongApiKey1234567',
                'Origin': 'http://localhost'})

            # Then
            assert response.status_code == 401

    class Returns403:
        class WithApiKeyAuthTest:
            @clean_database
            def when_api_key_given_not_related_to_booking_offerer(self, app):
                # Given
                user = create_user(email='user@email.fr')
                pro_user = create_user(email='pro@email.fr')
                offerer = create_offerer()
                offerer2 = create_offerer(siren='987654321')
                user_offerer = create_user_offerer(pro_user, offerer)
                venue = create_venue(offerer)
                stock = create_stock_with_event_offer(
                    offerer, venue, price=0, event_type=EventType.ACTIVATION)
                booking = create_booking(user, stock, venue=venue)

                PcObject.save(pro_user, booking, user_offerer, offerer2)

                offerer_api_key = create_api_key(offerer2, API_KEY_VALUE)
                PcObject.save(offerer_api_key)

                user2ApiKey = 'Bearer ' + offerer_api_key.value

                # When
                url = '/v2/bookings/use/token/{}'.format(booking.token)
                response = TestClient(app.test_client()).patch(
                    url,
                    headers={
                        'Authorization': user2ApiKey,
                        'Origin': 'http://localhost'}
                )

                # Then
                assert response.status_code == 403
                assert response.json['user'] == [
                    "Vous n'avez pas les droits suffisants pour valider cette contremarque."]

        class WithBasicAuthTest:
            @clean_database
            def when_user_is_not_attached_to_linked_offerer(self, app):
                # Given
                user = create_user()
                pro_user = create_user(email='pro@email.fr')
                offerer = create_offerer()
                venue = create_venue(offerer)
                stock = create_stock_with_event_offer(offerer, venue, price=0)
                booking = create_booking(user, stock, venue=venue)
                PcObject.save(booking, pro_user)
                booking_id = booking.id
                url = '/v2/bookings/use/token/{}'.format(
                    booking.token, user.email)

                # When
                response = TestClient(app.test_client()).with_auth(
                    'pro@email.fr').patch(url)

                # Then
                assert response.status_code == 403
                assert response.json['user'] == [
                    "Vous n'avez pas les droits suffisants pour valider cette contremarque."]
                assert Booking.query.get(booking_id).isUsed is False

            @clean_database
            def when_user_is_not_admin_and_tries_to_patch_activation_offer(self, app):
                # Given
                user = create_user()
                pro_user = create_user(email='pro@email.fr')
                offerer = create_offerer()
                user_offerer = create_user_offerer(pro_user, offerer)
                venue = create_venue(offerer)
                stock = create_stock_with_event_offer(
                    offerer, venue, price=0, event_type=EventType.ACTIVATION)
                booking = create_booking(user, stock, venue=venue)
                PcObject.save(booking, user_offerer)

                # When
                url = '/v2/bookings/use/token/{}'.format(booking.token)
                response = TestClient(app.test_client()).with_auth(
                    'pro@email.fr').patch(url)

                # Then
                assert response.status_code == 403
                assert response.json['user'] == [
                    "Vous n'avez pas les droits suffisants pour valider cette contremarque."]

    class Returns404:
        @clean_database
        def when_booking_is_not_provided_at_all(self, app):
            # Given
            user = create_user(email='user@email.fr')
            offerer = create_offerer()
            venue = create_venue(offerer)
            stock = create_stock_with_event_offer(offerer, venue, price=0)
            booking = create_booking(user, stock, venue=venue)

            PcObject.save(booking)

            # When
            url = '/v2/bookings/use/token/'
            response = TestClient(app.test_client()).patch(url)

            # Then
            assert response.status_code == 404

        class WithApiKeyAuthTest:
            @clean_database
            def when_api_key_is_provided_and_booking_does_not_exist(self, app):
                # Given
                user = create_user()
                offerer = create_offerer()
                venue = create_venue(offerer)
                stock = create_stock_with_event_offer(offerer, venue, price=0)
                booking = create_booking(user, stock, venue=venue)
                PcObject.save(booking)

                offerer_api_key = create_api_key(offerer, API_KEY_VALUE)
                PcObject.save(offerer_api_key)

                user2ApiKey = 'Bearer ' + offerer_api_key.value

                # When
                url = '/v2/bookings/use/token/{}'.format('456789')
                response = TestClient(app.test_client()).patch(
                    url,
                    headers={
                        'Authorization': user2ApiKey,
                        'Origin': 'http://localhost'
                    }
                )

                # Then
                assert response.status_code == 404
                assert response.json['global'] == [
                    "Cette contremarque n'a pas été trouvée"]

        class WithBasicAuthTest:
            @clean_database
            def when_user_is_logged_in_and_booking_does_not_exist(self, app):
                # Given
                user = create_user()
                pro_user = create_user(email='pro@email.fr')
                offerer = create_offerer()
                user_offerer = create_user_offerer(pro_user, offerer)
                venue = create_venue(offerer)
                stock = create_stock_with_event_offer(offerer, venue, price=0)
                booking = create_booking(user, stock, venue=venue)
                PcObject.save(booking, user_offerer)

                # When
                url = '/v2/bookings/use/token/{}'.format('123456')
                response = TestClient(app.test_client()).with_auth(
                    'pro@email.fr').patch(url)

                # Then
                assert response.status_code == 404
                assert response.json['global'] == [
                    "Cette contremarque n'a pas été trouvée"]

    class Returns405:
        class WhenLoggedUserIsAdmin:
            @clean_database
            def expect_no_new_deposits_when_the_linked_user_has_been_already_activated(self, app):
                # Given
                user = create_user(email='user@email.fr',
                                   can_book_free_offers=False)
                deposit = create_deposit(user, amount=0)

                admin_user = create_user(
                    email='admin@email.fr', can_book_free_offers=False, is_admin=True)

                offerer = create_offerer()
                admin_user_offerer = create_user_offerer(admin_user, offerer)
                venue = create_venue(offerer)
                activation_offer_stock = create_stock_with_event_offer(
                    offerer, venue, price=0, event_type=EventType.ACTIVATION)

                booking = create_booking(
                    user, activation_offer_stock, venue=venue)

                PcObject.save(booking, admin_user_offerer, deposit)

                user_id = user.id

                # When

                url = '/v2/bookings/use/token/{}'.format(booking.token)
                response = TestClient(app.test_client()).with_auth(
                    'admin@email.fr').patch(url)

                # Then
                deposits_for_user = Deposit.query.filter_by(
                    userId=user_id).all()
                assert response.status_code == 405
                assert response.json['user'] == [
                    "Cet utilisateur a déjà crédité son pass Culture"]
                assert len(deposits_for_user) == 1
                assert deposits_for_user[0].amount == 0

    class Returns410:
        class WithBasicAuthTest:
            @clean_database
            def when_user_is_logged_in_and_booking_has_been_cancelled_already(self, app):
                # Given
                user = create_user()
                pro_user = create_user(email='pro@email.fr')
                offerer = create_offerer()
                user_offerer = create_user_offerer(pro_user, offerer)
                venue = create_venue(offerer)
                stock = create_stock_with_event_offer(offerer, venue, price=0)
                booking = create_booking(user, stock, venue=venue)
                booking.isCancelled = True
                PcObject.save(booking, user_offerer)
                booking_id = booking.id

                # When
                url = '/v2/bookings/use/token/{}'.format(booking.token)
                response = TestClient(app.test_client()).with_auth(
                    'pro@email.fr').patch(url)

                # Then
                assert response.status_code == 410
                assert response.json['booking'] == [
                    'Cette réservation a été annulée']
                assert Booking.query.get(booking_id).isUsed is False

            @clean_database
            def when_user_is_logged_in_and_booking_has_been_validated_already(self, app):
                # Given
                user = create_user()
                pro_user = create_user(email='pro@email.fr')
                offerer = create_offerer()
                user_offerer = create_user_offerer(pro_user, offerer)
                venue = create_venue(offerer)
                stock = create_stock_with_event_offer(offerer, venue, price=0)
                booking = create_booking(user, stock, venue=venue)
                booking.isUsed = True
                PcObject.save(booking, user_offerer)
                booking_id = booking.id

                # When
                url = '/v2/bookings/use/token/{}'.format(booking.token)
                response = TestClient(app.test_client()).with_auth(
                    'pro@email.fr').patch(url)

                # Then
                assert response.status_code == 410
                assert response.json['booking'] == [
                    'Cette réservation a déjà été validée']
                assert Booking.query.get(booking_id).isUsed is True

        class WithApiKeyAuthTest:
            @clean_database
            def when_api_key_is_provided_and_booking_has_been_cancelled_already(self, app):
                # Given
                user = create_user()
                pro_user = create_user(email='pro@email.fr')
                offerer = create_offerer()
                user_offerer = create_user_offerer(pro_user, offerer)
                venue = create_venue(offerer)
                stock = create_stock_with_event_offer(offerer, venue, price=0)
                booking = create_booking(user, stock, venue=venue)
                booking.isCancelled = True
                PcObject.save(booking, user_offerer)
                booking_id = booking.id

                # When
                url = '/v2/bookings/use/token/{}'.format(booking.token)
                response = TestClient(app.test_client()).with_auth(
                    'pro@email.fr').patch(url)

                # Then
                assert response.status_code == 410
                assert response.json['booking'] == [
                    'Cette réservation a été annulée']
                assert Booking.query.get(booking_id).isUsed is False

            @clean_database
            def when_api_key_is_provided_and_booking_has_been_validated_already(self, app):
                # Given
                user = create_user()
                pro_user = create_user(email='pro@email.fr')
                offerer = create_offerer()
                user_offerer = create_user_offerer(pro_user, offerer)
                venue = create_venue(offerer)
                stock = create_stock_with_event_offer(offerer, venue, price=0)
                booking = create_booking(user, stock, venue=venue)
                booking.isUsed = True
                PcObject.save(booking, user_offerer)
                booking_id = booking.id

                # When
                url = '/v2/bookings/use/token/{}'.format(booking.token)
                response = TestClient(app.test_client()).with_auth(
                    'pro@email.fr').patch(url)

                # Then
                assert response.status_code == 410
                assert response.json['booking'] == [
                    'Cette réservation a déjà été validée']
                assert Booking.query.get(booking_id).isUsed is True
