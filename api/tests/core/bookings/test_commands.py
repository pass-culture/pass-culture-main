import datetime
import logging
from datetime import date
from datetime import timedelta
from unittest import mock
from unittest.mock import patch

import pytest
import time_machine

import pcapi.core.mails.testing as mails_testing
from pcapi.core.bookings import commands as bookings_commands
from pcapi.core.bookings import factories as bookings_factories
from pcapi.core.bookings import models as bookings_models
from pcapi.core.categories import subcategories
from pcapi.core.external.batch import testing as notifications_testing
from pcapi.core.external.batch import transactional_notifications
from pcapi.core.mails.transactional.bookings.booking_event_reminder_to_beneficiary import (
    get_booking_event_reminder_to_beneficiary_email_data,
)
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offers import factories as offers_factories
from pcapi.core.offers import models as offer_models
from pcapi.core.offers.factories import ProductFactory
from pcapi.core.testing import assert_no_duplicated_queries
from pcapi.core.users import factories as users_factories
from pcapi.models import db
from pcapi.utils import date as date_utils

from tests.test_utils import run_command


pytestmark = pytest.mark.usefixtures("db_session")


class ArchiveOldBookingsTest:
    @pytest.mark.usefixtures("clean_database")
    def test_basics(self, app):
        # given
        now = date_utils.get_naive_utc_now()
        recent = now - datetime.timedelta(days=29, hours=23)
        old = now - datetime.timedelta(days=30, hours=1)
        offer = offers_factories.OfferFactory(url="http://example.com")
        stock = offers_factories.StockFactory(offer=offer)
        recent_booking = bookings_factories.BookingFactory(stock=stock, dateCreated=recent)
        old_booking = bookings_factories.BookingFactory(stock=stock, dateCreated=old)
        offers_factories.ActivationCodeFactory(booking=recent_booking, stock=stock)
        offers_factories.ActivationCodeFactory(booking=old_booking, stock=stock)
        recent_booking_id = recent_booking.id
        old_booking_id = old_booking.id
        db.session.commit()
        db.session.close()
        # when
        run_command(app, "archive_old_bookings")

        # then
        old_booking = db.session.get(bookings_models.Booking, old_booking_id)
        recent_booking = db.session.get(bookings_models.Booking, recent_booking_id)
        assert old_booking.displayAsEnded
        assert not recent_booking.displayAsEnded

    @pytest.mark.usefixtures("clean_database")
    @pytest.mark.parametrize(
        "subcategoryId",
        offer_models.Stock.AUTOMATICALLY_USED_SUBCATEGORIES,
    )
    def test_old_subcategories_bookings_are_archived(self, app, subcategoryId):
        # given
        now = date_utils.get_naive_utc_now()
        recent = now - datetime.timedelta(days=29, hours=23)
        old = now - datetime.timedelta(days=30, hours=1)
        stock_free = offers_factories.StockFactory(
            offer=offers_factories.OfferFactory(subcategoryId=subcategoryId), price=0
        )
        stock_not_free = offers_factories.StockFactory(
            offer=offers_factories.OfferFactory(subcategoryId=subcategoryId), price=10
        )
        recent_booking = bookings_factories.BookingFactory(stock=stock_free, dateCreated=recent)
        old_booking = bookings_factories.BookingFactory(stock=stock_free, dateCreated=old)
        old_not_free_booking = bookings_factories.BookingFactory(stock=stock_not_free, dateCreated=old)
        recent_booking_id = recent_booking.id
        old_booking_id = old_booking.id
        old_not_free_booking_id = old_not_free_booking.id
        db.session.commit()
        db.session.close()

        # when
        run_command(app, "archive_old_bookings")

        # then

        old_booking = db.session.get(bookings_models.Booking, old_booking_id)
        old_not_free_booking = db.session.get(bookings_models.Booking, old_not_free_booking_id)
        recent_booking = db.session.get(bookings_models.Booking, recent_booking_id)
        assert not recent_booking.displayAsEnded
        assert not old_not_free_booking.displayAsEnded
        assert old_booking.displayAsEnded

    @pytest.mark.usefixtures("clean_database")
    @pytest.mark.parametrize(
        "subcategoryId",
        offer_models.Stock.AUTOMATICALLY_USED_SUBCATEGORIES,
    )
    def test_old_subcategories_bookings_are_archived_when_no_longer_free(self, app, subcategoryId, client):
        # given
        now = date_utils.get_naive_utc_now()
        recent = now - datetime.timedelta(days=29, hours=23)
        old = now - datetime.timedelta(days=30, hours=1)
        offer = offers_factories.ThingOfferFactory(subcategoryId=subcategoryId)
        stock_free = offers_factories.StockFactory(offer=offer, price=0)
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )

        recent_booking = bookings_factories.BookingFactory(stock=stock_free, dateCreated=recent)
        old_booking = bookings_factories.BookingFactory(stock=stock_free, dateCreated=old)
        recent_booking_id = recent_booking.id
        old_booking_id = old_booking.id
        stock_data = {
            "price": 10,
        }
        client.with_session_auth("user@example.com").post("/stocks/bulk/", json=stock_data)
        db.session.commit()
        db.session.close()

        # when
        run_command(app, "archive_old_bookings")

        # then
        recent_booking = db.session.get(bookings_models.Booking, recent_booking_id)
        old_booking = db.session.get(bookings_models.Booking, old_booking_id)
        assert not recent_booking.displayAsEnded
        assert old_booking.displayAsEnded


@pytest.mark.usefixtures("db_session")
class SendTodayEventsNotificationsTest:
    # Set time to evening so that `send_today_events_notifications_metropolitan_france()`
    # finds test stock in its `13:00 - 24:00` window.
    @time_machine.travel("20:00:00")
    def test_send_today_events_notifications_only_to_individual_bookings_users(self):
        """
        Test that each stock that is linked to an offer that occurs today and
        creates a job that will send a notification to all of the stock's users
        with a valid (not cancelled) booking, for individual bookings only.
        """
        in_one_hour = date_utils.get_naive_utc_now() + timedelta(hours=1)
        stock_today = offers_factories.EventStockFactory(beginningDatetime=in_one_hour, offer__name="my_offer")

        next_week = date_utils.get_naive_utc_now() + timedelta(days=7)
        stock_next_week = offers_factories.EventStockFactory(beginningDatetime=next_week)

        user1 = users_factories.BeneficiaryGrant18Factory()
        user2 = users_factories.BeneficiaryGrant18Factory()

        # should be fetched
        bookings_factories.BookingFactory(stock=stock_today, user=user1)
        bookings_factories.BookingFactory(stock=stock_today, user=user2)

        # should not be fetched: cancelled
        bookings_factories.BookingFactory(stock=stock_today, status=bookings_models.BookingStatus.CANCELLED, user=user2)

        # should not be fetched: next week
        bookings_factories.BookingFactory(stock=stock_next_week, user=user2)

        transactional_notifications.send_today_events_notifications_metropolitan_france()

        assert len(notifications_testing.requests) == 2
        assert all(data["message"]["title"] == "C'est aujourd'hui !" for data in notifications_testing.requests)

        user_ids = {user_id for data in notifications_testing.requests for user_id in data["user_ids"]}
        assert user_ids == {user1.id, user2.id}


@pytest.mark.usefixtures("db_session")
class NotifyUsersOfSoonToBeExpiredBookingsTest:
    @mock.patch("pcapi.core.mails.transactional.send_soon_to_be_expired_individual_bookings_recap_email_to_beneficiary")
    def should_call_email_service_for_individual_bookings_which_will_expire_in_7_days(
        self, mocked_email_recap, app
    ) -> None:
        # Given
        now = date.today()
        booking_date_23_days_ago = now - timedelta(days=23)
        booking_date_22_days_ago = now - timedelta(days=22)

        vinyle = ProductFactory(subcategoryId=subcategories.SUPPORT_PHYSIQUE_MUSIQUE_VINYLE.id)
        expire_in_7_days_dvd_individual_booking = bookings_factories.BookingFactory(
            stock__offer__product=vinyle,
            dateCreated=booking_date_23_days_ago,
        )
        non_expired_cd = ProductFactory(subcategoryId=subcategories.SUPPORT_PHYSIQUE_MUSIQUE_CD.id)
        dont_expire_in_7_days_cd_individual_booking = bookings_factories.BookingFactory(
            stock__offer__product=non_expired_cd,
            dateCreated=booking_date_22_days_ago,
        )
        db.session.add(dont_expire_in_7_days_cd_individual_booking)
        db.session.commit()

        # When
        bookings_commands._notify_soon_to_be_expired_individual_bookings()

        # Then
        mocked_email_recap.assert_called_once_with(
            expire_in_7_days_dvd_individual_booking.user, [expire_in_7_days_dvd_individual_booking]
        )


class SendEmailReminderTomorrowEventToBeneficiariesTest:
    @patch(
        "pcapi.core.mails.transactional.bookings.booking_event_reminder_to_beneficiary.get_booking_event_reminder_to_beneficiary_email_data"
    )
    def should_not_crash_when_an_error_happened_to_prevent_cron_to_be_restarted(
        self,
        mock_send_individual_booking_event_reminder_email_to_beneficiary,
    ):
        mock_send_individual_booking_event_reminder_email_to_beneficiary.side_effect = [
            None,
            RuntimeError("error should be caught"),
            None,
        ]

        tomorrow = date_utils.get_naive_utc_now() + datetime.timedelta(days=1)
        stock = offers_factories.EventStockFactory(
            beginningDatetime=tomorrow,
        )
        bookings_factories.BookingFactory.create_batch(3, stock=stock)

        assert bookings_commands._send_email_reminder_tomorrow_event_to_beneficiaries() is None

    @patch(
        "pcapi.core.mails.transactional.bookings.booking_event_reminder_to_beneficiary.get_booking_event_reminder_to_beneficiary_email_data"
    )
    def should_send_emails_to_users_even_if_there_is_an_error(
        self,
        mock_get_booking_event_reminder_to_beneficiary_email_data,
    ):
        tomorrow = date_utils.get_naive_utc_now() + datetime.timedelta(days=1)
        stock = offers_factories.EventStockFactory(
            beginningDatetime=tomorrow,
        )
        individual_bookings = bookings_factories.BookingFactory.create_batch(3, stock=stock)

        mock_get_booking_event_reminder_to_beneficiary_email_data.side_effect = [
            get_booking_event_reminder_to_beneficiary_email_data(individual_bookings[0]),
            RuntimeError("error should be caught"),
            get_booking_event_reminder_to_beneficiary_email_data(individual_bookings[2]),
        ]

        bookings_commands._send_email_reminder_tomorrow_event_to_beneficiaries()

        assert len(mails_testing.outbox) == 2

    @patch(
        "pcapi.core.mails.transactional.bookings.booking_event_reminder_to_beneficiary.get_booking_event_reminder_to_beneficiary_email_data"
    )
    def should_log_errors(self, mock_get_booking_event_reminder_to_beneficiary_email_data, caplog):
        tomorrow = date_utils.get_naive_utc_now() + datetime.timedelta(days=1)
        stock = offers_factories.EventStockFactory(
            beginningDatetime=tomorrow,
        )
        individual_booking_with_error = bookings_factories.BookingFactory(stock=stock)

        mock_get_booking_event_reminder_to_beneficiary_email_data.side_effect = Exception("error should be caught")

        with caplog.at_level(logging.ERROR):
            bookings_commands._send_email_reminder_tomorrow_event_to_beneficiaries()

            assert caplog.records[0].extra["BookingId"] == individual_booking_with_error.id
            assert caplog.records[0].extra["userId"] == individual_booking_with_error.userId

    def should_execute_one_query_only(self):
        tomorrow = date_utils.get_naive_utc_now() + datetime.timedelta(days=1)
        stock = offers_factories.EventStockFactory(beginningDatetime=tomorrow)
        bookings_factories.BookingFactory.create_batch(3, stock=stock)

        with assert_no_duplicated_queries():
            bookings_commands._send_email_reminder_tomorrow_event_to_beneficiaries()

            assert len(mails_testing.outbox) == 3
