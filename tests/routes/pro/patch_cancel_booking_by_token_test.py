import pytest

import pcapi.core.bookings.factories as bookings_factories
from pcapi.core.bookings.models import BookingStatus
from pcapi.core.offerers.factories import ApiKeyFactory
from pcapi.core.offerers.factories import DEFAULT_CLEAR_API_KEY
import pcapi.core.offers.factories as offers_factories
import pcapi.core.users.factories as users_factories
from pcapi.model_creators.generic_creators import create_booking
from pcapi.model_creators.generic_creators import create_offerer
from pcapi.model_creators.generic_creators import create_stock
from pcapi.model_creators.generic_creators import create_user_offerer
from pcapi.model_creators.generic_creators import create_venue
from pcapi.model_creators.specific_creators import create_offer_with_event_product
from pcapi.model_creators.specific_creators import create_offer_with_thing_product
from pcapi.models import Booking
import pcapi.notifications.push.testing as push_testing
from pcapi.repository import repository

from tests.conftest import TestClient


class Returns204Test:
    @pytest.mark.usefixtures("db_session")
    def test_should_returns_204_with_cancellation_allowed(self, app):
        # Given
        pro_user = users_factories.ProFactory(email="Mr Books@example.net", publicName="Mr Books")
        offerer = create_offerer(siren="793875030")
        user_offerer = create_user_offerer(pro_user, offerer)
        venue = create_venue(offerer)
        book_offer = create_offer_with_event_product(venue)
        stock = create_stock(offer=book_offer)

        user = users_factories.UserFactory()
        booking = create_booking(user=user, stock=stock, venue=venue)

        repository.save(booking, user_offerer)

        ApiKeyFactory(offerer=offerer)

        # When
        response = TestClient(app.test_client()).patch(
            "/v2/bookings/cancel/token/{}".format(booking.token),
            headers={"Authorization": "Bearer " + DEFAULT_CLEAR_API_KEY, "Origin": "http://localhost"},
        )

        # cancellation can trigger more than one request to Batch
        assert len(push_testing.requests) >= 1

        # Then
        assert response.status_code == 204
        updated_booking = Booking.query.first()
        assert updated_booking.isCancelled
        assert updated_booking.status is BookingStatus.CANCELLED

        assert push_testing.requests[-1] == {
            "group_id": "Cancel_booking",
            "message": {
                "body": 'Ta réservation "Test event" a été annulée par l\'offreur.',
                "title": "Réservation annulée",
            },
            "user_ids": [user.id],
        }

    @pytest.mark.usefixtures("db_session")
    def test_should_returns_204_with_lowercase_token(self, app):
        # Given
        pro_user = users_factories.ProFactory(email="Mr Books@example.net", publicName="Mr Books")
        offerer = create_offerer(siren="793875030")
        user_offerer = create_user_offerer(pro_user, offerer)
        venue = create_venue(offerer)
        book_offer = create_offer_with_event_product(venue)
        stock = create_stock(offer=book_offer)

        user = users_factories.BeneficiaryFactory()
        booking = create_booking(user=user, stock=stock, venue=venue)

        repository.save(booking, user_offerer)
        ApiKeyFactory(offerer=offerer)

        # When
        token = booking.token.lower()
        response = TestClient(app.test_client()).patch(
            "/v2/bookings/cancel/token/{}".format(token),
            headers={"Authorization": "Bearer " + DEFAULT_CLEAR_API_KEY, "Origin": "http://localhost"},
        )

        # cancellation can trigger more than one request to Batch
        assert len(push_testing.requests) >= 1

        # Then
        assert response.status_code == 204
        updated_booking = Booking.query.first()
        assert updated_booking.isCancelled
        assert updated_booking.status is BookingStatus.CANCELLED


class Returns401Test:
    @pytest.mark.usefixtures("db_session")
    def when_not_authenticated_used_api_key_or_login(self, app):
        # Given
        pro = users_factories.ProFactory()
        offerer = create_offerer()
        user_offerer = create_user_offerer(pro, offerer)
        venue = create_venue(offerer)
        offer = create_offer_with_event_product(venue)
        stock = create_stock(offer=offer)
        beneficiary = users_factories.BeneficiaryFactory()
        booking = create_booking(user=beneficiary, stock=stock, venue=venue)
        repository.save(user_offerer, booking)

        # When
        url = "/v2/bookings/cancel/token/{}".format(booking.token)
        response = TestClient(app.test_client()).patch(url)

        # Then
        assert response.status_code == 401
        assert push_testing.requests == []

    @pytest.mark.usefixtures("db_session")
    def when_giving_an_api_key_that_does_not_exists(self, app):
        # Given
        pro = users_factories.ProFactory()
        offerer = create_offerer()
        user_offerer = create_user_offerer(pro, offerer)
        venue = create_venue(offerer)
        offer = create_offer_with_event_product(venue)
        stock = create_stock(offer=offer)
        beneficiary = users_factories.BeneficiaryFactory()
        booking = create_booking(user=beneficiary, stock=stock, venue=venue)
        repository.save(user_offerer, booking)

        # When
        url = "/v2/bookings/cancel/token/{}".format(booking.token)
        wrong_api_key = "Bearer WrongApiKey1234567"
        response = TestClient(app.test_client()).patch(
            url, headers={"Authorization": wrong_api_key, "Origin": "http://localhost"}
        )

        assert response.status_code == 401
        assert push_testing.requests == []


class Returns403Test:
    @pytest.mark.usefixtures("db_session")
    def when_the_api_key_is_not_linked_to_the_right_offerer(self, app):
        # Given
        pro_user = users_factories.ProFactory(email="Mr Books@example.net", publicName="Mr Books")
        offerer = create_offerer(siren="793875030")
        user_offerer = create_user_offerer(pro_user, offerer)
        venue = create_venue(offerer)
        book_offer = create_offer_with_event_product(venue)
        stock = create_stock(offer=book_offer)

        user = users_factories.BeneficiaryFactory()
        booking = create_booking(user=user, stock=stock, venue=venue)

        repository.save(booking, user_offerer)

        offerer_with_api_key = create_offerer()
        repository.save(offerer_with_api_key)

        ApiKeyFactory(offerer=offerer_with_api_key)

        # When
        response = TestClient(app.test_client()).patch(
            "/v2/bookings/cancel/token/{}".format(booking.token),
            headers={"Authorization": "Bearer " + DEFAULT_CLEAR_API_KEY, "Origin": "http://localhost"},
        )

        # Then
        assert response.status_code == 403
        assert response.json["user"] == ["Vous n'avez pas les droits suffisants pour annuler cette réservation."]
        assert push_testing.requests == []

    @pytest.mark.usefixtures("db_session")
    def when_the_logged_user_has_not_rights_on_offerer(self, app):
        # Given
        pro_user = users_factories.ProFactory(email="mr.book@example.net", publicName="Mr Books")
        offerer = create_offerer(siren="793875030")
        user_offerer = create_user_offerer(pro_user, offerer)
        venue = create_venue(offerer)
        book_offer = create_offer_with_event_product(venue)
        stock = create_stock(offer=book_offer)

        user = users_factories.BeneficiaryFactory()
        booking = create_booking(user=user, stock=stock, venue=venue)

        repository.save(booking, user_offerer)

        offerer_with_api_key = create_offerer()
        repository.save(offerer_with_api_key)

        ApiKeyFactory(offerer=offerer)

        # When
        response = (
            TestClient(app.test_client())
            .with_auth(user.email)
            .patch("/v2/bookings/cancel/token/{}".format(booking.token))
        )

        # Then
        assert response.status_code == 403
        assert response.json["global"] == [
            "Vous n'avez pas les droits d'accès suffisant pour accéder à cette information."
        ]
        assert push_testing.requests == []

    class WhenTheBookingIsUsedTest:
        @pytest.mark.usefixtures("db_session")
        def test_should_prevent_a_used_booking_from_being_cancelled(self, app):
            # Given
            user_offerer = offers_factories.UserOffererFactory()
            booking = bookings_factories.BookingFactory(
                stock__offer__venue__managingOfferer=user_offerer.offerer, isUsed=True, status=BookingStatus.USED
            )

            ApiKeyFactory(offerer=user_offerer.offerer)

            # When
            response = TestClient(app.test_client()).patch(
                "/v2/bookings/cancel/token/{}".format(booking.token),
                headers={"Authorization": "Bearer " + DEFAULT_CLEAR_API_KEY, "Origin": "http://localhost"},
            )

            # Then
            assert response.status_code == 403
            assert response.json["global"] == ["Impossible d'annuler une réservation consommée"]
            updated_booking = Booking.query.first()
            assert updated_booking.isUsed
            assert updated_booking.isCancelled is False
            assert updated_booking.status is BookingStatus.USED
            assert push_testing.requests == []


class Returns404Test:
    @pytest.mark.usefixtures("db_session")
    def when_the_booking_does_not_exists(self, app):
        # Given
        pro = users_factories.ProFactory()
        offerer = create_offerer()
        user_offerer = create_user_offerer(pro, offerer)
        venue = create_venue(offerer)
        offer = create_offer_with_event_product(venue)
        stock = create_stock(offer=offer)
        beneficiary = users_factories.BeneficiaryFactory()
        booking = create_booking(user=beneficiary, stock=stock, venue=venue)
        repository.save(user_offerer, booking)

        ApiKeyFactory(offerer=offerer)

        # When
        response = TestClient(app.test_client()).patch(
            "/v2/bookings/cancel/token/FAKETOKEN",
            headers={"Authorization": f"Bearer {DEFAULT_CLEAR_API_KEY}", "Origin": "http://localhost"},
        )

        # Then
        assert response.status_code == 404
        assert response.json["global"] == ["Cette contremarque n'a pas été trouvée"]
        assert push_testing.requests == []


class Returns410Test:
    @pytest.mark.usefixtures("db_session")
    def test_cancel_a_booking_already_cancelled(self, app):
        # Given
        pro_user = users_factories.ProFactory(email="Mr Books@example.net", publicName="Mr Books")
        offerer = create_offerer(siren="793875030")
        user_offerer = create_user_offerer(pro_user, offerer)
        venue = create_venue(offerer)
        book_offer = create_offer_with_thing_product(venue)
        stock = create_stock(offer=book_offer)

        user = users_factories.BeneficiaryFactory()
        booking = create_booking(user=user, stock=stock, is_cancelled=True, venue=venue)

        repository.save(booking, user_offerer)
        ApiKeyFactory(offerer=offerer)

        # When
        response = TestClient(app.test_client()).patch(
            "/v2/bookings/cancel/token/{}".format(booking.token),
            headers={"Authorization": "Bearer " + DEFAULT_CLEAR_API_KEY, "Origin": "http://localhost"},
        )

        # Then
        assert response.status_code == 410
        assert response.json["global"] == ["Cette contremarque a déjà été annulée"]
        assert push_testing.requests == []
