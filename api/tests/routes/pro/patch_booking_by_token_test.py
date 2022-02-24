import urllib.parse

import pytest

import pcapi.core.bookings.factories as bookings_factories
from pcapi.core.bookings.models import Booking
from pcapi.core.bookings.models import BookingStatus
import pcapi.core.offers.factories as offers_factories
from pcapi.core.users import factories as users_factories
from pcapi.utils.human_ids import humanize


@pytest.mark.usefixtures("db_session")
class Returns204Test:
    class WhenUserIsAnonymousTest:
        def expect_booking_to_be_used(self, client):
            booking = bookings_factories.IndividualBookingFactory(token="ABCDEF")

            url = (
                f"/bookings/token/{booking.token}?" f"email={booking.email}&offer_id={humanize(booking.stock.offerId)}"
            )

            response = client.patch(url)

            assert response.status_code == 204
            booking = Booking.query.one()
            assert booking.status is BookingStatus.USED

    class WhenUserIsLoggedInTest:
        def expect_booking_to_be_used(self, client):
            booking = bookings_factories.IndividualBookingFactory(token="ABCDEF")
            pro_user = users_factories.ProFactory(email="pro@example.com")
            offers_factories.UserOffererFactory(user=pro_user, offerer=booking.offerer)

            url = f"/bookings/token/{booking.token}"
            response = client.with_session_auth("pro@example.com").patch(url)

            assert response.status_code == 204
            booking = Booking.query.one()
            assert booking.status is BookingStatus.USED

        def expect_booking_with_token_in_lower_case_to_be_used(self, client):
            booking = bookings_factories.IndividualBookingFactory(token="ABCDEF")
            pro_user = users_factories.ProFactory(email="pro@example.com")
            offers_factories.UserOffererFactory(user=pro_user, offerer=booking.offerer)

            url = f"/bookings/token/{booking.token.lower()}"
            response = client.with_session_auth("pro@example.com").patch(url)

            assert response.status_code == 204
            booking = Booking.query.one()
            assert booking.status is BookingStatus.USED

        # FIXME: what is the purpose of this test? Are we testing that
        # Flask knows how to URL-decode parameters?
        def expect_booking_to_be_used_with_special_char_in_url(self, client):
            booking = bookings_factories.IndividualBookingFactory(
                token="ABCDEF", individualBooking__user__email="user+plus@example.com"
            )
            pro_user = users_factories.ProFactory(email="pro@example.com")
            offers_factories.UserOffererFactory(user=pro_user, offerer=booking.offerer)

            quoted_email = urllib.parse.quote("user+plus@example.com")
            url = f"/bookings/token/{booking.token}?email={quoted_email}"
            client = client.with_session_auth("pro@example.com")
            response = client.patch(url)

            assert response.status_code == 204
            booking = Booking.query.one()
            assert booking.status is BookingStatus.USED


@pytest.mark.usefixtures("db_session")
class Returns400Test:
    class WhenUserIsAnonymousTest:
        def when_email_is_missing(self, client):
            # Given
            booking = bookings_factories.IndividualBookingFactory()
            url = "/bookings/token/{}?&offer_id={}".format(booking.token, humanize(booking.stock.offer.id))

            # When
            response = client.patch(url)

            # Then
            assert response.status_code == 400
            assert response.json["email"] == [
                "L'adresse email qui a servie à la réservation est obligatoire dans l'URL [?email=<email>]"
            ]

        def when_offer_id_is_missing(self, client):
            # Given
            booking = bookings_factories.IndividualBookingFactory()
            url = "/bookings/token/{}?email={}".format(booking.token, booking.email)

            # When
            response = client.patch(url)

            # Then
            assert response.status_code == 400
            assert response.json["offer_id"] == ["L'id de l'offre réservée est obligatoire dans l'URL [?offer_id=<id>]"]

        def when_both_email_and_offer_id_are_missing(self, client):
            # Given
            booking = bookings_factories.IndividualBookingFactory()
            url = "/bookings/token/{}".format(booking.token)

            # When
            response = client.patch(url)

            # Then
            assert response.status_code == 400
            assert response.json["offer_id"] == ["L'id de l'offre réservée est obligatoire dans l'URL [?offer_id=<id>]"]
            assert response.json["email"] == [
                "L'adresse email qui a servie à la réservation est obligatoire dans l'URL [?email=<email>]"
            ]


@pytest.mark.usefixtures("db_session")
class Returns403Test:  # Forbidden
    def when_user_is_not_attached_to_linked_offerer(self, client):
        # Given
        pro = users_factories.ProFactory(email="pro@example.com")
        booking = bookings_factories.IndividualBookingFactory()

        url = "/bookings/token/{}?email={}".format(booking.token, booking.email)

        # When
        response = client.with_session_auth(pro.email).patch(url)

        # Then
        booking = Booking.query.get(booking.id)
        assert response.status_code == 403
        assert response.json["global"] == [
            "Vous n'avez pas les droits d'accès suffisant pour accéder à cette information."
        ]
        assert booking.status is not BookingStatus.USED


@pytest.mark.usefixtures("db_session")
class Returns404Test:
    class WhenUserIsAnonymousTest:
        def when_booking_does_not_exist(self, client):
            # Given
            booking = bookings_factories.IndividualBookingFactory()

            url = "/bookings/token/{}?email={}&offer_id={}".format(
                booking.token, "wrong.email@test.com", humanize(booking.stock.offer.id)
            )

            # When
            response = client.patch(url)

            # Then
            assert response.status_code == 404
            assert response.json["global"] == ["Cette contremarque n'a pas été trouvée"]

    class WhenUserIsLoggedInTest:
        def when_user_is_not_editor_and_email_does_not_match(self, client):
            # Given
            user_admin = users_factories.AdminFactory(email="admin@example.com")
            booking = bookings_factories.IndividualBookingFactory()
            url = "/bookings/token/{}?email={}".format(booking.token, "wrong@example.com")

            # When
            response = client.with_session_auth(user_admin.email).patch(url)

            # Then
            assert response.status_code == 404
            assert Booking.query.get(booking.id).status is not BookingStatus.USED

        def when_email_has_special_characters_but_is_not_url_encoded(self, client):
            # Given
            user = users_factories.BeneficiaryGrant18Factory(email="user+plus@example.com")
            user_admin = users_factories.AdminFactory(email="admin@example.com")
            booking = bookings_factories.IndividualBookingFactory(individualBooking__user=user)

            url = "/bookings/token/{}?email={}".format(booking.token, booking.email)

            # When
            response = client.with_session_auth(user_admin.email).patch(url)
            # Then
            assert response.status_code == 404

        def when_user_is_not_editor_and_offer_id_is_invalid(self, client):
            # Given
            user_admin = users_factories.AdminFactory(email="admin@example.com")
            booking = bookings_factories.IndividualBookingFactory()

            url = "/bookings/token/{}?email={}&offer_id={}".format(booking.token, booking.email, humanize(123))

            # When
            response = client.with_session_auth(user_admin.email).patch(url)

            # Then
            assert response.status_code == 404
            assert Booking.query.get(booking.id).status is not BookingStatus.USED


@pytest.mark.usefixtures("db_session")
class Returns410Test:
    def when_booking_has_been_cancelled_already(self, client):
        # Given
        admin = users_factories.AdminFactory()
        booking = bookings_factories.CancelledBookingFactory()
        url = f"/bookings/token/{booking.token}"

        # When
        response = client.with_session_auth(admin.email).patch(url)

        # Then
        assert response.status_code == 410
        assert response.json["booking_cancelled"] == ["Cette réservation a été annulée"]
        assert Booking.query.get(booking.id).status is not BookingStatus.USED
