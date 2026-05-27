import pytest

import pcapi.core.mails.testing as mails_testing
from pcapi.core import testing
from pcapi.core.bookings.factories import BookingFactory
from pcapi.core.mails.transactional.bookings.booking_withdrawal_updated import send_email_for_each_ongoing_booking
from pcapi.core.offers import factories as offers_factories


@pytest.mark.usefixtures("db_session")
class SendBookingWithdrawalUpdatedTest:
    def test_send_email_for_each_ongoing_booking(self):
        offer = offers_factories.EventOfferFactory()
        booking_joe = BookingFactory(
            stock=offers_factories.EventStockFactory(offer=offer), user__email="joe.dalton@example.com"
        )
        BookingFactory(stock=booking_joe.stock, user__email="jack.dalton@example.com")
        BookingFactory(stock=booking_joe.stock, user__email="william.dalton@example.com")
        BookingFactory(
            stock=offers_factories.EventStockFactory(offer=offer),
            user__email="averell.dalton@example.com",
        )
        # load offer
        # load venue for venue_address
        # load offerer for offerer_name
        # load booking (with offer's offererAddress joined)
        with testing.assert_num_queries(4):
            send_email_for_each_ongoing_booking(offer)

        assert len(mails_testing.outbox) == 4
        assert set([email["To"] for email in mails_testing.outbox]) == {
            "joe.dalton@example.com",
            "jack.dalton@example.com",
            "william.dalton@example.com",
            "averell.dalton@example.com",
        }
