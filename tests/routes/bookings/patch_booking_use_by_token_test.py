from unittest.mock import Mock
from unittest.mock import patch

import pytest

import pcapi.core.bookings.factories as bookings_factories
import pcapi.core.offers.factories as offers_factories
import pcapi.core.users.factories as users_factories
from pcapi.domain.user_emails import send_activation_email
from pcapi.model_creators.generic_creators import create_api_key
from pcapi.model_creators.generic_creators import create_booking
from pcapi.model_creators.generic_creators import create_deposit
from pcapi.model_creators.generic_creators import create_offerer
from pcapi.model_creators.generic_creators import create_stock
from pcapi.model_creators.generic_creators import create_user
from pcapi.model_creators.generic_creators import create_user_offerer
from pcapi.model_creators.generic_creators import create_venue
from pcapi.model_creators.specific_creators import create_offer_with_thing_product
from pcapi.model_creators.specific_creators import create_stock_with_event_offer
from pcapi.models import Booking
from pcapi.models import Deposit
from pcapi.models import EventType
from pcapi.models import UserSQLEntity
from pcapi.models import db
from pcapi.repository import repository
from pcapi.utils.token import random_token

from tests.conftest import TestClient


API_KEY_VALUE = random_token(64)


@pytest.mark.usefixtures("db_session")
class Returns204:
    class WithApiKeyAuthTest:
        def when_api_key_is_provided_and_rights_and_regular_offer(self, app):
            booking = bookings_factories.BookingFactory(token='ABCDEF')
            offerer = booking.stock.offer.venue.managingOfferer
            api_key = offers_factories.ApiKeyFactory(offerer=offerer)

            url = f'/v2/bookings/use/token/{booking.token}'
            response = TestClient(app.test_client()).patch(
                url,
                headers={
                    'Authorization': f'Bearer {api_key.value}',
                    'Origin': 'http://localhost',
                }
            )

            assert response.status_code == 204
            booking = Booking.query.one()
            assert booking.isUsed

        def expect_booking_to_be_used_with_non_standard_origin_header(self, app):
            booking = bookings_factories.BookingFactory(token='ABCDEF')
            offerer = booking.stock.offer.venue.managingOfferer
            api_key = offers_factories.ApiKeyFactory(offerer=offerer)

            url = f'/v2/bookings/use/token/{booking.token}'
            response = TestClient(app.test_client()).patch(
                url,
                headers={
                    'Authorization': f'Bearer {api_key.value}',
                    'Origin': 'http://example.com',
                }
            )

            assert response.status_code == 204
            booking = Booking.query.one()
            assert booking.isUsed

    class WithBasicAuthTest:
        def when_user_is_logged_in_and_regular_offer(self, app):
            booking = bookings_factories.BookingFactory(token='ABCDEF')
            pro_user = users_factories.UserFactory(email='pro@example.com')
            offerer = booking.stock.offer.venue.managingOfferer
            offers_factories.UserOffererFactory(user=pro_user, offerer=offerer)

            url = f'/v2/bookings/use/token/{booking.token}'
            response = TestClient(app.test_client()).with_auth('pro@example.com').patch(url)

            assert response.status_code == 204
            booking = Booking.query.one()
            assert booking.isUsed

        def when_user_is_logged_in_expect_booking_with_token_in_lower_case_to_be_used(self, app):
            booking = bookings_factories.BookingFactory(token='ABCDEF')
            pro_user = users_factories.UserFactory(email='pro@example.com')
            offerer = booking.stock.offer.venue.managingOfferer
            offers_factories.UserOffererFactory(user=pro_user, offerer=offerer)

            url = f'/v2/bookings/use/token/{booking.token.lower()}'
            response = TestClient(app.test_client()).with_auth('pro@example.com').patch(url)

            assert response.status_code == 204
            booking = Booking.query.one()
            assert booking.isUsed

        def when_admin_user_is_logged_in_expect_activation_booking_to_be_used_and_linked_user_to_be_able_to_book(self, app):
            booking = bookings_factories.BookingFactory(
                token='ABCDEF',
                stock__price=0,
                stock__offer__product__type=str(EventType.ACTIVATION),
                user__canBookFreeOffers=False,
            )
            pro_user = users_factories.UserFactory(email='pro@example.com', canBookFreeOffers=False, isAdmin=True)
            offerer = booking.stock.offer.venue.managingOfferer
            offers_factories.UserOffererFactory(user=pro_user, offerer=offerer)

            url = f'/v2/bookings/use/token/{booking.token}'
            response = TestClient(app.test_client()).with_auth('pro@example.com').patch(url)

            # Then
            assert response.status_code == 204
            user = booking.user
            assert user.canBookFreeOffers
            assert user.deposits[0].amount == 500

        def when_admin_user_is_logged_in_expect_to_send_notification_email(self, app):
            # Given
            user = create_user(email='user@email.fr', first_name='John')
            admin_user = create_user(can_book_free_offers=False, email='pro@email.fr', is_admin=True)
            offerer = create_offerer()
            user_offerer = create_user_offerer(admin_user, offerer)
            venue = create_venue(offerer)
            stock = create_stock_with_event_offer(offerer, venue, price=0, event_type=EventType.ACTIVATION)
            booking = create_booking(user=user, stock=stock, venue=venue)
            repository.save(booking, user_offerer)
            user_id = user.id

            mocked_send_email = Mock()
            return_value = Mock()
            mocked_send_email.return_value = return_value

            # When
            url = '/v2/bookings/use/token/{}'.format(booking.token)
            with patch('pcapi.utils.mailing.feature_send_mail_to_users_enabled', return_value=True):
                send_activation_email(user, mocked_send_email)
            response = TestClient(app.test_client()).with_auth('pro@email.fr').patch(url)

            # Then
            user = UserSQLEntity.query.get(user_id)
            assert response.status_code == 204
            assert user.canBookFreeOffers is True
            assert user.deposits[0].amount == 500
            mocked_send_email.assert_called_once()
            args = mocked_send_email.call_args

class Returns401:
    @pytest.mark.usefixtures("db_session")
    def when_user_not_logged_in_and_doesnt_give_api_key(self, app):
        # Given
        user = create_user(email='user@email.fr')
        offerer = create_offerer()
        venue = create_venue(offerer)
        stock = create_stock_with_event_offer(offerer, venue, price=0)
        booking = create_booking(user=user, stock=stock, venue=venue)

        repository.save(booking)

        # When
        url = '/v2/bookings/use/token/{}'.format(booking.token)
        response = TestClient(app.test_client()).patch(url)

        # Then
        assert response.status_code == 401

    @pytest.mark.usefixtures("db_session")
    def when_user_not_logged_in_and_not_existing_api_key_given(self, app):
        # Given
        user = create_user(email='user@email.fr')
        pro_user = create_user(email='pro@email.fr')
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock = create_stock(offer=offer, price=0)
        booking = create_booking(user=user, stock=stock, venue=venue)

        repository.save(pro_user, booking)

        # When
        url = '/v2/bookings/use/token/{}'.format(booking.token)
        response = TestClient(app.test_client()).patch(url, headers={
            'Authorization': 'Bearer WrongApiKey1234567',
            'Origin': 'http://localhost'})

        # Then
        assert response.status_code == 401

class Returns403:
    class WithApiKeyAuthTest:
        @pytest.mark.usefixtures("db_session")
        def when_api_key_given_not_related_to_booking_offerer(self, app):
            # Given
            user = create_user(email='user@email.fr')
            pro_user = create_user(email='pro@email.fr')
            offerer = create_offerer()
            offerer2 = create_offerer(siren='987654321')
            user_offerer = create_user_offerer(pro_user, offerer)
            venue = create_venue(offerer)
            stock = create_stock_with_event_offer(offerer, venue, price=0, event_type=EventType.ACTIVATION)
            booking = create_booking(user=user, stock=stock, venue=venue)

            repository.save(pro_user, booking, user_offerer, offerer2)

            offerer_api_key = create_api_key(offerer_id=offerer2.id)
            repository.save(offerer_api_key)

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
            assert response.json['user'] == ["Vous n'avez pas les droits suffisants pour valider cette contremarque."]

    class WithBasicAuthTest:
        @pytest.mark.usefixtures("db_session")
        def when_user_is_not_attached_to_linked_offerer(self, app):
            # Given
            user = create_user()
            pro_user = create_user(email='pro@email.fr')
            offerer = create_offerer()
            venue = create_venue(offerer)
            stock = create_stock_with_event_offer(offerer, venue, price=0)
            booking = create_booking(user=user, stock=stock, venue=venue)
            repository.save(booking, pro_user)
            booking_id = booking.id
            url = '/v2/bookings/use/token/{}'.format(booking.token, user.email)

            # When
            response = TestClient(app.test_client()).with_auth('pro@email.fr').patch(url)

            # Then
            assert response.status_code == 403
            assert response.json['user'] == ["Vous n'avez pas les droits suffisants pour valider cette contremarque."]
            assert Booking.query.get(booking_id).isUsed is False

        @pytest.mark.usefixtures("db_session")
        def when_user_is_not_admin_and_tries_to_patch_activation_offer(self, app):
            # Given
            user = create_user()
            pro_user = create_user(email='pro@email.fr')
            offerer = create_offerer()
            user_offerer = create_user_offerer(pro_user, offerer)
            venue = create_venue(offerer)
            stock = create_stock_with_event_offer(offerer, venue, price=0, event_type=EventType.ACTIVATION)
            booking = create_booking(user=user, stock=stock, venue=venue)
            repository.save(booking, user_offerer)

            # When
            url = '/v2/bookings/use/token/{}'.format(booking.token)
            response = TestClient(app.test_client()).with_auth('pro@email.fr').patch(url)

            # Then
            assert response.status_code == 403
            assert response.json['user'] == ["Vous n'avez pas les droits suffisants pour valider cette contremarque."]

class Returns404:
    @pytest.mark.usefixtures("db_session")
    def when_booking_is_not_provided_at_all(self, app):
        # Given
        user = create_user(email='user@email.fr')
        offerer = create_offerer()
        venue = create_venue(offerer)
        stock = create_stock_with_event_offer(offerer, venue, price=0)
        booking = create_booking(user=user, stock=stock, venue=venue)

        repository.save(booking)

        # When
        url = '/v2/bookings/use/token/'
        response = TestClient(app.test_client()).patch(url)

        # Then
        assert response.status_code == 404

    class WithApiKeyAuthTest:
        @pytest.mark.usefixtures("db_session")
        def when_api_key_is_provided_and_booking_does_not_exist(self, app):
            # Given
            user = create_user()
            offerer = create_offerer()
            venue = create_venue(offerer)
            stock = create_stock_with_event_offer(offerer, venue, price=0)
            booking = create_booking(user=user, stock=stock, venue=venue)
            repository.save(booking)

            offerer_api_key = create_api_key(offerer_id=offerer.id)
            repository.save(offerer_api_key)

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
            assert response.json['global'] == ["Cette contremarque n'a pas été trouvée"]

    class WithBasicAuthTest:
        @pytest.mark.usefixtures("db_session")
        def when_user_is_logged_in_and_booking_does_not_exist(self, app):
            # Given
            user = create_user()
            pro_user = create_user(email='pro@email.fr')
            offerer = create_offerer()
            user_offerer = create_user_offerer(pro_user, offerer)
            venue = create_venue(offerer)
            stock = create_stock_with_event_offer(offerer, venue, price=0)
            booking = create_booking(user=user, stock=stock, venue=venue)
            repository.save(booking, user_offerer)

            # When
            url = '/v2/bookings/use/token/{}'.format('123456')
            response = TestClient(app.test_client()).with_auth('pro@email.fr').patch(url)

            # Then
            assert response.status_code == 404
            assert response.json['global'] == ["Cette contremarque n'a pas été trouvée"]

class Returns405:
    class WhenLoggedUserIsAdmin:
        @pytest.mark.usefixtures("db_session")
        def expect_no_new_deposits_when_the_linked_user_has_been_already_activated(self, app):
            # Given
            user = create_user(can_book_free_offers=False, email='user@email.fr')
            deposit = create_deposit(user, amount=0)

            admin_user = create_user(can_book_free_offers=False, email='admin@email.fr', is_admin=True)

            offerer = create_offerer()
            admin_user_offerer = create_user_offerer(admin_user, offerer)
            venue = create_venue(offerer)
            activation_offer_stock = create_stock_with_event_offer(offerer, venue, price=0,
                                                                   event_type=EventType.ACTIVATION)

            booking = create_booking(user=user, stock=activation_offer_stock, venue=venue)

            repository.save(booking, admin_user_offerer, deposit)

            user_id = user.id

            # When
            url = '/v2/bookings/use/token/{}'.format(booking.token)
            response = TestClient(app.test_client()).with_auth('admin@email.fr').patch(url)

            # Then
            deposits_for_user = Deposit.query.filter_by(userId=user_id).all()
            assert response.status_code == 405
            assert response.json['user'] == ["Cet utilisateur a déjà crédité son pass Culture"]
            assert len(deposits_for_user) == 1
            assert deposits_for_user[0].amount == 0

class Returns410:
    class WithBasicAuthTest:
        @pytest.mark.usefixtures("db_session")
        def when_user_is_logged_in_and_booking_has_been_cancelled_already(self, app):
            # Given
            user = create_user()
            pro_user = create_user(email='pro@email.fr')
            offerer = create_offerer()
            user_offerer = create_user_offerer(pro_user, offerer)
            venue = create_venue(offerer)
            stock = create_stock_with_event_offer(offerer, venue, price=0)
            booking = create_booking(user=user, stock=stock, venue=venue)
            booking.isCancelled = True
            repository.save(booking, user_offerer)
            booking_id = booking.id

            # When
            url = '/v2/bookings/use/token/{}'.format(booking.token)
            response = TestClient(app.test_client()).with_auth('pro@email.fr').patch(url)

            # Then
            assert response.status_code == 410
            assert response.json['booking'] == ['Cette réservation a été annulée']
            assert Booking.query.get(booking_id).isUsed is False

        @pytest.mark.usefixtures("db_session")
        def when_user_is_logged_in_and_booking_has_been_validated_already(self, app):
            # Given
            user = create_user()
            pro_user = create_user(email='pro@email.fr')
            offerer = create_offerer()
            user_offerer = create_user_offerer(pro_user, offerer)
            venue = create_venue(offerer)
            stock = create_stock_with_event_offer(offerer, venue, price=0)
            booking = create_booking(user=user, stock=stock, venue=venue)
            booking.isUsed = True
            repository.save(booking, user_offerer)
            booking_id = booking.id

            # When
            url = '/v2/bookings/use/token/{}'.format(booking.token)
            response = TestClient(app.test_client()).with_auth('pro@email.fr').patch(url)

            # Then
            assert response.status_code == 410
            assert response.json['booking'] == ['Cette réservation a déjà été validée']
            assert Booking.query.get(booking_id).isUsed is True

    class WithApiKeyAuthTest:
        @pytest.mark.usefixtures("db_session")
        def when_api_key_is_provided_and_booking_has_been_cancelled_already(self, app):
            # Given
            user = create_user()
            pro_user = create_user(email='pro@email.fr')
            offerer = create_offerer()
            user_offerer = create_user_offerer(pro_user, offerer)
            venue = create_venue(offerer)
            stock = create_stock_with_event_offer(offerer, venue, price=0)
            booking = create_booking(user=user, stock=stock, venue=venue)
            booking.isCancelled = True
            repository.save(booking, user_offerer)
            booking_id = booking.id

            # When
            url = '/v2/bookings/use/token/{}'.format(booking.token)
            response = TestClient(app.test_client()).with_auth('pro@email.fr').patch(url)

            # Then
            assert response.status_code == 410
            assert response.json['booking'] == ['Cette réservation a été annulée']
            assert Booking.query.get(booking_id).isUsed is False

        @pytest.mark.usefixtures("db_session")
        def when_api_key_is_provided_and_booking_has_been_validated_already(self, app):
            # Given
            user = create_user()
            pro_user = create_user(email='pro@email.fr')
            offerer = create_offerer()
            user_offerer = create_user_offerer(pro_user, offerer)
            venue = create_venue(offerer)
            stock = create_stock_with_event_offer(offerer, venue, price=0)
            booking = create_booking(user=user, stock=stock, venue=venue)
            booking.isUsed = True
            repository.save(booking, user_offerer)
            booking_id = booking.id

            # When
            url = '/v2/bookings/use/token/{}'.format(booking.token)
            response = TestClient(app.test_client()).with_auth('pro@email.fr').patch(url)

            # Then
            assert response.status_code == 410
            assert response.json['booking'] == ['Cette réservation a déjà été validée']
            assert Booking.query.get(booking_id).isUsed is True
