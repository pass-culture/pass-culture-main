import hashlib
import hmac

import pytest

import pcapi.core.bookings.factories as bookings_factories
import pcapi.core.external_bookings.factories as external_bookings_factories
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
import pcapi.core.providers.factories as providers_factories
import pcapi.core.users.factories as users_factories
import pcapi.notifications.push.testing as push_testing
from pcapi.core.bookings.models import Booking
from pcapi.core.bookings.models import BookingStatus
from pcapi.core.categories import subcategories
from pcapi.models import db


class Returns204Test:
    @pytest.mark.usefixtures("db_session")
    @pytest.mark.features(WIP_DISABLE_CANCEL_BOOKING_NOTIFICATION=False)
    def test_should_returns_204_with_cancellation_allowed(self, client):
        # Given
        stock = offers_factories.EventStockFactory(offer__name="Chouette concert")
        booking = bookings_factories.BookingFactory(stock=stock)
        offerers_factories.ApiKeyFactory(offerer=booking.offerer)

        # When
        response = client.patch(
            f"/v2/bookings/cancel/token/{booking.token}",
            headers={"Authorization": "Bearer " + offerers_factories.DEFAULT_CLEAR_API_KEY},
        )

        # Then
        # cancellation can trigger more than one request to Batch
        assert len(push_testing.requests) >= 1
        assert response.status_code == 204
        updated_booking = db.session.query(Booking).one()
        assert updated_booking.status is BookingStatus.CANCELLED

        assert push_testing.requests[-1] == {
            "group_id": "Cancel_booking",
            "message": {
                "body": """Ta réservation "Chouette concert" a été annulée par l'offreur.""",
                "title": "Réservation annulée",
            },
            "user_ids": [booking.userId],
            "can_be_asynchronously_retried": False,
        }

    @pytest.mark.usefixtures("db_session")
    @pytest.mark.features(WIP_DISABLE_CANCEL_BOOKING_NOTIFICATION=True)
    def test_should_returns_204_with_cancellation_allowed_with_FF(self, client):
        # Given
        stock = offers_factories.EventStockFactory(offer__name="Chouette concert")
        booking = bookings_factories.BookingFactory(stock=stock)
        offerers_factories.ApiKeyFactory(offerer=booking.offerer)

        # When
        response = client.patch(
            f"/v2/bookings/cancel/token/{booking.token}",
            headers={"Authorization": "Bearer " + offerers_factories.DEFAULT_CLEAR_API_KEY},
        )

        # Then
        # cancellation can trigger more than one request to Batch
        assert len(push_testing.requests) >= 1
        assert response.status_code == 204
        updated_booking = db.session.query(Booking).one()
        assert updated_booking.status is BookingStatus.CANCELLED

        cancel_notification_requests = [req for req in push_testing.requests if req.get("group_id") == "Cancel_booking"]
        assert len(cancel_notification_requests) == 0

    @pytest.mark.usefixtures("db_session")
    def test_should_returns_204_with_lowercase_token(self, client):
        # Given
        booking = bookings_factories.BookingFactory()
        offerers_factories.ApiKeyFactory(offerer=booking.offerer)

        # When
        response = client.patch(
            f"/v2/bookings/cancel/token/{booking.token.lower()}",
            headers={"Authorization": "Bearer " + offerers_factories.DEFAULT_CLEAR_API_KEY},
        )

        assert response.status_code == 204
        booking = db.session.query(Booking).one()
        assert booking.status is BookingStatus.CANCELLED

    @pytest.mark.usefixtures("db_session")
    def test_should_returns_204_for_external_booking(self, client, requests_mock):
        external_url = "https://book_my_offer.com"
        provider = providers_factories.ProviderFactory(
            name="Technical provider",
            bookingExternalUrl=external_url + "/book",
            cancelExternalUrl=external_url + "/cancel",
        )
        providers_factories.OffererProviderFactory(provider=provider)
        stock = offers_factories.EventStockFactory(
            lastProvider=provider,
            offer__subcategoryId=subcategories.SEANCE_ESSAI_PRATIQUE_ART.id,
            offer__lastProvider=provider,
            idAtProviders="",
            quantity=20,
            dnBookedQuantity=4,
        )
        # This booking increseaes the stock.dnBookedQuantity to 5
        booking = bookings_factories.BookingFactory(stock=stock)
        offerers_factories.ApiKeyFactory(offerer=booking.offerer)
        external_bookings_factories.ExternalBookingFactory(booking=booking, barcode="1234567890123")
        requests_mock.post(
            external_url + "/cancel",
            json={"remainingQuantity": 10},
            status_code=200,
        )

        response = client.patch(
            f"/v2/bookings/cancel/token/{booking.token}",
            headers={"Authorization": "Bearer " + offerers_factories.DEFAULT_CLEAR_API_KEY},
        )

        assert response.status_code == 204
        booking = db.session.query(Booking).one()
        assert booking.status is BookingStatus.CANCELLED
        assert stock.dnBookedQuantity == 4
        assert booking.stock.quantity == 14  # 4 already booked + 10 remaining

        assert (
            requests_mock.last_request.headers["PassCulture-Signature"]
            == hmac.new(
                provider.hmacKey.encode(), '{"barcodes": ["1234567890123"]}'.encode(), hashlib.sha256
            ).hexdigest()
        )

    @pytest.mark.usefixtures("db_session")
    def test_should_returns_204_for_external_booking_and_remaining_quantity_is_unlimited(self, client, requests_mock):
        external_url = "https://book_my_offer.com"
        provider = providers_factories.ProviderFactory(
            name="Technical provider",
            bookingExternalUrl=external_url + "/book",
            cancelExternalUrl=external_url + "/cancel",
        )
        providers_factories.OffererProviderFactory(provider=provider)
        stock = offers_factories.EventStockFactory(
            lastProvider=provider,
            offer__subcategoryId=subcategories.SEANCE_ESSAI_PRATIQUE_ART.id,
            offer__lastProvider=provider,
            idAtProviders="",
            quantity=20,
            dnBookedQuantity=4,
        )
        # This booking increseaes the stock.dnBookedQuantity to 5
        booking = bookings_factories.BookingFactory(stock=stock)
        offerers_factories.ApiKeyFactory(offerer=booking.offerer)
        external_bookings_factories.ExternalBookingFactory(booking=booking, barcode="1234567890123")
        requests_mock.post(
            external_url + "/cancel",
            json={"remainingQuantity": None},
            status_code=200,
        )

        response = client.patch(
            f"/v2/bookings/cancel/token/{booking.token}",
            headers={"Authorization": "Bearer " + offerers_factories.DEFAULT_CLEAR_API_KEY},
        )

        assert response.status_code == 204
        booking = db.session.query(Booking).one()
        assert booking.status is BookingStatus.CANCELLED
        assert stock.dnBookedQuantity == 4
        assert booking.stock.quantity == None  # stock quantity is unlimited when value is None
        assert booking.stock.remainingQuantity == "unlimited"

    @pytest.mark.usefixtures("db_session")
    def test_should_returns_204_for_booking_duo_external_booking(self, client, requests_mock):
        external_url = "https://book_my_offer.com"
        # Given
        provider = providers_factories.ProviderFactory(
            name="Technical provider",
            bookingExternalUrl=external_url + "/book",
            cancelExternalUrl=external_url + "/cancel",
        )
        providers_factories.OffererProviderFactory(provider=provider)
        stock = offers_factories.EventStockFactory(
            lastProvider=provider,
            offer__subcategoryId=subcategories.SEANCE_ESSAI_PRATIQUE_ART.id,
            offer__lastProvider=provider,
            idAtProviders="",
            quantity=10,
            dnBookedQuantity=2,
        )
        # This booking increseaes the stock.dnBookedQuantity to 4
        booking = bookings_factories.BookingFactory(stock=stock, quantity=2)
        offerers_factories.ApiKeyFactory(offerer=booking.offerer)
        external_bookings_factories.ExternalBookingFactory(booking=booking, barcode="1234567890123")
        external_bookings_factories.ExternalBookingFactory(booking=booking, barcode="1234567890124")
        requests_mock.post(
            external_url + "/cancel",
            json={"remainingQuantity": 15},
            status_code=200,
        )

        # When
        response = client.patch(
            f"/v2/bookings/cancel/token/{booking.token}",
            headers={"Authorization": "Bearer " + offerers_factories.DEFAULT_CLEAR_API_KEY},
        )

        assert response.status_code == 204
        booking = db.session.query(Booking).one()
        assert booking.status is BookingStatus.CANCELLED
        assert booking.stock.quantity == 17  # 2 already booked + 15 remaining
        assert booking.stock.dnBookedQuantity == 2

    @pytest.mark.usefixtures("db_session")
    def test_should_returns_204_for_external_booking_when_external_api_returns_200_without_remaining_quantity(
        self, client, requests_mock
    ):
        external_url = "https://book_my_offer.com"
        # Given
        provider = providers_factories.ProviderFactory(
            name="Technical provider",
            bookingExternalUrl=external_url + "/book",
            cancelExternalUrl=external_url + "/cancel",
        )
        providers_factories.OffererProviderFactory(provider=provider)
        stock = offers_factories.EventStockFactory(
            lastProvider=provider,
            offer__subcategoryId=subcategories.SEANCE_ESSAI_PRATIQUE_ART.id,
            offer__lastProvider=provider,
            idAtProviders="",
            dnBookedQuantity=4,
            quantity=37,
        )
        # this booking increases dnBookedQuantity to 5
        booking = bookings_factories.BookingFactory(stock=stock)
        offerers_factories.ApiKeyFactory(offerer=booking.offerer)
        external_bookings_factories.ExternalBookingFactory(booking=booking, barcode="1234567890123")
        requests_mock.post(
            external_url + "/cancel",
            text="{remainingQuantity: }",
            status_code=200,
        )

        # When
        response = client.patch(
            f"/v2/bookings/cancel/token/{booking.token}",
            headers={"Authorization": "Bearer " + offerers_factories.DEFAULT_CLEAR_API_KEY},
        )

        assert response.status_code == 204
        booking = db.session.query(Booking).one()
        assert booking.status is BookingStatus.CANCELLED
        assert booking.stock.dnBookedQuantity == 4
        assert booking.stock.quantity == 37  # shouldn't change


class Returns401Test:
    @pytest.mark.usefixtures("db_session")
    def when_not_authenticated_used_api_key_or_login(self, client):
        response = client.patch("/v2/bookings/cancel/token/TOKEN")
        assert response.status_code == 401

    @pytest.mark.usefixtures("db_session")
    def when_giving_an_api_key_that_does_not_exists(self, client):
        headers = {"Authorization": "Bearer WrongApiKey1234567"}
        response = client.patch("/v2/bookings/cancel/token/TOKEN", headers=headers)
        assert response.status_code == 401


class Returns403Test:
    @pytest.mark.usefixtures("db_session")
    def when_the_api_key_is_not_linked_to_the_right_offerer(self, client):
        # Given
        booking = bookings_factories.BookingFactory()
        offerers_factories.ApiKeyFactory()  # another offerer's API key

        # When
        response = client.patch(
            f"/v2/bookings/cancel/token/{booking.token}",
            headers={"Authorization": "Bearer " + offerers_factories.DEFAULT_CLEAR_API_KEY},
        )

        # Then
        assert response.status_code == 403
        assert response.json["user"] == ["Vous n'avez pas les droits suffisants pour annuler cette réservation."]

    @pytest.mark.usefixtures("db_session")
    def when_the_logged_user_has_not_rights_on_offerer(self, client):
        # Given
        booking = bookings_factories.BookingFactory()
        another_pro_user = offerers_factories.UserOffererFactory().user

        # When
        url = f"/v2/bookings/cancel/token/{booking.token}"
        response = client.with_session_auth(another_pro_user.email).patch(url)

        # Then
        assert response.status_code == 403
        assert response.json["global"] == [
            "Vous n'avez pas les droits d'accès suffisants pour accéder à cette information."
        ]

    @pytest.mark.usefixtures("db_session")
    def test_should_prevent_a_used_booking_from_being_cancelled(self, client):
        # Given
        booking = bookings_factories.UsedBookingFactory()
        pro_user = offerers_factories.UserOffererFactory(offerer=booking.offerer).user

        # When
        url = f"/v2/bookings/cancel/token/{booking.token}"
        response = client.with_basic_auth(pro_user.email).patch(url)

        # Then
        assert response.status_code == 403
        assert response.json["global"] == ["Impossible d'annuler une réservation consommée"]
        booking = db.session.query(Booking).first()
        assert booking.status is BookingStatus.USED
        assert not push_testing.requests


class Returns404Test:
    @pytest.mark.usefixtures("db_session")
    def when_the_booking_does_not_exists(self, client):
        user = users_factories.ProFactory()
        url = "/v2/bookings/cancel/token/FAKETOKEN"
        response = client.with_basic_auth(user.email).patch(url)
        assert response.status_code == 404
        assert response.json["global"] == ["Cette contremarque n'a pas été trouvée"]


class Returns410Test:
    @pytest.mark.usefixtures("db_session")
    def test_cancel_a_booking_already_cancelled(self, client):
        # Given
        booking = bookings_factories.CancelledBookingFactory()
        pro_user = offerers_factories.UserOffererFactory(offerer=booking.offerer).user

        # When
        url = f"/v2/bookings/cancel/token/{booking.token}"
        response = client.with_basic_auth(pro_user.email).patch(url)

        # Then
        assert response.status_code == 410
        assert response.json["global"] == ["Cette contremarque a déjà été annulée"]


class Returns400Test:
    @pytest.mark.usefixtures("db_session")
    def test_should_raise_error_for_external_booking_when_external_api_returns_error_code(self, client, requests_mock):
        external_url = "https://book_my_offer.com"
        provider = providers_factories.ProviderFactory(
            name="Technical provider",
            bookingExternalUrl=external_url + "/book",
            cancelExternalUrl=external_url + "/cancel",
        )
        providers_factories.OffererProviderFactory(provider=provider)
        stock = offers_factories.EventStockFactory(
            lastProvider=provider,
            offer__subcategoryId=subcategories.SEANCE_ESSAI_PRATIQUE_ART.id,
            offer__lastProvider=provider,
            idAtProviders="",
            dnBookedQuantity=4,
            quantity=10,
        )
        # This bookings bumps the stock.dnBookedQuantity to 5
        booking = bookings_factories.BookingFactory(stock=stock)
        offerers_factories.ApiKeyFactory(offerer=booking.offerer)
        external_bookings_factories.ExternalBookingFactory(booking=booking, barcode="1234567890123")
        requests_mock.post(
            external_url + "/cancel",
            text="internal error",
            status_code=500,
        )

        # When
        response = client.patch(
            f"/v2/bookings/cancel/token/{booking.token}",
            headers={"Authorization": "Bearer " + offerers_factories.DEFAULT_CLEAR_API_KEY},
        )

        assert response.status_code == 400
        assert response.json == {
            "global": ["L'annulation de réservation a échoué."],
        }
        booking = db.session.query(Booking).one()
        assert booking.status is BookingStatus.CONFIRMED
        assert booking.stock.dnBookedQuantity == 5
