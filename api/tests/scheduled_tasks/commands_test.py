import datetime
from datetime import datetime
from datetime import timedelta
import logging
from unittest.mock import patch

import pytest

import pcapi.core.bookings.factories as bookings_factories
import pcapi.core.mails.testing as mails_testing
from pcapi.core.mails.transactional.bookings.booking_event_reminder_to_beneficiary import (
    get_booking_event_reminder_to_beneficiary_email_data,
)
import pcapi.core.offers.factories as offers_factories
from pcapi.core.testing import assert_num_queries
from pcapi.scheduled_tasks.commands import send_email_reminder_tomorrow_event_to_beneficiaries


pytestmark = pytest.mark.usefixtures("db_session")


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

        tomorrow = datetime.utcnow() + timedelta(days=1)
        stock = offers_factories.EventStockFactory(
            beginningDatetime=tomorrow,
        )
        bookings_factories.IndividualBookingFactory.create_batch(3, stock=stock)

        assert send_email_reminder_tomorrow_event_to_beneficiaries() is None

    @patch(
        "pcapi.core.mails.transactional.bookings.booking_event_reminder_to_beneficiary.get_booking_event_reminder_to_beneficiary_email_data"
    )
    def should_send_emails_to_users_even_if_there_is_an_error(
        self,
        mock_get_booking_event_reminder_to_beneficiary_email_data,
    ):
        tomorrow = datetime.utcnow() + timedelta(days=1)
        stock = offers_factories.EventStockFactory(
            beginningDatetime=tomorrow,
        )
        individual_bookings = bookings_factories.IndividualBookingFactory.create_batch(3, stock=stock)

        mock_get_booking_event_reminder_to_beneficiary_email_data.side_effect = [
            get_booking_event_reminder_to_beneficiary_email_data(individual_bookings[0].individualBooking),
            RuntimeError("error should be caught"),
            get_booking_event_reminder_to_beneficiary_email_data(individual_bookings[2].individualBooking),
        ]

        send_email_reminder_tomorrow_event_to_beneficiaries()

        assert len(mails_testing.outbox) == 2

    @patch(
        "pcapi.core.mails.transactional.bookings.booking_event_reminder_to_beneficiary.get_booking_event_reminder_to_beneficiary_email_data"
    )
    def should_log_errors(self, mock_get_booking_event_reminder_to_beneficiary_email_data, caplog):
        tomorrow = datetime.utcnow() + timedelta(days=1)
        stock = offers_factories.EventStockFactory(
            beginningDatetime=tomorrow,
        )
        individual_booking_with_error = bookings_factories.IndividualBookingFactory(stock=stock).individualBooking

        mock_get_booking_event_reminder_to_beneficiary_email_data.side_effect = Exception("error should be caught")

        with caplog.at_level(logging.ERROR):
            send_email_reminder_tomorrow_event_to_beneficiaries()

            assert caplog.records[0].extra["individualBookingId"] == individual_booking_with_error.id
            assert caplog.records[0].extra["userId"] == individual_booking_with_error.userId

    def should_execute_one_query_only(self):
        tomorrow = datetime.utcnow() + timedelta(days=1)
        stock = offers_factories.EventStockFactory(beginningDatetime=tomorrow)
        bookings_factories.IndividualBookingFactory.create_batch(3, stock=stock)

        with assert_num_queries(1):
            send_email_reminder_tomorrow_event_to_beneficiaries()

            assert len(mails_testing.outbox) == 3
