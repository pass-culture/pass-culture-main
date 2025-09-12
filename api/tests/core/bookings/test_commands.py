import datetime
import logging
from datetime import date
from datetime import timedelta
from unittest import mock
from unittest.mock import patch

import pytest

import pcapi.core.mails.testing as mails_testing
import pcapi.core.offerers.factories as offerers_factories
from pcapi.core.bookings import commands as bookings_commands
from pcapi.core.bookings import factories as bookings_factories
from pcapi.core.bookings import models as bookings_models
from pcapi.core.categories import subcategories
from pcapi.core.mails.transactional.bookings.booking_event_reminder_to_beneficiary import (
    get_booking_event_reminder_to_beneficiary_email_data,
)
from pcapi.core.offers import factories as offers_factories
from pcapi.core.offers import models as offer_models
from pcapi.core.products.factories import ProductFactory
from pcapi.core.testing import assert_no_duplicated_queries
from pcapi.models import db
from pcapi.utils import repository

from tests.test_utils import run_command


pytestmark = pytest.mark.usefixtures("db_session")


class ArchiveOldBookingsTest:
    @pytest.mark.usefixtures("clean_database")
    def test_basics(self, app):
        # given
        now = datetime.datetime.utcnow()
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
        now = datetime.datetime.utcnow()
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
        now = datetime.datetime.utcnow()
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
        repository.save(dont_expire_in_7_days_cd_individual_booking)

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

        tomorrow = datetime.datetime.utcnow() + datetime.timedelta(days=1)
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
        tomorrow = datetime.datetime.utcnow() + datetime.timedelta(days=1)
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
        tomorrow = datetime.datetime.utcnow() + datetime.timedelta(days=1)
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
        tomorrow = datetime.datetime.utcnow() + datetime.timedelta(days=1)
        stock = offers_factories.EventStockFactory(beginningDatetime=tomorrow)
        bookings_factories.BookingFactory.create_batch(3, stock=stock)

        with assert_no_duplicated_queries():
            bookings_commands._send_email_reminder_tomorrow_event_to_beneficiaries()

            assert len(mails_testing.outbox) == 3
