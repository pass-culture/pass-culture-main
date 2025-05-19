import dataclasses

import pytest

import pcapi.core.mails.testing as mails_testing
from pcapi.core import testing as core_testing
from pcapi.core.bookings.factories import BookingFactory
from pcapi.core.mails.transactional.bookings.booking_withdrawal_updated import send_booking_withdrawal_updated
from pcapi.core.mails.transactional.bookings.booking_withdrawal_updated import send_email_for_each_ongoing_booking
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.offers import factories as offers_factories
from pcapi.core.testing import assert_no_duplicated_queries


@pytest.mark.usefixtures("db_session")
class SendBookingWithdrawalUpdatedTest:
    def test_send_withdrawalchanged_email(self):
        with assert_no_duplicated_queries():
            send_booking_withdrawal_updated(
                recipients=["georges@example.com"],
                user_first_name="Georges",
                offer_name="my awesome offer",
                offer_token="XXXXXX",
                offer_withdrawal_delay="2 semaines",
                offer_withdrawal_details="my withdrawal details",
                offer_withdrawal_type="no_ticket",
                offerer_name="my offerer name",
                offer_address="my awesome offer address",
            )

        assert len(mails_testing.outbox) == 1
        email = mails_testing.outbox[0]
        assert email["To"] == "georges@example.com"
        assert email["template"] == dataclasses.asdict(TransactionalEmail.OFFER_WITHDRAWAL_UPDATED_BY_PRO.value)
        assert email["params"]["OFFER_NAME"] == "my awesome offer"
        assert email["params"]["OFFER_TOKEN"] == "XXXXXX"
        assert email["params"]["OFFER_WITHDRAWAL_DELAY"] == "2 semaines"
        assert email["params"]["OFFER_WITHDRAWAL_DETAILS"] == "my withdrawal details"
        assert email["params"]["OFFER_WITHDRAWAL_TYPE"] == "no_ticket"
        assert email["params"]["OFFERER_NAME"] == "my offerer name"
        assert email["params"]["USER_FIRST_NAME"] == "Georges"
        assert email["params"]["OFFER_ADDRESS"] == "my awesome offer address"

    def test_send_email_for_each_ongoing_booking(
        self,
    ):
        stock = offers_factories.EventStockFactory()
        BookingFactory.create_batch(size=3, stock=stock)
        offer = stock.offer
        # load offer
        # load venue for venue_address
        # load offerer for offerer_name
        # load booking
        BookingFactory(stock=offers_factories.EventStockFactory(offer=offer))
        with core_testing.assert_num_queries(5):
            send_email_for_each_ongoing_booking(offer)
