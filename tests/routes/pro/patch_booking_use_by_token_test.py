import datetime

import pytest

import pcapi.core.bookings.factories as bookings_factories
from pcapi.core.bookings.models import BookingStatus
from pcapi.core.categories import subcategories
from pcapi.core.educational.models import EducationalBookingStatus
from pcapi.core.offerers.factories import ApiKeyFactory
from pcapi.core.offerers.factories import DEFAULT_CLEAR_API_KEY
import pcapi.core.offers.factories as offers_factories
from pcapi.core.users import factories as users_factories
from pcapi.model_creators.generic_creators import create_booking
from pcapi.model_creators.generic_creators import create_offerer
from pcapi.model_creators.generic_creators import create_stock
from pcapi.model_creators.generic_creators import create_user_offerer
from pcapi.model_creators.generic_creators import create_venue
from pcapi.model_creators.specific_creators import create_offer_with_thing_product
from pcapi.model_creators.specific_creators import create_stock_with_event_offer
from pcapi.models import Booking
from pcapi.repository import repository
from pcapi.utils.token import random_token

from tests.conftest import TestClient


pytestmark = pytest.mark.usefixtures("db_session")

API_KEY_VALUE = random_token(64)


class Returns204Test:
    class WithApiKeyAuthTest:
        def test_when_api_key_is_provided_and_rights_and_regular_offer(self, app):
            booking = bookings_factories.BookingFactory(token="ABCDEF")
            offerer = booking.stock.offer.venue.managingOfferer
            ApiKeyFactory(offerer=offerer)

            url = f"/v2/bookings/use/token/{booking.token}"
            response = TestClient(app.test_client()).patch(
                url,
                headers={
                    "Authorization": f"Bearer {DEFAULT_CLEAR_API_KEY}",
                    "Origin": "http://localhost",
                },
            )

            assert response.status_code == 204
            booking = Booking.query.one()
            assert booking.isUsed
            assert booking.status == BookingStatus.USED

        def test_expect_booking_to_be_used_with_non_standard_origin_header(self, app):
            booking = bookings_factories.BookingFactory(token="ABCDEF")
            offerer = booking.stock.offer.venue.managingOfferer
            ApiKeyFactory(offerer=offerer)

            url = f"/v2/bookings/use/token/{booking.token}"
            response = TestClient(app.test_client()).patch(
                url,
                headers={
                    "Authorization": f"Bearer {DEFAULT_CLEAR_API_KEY}",
                    "Origin": "http://example.com",
                },
            )

            assert response.status_code == 204
            booking = Booking.query.one()
            assert booking.isUsed
            assert booking.status == BookingStatus.USED

    class WithBasicAuthTest:
        def test_when_user_is_logged_in_and_regular_offer(self, app):
            booking = bookings_factories.BookingFactory(token="ABCDEF")
            pro_user = users_factories.ProFactory(email="pro@example.com")
            offerer = booking.stock.offer.venue.managingOfferer
            offers_factories.UserOffererFactory(user=pro_user, offerer=offerer)

            url = f"/v2/bookings/use/token/{booking.token}"
            response = TestClient(app.test_client()).with_session_auth("pro@example.com").patch(url)

            assert response.status_code == 204
            booking = Booking.query.one()
            assert booking.isUsed
            assert booking.status == BookingStatus.USED

        def test_when_user_is_logged_in_expect_booking_with_token_in_lower_case_to_be_used(self, app):
            booking = bookings_factories.BookingFactory(token="ABCDEF")
            pro_user = users_factories.ProFactory(email="pro@example.com")
            offerer = booking.stock.offer.venue.managingOfferer
            offers_factories.UserOffererFactory(user=pro_user, offerer=offerer)

            url = f"/v2/bookings/use/token/{booking.token.lower()}"
            response = TestClient(app.test_client()).with_session_auth("pro@example.com").patch(url)

            assert response.status_code == 204
            booking = Booking.query.one()
            assert booking.isUsed
            assert booking.status == BookingStatus.USED

        def test_when_user_is_logged_in_and_offer_is_educational_validated_by_institution(self, app):
            # Given
            booking = bookings_factories.EducationalBookingFactory(
                token="ABCDEF",
                dateCreated=datetime.datetime.utcnow() - datetime.timedelta(days=3),
                educationalBooking__status=EducationalBookingStatus.USED_BY_INSTITUTE,
            )
            pro_user = users_factories.ProFactory(email="pro@example.com")
            offerer = booking.stock.offer.venue.managingOfferer
            offers_factories.UserOffererFactory(user=pro_user, offerer=offerer)

            # When
            url = f"/v2/bookings/use/token/{booking.token}"
            response = TestClient(app.test_client()).with_session_auth("pro@example.com").patch(url)

            # Then
            assert response.status_code == 204
            booking = Booking.query.one()
            assert booking.isUsed
            assert booking.status == BookingStatus.USED


class Returns401Test:
    def test_when_user_not_logged_in_and_doesnt_give_api_key(self, app):
        # Given
        user = users_factories.BeneficiaryFactory(email="user@example.com")
        offerer = create_offerer()
        venue = create_venue(offerer)
        stock = create_stock_with_event_offer(offerer, venue, price=0)
        booking = create_booking(user=user, stock=stock, venue=venue)

        repository.save(booking)

        # When
        url = "/v2/bookings/use/token/{}".format(booking.token)
        response = TestClient(app.test_client()).patch(url)

        # Then
        assert response.status_code == 401

    def test_when_user_not_logged_in_and_not_existing_api_key_given(self, app):
        # Given
        user = users_factories.BeneficiaryFactory(email="user@example.com")
        users_factories.ProFactory(email="pro@example.com")
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock = create_stock(offer=offer, price=0)
        booking = create_booking(user=user, stock=stock, venue=venue)

        repository.save(booking)

        # When
        url = "/v2/bookings/use/token/{}".format(booking.token)
        response = TestClient(app.test_client()).patch(
            url, headers={"Authorization": "Bearer WrongApiKey1234567", "Origin": "http://localhost"}
        )

        # Then
        assert response.status_code == 401


class Returns403Test:
    class WithApiKeyAuthTest:
        def test_when_api_key_given_not_related_to_booking_offerer(self, app):
            # Given
            user = users_factories.BeneficiaryFactory(email="user@example.com")
            offerer2 = offers_factories.OffererFactory(siren="987654321")
            offer = offers_factories.EventOfferFactory(subcategoryId=subcategories.SEANCE_CINE.id)
            stock = offers_factories.EventStockFactory(offer=offer, price=0)
            booking = bookings_factories.BookingFactory(user=user, stock=stock)

            ApiKeyFactory(offerer=offerer2)

            user2ApiKey = "Bearer " + DEFAULT_CLEAR_API_KEY

            # When
            url = "/v2/bookings/use/token/{}".format(booking.token)
            response = TestClient(app.test_client()).patch(
                url, headers={"Authorization": user2ApiKey, "Origin": "http://localhost"}
            )

            # Then
            assert response.status_code == 403
            assert response.json["user"] == ["Vous n'avez pas les droits suffisants pour valider cette contremarque."]

        def test_when_api_key_is_provided_and_booking_has_been_cancelled_already(self, app):
            # Given
            user = users_factories.BeneficiaryFactory()
            pro_user = users_factories.ProFactory(email="pro@example.com")
            offerer = create_offerer()
            user_offerer = create_user_offerer(pro_user, offerer)
            venue = create_venue(offerer)
            stock = create_stock_with_event_offer(offerer, venue, price=0)
            booking = create_booking(user=user, stock=stock, venue=venue, is_cancelled=True)
            repository.save(booking, user_offerer)
            url = f"/v2/bookings/use/token/{booking.token}"

            # When
            response = TestClient(app.test_client()).with_session_auth(pro_user.email).patch(url)

            # Then
            assert response.status_code == 403
            assert response.json["booking"] == ["Cette réservation a été annulée"]
            booking = Booking.query.get(booking.id)
            assert not booking.isUsed
            assert booking.status is not BookingStatus.USED

    class WithBasicAuthTest:
        def test_when_user_is_not_attached_to_linked_offerer(self, app):
            # Given
            user = users_factories.BeneficiaryFactory()
            users_factories.ProFactory(email="pro@example.com")
            offerer = create_offerer()
            venue = create_venue(offerer)
            stock = create_stock_with_event_offer(offerer, venue, price=0)
            booking = create_booking(user=user, stock=stock, venue=venue)
            repository.save(booking)
            url = f"/v2/bookings/use/token/{booking.token}"

            # When
            response = TestClient(app.test_client()).with_session_auth("pro@example.com").patch(url)

            # Then
            assert response.status_code == 403
            assert response.json["user"] == ["Vous n'avez pas les droits suffisants pour valider cette contremarque."]
            booking = Booking.query.get(booking.id)
            assert not booking.isUsed
            assert booking.status is not BookingStatus.USED

        def test_when_user_is_logged_in_and_booking_has_been_cancelled_already(self, app):
            # Given
            admin = users_factories.AdminFactory()
            booking = bookings_factories.CancelledBookingFactory()
            url = f"/v2/bookings/use/token/{booking.token}"

            # When
            response = TestClient(app.test_client()).with_session_auth(admin.email).patch(url)

            # Then
            assert response.status_code == 403
            assert response.json["booking"] == ["Cette réservation a été annulée"]
            booking = Booking.query.get(booking.id)
            assert not booking.isUsed
            assert booking.status is not BookingStatus.USED

        def test_when_user_is_logged_in_and_offer_is_educational_but_not_validated_by_institution_yet(self, app):
            # Given
            booking = bookings_factories.EducationalBookingFactory(
                token="ABCDEF",
                dateCreated=datetime.datetime.utcnow() - datetime.timedelta(days=3),
                educationalBooking__status=None,
            )
            pro_user = users_factories.ProFactory(email="pro@example.com")
            offerer = booking.stock.offer.venue.managingOfferer
            offers_factories.UserOffererFactory(user=pro_user, offerer=offerer)

            # When
            url = f"/v2/bookings/use/token/{booking.token}"
            response = TestClient(app.test_client()).with_session_auth("pro@example.com").patch(url)

            # Then
            assert response.status_code == 403
            assert (
                response.json["educationalBooking"]
                == "Cette réservation pour une offre éducationnelle n'est pas encore validée par le chef d'établissement"
            )
            booking = Booking.query.get(booking.id)
            assert not booking.isUsed
            assert booking.status is not BookingStatus.USED

        def test_when_user_is_logged_in_and_offer_is_educational_but_has_been_refused_by_institution(self, app):
            # Given
            booking = bookings_factories.EducationalBookingFactory(
                token="ABCDEF",
                dateCreated=datetime.datetime.utcnow() - datetime.timedelta(days=3),
                educationalBooking__status=EducationalBookingStatus.REFUSED,
            )
            pro_user = users_factories.ProFactory(email="pro@example.com")
            offerer = booking.stock.offer.venue.managingOfferer
            offers_factories.UserOffererFactory(user=pro_user, offerer=offerer)

            # When
            url = f"/v2/bookings/use/token/{booking.token}"
            response = TestClient(app.test_client()).with_session_auth("pro@example.com").patch(url)

            # Then
            assert response.status_code == 403
            assert (
                response.json["educationalBooking"]
                == "Cette réservation pour une offre éducationnelle a été refusée par le chef d'établissement"
            )
            booking = Booking.query.get(booking.id)
            assert booking.isUsed is False
            assert booking.status is not BookingStatus.USED


class Returns404Test:
    def test_when_booking_is_not_provided_at_all(self, app):
        # Given
        user = users_factories.BeneficiaryFactory(email="user@example.com")
        offerer = create_offerer()
        venue = create_venue(offerer)
        stock = create_stock_with_event_offer(offerer, venue, price=0)
        booking = create_booking(user=user, stock=stock, venue=venue)

        repository.save(booking)

        # When
        url = "/v2/bookings/use/token/"
        response = TestClient(app.test_client()).patch(url)

        # Then
        assert response.status_code == 404

    class WithApiKeyAuthTest:
        def test_when_api_key_is_provided_and_booking_does_not_exist(self, app):
            # Given
            user = users_factories.BeneficiaryFactory()
            offerer = create_offerer()
            venue = create_venue(offerer)
            stock = create_stock_with_event_offer(offerer, venue, price=0)
            booking = create_booking(user=user, stock=stock, venue=venue)
            repository.save(booking)

            ApiKeyFactory(offerer=offerer)

            user2ApiKey = "Bearer " + DEFAULT_CLEAR_API_KEY

            # When
            url = "/v2/bookings/use/token/{}".format("456789")
            response = TestClient(app.test_client()).patch(
                url, headers={"Authorization": user2ApiKey, "Origin": "http://localhost"}
            )

            # Then
            assert response.status_code == 404
            assert response.json["global"] == ["Cette contremarque n'a pas été trouvée"]

    class WithBasicAuthTest:
        def test_when_user_is_logged_in_and_booking_does_not_exist(self, app):
            # Given
            user = users_factories.BeneficiaryFactory()
            pro_user = users_factories.ProFactory(email="pro@example.com")
            offerer = create_offerer()
            user_offerer = create_user_offerer(pro_user, offerer)
            venue = create_venue(offerer)
            stock = create_stock_with_event_offer(offerer, venue, price=0)
            booking = create_booking(user=user, stock=stock, venue=venue)
            repository.save(booking, user_offerer)

            # When
            url = "/v2/bookings/use/token/{}".format("123456")
            response = TestClient(app.test_client()).with_session_auth("pro@example.com").patch(url)

            # Then
            assert response.status_code == 404
            assert response.json["global"] == ["Cette contremarque n'a pas été trouvée"]
