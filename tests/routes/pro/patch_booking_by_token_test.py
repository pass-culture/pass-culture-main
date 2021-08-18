import urllib.parse

import pytest

import pcapi.core.bookings.factories as bookings_factories
from pcapi.core.bookings.models import BookingStatus
import pcapi.core.offers.factories as offers_factories
from pcapi.core.users import factories as users_factories
from pcapi.model_creators.generic_creators import create_booking
from pcapi.model_creators.generic_creators import create_offerer
from pcapi.model_creators.generic_creators import create_user_offerer
from pcapi.model_creators.generic_creators import create_venue
from pcapi.model_creators.specific_creators import create_event_occurrence
from pcapi.model_creators.specific_creators import create_offer_with_event_product
from pcapi.model_creators.specific_creators import create_stock_from_event_occurrence
from pcapi.model_creators.specific_creators import create_stock_with_event_offer
from pcapi.models import Booking
from pcapi.repository import repository
from pcapi.utils.human_ids import humanize

from tests.conftest import TestClient


@pytest.mark.usefixtures("db_session")
class Returns204Test:
    class WhenUserIsAnonymousTest:
        def expect_booking_to_be_used(self, app):
            booking = bookings_factories.BookingFactory(token="ABCDEF")

            url = (
                f"/bookings/token/{booking.token}?"
                f"email={booking.user.email}&offer_id={humanize(booking.stock.offerId)}"
            )
            response = TestClient(app.test_client()).patch(url)

            assert response.status_code == 204
            booking = Booking.query.one()
            assert booking.isUsed
            assert booking.status is BookingStatus.USED

    class WhenUserIsLoggedInTest:
        def expect_booking_to_be_used(self, app):
            booking = bookings_factories.BookingFactory(token="ABCDEF")
            pro_user = users_factories.ProFactory(email="pro@example.com")
            offerer = booking.stock.offer.venue.managingOfferer
            offers_factories.UserOffererFactory(user=pro_user, offerer=offerer)

            url = f"/bookings/token/{booking.token}"
            response = TestClient(app.test_client()).with_auth("pro@example.com").patch(url)

            assert response.status_code == 204
            booking = Booking.query.one()
            assert booking.isUsed
            assert booking.status is BookingStatus.USED

        def expect_booking_with_token_in_lower_case_to_be_used(self, app):
            booking = bookings_factories.BookingFactory(token="ABCDEF")
            pro_user = users_factories.ProFactory(email="pro@example.com")
            offerer = booking.stock.offer.venue.managingOfferer
            offers_factories.UserOffererFactory(user=pro_user, offerer=offerer)

            url = f"/bookings/token/{booking.token.lower()}"
            response = TestClient(app.test_client()).with_auth("pro@example.com").patch(url)

            assert response.status_code == 204
            booking = Booking.query.one()
            assert booking.isUsed
            assert booking.status is BookingStatus.USED

        def expect_booking_to_be_used_with_non_standard_origin_header(self, app):
            booking = bookings_factories.BookingFactory(token="ABCDEF")
            pro_user = users_factories.ProFactory(email="pro@example.com")
            offerer = booking.stock.offer.venue.managingOfferer
            offers_factories.UserOffererFactory(user=pro_user, offerer=offerer)

            url = f"/bookings/token/{booking.token.lower()}"
            client = TestClient(app.test_client()).with_auth("pro@example.com")
            response = client.patch(url, headers={"origin": "http://random_header.fr"})

            assert response.status_code == 204
            booking = Booking.query.one()
            assert booking.isUsed
            assert booking.status is BookingStatus.USED

        # FIXME: what is the purpose of this test? Are we testing that
        # Flask knows how to URL-decode parameters?
        def expect_booking_to_be_used_with_special_char_in_url(self, app):
            booking = bookings_factories.BookingFactory(token="ABCDEF", user__email="user+plus@example.com")
            pro_user = users_factories.ProFactory(email="pro@example.com")
            offerer = booking.stock.offer.venue.managingOfferer
            offers_factories.UserOffererFactory(user=pro_user, offerer=offerer)

            quoted_email = urllib.parse.quote("user+plus@example.com")
            url = f"/bookings/token/{booking.token}?email={quoted_email}"
            client = TestClient(app.test_client()).with_auth("pro@example.com")
            response = client.patch(url, headers={"origin": "http://random_header.fr"})

            assert response.status_code == 204
            booking = Booking.query.one()
            assert booking.isUsed
            assert booking.status is BookingStatus.USED


@pytest.mark.usefixtures("db_session")
class Returns400Test:
    class WhenUserIsAnonymousTest:
        def when_email_is_missing(self, app):
            # Given
            user = users_factories.BeneficiaryFactory()
            offerer = create_offerer()
            venue = create_venue(offerer)
            stock = create_stock_with_event_offer(offerer, venue, price=0)
            booking = create_booking(user=user, stock=stock, venue=venue)
            repository.save(booking)
            url = "/bookings/token/{}?&offer_id={}".format(booking.token, humanize(stock.offer.id))

            # When
            response = TestClient(app.test_client()).patch(url)

            # Then
            assert response.status_code == 400
            assert response.json["email"] == [
                "L'adresse email qui a servie à la réservation est obligatoire dans l'URL [?email=<email>]"
            ]

        def when_offer_id_is_missing(self, app):
            # Given
            user = users_factories.BeneficiaryFactory()
            offerer = create_offerer()
            venue = create_venue(offerer)
            stock = create_stock_with_event_offer(offerer, venue, price=0)
            booking = create_booking(user=user, stock=stock, venue=venue)
            repository.save(booking)
            url = "/bookings/token/{}?email={}".format(booking.token, user.email)

            # When
            response = TestClient(app.test_client()).patch(url)

            # Then
            assert response.status_code == 400
            assert response.json["offer_id"] == ["L'id de l'offre réservée est obligatoire dans l'URL [?offer_id=<id>]"]

        def when_both_email_and_offer_id_are_missing(self, app):
            # Given
            user = users_factories.BeneficiaryFactory()
            offerer = create_offerer()
            venue = create_venue(offerer)
            stock = create_stock_with_event_offer(offerer, venue, price=0)
            booking = create_booking(user=user, stock=stock, venue=venue)
            repository.save(booking)
            url = "/bookings/token/{}".format(booking.token)

            # When
            response = TestClient(app.test_client()).patch(url)

            # Then
            assert response.status_code == 400
            assert response.json["offer_id"] == ["L'id de l'offre réservée est obligatoire dans l'URL [?offer_id=<id>]"]
            assert response.json["email"] == [
                "L'adresse email qui a servie à la réservation est obligatoire dans l'URL [?email=<email>]"
            ]


@pytest.mark.usefixtures("db_session")
class Returns403Test:  # Forbidden
    def when_user_is_not_attached_to_linked_offerer(self, app):
        # Given
        user = users_factories.BeneficiaryFactory.build()
        pro = users_factories.ProFactory.build(email="pro@example.com")

        offerer = create_offerer()
        venue = create_venue(offerer)
        stock = create_stock_with_event_offer(offerer, venue, price=0)
        booking = create_booking(user=user, stock=stock, venue=venue)
        repository.save(booking, pro)
        booking_id = booking.id
        url = "/bookings/token/{}?email={}".format(booking.token, user.email)

        # When
        response = TestClient(app.test_client()).with_auth("pro@example.com").patch(url)

        # Then
        booking = Booking.query.get(booking_id)
        assert response.status_code == 403
        assert response.json["global"] == [
            "Vous n'avez pas les droits d'accès suffisant pour accéder à cette information."
        ]
        assert not booking.isUsed
        assert booking.status is not BookingStatus.USED

    def when_booking_has_been_cancelled_already(self, app):
        # Given
        admin = users_factories.AdminFactory()
        booking = bookings_factories.CancelledBookingFactory()
        url = f"/bookings/token/{booking.token}"

        # When
        response = TestClient(app.test_client()).with_auth(admin.email).patch(url)

        # Then
        assert response.status_code == 403
        assert response.json["booking"] == ["Cette réservation a été annulée"]
        assert Booking.query.get(booking.id).isUsed is False


@pytest.mark.usefixtures("db_session")
class Returns404Test:
    class WhenUserIsAnonymousTest:
        def when_booking_does_not_exist(self, app):
            # Given
            user = users_factories.BeneficiaryFactory()
            offerer = create_offerer()
            venue = create_venue(offerer)
            stock = create_stock_with_event_offer(offerer, venue, price=0)
            booking = create_booking(user=user, stock=stock, venue=venue)
            repository.save(booking)
            url = "/bookings/token/{}?email={}&offer_id={}".format(
                booking.token, "wrong.email@test.com", humanize(stock.offer.id)
            )

            # When
            response = TestClient(app.test_client()).patch(url)

            # Then
            assert response.status_code == 404
            assert response.json["global"] == ["Cette contremarque n'a pas été trouvée"]

    class WhenUserIsLoggedInTest:
        def when_user_is_not_editor_and_email_does_not_match(self, app):
            # Given
            user = users_factories.BeneficiaryFactory()
            users_factories.AdminFactory(email="admin@example.com")
            offerer = create_offerer()
            venue = create_venue(offerer)
            stock = create_stock_with_event_offer(offerer, venue, price=0)
            booking = create_booking(user=user, stock=stock, venue=venue)
            repository.save(booking)
            booking_id = booking.id
            url = "/bookings/token/{}?email={}".format(booking.token, "wrong@example.com")

            # When
            response = TestClient(app.test_client()).with_auth("admin@example.com").patch(url)

            # Then
            assert response.status_code == 404
            assert Booking.query.get(booking_id).isUsed is False

        def when_email_has_special_characters_but_is_not_url_encoded(self, app):
            # Given
            user = users_factories.BeneficiaryFactory(email="user+plus@example.com")
            user_admin = users_factories.AdminFactory(email="admin@example.com")
            offerer = create_offerer()
            user_offerer = create_user_offerer(user_admin, offerer)
            venue = create_venue(offerer)
            offer = create_offer_with_event_product(venue, event_name="Event Name")
            event_occurrence = create_event_occurrence(offer)
            stock = create_stock_from_event_occurrence(event_occurrence, price=0)
            booking = create_booking(user=user, stock=stock, venue=venue)

            repository.save(user_offerer, booking)
            url = "/bookings/token/{}?email={}".format(booking.token, user.email)

            # When
            response = TestClient(app.test_client()).with_auth("admin@example.com").patch(url)
            # Then
            assert response.status_code == 404

        def when_user_is_not_editor_and_offer_id_is_invalid(self, app):
            # Given
            user = users_factories.BeneficiaryFactory()
            users_factories.AdminFactory(email="admin@example.com")
            offerer = create_offerer()
            venue = create_venue(offerer)
            stock = create_stock_with_event_offer(offerer, venue, price=0)
            booking = create_booking(user=user, stock=stock, venue=venue)
            repository.save(booking)
            booking_id = booking.id
            url = "/bookings/token/{}?email={}&offer_id={}".format(booking.token, user.email, humanize(123))

            # When
            response = TestClient(app.test_client()).with_auth("admin@example.com").patch(url)

            # Then
            assert response.status_code == 404
            assert Booking.query.get(booking_id).isUsed is False
