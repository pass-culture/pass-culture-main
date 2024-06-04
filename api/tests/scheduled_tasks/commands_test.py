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
from pcapi.core.offerers.factories import OffererAddressFactory
import pcapi.core.offers.factories as offers_factories
from pcapi.core.testing import assert_no_duplicated_queries
from pcapi.core.testing import assert_num_queries
from pcapi.core.testing import override_settings
import pcapi.notifications.push.testing as notifications_testing
from pcapi.scheduled_tasks.commands import _send_notification_favorites_not_booked
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
        bookings_factories.BookingFactory.create_batch(3, stock=stock)

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
        individual_bookings = bookings_factories.BookingFactory.create_batch(3, stock=stock)

        mock_get_booking_event_reminder_to_beneficiary_email_data.side_effect = [
            get_booking_event_reminder_to_beneficiary_email_data(individual_bookings[0]),
            RuntimeError("error should be caught"),
            get_booking_event_reminder_to_beneficiary_email_data(individual_bookings[2]),
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
        individual_booking_with_error = bookings_factories.BookingFactory(stock=stock)

        mock_get_booking_event_reminder_to_beneficiary_email_data.side_effect = Exception("error should be caught")

        with caplog.at_level(logging.ERROR):
            send_email_reminder_tomorrow_event_to_beneficiaries()

            assert caplog.records[0].extra["BookingId"] == individual_booking_with_error.id
            assert caplog.records[0].extra["userId"] == individual_booking_with_error.userId

    def should_execute_one_query_only(self):
        tomorrow = datetime.utcnow() + timedelta(days=1)
        stock = offers_factories.EventStockFactory(beginningDatetime=tomorrow)
        bookings_factories.BookingFactory.create_batch(3, stock=stock)

        with assert_no_duplicated_queries():
            send_email_reminder_tomorrow_event_to_beneficiaries()

            assert len(mails_testing.outbox) == 3

    def should_send_an_email_to_user_using_venue_name_if_localized_at_same_address(
        self,
    ):
        tomorrow = datetime.utcnow() + timedelta(days=1)
        stock = offers_factories.EventStockFactory(beginningDatetime=tomorrow, offer__offererAddress=None)
        bookings_factories.BookingFactory.create_batch(2, stock=stock)

        # select booking and extradata
        # check FF metadata
        with assert_num_queries(2):
            send_email_reminder_tomorrow_event_to_beneficiaries()

        assert len(mails_testing.outbox) == 2
        assert (
            mails_testing.outbox[0]["params"]["VENUE_NAME"] == stock.offer.addressName == stock.offer.venue.common_name
        )
        assert (
            mails_testing.outbox[1]["params"]["VENUE_NAME"] == stock.offer.addressName == stock.offer.venue.common_name
        )

    def should_send_an_email_to_user_using_offer_address_label_if_localized_elsewhere(
        self,
    ):
        tomorrow = datetime.utcnow() + timedelta(days=1)
        offerer_address = OffererAddressFactory(label="Ma super librairie")
        stock = offers_factories.EventStockFactory(beginningDatetime=tomorrow, offer__offererAddress=offerer_address)
        bookings_factories.BookingFactory.create_batch(2, stock=stock)

        # select booking and extradata
        # check FF metadata
        with assert_num_queries(2):
            send_email_reminder_tomorrow_event_to_beneficiaries()

        assert len(mails_testing.outbox) == 2
        assert (
            mails_testing.outbox[0]["params"]["VENUE_NAME"]
            == stock.offer.addressName
            == stock.offer.offererAddress.label
        )
        assert (
            mails_testing.outbox[1]["params"]["VENUE_NAME"]
            == stock.offer.addressName
            == stock.offer.offererAddress.label
        )


class SendNotificationFavoritesNotBookedTest:
    def test_send(self):
        rows = [
            {"offer_id": 1, "offer_name": "my offer", "user_ids": [1, 2], "count": 2},
            {"offer_id": 2, "offer_name": "another offer", "user_ids": [3], "count": 1},
        ]

        with patch("pcapi.connectors.big_query.TestingBackend.run_query") as mock_run_query:
            mock_run_query.return_value = rows
            _send_notification_favorites_not_booked()

        requests = notifications_testing.requests
        assert len(requests) == 2

        user_ids = {*requests[0]["user_ids"], *requests[1]["user_ids"]}
        assert user_ids == {1, 2, 3}

    @override_settings(BATCH_MAX_USERS_PER_TRANSACTIONAL_NOTIFICATION=2)
    def test_send_with_split_because_too_many_users(self):
        rows = [
            {"offer_id": 1, "offer_name": "my offer", "user_ids": [1, 2, 3, 4, 5], "count": 5},
        ]

        with patch("pcapi.connectors.big_query.TestingBackend.run_query") as mock_run_query:
            mock_run_query.return_value = rows
            _send_notification_favorites_not_booked()

        # one request with users 1 and 2
        # another one with users 3 and 4
        # and a final one with user 5
        assert len(notifications_testing.requests) == 3
