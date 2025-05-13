from dataclasses import asdict
from datetime import date

import pytest

from pcapi.core.bookings import factories as bookings_factories
from pcapi.core.categories import subcategories
from pcapi.core.educational import factories as educational_factories
import pcapi.core.mails.testing as mails_testing
from pcapi.core.mails.transactional.pro import offerer_closed
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offers import factories as offers_factories


@pytest.mark.usefixtures("db_session")
class SendOffererClosedEmailTest:
    def test_send_mail(self):
        offerer = offerers_factories.OffererFactory()
        user_offerer_1 = offerers_factories.UserOffererFactory(offerer=offerer)
        user_offerer_2 = offerers_factories.UserOffererFactory(offerer=offerer)
        offerers_factories.NotValidatedUserOffererFactory(offerer=offerer)
        offerers_factories.RejectedUserOffererFactory(offerer=offerer)

        bookings_factories.CancelledBookingFactory(stock__offer__venue__managingOfferer=offerer)
        bookings_factories.ReimbursedBookingFactory(stock__offer__venue__managingOfferer=offerer)
        educational_factories.ReimbursedCollectiveBookingFactory(offerer=offerer)

        offerer_closed.send_offerer_closed_email_to_pro(offerer, False, date(2025, 3, 7))

        assert len(mails_testing.outbox) == 2
        for mail, user_offerer in zip(mails_testing.outbox, (user_offerer_1, user_offerer_2)):
            assert mail["To"] == user_offerer.user.email
            assert mail["template"] == asdict(TransactionalEmail.OFFERER_CLOSED.value)
            assert mail["params"] == {
                "OFFERER_NAME": offerer.name,
                "SIREN": offerer.siren,
                "END_DATE": "vendredi 7 mars 2025",
                "HAS_THING_BOOKINGS": False,
                "HAS_EVENT_BOOKINGS": False,
            }

    @pytest.mark.parametrize(
        "booking_factory", [bookings_factories.BookingFactory, bookings_factories.UsedBookingFactory]
    )
    def test_send_mail_with_thing_booking(self, booking_factory):
        offerer = offerers_factories.OffererFactory()
        user_offerer = offerers_factories.UserOffererFactory(offerer=offerer)

        booking_factory(
            stock=offers_factories.ThingStockFactory(
                offer__venue__managingOfferer=offerer, offer__subcategoryId=subcategories.LIVRE_PAPIER.id
            )
        )

        offerer_closed.send_offerer_closed_email_to_pro(offerer, False, date(2025, 3, 17))

        assert len(mails_testing.outbox) == 1
        assert mails_testing.outbox[0]["To"] == user_offerer.user.email
        assert mails_testing.outbox[0]["template"] == asdict(TransactionalEmail.OFFERER_CLOSED.value)
        assert mails_testing.outbox[0]["params"] == {
            "OFFERER_NAME": offerer.name,
            "SIREN": offerer.siren,
            "END_DATE": "lundi 17 mars 2025",
            "HAS_THING_BOOKINGS": True,
            "HAS_EVENT_BOOKINGS": False,
        }

    @pytest.mark.parametrize(
        "booking_factory", [bookings_factories.BookingFactory, bookings_factories.UsedBookingFactory]
    )
    def test_send_mail_with_event_booking(self, booking_factory):
        offerer = offerers_factories.OffererFactory()
        user_offerer = offerers_factories.UserOffererFactory(offerer=offerer)

        booking_factory(
            stock=offers_factories.EventStockFactory(
                offer__venue__managingOfferer=offerer, offer__subcategoryId=subcategories.FESTIVAL_MUSIQUE.id
            )
        )

        offerer_closed.send_offerer_closed_email_to_pro(offerer, False, date(2025, 3, 17))

        assert len(mails_testing.outbox) == 1
        assert mails_testing.outbox[0]["To"] == user_offerer.user.email
        assert mails_testing.outbox[0]["template"] == asdict(TransactionalEmail.OFFERER_CLOSED.value)
        assert mails_testing.outbox[0]["params"] == {
            "OFFERER_NAME": offerer.name,
            "SIREN": offerer.siren,
            "END_DATE": "lundi 17 mars 2025",
            "HAS_THING_BOOKINGS": False,
            "HAS_EVENT_BOOKINGS": True,
        }

    @pytest.mark.parametrize(
        "booking_factory",
        [educational_factories.PendingCollectiveBookingFactory, educational_factories.UsedCollectiveBookingFactory],
    )
    def test_send_mail_with_collective_booking(self, booking_factory):
        offerer = offerers_factories.OffererFactory()
        user_offerer = offerers_factories.UserOffererFactory(offerer=offerer)

        booking_factory(offerer=offerer)

        offerer_closed.send_offerer_closed_email_to_pro(offerer, False, date(2025, 3, 17))

        assert len(mails_testing.outbox) == 1
        assert mails_testing.outbox[0]["To"] == user_offerer.user.email
        assert mails_testing.outbox[0]["template"] == asdict(TransactionalEmail.OFFERER_CLOSED.value)
        assert mails_testing.outbox[0]["params"] == {
            "OFFERER_NAME": offerer.name,
            "SIREN": offerer.siren,
            "END_DATE": "lundi 17 mars 2025",
            "HAS_THING_BOOKINGS": False,
            "HAS_EVENT_BOOKINGS": True,
        }

    def test_send_mail_is_manual(self):
        offerer = offerers_factories.OffererFactory()
        user_offerer_1 = offerers_factories.UserOffererFactory(offerer=offerer)
        user_offerer_2 = offerers_factories.UserOffererFactory(offerer=offerer)
        offerers_factories.NotValidatedUserOffererFactory(offerer=offerer)
        offerers_factories.RejectedUserOffererFactory(offerer=offerer)

        bookings_factories.CancelledBookingFactory(stock__offer__venue__managingOfferer=offerer)
        bookings_factories.ReimbursedBookingFactory(stock__offer__venue__managingOfferer=offerer)
        educational_factories.ReimbursedCollectiveBookingFactory(offerer=offerer)

        offerer_closed.send_offerer_closed_email_to_pro(offerer, True, None)

        assert len(mails_testing.outbox) == 2
        for mail, user_offerer in zip(mails_testing.outbox, (user_offerer_1, user_offerer_2)):
            assert mail["To"] == user_offerer.user.email
            assert mail["template"] == asdict(TransactionalEmail.OFFERER_CLOSED_MANUALLY.value)
            assert mail["params"] == {
                "OFFERER_NAME": offerer.name,
                "SIREN": offerer.siren,
                "END_DATE": "",
                "HAS_THING_BOOKINGS": False,
                "HAS_EVENT_BOOKINGS": False,
            }
