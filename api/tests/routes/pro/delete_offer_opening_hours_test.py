import contextlib

import pytest

import pcapi.core.bookings.factories as bookings_factories
from pcapi.core.bookings.models import BookingStatus
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
from pcapi.core.testing import assert_num_queries
from pcapi.models import db


pytestmark = pytest.mark.usefixtures("db_session")


def build_venue(user_email):
    offerer = offerers_factories.UserOffererFactory(user__email=user_email).offerer
    return offerers_factories.VirtualVenueFactory(managingOfferer=offerer)


class DeleteEventOpeningHoursTest:
    endpoint = "/offers/{offer_id}/event_opening_hours/{event_opening_hour_id}"

    queries_base_count = 1  # fetch session
    queries_base_count += 1  # fetch user
    queries_base_count += 1  # fetch offer and its venue
    queries_base_count += 1  # fetch offer's stocks
    queries_base_count += 1  # check offer access to venue
    queries_base_count += 1  # fetch offer's event opening hours and its week day opening hours
    queries_base_count += 1  # update event opening hours

    def test_offer_without_stock_is_soft_deleted(self, auth_client, client_email):
        event = offers_factories.EventOpeningHoursFactory(offer__venue=build_venue(client_email))

        with assert_opening_hours_is_soft_deleted(event):
            response = self._delete_opening_hours(auth_client, event, queries_count=self.queries_base_count)
            assert response.status_code == 204

    def test_offer_with_stock_and_no_booking_is_soft_deleted(self, auth_client, client_email):
        venue = build_venue(client_email)
        offer = offers_factories.EventStockFactory(offer__venue=venue, quantity=2).offer
        event = offers_factories.EventOpeningHoursFactory(offer=offer)

        # fetch bookings (even if none) and update stock
        expected_queries_count = self.queries_base_count + 2

        with assert_opening_hours_is_soft_deleted(event):
            response = self._delete_opening_hours(auth_client, event, queries_count=expected_queries_count)
            assert response.status_code == 204

    def test_offer_with_cancellable_booking_is_soft_deleted(self, auth_client, client_email):
        venue = build_venue(client_email)
        offer = bookings_factories.BookingFactory(status=BookingStatus.CONFIRMED, stock__offer__venue=venue).stock.offer
        event = offers_factories.EventOpeningHoursFactory(offer=offer)

        with assert_opening_hours_is_soft_deleted(event):
            # calling assert_num_queries might be a little tricky since booking
            # cancellation triggers a lot of queries which is difficult to
            # track and is not related to a missing selectinload/joinedload
            # called early from the controller.
            response = self._delete_opening_hours(auth_client, event)
            assert response.status_code == 204

    def test_offer_with_cancelled_or_reimbursed_bookings_is_soft_deleted(self, auth_client, client_email):
        venue = build_venue(client_email)
        offer = offers_factories.EventStockFactory(offer__venue=venue, quantity=2).offer
        event = offers_factories.EventOpeningHoursFactory(offer=offer)

        bookings_factories.BookingFactory(stock__offer=offer, status=BookingStatus.CANCELLED)
        bookings_factories.BookingFactory(stock__offer=offer, status=BookingStatus.REIMBURSED)

        with assert_opening_hours_is_soft_deleted(event):
            # calling assert_num_queries might be a little tricky since booking
            # cancellation triggers a lot of queries which is difficult to
            # track and is not related to a missing selectinload/joinedload
            # called early from the controller.
            response = self._delete_opening_hours(auth_client, event)
            assert response.status_code == 204

    def test_offer_with_used_booking_is_not_soft_deleted(self, auth_client, client_email):
        venue = build_venue(client_email)
        offer = bookings_factories.BookingFactory(status=BookingStatus.USED, stock__offer__venue=venue).stock.offer
        event = offers_factories.EventOpeningHoursFactory(offer=offer)

        expected_queries_count = self.queries_base_count + 1  # rollback

        with assert_opening_hours_is_not_soft_deleted(event):
            response = self._delete_opening_hours(auth_client, event, queries_count=expected_queries_count)
            assert response.status_code == 400

    def test_delete_unknown_offer_returns_an_error(self, auth_client, client_email):
        venue = build_venue(client_email)
        event = offers_factories.EventOpeningHoursFactory(offer__venue=venue)

        with assert_opening_hours_is_not_soft_deleted(event):
            url = self.endpoint.format(offer_id=0, event_opening_hour_id=event.id)

            # fetch session + fetch user + fetch offer + rollback
            with assert_num_queries(4):
                response = auth_client.delete(url)
                assert response.status_code == 404

    def test_delete_unknown_event_opening_hours_returns_an_error(self, auth_client, client_email):
        venue = build_venue(client_email)
        event = offers_factories.EventOpeningHoursFactory(offer__venue=venue)

        with assert_opening_hours_is_not_soft_deleted(event):
            url = self.endpoint.format(offer_id=event.offer.id, event_opening_hour_id=0)

            # fetch session + fetch user + fetch offer + fetch stocks
            # + check if user has access to offer
            # + fetch event opening hours
            # + rollback
            with assert_num_queries(7):
                response = auth_client.delete(url)
                assert response.status_code == 404

    def test_delete_offer_from_another_offerer_returns_an_error(self, auth_client, client_email):
        offers_factories.EventOpeningHoursFactory(offer__venue=build_venue(client_email))

        # other venue -> other offerer -> no link to it, no right access
        unreachable_event = offers_factories.EventOpeningHoursFactory()
        offer = unreachable_event.offer

        with assert_opening_hours_is_not_soft_deleted(unreachable_event):
            url = self.endpoint.format(offer_id=offer.id, event_opening_hour_id=unreachable_event.id)

            # fetch session + fetch user + fetch offer + fetch stock
            # + check if user has access to offer
            # + rollback
            with assert_num_queries(6):
                response = auth_client.delete(url)
                assert response.status_code == 403

    def test_delete_offer_from_unauthenticated_client_returns_an_error(self, client):
        event = offers_factories.EventOpeningHoursFactory(offer__venue=build_venue("other@user.com"))

        with assert_opening_hours_is_not_soft_deleted(event):
            response = self._delete_opening_hours(client, event)
            assert response.status_code == 401

    def _delete_opening_hours(self, auth_client, event_opening_hours, queries_count=None):
        offer = event_opening_hours.offer
        url = self.endpoint.format(offer_id=offer.id, event_opening_hour_id=event_opening_hours.id)
        if queries_count is not None:
            with assert_num_queries(queries_count):
                return auth_client.delete(url)
        return auth_client.delete(url)


@contextlib.contextmanager
def assert_opening_hours_is_soft_deleted(event_opening_hours):
    yield

    db.session.refresh(event_opening_hours)
    assert event_opening_hours.isSoftDeleted

    for stock in event_opening_hours.offer.stocks:
        assert stock.isSoftDeleted

        for booking in stock.bookings:
            assert booking.status in (
                BookingStatus.CANCELLED,
                BookingStatus.REIMBURSED,
            )


@contextlib.contextmanager
def assert_opening_hours_is_not_soft_deleted(event_opening_hours):
    old_bookings_status = {
        booking.id: booking.status for stock in event_opening_hours.offer.stocks for booking in stock.bookings
    }

    yield

    new_bookings_status = {
        booking.id: booking.status for stock in event_opening_hours.offer.stocks for booking in stock.bookings
    }

    db.session.refresh(event_opening_hours)
    assert not event_opening_hours.isSoftDeleted

    for stock in event_opening_hours.offer.stocks:
        assert not stock.isSoftDeleted

    assert old_bookings_status == new_bookings_status
