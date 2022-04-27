import pytest

from pcapi.core.bookings import factories as bookings_factories
from pcapi.core.categories import subcategories
import pcapi.core.mails.testing as mails_testing
from pcapi.core.mails.transactional.bookings.booking_expiration_to_pro import send_bookings_expiration_to_pro_email
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
import pcapi.core.offerers.factories as offerers_factories


pytestmark = pytest.mark.usefixtures("db_session")


class SendExpiredBookingsRecapEmailToOffererTest:
    def test_should_send_email_to_offerer_when_expired_bookings_cancelled(self, app):
        offerer = offerers_factories.OffererFactory()
        expired_today_dvd_booking = bookings_factories.IndividualBookingFactory(
            stock__offer__bookingEmail="offerer.booking@example.com"
        )
        expired_today_cd_booking = bookings_factories.IndividualBookingFactory(
            stock__offer__bookingEmail="offerer.booking@example.com"
        )

        send_bookings_expiration_to_pro_email(offerer, [expired_today_cd_booking, expired_today_dvd_booking])
        assert len(mails_testing.outbox) == 1
        assert (
            mails_testing.outbox[0].sent_data["template"] == TransactionalEmail.BOOKING_EXPIRATION_TO_PRO.value.__dict__
        )
        assert mails_testing.outbox[0].sent_data["params"]

    def test_should_send_two_emails_to_offerer_when_expired_books_bookings_and_other_bookings_cancelled(self):
        offerer = offerers_factories.OffererFactory()
        expired_today_dvd_booking = bookings_factories.IndividualBookingFactory(
            stock__offer__name="Intouchables",
            stock__offer__bookingEmail="offerer.booking@example.com",
            stock__offer__subcategoryId=subcategories.SUPPORT_PHYSIQUE_FILM.id,
        )
        expired_today_book_booking = bookings_factories.IndividualBookingFactory(
            stock__offer__name="Les misérables",
            stock__offer__bookingEmail="offerer.booking@example.com",
            stock__offer__subcategoryId=subcategories.LIVRE_PAPIER.id,
        )

        send_bookings_expiration_to_pro_email(offerer, [expired_today_dvd_booking, expired_today_book_booking])

        assert len(mails_testing.outbox) == 2
        assert (
            mails_testing.outbox[0].sent_data["template"] == TransactionalEmail.BOOKING_EXPIRATION_TO_PRO.value.__dict__
        )
        assert mails_testing.outbox[0].sent_data["params"]["WITHDRAWAL_PERIOD"] == 10
        assert mails_testing.outbox[0].sent_data["params"]["BOOKINGS"][0]["offer_name"] == "Les misérables"
        assert len(mails_testing.outbox[0].sent_data["params"]["BOOKINGS"]) == 1
        assert (
            mails_testing.outbox[1].sent_data["template"] == TransactionalEmail.BOOKING_EXPIRATION_TO_PRO.value.__dict__
        )
        assert mails_testing.outbox[1].sent_data["params"]["WITHDRAWAL_PERIOD"] == 30
        assert mails_testing.outbox[1].sent_data["params"]["BOOKINGS"][0]["offer_name"] == "Intouchables"
        assert len(mails_testing.outbox[1].sent_data["params"]["BOOKINGS"]) == 1
