from datetime import datetime
from datetime import timedelta
from unittest import mock
import urllib.parse

import pytest

import pcapi.core.bookings.factories as bookings_factories
import pcapi.core.bookings.models as bookings_models
from pcapi.core.bookings.models import Booking
import pcapi.core.offers.factories as offers_factories
from pcapi.core.users import factories as users_factories
from pcapi.models import api_errors
from pcapi.utils.human_ids import humanize


tomorrow = datetime.utcnow() + timedelta(days=1)
tomorrow_minus_one_hour = tomorrow - timedelta(hours=1)


@pytest.mark.usefixtures("db_session")
class Returns204Test:  # No Content
    def when_user_has_rights(self, client):
        booking = bookings_factories.IndividualBookingFactory(token="ABCDEF")
        pro_user = users_factories.ProFactory(email="pro@example.com")
        offers_factories.UserOffererFactory(user=pro_user, offerer=booking.offerer)

        url = f"/bookings/token/{booking.token}"
        response = client.with_session_auth("pro@example.com").patch(url)

        assert response.status_code == 204
        booking = bookings_models.Booking.query.one()
        assert booking.dateUsed is not None
        assert booking.status is bookings_models.BookingStatus.USED

    def when_header_is_not_standard_but_request_is_valid(self, client):
        booking = bookings_factories.IndividualBookingFactory(token="ABCDEF")
        pro_user = users_factories.ProFactory(email="pro@example.com")
        offers_factories.UserOffererFactory(user=pro_user, offerer=booking.offerer)

        url = f"/bookings/token/{booking.token}"
        client = client.with_session_auth("pro@example.com")
        response = client.patch(url)

        assert response.status_code == 204
        booking = bookings_models.Booking.query.one()
        assert booking.status is bookings_models.BookingStatus.USED

    # FIXME: what is the purpose of this test? Are we testing that
    # Flask knows how to URL-decode parameters?
    def when_booking_user_email_has_special_character_url_encoded(self, client):
        booking = bookings_factories.IndividualBookingFactory(
            token="ABCDEF",
            individualBooking__user__email="user+plus@example.com",
        )
        pro_user = users_factories.ProFactory(email="pro@example.com")
        offers_factories.UserOffererFactory(user=pro_user, offerer=booking.offerer)

        quoted_email = urllib.parse.quote("user+plus@example.com")
        url = f"/bookings/token/{booking.token}?email={quoted_email}"
        client = client.with_session_auth("pro@example.com")
        response = client.patch(url)

        assert response.status_code == 204
        booking = bookings_models.Booking.query.one()
        assert booking.status is bookings_models.BookingStatus.USED


class Returns403Test:
    @pytest.mark.usefixtures("db_session")
    def when_user_not_editor_and_valid_email(self, client):
        # Given
        pro = users_factories.ProFactory(email="pro@example.com")
        stock = offers_factories.EventStockFactory(
            price=0, beginningDatetime=tomorrow, bookingLimitDatetime=tomorrow_minus_one_hour
        )
        booking = bookings_factories.IndividualBookingFactory(stock=stock)
        url = "/bookings/token/{}?email={}".format(booking.token, booking.email)

        # When
        response = client.with_session_auth(pro.email).patch(url)

        # Then
        assert response.status_code == 403
        assert response.json["global"] == [
            "Vous n'avez pas les droits d'accès suffisant pour accéder à cette information."
        ]
        assert Booking.query.get(booking.id).status is not bookings_models.BookingStatus.USED

    @mock.patch("pcapi.core.bookings.validation.check_is_usable")
    @pytest.mark.usefixtures("db_session")
    def when_booking_not_confirmed(self, mocked_check_is_usable, client):
        # Given
        next_week = datetime.utcnow() + timedelta(weeks=1)
        booking = bookings_factories.IndividualBookingFactory(stock__beginningDatetime=next_week)
        pro_user = users_factories.ProFactory(email="pro@example.com")
        offers_factories.UserOffererFactory(user=pro_user, offerer=booking.offerer)
        url = "/bookings/token/{}".format(booking.token)
        mocked_check_is_usable.side_effect = api_errors.ForbiddenError(errors={"booking": ["Not confirmed"]})

        # When
        response = client.with_session_auth("pro@example.com").patch(url)

        # Then
        assert response.status_code == 403
        assert response.json["booking"] == ["Not confirmed"]


class Returns404Test:
    @pytest.mark.usefixtures("db_session")
    def when_user_not_editor_and_invalid_email(self, client):
        # Given
        admin_user = users_factories.AdminFactory(email="admin@example.com")
        stock = offers_factories.EventStockFactory(
            price=0, beginningDatetime=tomorrow, bookingLimitDatetime=tomorrow_minus_one_hour
        )
        booking = bookings_factories.IndividualBookingFactory(stock=stock)
        url = "/bookings/token/{}?email={}".format(booking.token, "wrong@example.com")

        # When
        response = client.with_session_auth(admin_user.email).patch(url)

        # Then
        assert response.status_code == 404
        assert Booking.query.get(booking.id).status is not bookings_models.BookingStatus.USED

    @pytest.mark.usefixtures("db_session")
    def when_booking_user_email_with_special_character_not_url_encoded(self, client):
        # Given
        user = users_factories.BeneficiaryGrant18Factory(email="user+plus@example.com")
        admin_user = users_factories.AdminFactory(email="admin@example.com")
        stock = offers_factories.EventStockFactory(
            price=0, beginningDatetime=tomorrow, bookingLimitDatetime=tomorrow_minus_one_hour
        )
        booking = bookings_factories.IndividualBookingFactory(individualBooking__user=user, stock=stock)
        url = "/bookings/token/{}?email={}".format(booking.token, user.email)

        # When
        response = client.with_session_auth(admin_user.email).patch(url)

        # Then
        assert response.status_code == 404

    @pytest.mark.usefixtures("db_session")
    def when_user_not_editor_and_valid_email_but_invalid_offer_id(self, client):
        # Given
        admin_user = users_factories.AdminFactory(email="admin@example.com")
        stock = offers_factories.EventStockFactory(
            price=0, beginningDatetime=tomorrow, bookingLimitDatetime=tomorrow_minus_one_hour
        )
        booking = bookings_factories.IndividualBookingFactory(stock=stock)
        booking_id = booking.id
        url = "/bookings/token/{}?email={}&offer_id={}".format(booking.token, booking.email, humanize(123))

        # When
        response = client.with_session_auth(admin_user.email).patch(url)

        # Then
        assert response.status_code == 404
        assert Booking.query.get(booking_id).status is not bookings_models.BookingStatus.USED


class Returns410Test:
    @pytest.mark.usefixtures("db_session")
    def when_booking_is_cancelled(self, client):
        # Given
        admin = users_factories.AdminFactory()
        booking = bookings_factories.CancelledBookingFactory()
        url = f"/bookings/token/{booking.token}"

        # When
        response = client.with_session_auth(admin.email).patch(url)

        # Then
        assert response.status_code == 410
        assert response.json["booking_cancelled"] == ["Cette réservation a été annulée"]
        assert Booking.query.get(booking.id).status is not bookings_models.BookingStatus.USED
