import dataclasses

import pytest

import pcapi.core.mails.testing as mails_testing
from pcapi.core.mails.transactional.bookings.booking_withdrawal_updated import send_booking_withdrawal_updated
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.testing import assert_no_duplicated_queries


def test_send_withdrawalchanged_email():
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
            venue_address="my awesome address",
        )

    assert len(mails_testing.outbox) == 1
    email = mails_testing.outbox[0]
    assert email.sent_data["To"] == "georges@example.com"
    assert email.sent_data["template"] == dataclasses.asdict(TransactionalEmail.OFFER_WITHDRAWAL_UPDATED_BY_PRO.value)
    assert email.sent_data["params"]["OFFER_NAME"] == "my awesome offer"
    assert email.sent_data["params"]["OFFER_TOKEN"] == "XXXXXX"
    assert email.sent_data["params"]["OFFER_WITHDRAWAL_DELAY"] == "2 semaines"
    assert email.sent_data["params"]["OFFER_WITHDRAWAL_DETAILS"] == "my withdrawal details"
    assert email.sent_data["params"]["OFFER_WITHDRAWAL_TYPE"] == "no_ticket"
    assert email.sent_data["params"]["OFFERER_NAME"] == "my offerer name"
    assert email.sent_data["params"]["USER_FIRST_NAME"] == "Georges"
    assert email.sent_data["params"]["VENUE_ADDRESS"] == "my awesome address"
