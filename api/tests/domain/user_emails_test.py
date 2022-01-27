from unittest.mock import patch

import pytest

from pcapi.core.bookings import factories as bookings_factories
from pcapi.core.categories import subcategories
import pcapi.core.mails.testing as mails_testing
from pcapi.core.offers.factories import OffererFactory
from pcapi.core.offers.factories import UserOffererFactory
import pcapi.core.users.factories as users_factories
from pcapi.domain.user_emails import send_activation_email
from pcapi.domain.user_emails import send_admin_user_validation_email
from pcapi.domain.user_emails import send_expired_individual_bookings_recap_email_to_offerer
from pcapi.domain.user_emails import send_individual_booking_confirmation_email_to_offerer
from pcapi.domain.user_emails import send_offerer_bookings_recap_email_after_offerer_cancellation
from pcapi.domain.user_emails import send_offerer_driven_cancellation_email_to_offerer
from pcapi.domain.user_emails import send_pro_user_validation_email
from pcapi.domain.user_emails import send_user_driven_cancellation_email_to_offerer
from pcapi.domain.user_emails import send_withdrawal_terms_to_newly_validated_offerer


pytestmark = pytest.mark.usefixtures("db_session")


# FIXME (dbaty, 2020-02-01): I am not sure what we are really testing
# here. We seem to mock way too much. (At least, we could remove a few
# duplicate tests that check what happens when there is a bookingEmail
# and when there is none. We use a function for that in the
# implementation, there is no need to test it again and again here.)
#
# We should probably rewrite all tests and turn them into light
# integration tests that:
# - do NOT mock the functions that return data to be injected into
#   Mailjet (e.g. make_beneficiary_booking_cancellation_email_data)
# - check the recipients
# - ... and that's all.


class SendOffererDrivenCancellationEmailToOffererTest:
    @patch(
        "pcapi.domain.user_emails.make_offerer_driven_cancellation_email_for_offerer", return_value={"Html-part": ""}
    )
    def test_should_send_cancellation_by_offerer_email_to_offerer(
        self, make_offerer_driven_cancellation_email_for_offerer
    ):
        # Given
        booking = bookings_factories.BookingFactory(
            stock__offer__bookingEmail="offer@example.com",
        )

        # When
        send_offerer_driven_cancellation_email_to_offerer(booking)

        # Then
        make_offerer_driven_cancellation_email_for_offerer.assert_called_once_with(booking)
        assert len(mails_testing.outbox) == 1  # test number of emails sent
        assert mails_testing.outbox[0].sent_data["To"] == "offer@example.com"


class SendBeneficiaryUserDrivenCancellationEmailToOffererTest:
    def test_should_send_booking_cancellation_email_to_offerer(self):
        # Given
        booking = bookings_factories.IndividualBookingFactory(stock__offer__bookingEmail="booking@example.com")

        # When
        send_user_driven_cancellation_email_to_offerer(booking)

        # Then
        assert len(mails_testing.outbox) == 1  # test number of emails sent
        assert mails_testing.outbox[0].sent_data["To"] == "booking@example.com"
        assert mails_testing.outbox[0].sent_data["MJ-TemplateID"] == 780015


class SendBookingConfirmationEmailToOffererTest:
    def test_send_to_offerer(self):
        booking = bookings_factories.IndividualBookingFactory(
            stock__offer__bookingEmail="booking.email@example.com",
        )

        send_individual_booking_confirmation_email_to_offerer(booking.individualBooking)

        assert len(mails_testing.outbox) == 1  # test number of emails sent
        assert mails_testing.outbox[0].sent_data["To"] == "booking.email@example.com"
        assert mails_testing.outbox[0].sent_data["MJ-TemplateID"] == 3095147


class SendOffererBookingsRecapEmailAfterOffererCancellationTest:
    @patch(
        "pcapi.domain.user_emails.retrieve_offerer_bookings_recap_email_data_after_offerer_cancellation",
        return_value={"Mj-TemplateID": 1116333},
    )
    def test_sends_to_offerer_administration(
        self, retrieve_offerer_bookings_recap_email_data_after_offerer_cancellation
    ):
        # Given
        booking = bookings_factories.IndividualBookingFactory(stock__offer__bookingEmail="offerer@example.com")

        # When
        send_offerer_bookings_recap_email_after_offerer_cancellation([booking])

        # Then
        retrieve_offerer_bookings_recap_email_data_after_offerer_cancellation.assert_called_once_with([booking])
        assert len(mails_testing.outbox) == 1  # test number of emails sent
        assert mails_testing.outbox[0].sent_data["Mj-TemplateID"] == 1116333


class SendProUserValidationEmailTest:
    def test_sends_email_to_pro_user(self):
        # Given
        user = users_factories.ProFactory()
        user.generate_validation_token()

        # When
        send_pro_user_validation_email(user)

        # Then
        assert len(mails_testing.outbox) == 1  # test number of emails sent
        assert mails_testing.outbox[0].sent_data["To"] == user.email


class SendAdminUserValidationEmailTest:
    def test_send_mail_to_admin_user(self):
        # Given
        user = users_factories.AdminFactory()
        token = users_factories.ResetPasswordToken(user=user)

        # When
        send_admin_user_validation_email(user, token)

        # Then
        assert len(mails_testing.outbox) == 1  # test number of emails sent
        assert mails_testing.outbox[0].sent_data["To"] == user.email


class SendActivationEmailTest:
    def test_send_activation_email(self):
        # given
        beneficiary = users_factories.BeneficiaryGrant18Factory.build()

        # when
        send_activation_email(beneficiary)

        # then
        assert len(mails_testing.outbox) == 1
        assert mails_testing.outbox[0].sent_data["Mj-TemplateID"] == 994771


class SendExpiredBookingsRecapEmailToOffererTest:
    def test_should_send_email_to_offerer_when_expired_bookings_cancelled(self, app):
        offerer = OffererFactory()
        expired_today_dvd_booking = bookings_factories.IndividualBookingFactory(
            stock__offer__bookingEmail="offerer.booking@example.com"
        )
        expired_today_cd_booking = bookings_factories.IndividualBookingFactory(
            stock__offer__bookingEmail="offerer.booking@example.com"
        )

        send_expired_individual_bookings_recap_email_to_offerer(
            offerer, [expired_today_cd_booking, expired_today_dvd_booking]
        )
        assert len(mails_testing.outbox) == 1
        assert mails_testing.outbox[0].sent_data["Mj-TemplateID"] == 3095184
        assert mails_testing.outbox[0].sent_data["Vars"]

    def test_should_send_two_emails_to_offerer_when_expired_books_bookings_and_other_bookings_cancelled(self):
        offerer = OffererFactory()
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

        send_expired_individual_bookings_recap_email_to_offerer(
            offerer, [expired_today_dvd_booking, expired_today_book_booking]
        )

        assert len(mails_testing.outbox) == 2
        assert mails_testing.outbox[0].sent_data["Mj-TemplateID"] == 3095184
        assert mails_testing.outbox[0].sent_data["Vars"]["withdrawal_period"] == 10
        assert mails_testing.outbox[0].sent_data["Vars"]["bookings"][0]["offer_name"] == "Les misérables"
        assert mails_testing.outbox[1].sent_data["Mj-TemplateID"] == 3095184
        assert mails_testing.outbox[1].sent_data["Vars"]["withdrawal_period"] == 30
        assert mails_testing.outbox[1].sent_data["Vars"]["bookings"][0]["offer_name"] == "Intouchables"


class SendWithdrawalTermsToNewlyValidatedOffererTest:
    @patch(
        "pcapi.domain.user_emails.retrieve_data_for_new_offerer_validated_withdrawal_terms_email",
        return_value={"Mj-TemplateID": 11330916},
    )
    def test_send_withdrawal_terms_to_newly_validated_offerer(
        self, mock_retrieve_data_for_new_offerer_validated_withdrawal_terms_email
    ):
        # Given
        offerer = UserOffererFactory().offerer

        # When
        send_withdrawal_terms_to_newly_validated_offerer(offerer)

        # Then
        mock_retrieve_data_for_new_offerer_validated_withdrawal_terms_email.assert_called_once()
        assert len(mails_testing.outbox) == 1  # test number of emails sent
        assert mails_testing.outbox[0].sent_data["Mj-TemplateID"] == 11330916
