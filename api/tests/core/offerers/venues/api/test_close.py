import dataclasses

import pytest

import pcapi.core.mails.testing as mails_testing
from pcapi.core.bookings import api as bookings_api
from pcapi.core.bookings import factories as bookings_factories
from pcapi.core.bookings import models as bookings_models
from pcapi.core.mails.transactional.brevo_template_ids import TransactionalEmail
from pcapi.core.offerers import factories
from pcapi.core.offerers.venues.api import close as api
from pcapi.core.offers import factories as offers_factories
from pcapi.core.users import factories as users_factories
from pcapi.models import db


pytestmark = pytest.mark.usefixtures("db_session")


class CancelVenueBookingsTest:
    def test_cancel_venue_bookings(self):
        venue = factories.VenueFactory()
        booking = bookings_factories.BookingFactory(stock__offer__venue=venue)

        cancelled = api.cancel_venue_bookings(venue)

        db.session.refresh(booking)
        assert {o.id for o in cancelled} == {booking.id}
        assert booking.status == bookings_models.BookingStatus.CANCELLED

    def test_cancel_venue_bookings_with_author(self):
        author = users_factories.UserFactory()
        venue = factories.VenueFactory()
        booking = bookings_factories.BookingFactory(stock__offer__venue=venue)

        cancelled = api.cancel_venue_bookings(venue, author_id=author.id)

        db.session.refresh(booking)
        assert {o.id for o in cancelled} == {booking.id}
        assert booking.status == bookings_models.BookingStatus.CANCELLED
        assert booking.cancellationUserId == author.id

    def test_cancel_venue_bookings_with_connect_as(self):
        venue = factories.VenueFactory()
        booking = bookings_factories.BookingFactory(stock__offer__venue=venue)

        cancelled = api.cancel_venue_bookings(venue, user_connect_as=True)

        db.session.refresh(booking)
        assert {o.id for o in cancelled} == {booking.id}
        assert booking.status == bookings_models.BookingStatus.CANCELLED
        assert booking.cancellationReason == bookings_models.BookingCancellationReasons.OFFERER_CONNECT_AS


class DoNotSendEmailsAnymoreTest:
    def test_emails_are_nullified_and_none_is_sent_after_a_booking(self):
        venue = factories.VenueFactory(bookingEmail="booking@test.com", contact__email="hey@test.com")
        user = users_factories.BaseUserFactory()

        api.do_not_send_emails_anymore(venue, user)

        beneficiary = users_factories.BeneficiaryFactory()
        stock = offers_factories.StockFactory(offer__venue=venue)
        bookings_api.book_offer(beneficiary, stock.id, 1)

        assert len(mails_testing.outbox) == 1

        email_data = mails_testing.outbox[0]
        assert email_data["template"] == dataclasses.asdict(
            TransactionalEmail.BOOKING_CONFIRMATION_BY_BENEFICIARY.value
        )  # to beneficiary
