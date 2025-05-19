import pytest

import pcapi.core.mails.testing as mails_testing
import pcapi.core.offerers.factories as offerers_factories
from pcapi.core.bookings import factories as bookings_factories
from pcapi.core.categories import subcategories
from pcapi.core.mails.transactional.bookings.booking_expiration_to_pro import send_bookings_expiration_to_pro_email
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail


pytestmark = pytest.mark.usefixtures("db_session")


class SendExpiredBookingsRecapEmailToOffererTest:
    @pytest.mark.parametrize(
        "offerer_factory, formatted_price",
        [
            (offerers_factories.OffererFactory, "10,10 €"),
            (offerers_factories.CaledonianOffererFactory, "1205 F"),
        ],
    )
    def test_should_send_email_to_offerer_when_expired_bookings_cancelled(self, app, offerer_factory, formatted_price):
        offerer = offerer_factory()
        expired_today_dvd_booking = bookings_factories.BookingFactory(
            stock__offer__bookingEmail="offerer.booking@example.com"
        )
        expired_today_cd_booking = bookings_factories.BookingFactory(
            stock__offer__bookingEmail="offerer.booking@example.com"
        )

        send_bookings_expiration_to_pro_email(offerer, [expired_today_cd_booking, expired_today_dvd_booking])
        assert len(mails_testing.outbox) == 1
        assert mails_testing.outbox[0]["template"] == TransactionalEmail.BOOKING_EXPIRATION_TO_PRO.value.__dict__
        assert mails_testing.outbox[0]["params"]
        assert len(mails_testing.outbox[0]["params"]["BOOKINGS"]) == 2
        assert mails_testing.outbox[0]["params"]["BOOKINGS"][0]["formatted_price"] == formatted_price
        assert mails_testing.outbox[0]["params"]["BOOKINGS"][1]["formatted_price"] == formatted_price

    @pytest.mark.parametrize("has_offerer_address", [True, False])
    def test_should_send_two_emails_to_offerer_when_expired_books_bookings_and_other_bookings_cancelled(
        self, has_offerer_address
    ):
        offerer = offerers_factories.OffererFactory()
        oa = offerers_factories.OffererAddressFactory(offerer=offerer)
        expired_today_dvd_booking = bookings_factories.BookingFactory(
            stock__offer__name="Intouchables",
            stock__offer__bookingEmail="offerer.booking@example.com",
            stock__offer__subcategoryId=subcategories.SUPPORT_PHYSIQUE_FILM.id,
            stock__offer__offererAddress=oa if has_offerer_address else None,
        )
        expired_today_book_booking = bookings_factories.BookingFactory(
            stock__offer__name="Les misérables",
            stock__offer__bookingEmail="offerer.booking@example.com",
            stock__offer__subcategoryId=subcategories.LIVRE_PAPIER.id,
        )

        send_bookings_expiration_to_pro_email(offerer, [expired_today_dvd_booking, expired_today_book_booking])

        assert len(mails_testing.outbox) == 2
        email1, email2 = mails_testing.outbox
        if has_offerer_address:
            assert email1["params"]["OFFER_ADDRESS"] == expired_today_book_booking.stock.offer.fullAddress
            assert email2["params"]["OFFER_ADDRESS"] == expired_today_dvd_booking.stock.offer.fullAddress
        assert email1["template"] == TransactionalEmail.BOOKING_EXPIRATION_TO_PRO.value.__dict__
        assert email1["params"]["WITHDRAWAL_PERIOD"] == 10
        assert len(email1["params"]["BOOKINGS"]) == 1
        assert email1["params"]["BOOKINGS"][0]["offer_name"] == "Les misérables"
        assert email1["params"]["BOOKINGS"][0]["formatted_price"] == "10,10 €"
        assert email2["template"] == TransactionalEmail.BOOKING_EXPIRATION_TO_PRO.value.__dict__
        assert email2["params"]["WITHDRAWAL_PERIOD"] == 30
        assert len(email2["params"]["BOOKINGS"]) == 1
        assert email2["params"]["BOOKINGS"][0]["offer_name"] == "Intouchables"
        assert email2["params"]["BOOKINGS"][0]["formatted_price"] == "10,10 €"
