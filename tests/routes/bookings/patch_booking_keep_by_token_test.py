from decimal import Decimal

import pcapi.core.bookings.factories as bookings_factories
import pcapi.core.offers.factories as offers_factories
import pcapi.core.users.factories as users_factories
from pcapi.models import EventType, BookingSQLEntity
from pcapi.repository import repository
import pytest
from tests.conftest import TestClient
from pcapi.model_creators.generic_creators import create_booking, create_user, create_offerer, create_venue, \
    create_user_offerer, create_payment, create_api_key
from pcapi.model_creators.specific_creators import create_stock_with_event_offer, create_stock_from_event_occurrence, \
    create_offer_with_event_product, create_event_occurrence
from pcapi.utils.token import random_token

API_KEY_VALUE = random_token(64)


@pytest.mark.usefixtures("db_session")
class Returns204:
    class WithApiKeyAuthTest:
        def when_api_key_provided_is_related_to_regular_offer_with_rights(self, app):
            booking = bookings_factories.BookingFactory(isUsed=True, token='ABCDEF')
            offerer = booking.stock.offer.venue.managingOfferer
            api_key = offers_factories.ApiKeyFactory(offerer=offerer)

            url = f'/v2/bookings/keep/token/{booking.token}'
            response = TestClient(app.test_client()).patch(
                url,
                headers={
                    'Authorization': f'Bearer {api_key.value}',
                    'Origin': 'http://localhost',
                }
            )

            assert response.status_code == 204
            booking = BookingSQLEntity.query.one()
            assert not booking.isUsed
            assert booking.dateUsed is None

        def expect_booking_to_be_used_with_non_standard_origin_header(self, app):
            booking = bookings_factories.BookingFactory(isUsed=True, token='ABCDEF')
            offerer = booking.stock.offer.venue.managingOfferer
            api_key = offers_factories.ApiKeyFactory(offerer=offerer)

            url = f'/v2/bookings/keep/token/{booking.token}'
            response = TestClient(app.test_client()).patch(
                url,
                headers={
                    'Authorization': f'Bearer {api_key.value}',
                    'Origin': 'http://example.com',
                }
            )

            assert response.status_code == 204
            booking = BookingSQLEntity.query.one()
            assert not booking.isUsed
            assert booking.dateUsed is None

    class WithBasicAuthTest:
        def when_user_is_logged_in_and_regular_offer(self, app):
            booking = bookings_factories.BookingFactory(isUsed=True, token='ABCDEF')
            pro_user = users_factories.UserFactory(email='pro@example.com')
            offerer = booking.stock.offer.venue.managingOfferer
            offers_factories.UserOffererFactory(user=pro_user, offerer=offerer)

            url = f'/v2/bookings/keep/token/{booking.token}'
            response = TestClient(app.test_client()).with_auth('pro@example.com').patch(url)

            assert response.status_code == 204
            booking = BookingSQLEntity.query.one()
            assert not booking.isUsed
            assert booking.dateUsed is None

        def when_user_is_logged_in_expect_booking_with_token_in_lower_case_to_be_used(self, app):
            booking = bookings_factories.BookingFactory(isUsed=True, token='ABCDEF')
            pro_user = users_factories.UserFactory(email='pro@example.com')
            offerer = booking.stock.offer.venue.managingOfferer
            offers_factories.UserOffererFactory(user=pro_user, offerer=offerer)

            url = f'/v2/bookings/keep/token/{booking.token.lower()}'
            response = TestClient(app.test_client()).with_auth('pro@example.com').patch(url)

            assert response.status_code == 204
            booking = BookingSQLEntity.query.one()
            assert not booking.isUsed
            assert booking.dateUsed is None

        # FIXME: I don't understand what we're trying to test, here.
        def when_there_is_no_remaining_quantity_after_validating(self, app):
            booking = bookings_factories.BookingFactory(
                isUsed=True,
                token='ABCDEF',
                stock__quantity=1,
            )
            pro_user = users_factories.UserFactory(email='pro@example.com')
            offerer = booking.stock.offer.venue.managingOfferer
            offers_factories.UserOffererFactory(user=pro_user, offerer=offerer)

            url = f'/v2/bookings/keep/token/{booking.token.lower()}'
            response = TestClient(app.test_client()).with_auth('pro@example.com').patch(url)

            assert response.status_code == 204
            booking = BookingSQLEntity.query.one()
            assert not booking.isUsed
            assert booking.dateUsed is None


class Returns401:
    @pytest.mark.usefixtures("db_session")
    def when_user_not_logged_in_and_doesnt_give_api_key(self, app):
        # Given
        user = create_user(email='user@example.net')
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_event_product(venue, event_name='Event Name')
        event_occurrence = create_event_occurrence(offer)
        stock = create_stock_from_event_occurrence(event_occurrence, price=0)
        booking = create_booking(user=user, stock=stock, venue=venue)

        repository.save(booking)

        # When
        url = '/v2/bookings/keep/token/{}'.format(booking.token)
        response = TestClient(app.test_client()).patch(url)

        # Then
        assert response.status_code == 401

    @pytest.mark.usefixtures("db_session")
    def when_user_not_logged_in_and_given_api_key_that_does_not_exists(self, app):
        # Given
        user = create_user(email='user@example.net')
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_event_product(venue, event_name='Event Name')
        event_occurrence = create_event_occurrence(offer)
        stock = create_stock_from_event_occurrence(event_occurrence, price=0)
        booking = create_booking(user=user, stock=stock, venue=venue)

        repository.save(booking)

        # When
        wrong_api_key = 'Bearer WrongApiKey1234567'
        url = '/v2/bookings/keep/token/{}'.format(booking.token)
        response = TestClient(app.test_client()).patch(url, headers={
                'Authorization': wrong_api_key,
                'Origin': 'http://localhost'})

        # Then
        assert response.status_code == 401

class Returns403:
    class WithApiKeyAuthTest:
        @pytest.mark.usefixtures("db_session")
        def when_the_api_key_is_not_linked_to_the_right_offerer(self, app):
            # Given
            user = create_user(email='user@example.net')
            pro_user = create_user(email='pro@example.net')
            offerer = create_offerer()
            offerer2 = create_offerer(siren='987654321')
            user_offerer = create_user_offerer(pro_user, offerer)
            venue = create_venue(offerer)
            offer = create_offer_with_event_product(venue, event_name='Event Name')
            event_occurrence = create_event_occurrence(offer)
            stock = create_stock_from_event_occurrence(event_occurrence, price=0)
            booking = create_booking(user=user, stock=stock, venue=venue)

            repository.save(pro_user, booking, user_offerer, offerer2)

            offererApiKey = create_api_key(offerer_id=offerer2.id)
            repository.save(offererApiKey)

            # When
            user2_api_key = 'Bearer ' + offererApiKey.value
            url = '/v2/bookings/keep/token/{}'.format(booking.token)

            response = TestClient(app.test_client()).patch(
                url,
                headers={
                    'Authorization': user2_api_key,
                    'Origin': 'http://localhost'}
            )

            # Then
            assert response.status_code == 403
            assert response.json['user'] == [
                "Vous n'avez pas les droits suffisants pour valider cette contremarque."]

    class WithBasicAuthTest:
        @pytest.mark.usefixtures("db_session")
        def when_user_is_not_attached_to_linked_offerer(self, app):
            # Given
            user = create_user()
            pro_user = create_user(email='pro@example.net')
            offerer = create_offerer()
            venue = create_venue(offerer)
            stock = create_stock_with_event_offer(offerer, venue, price=0)


            booking = create_booking(user=user, stock=stock, venue=venue)
            repository.save(booking, pro_user)

            # When
            url = '/v2/bookings/keep/token/{}?email={}'.format(booking.token, user.email)
            response = TestClient(app.test_client()).with_auth('pro@example.net').patch(url)

            # Then
            assert response.status_code == 403
            assert response.json['user'] == [
                "Vous n'avez pas les droits suffisants pour valider cette contremarque."]
            assert BookingSQLEntity.query.get(booking.id).isUsed is False

        @pytest.mark.usefixtures("db_session")
        def when_user_tries_to_patch_activation_offer(self, app):
            # Given
            user = create_user()

            offerer = create_offerer()
            user_offerer = create_user_offerer(user, offerer)
            venue = create_venue(offerer)

            activation_offer = create_offer_with_event_product(venue, event_type=EventType.ACTIVATION)
            activation_event_occurrence = create_event_occurrence(activation_offer)
            stock = create_stock_from_event_occurrence(activation_event_occurrence, price=0)

            booking = create_booking(user=user, stock=stock, venue=venue)

            repository.save(booking, user_offerer)

            # When
            url = '/v2/bookings/keep/token/{}'.format(booking.token)
            response = TestClient(app.test_client()).with_auth(user.email).patch(url)

            # Then
            assert response.status_code == 403
            assert BookingSQLEntity.query.get(booking.id).isUsed is False
            assert response.json['booking'] == [
                "Impossible d'annuler une offre d'activation"]

class Returns404:
    class WithApiKeyAuthTest:
        @pytest.mark.usefixtures("db_session")
        def when_booking_is_not_provided_at_all(self, app):
            # Given
            user = create_user(email='user@example.net')
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_offer_with_event_product(venue, event_name='Event Name')
            event_occurrence = create_event_occurrence(offer)
            stock = create_stock_from_event_occurrence(event_occurrence, price=0)

            booking = create_booking(user=user, stock=stock, venue=venue)

            repository.save(booking)

            offererApiKey = create_api_key(offerer_id=offerer.id)
            repository.save(offererApiKey)

            # When
            url = '/v2/bookings/keep/token/'
            user2_api_key = 'Bearer ' + offererApiKey.value

            response = TestClient(app.test_client()).patch(
                url,
                headers={
                    'Authorization': user2_api_key,
                    'Origin': 'http://localhost'
                }
            )

            # Then
            assert response.status_code == 404

        @pytest.mark.usefixtures("db_session")
        def when_api_key_is_provided_and_booking_does_not_exist(self, app):
            # Given
            user = create_user()
            offerer = create_offerer()
            venue = create_venue(offerer)
            stock = create_stock_with_event_offer(offerer, venue, price=0)

            booking = create_booking(user=user, stock=stock, venue=venue)
            repository.save(booking)

            offererApiKey = create_api_key(offerer_id=offerer.id)
            repository.save(offererApiKey)

            # When
            url = '/v2/bookings/keep/token/{}'.format('456789')
            user2_api_key = 'Bearer ' + offererApiKey.value

            response = TestClient(app.test_client()).patch(
                url,
                headers={
                    'Authorization': user2_api_key,
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
            pro_user= create_user(email='pro@example.net')
            offerer = create_offerer()
            user_offerer = create_user_offerer(pro_user, offerer)
            venue = create_venue(offerer)
            stock = create_stock_with_event_offer(offerer, venue, price=0)

            booking = create_booking(user=user, stock=stock, venue=venue)
            repository.save(booking, user_offerer)

            # When
            url = '/v2/bookings/keep/token/{}'.format('123456')
            response = TestClient(app.test_client()).with_auth('pro@example.net').patch(url)

            # Then
            assert response.status_code == 404
            assert response.json['global'] == ["Cette contremarque n'a pas été trouvée"]

        @pytest.mark.usefixtures("db_session")
        def when_user_is_logged_in_and_booking_token_is_null(self, app):
            # Given
            user = create_user()
            pro_user = create_user(email='pro@example.net')
            offerer = create_offerer()
            user_offerer = create_user_offerer(pro_user, offerer)
            venue = create_venue(offerer)
            stock = create_stock_with_event_offer(offerer, venue, price=0)

            booking = create_booking(user=user, stock=stock, venue=venue)

            repository.save(booking, user_offerer)

            # When
            url = '/v2/bookings/keep/token/'
            response = TestClient(app.test_client()).with_auth('pro@example.net').patch(url)

            # Then
            assert response.status_code == 404

class Returns410:
    class WithBasicAuthTest:
        @pytest.mark.usefixtures("db_session")
        def when_user_is_logged_in_and_booking_has_been_cancelled_already(self, app):
            # Given
            user = create_user()
            pro_user = create_user(email='pro@example.net')
            offerer = create_offerer()
            user_offerer = create_user_offerer(pro_user, offerer)
            venue = create_venue(offerer)
            stock = create_stock_with_event_offer(offerer, venue, price=0)

            booking = create_booking(user=user, stock=stock, is_used=True, venue=venue)

            booking.isCancelled = True
            repository.save(booking, user_offerer)

            # When
            url = '/v2/bookings/keep/token/{}'.format(booking.token)
            response = TestClient(app.test_client()).with_auth('pro@example.net').patch(url)

            # Then
            assert response.status_code == 410
            assert response.json['booking'] == ['Cette réservation a été annulée']
            assert BookingSQLEntity.query.get(booking.id).isUsed is True

        @pytest.mark.usefixtures("db_session")
        def when_user_is_logged_in_and_booking_has_not_been_validated_already(self, app):
            # Given
            user = create_user()
            pro_user = create_user(email='pro@example.net')
            offerer = create_offerer()
            user_offerer = create_user_offerer(pro_user, offerer)
            venue = create_venue(offerer)
            stock = create_stock_with_event_offer(offerer, venue, price=0)

            booking = create_booking(user=user, stock=stock, venue=venue)
            repository.save(booking, user_offerer)

            # When
            url = '/v2/bookings/keep/token/{}'.format(booking.token)
            response = TestClient(app.test_client()).with_auth('pro@example.net').patch(url)

            # Then
            assert response.status_code == 410
            assert response.json['booking'] == ["Cette réservation n'a pas encore été validée"]
            assert BookingSQLEntity.query.get(booking.id).isUsed is False

        @pytest.mark.usefixtures("db_session")
        def when_user_is_logged_in_and_booking_payment_exists(self, app):
            # Given
            user = create_user()
            pro_user = create_user(email='pro@example.net')
            offerer = create_offerer()
            user_offerer = create_user_offerer(pro_user, offerer)
            venue = create_venue(offerer)
            stock = create_stock_with_event_offer(offerer, venue, price=0)

            booking = create_booking(user=user, stock=stock, venue=venue, is_used=True)
            payment = create_payment(booking, offerer, Decimal(10), iban='CF13QSDFGH456789', bic='QSDFGH8Z555')

            repository.save(booking, user_offerer, payment)

            # When
            url = '/v2/bookings/keep/token/{}'.format(booking.token)
            response = TestClient(app.test_client()).with_auth('pro@example.net').patch(url)

            # Then
            assert response.status_code == 410
            assert response.json['payment'] == ["Le remboursement est en cours de traitement"]
            assert BookingSQLEntity.query.get(booking.id).isUsed is True

    class WithApiKeyAuthTest:
        @pytest.mark.usefixtures("db_session")
        def when_api_key_is_provided_and_booking_has_been_cancelled_already(self, app):
            # Given
            user = create_user()
            pro_user = create_user(email='pro@example.net')

            offerer = create_offerer()
            user_offerer = create_user_offerer(pro_user, offerer)
            venue = create_venue(offerer)

            stock = create_stock_with_event_offer(offerer, venue, price=0)

            booking = create_booking(user=user, stock=stock, is_used=True, venue=venue)
            booking.isCancelled = True

            repository.save(booking, user_offerer)

            offererApiKey = create_api_key(offerer_id=offerer.id)
            repository.save(offererApiKey)

            # When
            url = '/v2/bookings/keep/token/{}'.format(booking.token)
            user2_api_key = 'Bearer ' + offererApiKey.value

            response = TestClient(app.test_client()).patch(
                url,
                headers={
                    'Authorization': user2_api_key,
                    'Origin': 'http://localhost'
                }
            )

            # Then
            assert response.status_code == 410
            assert response.json['booking'] == ['Cette réservation a été annulée']
            assert BookingSQLEntity.query.get(booking.id).isUsed is True

        @pytest.mark.usefixtures("db_session")
        def when_api_key_is_provided_and_booking_has_not_been_validated_already(self, app):
            # Given
            user = create_user()
            pro_user = create_user(email='pro@example.net')
            offerer = create_offerer()
            user_offerer = create_user_offerer(pro_user, offerer)
            venue = create_venue(offerer)
            stock = create_stock_with_event_offer(offerer, venue, price=0)
            booking = create_booking(user=user, stock=stock, venue=venue)
            repository.save(booking, user_offerer)

            offererApiKey = create_api_key(offerer_id=offerer.id)
            repository.save(offererApiKey)

            # When
            url = '/v2/bookings/keep/token/{}'.format(booking.token)
            user2_api_key = 'Bearer ' + offererApiKey.value

            response = TestClient(app.test_client()).patch(
                url,
                headers={
                    'Authorization': user2_api_key,
                    'Origin': 'http://localhost'
                }
            )
            # Then
            assert response.status_code == 410
            assert response.json['booking'] == ["Cette réservation n'a pas encore été validée"]
            assert BookingSQLEntity.query.get(booking.id).isUsed is False

        @pytest.mark.usefixtures("db_session")
        def when_api_key_is_provided_and_booking_payment_exists(self, app):
            # Given
            user = create_user()
            pro_user = create_user(email='pro@example.net')
            offerer = create_offerer()
            user_offerer = create_user_offerer(pro_user, offerer)
            venue = create_venue(offerer)
            stock = create_stock_with_event_offer(offerer, venue, price=0)

            booking = create_booking(user=user, stock=stock, venue=venue, is_used=True)
            payment = create_payment(booking, offerer, Decimal(10), iban='CF13QSDFGH456789', bic='QSDFGH8Z555')

            repository.save(booking, user_offerer, payment)

            offererApiKey = create_api_key(offerer_id=offerer.id)
            repository.save(offererApiKey)

            # When
            url = '/v2/bookings/keep/token/{}'.format(booking.token)
            user2_api_key = 'Bearer ' + offererApiKey.value

            response = TestClient(app.test_client()).patch(
                url,
                headers={
                    'Authorization': user2_api_key,
                    'Origin': 'http://localhost'
                }
            )
            # Then
            assert response.status_code == 410
            assert response.json['payment'] == ["Le remboursement est en cours de traitement"]
            assert BookingSQLEntity.query.get(booking.id).isUsed is True
