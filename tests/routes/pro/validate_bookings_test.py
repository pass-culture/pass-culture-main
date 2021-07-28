from datetime import datetime
from datetime import timedelta
from unittest import mock
import urllib.parse

import pytest

from pcapi.core.bookings.factories import BookingFactory
import pcapi.core.bookings.models as bookings_models
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
from pcapi.models import api_errors
from pcapi.repository import repository
from pcapi.utils.human_ids import humanize

from tests.conftest import TestClient


tomorrow = datetime.utcnow() + timedelta(days=1)
tomorrow_minus_one_hour = tomorrow - timedelta(hours=1)


@pytest.mark.usefixtures("db_session")
class Returns204Test:  # No Content
    def when_user_has_rights(self, app):
        booking = BookingFactory(token="ABCDEF")
        pro_user = users_factories.ProFactory(email="pro@example.com")
        offerer = booking.stock.offer.venue.managingOfferer
        offers_factories.UserOffererFactory(user=pro_user, offerer=offerer)

        url = f"/bookings/token/{booking.token}"
        response = TestClient(app.test_client()).with_auth("pro@example.com").patch(url)

        assert response.status_code == 204
        booking = bookings_models.Booking.query.one()
        assert booking.isUsed
        assert booking.dateUsed is not None

    def when_header_is_not_standard_but_request_is_valid(self, app):
        booking = BookingFactory(token="ABCDEF")
        pro_user = users_factories.ProFactory(email="pro@example.com")
        offerer = booking.stock.offer.venue.managingOfferer
        offers_factories.UserOffererFactory(user=pro_user, offerer=offerer)

        url = f"/bookings/token/{booking.token}"
        client = TestClient(app.test_client()).with_auth("pro@example.com")
        response = client.patch(url, headers={"origin": "http://random_header.fr"})

        assert response.status_code == 204
        booking = bookings_models.Booking.query.one()
        assert booking.isUsed

    # FIXME: what is the purpose of this test? Are we testing that
    # Flask knows how to URL-decode parameters?
    def when_booking_user_email_has_special_character_url_encoded(self, app):
        booking = BookingFactory(
            token="ABCDEF",
            user__email="user+plus@example.com",
        )
        pro_user = users_factories.ProFactory(email="pro@example.com")
        offerer = booking.stock.offer.venue.managingOfferer
        offers_factories.UserOffererFactory(user=pro_user, offerer=offerer)

        quoted_email = urllib.parse.quote("user+plus@example.com")
        url = f"/bookings/token/{booking.token}?email={quoted_email}"
        client = TestClient(app.test_client()).with_auth("pro@example.com")
        response = client.patch(url, headers={"origin": "http://random_header.fr"})

        assert response.status_code == 204
        booking = bookings_models.Booking.query.one()
        assert booking.isUsed
        assert booking.status is bookings_models.BookingStatus.USED


class Returns403Test:
    @pytest.mark.usefixtures("db_session")
    def when_user_not_editor_and_valid_email(self, app):
        # Given
        user = users_factories.BeneficiaryFactory()
        pro = users_factories.ProFactory(email="pro@example.com")
        offerer = create_offerer()
        venue = create_venue(offerer)
        stock = create_stock_with_event_offer(
            offerer, venue, price=0, beginning_datetime=tomorrow, booking_limit_datetime=tomorrow_minus_one_hour
        )
        booking = create_booking(user=user, stock=stock, venue=venue)
        repository.save(booking, pro)
        booking_id = booking.id
        url = "/bookings/token/{}?email={}".format(booking.token, user.email)

        # When
        response = TestClient(app.test_client()).with_auth("pro@example.com").patch(url)

        # Then
        assert response.status_code == 403
        assert response.json["global"] == [
            "Vous n'avez pas les droits d'accès suffisant pour accéder à cette information."
        ]
        assert not Booking.query.get(booking_id).isUsed

    @mock.patch("pcapi.core.bookings.validation.check_is_usable")
    @pytest.mark.usefixtures("db_session")
    def when_booking_not_confirmed(self, mocked_check_is_usable, app):
        # Given
        next_week = datetime.utcnow() + timedelta(weeks=1)
        booking = BookingFactory(stock__beginningDatetime=next_week)
        pro_user = users_factories.ProFactory(email="pro@example.com")
        offerer = booking.stock.offer.venue.managingOfferer
        offers_factories.UserOffererFactory(user=pro_user, offerer=offerer)
        url = "/bookings/token/{}".format(booking.token)
        mocked_check_is_usable.side_effect = api_errors.ForbiddenError(errors={"booking": ["Not confirmed"]})

        # When
        response = TestClient(app.test_client()).with_auth("pro@example.com").patch(url)

        # Then
        assert response.status_code == 403
        assert response.json["booking"] == ["Not confirmed"]

    @pytest.mark.usefixtures("db_session")
    def when_booking_is_cancelled(self, app):
        # Given
        admin = users_factories.AdminFactory()
        booking = BookingFactory(isCancelled=True, status=bookings_models.BookingStatus.CANCELLED)
        url = f"/bookings/token/{booking.token}"

        # When
        response = TestClient(app.test_client()).with_auth(admin.email).patch(url)

        # Then
        assert response.status_code == 403
        assert response.json["booking"] == ["Cette réservation a été annulée"]
        assert not Booking.query.get(booking.id).isUsed


class Returns404Test:
    @pytest.mark.usefixtures("db_session")
    def when_user_not_editor_and_invalid_email(self, app):
        # Given
        user = users_factories.BeneficiaryFactory()
        admin_user = users_factories.AdminFactory(email="admin@example.com")
        offerer = create_offerer()
        venue = create_venue(offerer)
        stock = create_stock_with_event_offer(
            offerer, venue, price=0, beginning_datetime=tomorrow, booking_limit_datetime=tomorrow_minus_one_hour
        )
        booking = create_booking(user=user, stock=stock, venue=venue)
        repository.save(booking, admin_user)
        booking_id = booking.id
        url = "/bookings/token/{}?email={}".format(booking.token, "wrong@example.com")

        # When
        response = TestClient(app.test_client()).with_auth("admin@example.com").patch(url)

        # Then
        assert response.status_code == 404
        assert not Booking.query.get(booking_id).isUsed

    @pytest.mark.usefixtures("db_session")
    def when_booking_user_email_with_special_character_not_url_encoded(self, app):
        # Given
        user = users_factories.BeneficiaryFactory(email="user+plus@example.com")
        admin_user = users_factories.AdminFactory(email="admin@example.com")
        offerer = create_offerer()
        user_offerer = create_user_offerer(admin_user, offerer)
        venue = create_venue(offerer)
        offer = create_offer_with_event_product(venue, event_name="Event Name")
        event_occurrence = create_event_occurrence(offer, beginning_datetime=tomorrow)
        stock = create_stock_from_event_occurrence(
            event_occurrence, price=0, booking_limit_date=tomorrow_minus_one_hour
        )
        booking = create_booking(user=user, stock=stock, venue=venue)

        repository.save(user_offerer, booking)
        url = "/bookings/token/{}?email={}".format(booking.token, user.email)

        # When
        response = TestClient(app.test_client()).with_auth("admin@example.com").patch(url)

        # Then
        assert response.status_code == 404

    @pytest.mark.usefixtures("db_session")
    def when_user_not_editor_and_valid_email_but_invalid_offer_id(self, app):
        # Given
        user = users_factories.BeneficiaryFactory()
        admin_user = users_factories.AdminFactory(email="admin@example.com")
        offerer = create_offerer()
        venue = create_venue(offerer)
        stock = create_stock_with_event_offer(
            offerer, venue, price=0, beginning_datetime=tomorrow, booking_limit_datetime=tomorrow_minus_one_hour
        )
        booking = create_booking(user=user, stock=stock, venue=venue)
        repository.save(booking, admin_user)
        booking_id = booking.id
        url = "/bookings/token/{}?email={}&offer_id={}".format(booking.token, user.email, humanize(123))

        # When
        response = TestClient(app.test_client()).with_auth("admin@example.com").patch(url)

        # Then
        assert response.status_code == 404
        assert not Booking.query.get(booking_id).isUsed
