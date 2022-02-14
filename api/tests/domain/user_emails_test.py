from unittest.mock import patch

import pytest

from pcapi.core.bookings import factories as bookings_factories
import pcapi.core.mails.testing as mails_testing
from pcapi.core.offers.factories import UserOffererFactory
import pcapi.core.users.factories as users_factories
from pcapi.domain.user_emails import send_activation_email
from pcapi.domain.user_emails import send_individual_booking_confirmation_email_to_offerer
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


class SendBookingConfirmationEmailToOffererTest:
    def test_send_to_offerer(self):
        booking = bookings_factories.IndividualBookingFactory(
            stock__offer__bookingEmail="booking.email@example.com",
        )

        send_individual_booking_confirmation_email_to_offerer(booking.individualBooking)

        assert len(mails_testing.outbox) == 1  # test number of emails sent
        assert mails_testing.outbox[0].sent_data["To"] == "booking.email@example.com"
        assert mails_testing.outbox[0].sent_data["MJ-TemplateID"] == 3095147


class SendActivationEmailTest:
    def test_send_activation_email(self):
        # given
        beneficiary = users_factories.BeneficiaryGrant18Factory.build()

        # when
        send_activation_email(beneficiary)

        # then
        assert len(mails_testing.outbox) == 1
        assert mails_testing.outbox[0].sent_data["Mj-TemplateID"] == 994771


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
