from dataclasses import asdict
from datetime import datetime
from datetime import timedelta
from unittest.mock import call
from unittest.mock import patch

from dateutil.relativedelta import relativedelta
import pytest

from pcapi.core.bookings import factories as booking_factories
from pcapi.core.categories import subcategories
import pcapi.core.mails.testing as mails_testing
from pcapi.core.mails.transactional import users as user_emails
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.mails.transactional.users.email_confirmation_email import send_email_confirmation_email
from pcapi.core.offers.factories import OfferFactory
from pcapi.core.offers.factories import OffererFactory
from pcapi.core.offers.factories import ProductFactory
from pcapi.core.offers.factories import UserOffererFactory
from pcapi.core.offers.factories import VenueFactory
from pcapi.core.offers.models import OfferValidationStatus
from pcapi.core.subscription.factories import BeneficiaryPreSubscriptionFactory
from pcapi.core.testing import override_features
import pcapi.core.users.factories as users_factories
from pcapi.domain.user_emails import send_activation_email
from pcapi.domain.user_emails import send_admin_user_validation_email
from pcapi.domain.user_emails import send_expired_bookings_recap_email_to_beneficiary
from pcapi.domain.user_emails import send_expired_individual_bookings_recap_email_to_offerer
from pcapi.domain.user_emails import send_individual_booking_cancellation_email
from pcapi.domain.user_emails import send_individual_booking_confirmation_email_to_beneficiary
from pcapi.domain.user_emails import send_individual_booking_confirmation_email_to_offerer
from pcapi.domain.user_emails import send_newly_eligible_user_email
from pcapi.domain.user_emails import send_offer_validation_status_update_email
from pcapi.domain.user_emails import send_offerer_bookings_recap_email_after_offerer_cancellation
from pcapi.domain.user_emails import send_offerer_driven_cancellation_email_to_offerer
from pcapi.domain.user_emails import send_pro_user_validation_email
from pcapi.domain.user_emails import send_rejection_email_to_beneficiary_pre_subscription
from pcapi.domain.user_emails import send_reset_password_email_to_pro
from pcapi.domain.user_emails import send_soon_to_be_expired_individual_bookings_recap_email_to_beneficiary
from pcapi.domain.user_emails import send_user_driven_cancellation_email_to_offerer
from pcapi.domain.user_emails import send_warning_to_user_after_pro_booking_cancellation
from pcapi.domain.user_emails import send_withdrawal_terms_to_newly_validated_offerer
from pcapi.model_creators.generic_creators import create_booking
from pcapi.model_creators.generic_creators import create_offerer
from pcapi.model_creators.generic_creators import create_venue
from pcapi.model_creators.specific_creators import create_stock_with_event_offer
from pcapi.utils.human_ids import humanize


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


class SendBeneficiaryBookingCancellationEmailTest:
    @patch(
        "pcapi.domain.user_emails.make_beneficiary_booking_cancellation_email_data",
        return_value={"Mj-TemplateID": 1091464},
    )
    def test_should_called_mocked_send_email_with_valid_data(
        self, mocked_make_beneficiary_booking_cancellation_email_data
    ):
        # given
        booking = booking_factories.IndividualBookingFactory()

        # when
        send_individual_booking_cancellation_email(booking.individualBooking)

        # then
        mocked_make_beneficiary_booking_cancellation_email_data.assert_called_once_with(booking.individualBooking)
        assert len(mails_testing.outbox) == 1  # test number of emails sent
        assert mails_testing.outbox[0].sent_data["Mj-TemplateID"] == 1091464


class SendOffererDrivenCancellationEmailToOffererTest:
    @patch(
        "pcapi.domain.user_emails.make_offerer_driven_cancellation_email_for_offerer", return_value={"Html-part": ""}
    )
    def test_should_send_cancellation_by_offerer_email_to_offerer(
        self, make_offerer_driven_cancellation_email_for_offerer
    ):
        # Given
        user = users_factories.BeneficiaryGrant18Factory.build(email="user@example.com")
        offerer = create_offerer()
        venue = create_venue(offerer)
        venue.bookingEmail = "booking@example.com"
        stock = create_stock_with_event_offer(offerer, venue)
        stock.offer.bookingEmail = "offer@example.com"
        booking = create_booking(user=user, stock=stock)

        # When
        send_offerer_driven_cancellation_email_to_offerer(booking)

        # Then
        make_offerer_driven_cancellation_email_for_offerer.assert_called_once_with(booking)
        assert len(mails_testing.outbox) == 1  # test number of emails sent
        assert mails_testing.outbox[0].sent_data["To"] == "offer@example.com"


class SendBeneficiaryUserDrivenCancellationEmailToOffererTest:
    def test_should_send_booking_cancellation_email_to_offerer(self):
        # Given
        booking = booking_factories.IndividualBookingFactory(stock__offer__bookingEmail="booking@example.com")

        # When
        send_user_driven_cancellation_email_to_offerer(booking)

        # Then
        assert len(mails_testing.outbox) == 1  # test number of emails sent
        assert mails_testing.outbox[0].sent_data["To"] == "booking@example.com"
        assert mails_testing.outbox[0].sent_data["MJ-TemplateID"] == 780015


class SendWarningToBeneficiaryAfterProBookingCancellationTest:
    def test_should_sends_email_to_beneficiary_when_pro_cancels_booking(self):
        # Given
        booking = booking_factories.IndividualBookingFactory(
            individualBooking__user__email="user@example.com",
            user__firstName="Jeanne",
        )

        # When
        send_warning_to_user_after_pro_booking_cancellation(booking)

        # Then
        assert mails_testing.outbox[0].sent_data == {
            "FromEmail": "support@example.com",
            "MJ-TemplateID": 1116690,
            "MJ-TemplateLanguage": True,
            "To": "user@example.com",
            "Vars": {
                "event_date": "",
                "event_hour": "",
                "is_event": 0,
                "is_free_offer": 0,
                "is_thing": 1,
                "is_online": 0,
                "offer_name": booking.stock.offer.name,
                "offer_price": "10.00",
                "offerer_name": booking.offerer.name,
                "user_first_name": "Jeanne",
                "user_last_name": "Doux",
                "venue_name": booking.venue.name,
                "env": "-development",
            },
        }


class SendBookingConfirmationEmailToBeneficiaryTest:
    @patch(
        "pcapi.domain.user_emails.retrieve_data_for_beneficiary_booking_confirmation_email",
        return_value={"MJ-TemplateID": 2942751},
    )
    def when_called_calls_send_email(self, mocked_retrieve_data_for_beneficiary_booking_confirmation_email):
        # Given
        user = users_factories.BeneficiaryGrant18Factory()
        booking = booking_factories.IndividualBookingFactory(individualBooking__user=user)

        # When
        send_individual_booking_confirmation_email_to_beneficiary(booking.individualBooking)

        # Then
        mocked_retrieve_data_for_beneficiary_booking_confirmation_email.assert_called_once_with(
            booking.individualBooking
        )
        assert len(mails_testing.outbox) == 1  # test number of emails sent
        assert mails_testing.outbox[0].sent_data["MJ-TemplateID"] == 2942751


class SendBookingConfirmationEmailToOffererTest:
    def test_send_to_offerer(self):
        booking = booking_factories.IndividualBookingFactory(
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
        booking = booking_factories.IndividualBookingFactory(stock__offer__bookingEmail="offerer@example.com")

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

    def test_send_activation_email_for_native(self):
        # given
        beneficiary = users_factories.BeneficiaryGrant18Factory.build()
        token = users_factories.EmailValidationToken.build(user=beneficiary)

        # when
        send_email_confirmation_email(beneficiary, token=token)

        # then
        assert len(mails_testing.outbox) == 1  # test number of emails sent
        native_app_link = mails_testing.outbox[0].sent_data["Vars"]["nativeAppLink"]
        assert token.value in native_app_link


class SendResetPasswordProEmailTest:
    @patch(
        "pcapi.domain.user_emails.retrieve_data_for_reset_password_pro_email", return_value={"MJ-TemplateID": 779295}
    )
    def when_feature_send_emails_enabled_sends_a_reset_password_email_to_pro_user(
        self, mock_retrieve_data_for_reset_password_pro_email, app
    ):
        # given
        user = users_factories.ProFactory(email="pro@example.com")

        # when
        send_reset_password_email_to_pro(user)

        # then
        mock_retrieve_data_for_reset_password_pro_email.assert_called_once_with(user, user.tokens[0])
        assert len(mails_testing.outbox) == 1  # test number of emails sent
        assert mails_testing.outbox[0].sent_data["MJ-TemplateID"] == 779295


class SendResetPasswordUserEmailTest:
    @patch(
        "pcapi.core.mails.transactional.users.reset_password_email.retrieve_data_for_reset_password_user_email",
        return_value={"MJ-TemplateID": 912168},
    )
    def when_feature_send_emails_enabled_sends_a_reset_password_email_to_user(
        self, mock_retrieve_data_for_reset_password_user_email, app
    ):
        # given
        user = users_factories.UserFactory(email="bobby@example.com")

        # when
        user_emails.send_reset_password_email_to_user(user)

        # then
        mock_retrieve_data_for_reset_password_user_email.assert_called_once_with(user, user.tokens[0])
        assert len(mails_testing.outbox) == 1  # test number of emails sent
        assert mails_testing.outbox[0].sent_data["MJ-TemplateID"] == 912168

    @patch(
        "pcapi.core.mails.transactional.users.reset_password_email.retrieve_data_for_reset_password_native_app_email",
        return_value={"MJ-TemplateID": 12345},
    )
    def when_feature_send_emails_enabled_sends_a_reset_password_email_to_native_app_user(
        self, retrieve_data_for_reset_password_native_app_email
    ):
        # given
        user = users_factories.UserFactory(email="bobby@example.com")

        # when
        user_emails.send_reset_password_email_to_native_app_user(user)

        # then
        retrieve_data_for_reset_password_native_app_email.assert_called_once_with(user, user.tokens[0])
        assert len(mails_testing.outbox) == 1  # test number of emails sent
        assert mails_testing.outbox[0].sent_data["MJ-TemplateID"] == 12345

    @override_features(ENABLE_SENDINBLUE_TRANSACTIONAL_EMAILS=True)
    def test_send_a_reset_password_email_to_native_app_user_via_sendinblue(self):
        # given
        user = users_factories.UserFactory(email="bobby@example.com")

        # when
        user_emails.send_reset_password_email_to_native_app_user(user)

        # then
        assert len(mails_testing.outbox) == 1  # test number of emails sent

        native_app_link = mails_testing.outbox[0].sent_data["params"]["NATIVE_APP_LINK"]
        assert user.tokens[0].value in native_app_link
        assert mails_testing.outbox[0].sent_data["template"] == asdict(TransactionalEmail.NEW_PASSWORD_REQUEST.value)
        assert mails_testing.outbox[0].sent_data["To"] == "bobby@example.com"


class SendRejectionEmailToBeneficiaryPreSubscriptionTest:
    @patch(
        "pcapi.core.mails.transactional.users.email_duplicate_pre_subscription_rejected.get_duplicate_beneficiary_pre_subscription_rejected_data",
        return_value={"MJ-TemplateID": 1530996},
    )
    @override_features(ENABLE_SENDINBLUE_TRANSACTIONAL_EMAILS=False)
    def when_beneficiary_is_a_duplicate_sends_correct_template(self, mocked_make_data, app):
        # given
        beneficiary_pre_subscription = BeneficiaryPreSubscriptionFactory()

        # when
        send_rejection_email_to_beneficiary_pre_subscription(beneficiary_pre_subscription, beneficiary_is_eligible=True)

        # then
        mocked_make_data.assert_called_once()
        assert len(mails_testing.outbox) == 1  # test number of emails sent
        assert mails_testing.outbox[0].sent_data["MJ-TemplateID"] == 1530996

    @override_features(ENABLE_SENDINBLUE_TRANSACTIONAL_EMAILS=True)
    def when_beneficiary_is_a_duplicate_sends_correct_template_sendinblue(self, app):
        # given
        beneficiary_pre_subscription = BeneficiaryPreSubscriptionFactory()

        # when
        send_rejection_email_to_beneficiary_pre_subscription(beneficiary_pre_subscription, beneficiary_is_eligible=True)

        # then
        assert len(mails_testing.outbox) == 1  # test number of emails sent
        assert mails_testing.outbox[0].sent_data["template"] == asdict(
            TransactionalEmail.EMAIL_DUPLICATE_BENEFICIARY_PRE_SUBCRIPTION_REJECTED.value
        )

    @patch(
        "pcapi.core.mails.transactional.users.email_duplicate_pre_subscription_rejected.get_not_eligible_beneficiary_pre_subscription_rejected_data",
        return_value={"MJ-TemplateID": 1619528},
    )
    @override_features(ENABLE_SENDINBLUE_TRANSACTIONAL_EMAILS=False)
    def when_beneficiary_is_not_eligible_sends_correct_template(self, mocked_make_data, app):
        # given
        beneficiary_pre_subscription = BeneficiaryPreSubscriptionFactory()

        # when
        send_rejection_email_to_beneficiary_pre_subscription(
            beneficiary_pre_subscription, beneficiary_is_eligible=False
        )

        # then
        mocked_make_data.assert_called_once()
        assert len(mails_testing.outbox) == 1  # test number of emails sent
        assert mails_testing.outbox[0].sent_data["MJ-TemplateID"] == 1619528

    @patch(
        "pcapi.core.mails.transactional.users.email_duplicate_pre_subscription_rejected.get_not_eligible_beneficiary_pre_subscription_rejected_data",
        return_value={"MJ-TemplateID": 1619528},
    )
    @override_features(ENABLE_SENDINBLUE_TRANSACTIONAL_EMAILS=True)
    def when_beneficiary_is_not_eligible_sends_correct_template_sendinblue(self, mocked_make_data, app):
        # given
        beneficiary_pre_subscription = BeneficiaryPreSubscriptionFactory()

        # when
        send_rejection_email_to_beneficiary_pre_subscription(
            beneficiary_pre_subscription, beneficiary_is_eligible=False
        )

        # then
        mocked_make_data.assert_called_once()
        assert len(mails_testing.outbox) == 1  # test number of emails sent
        assert mails_testing.outbox[0].sent_data["MJ-TemplateID"] == 1619528


class SendExpiredBookingsRecapEmailToBeneficiaryTest:
    def test_should_send_email_to_beneficiary_when_expired_book_booking_cancelled(self, app):
        amnesiac_user = users_factories.BeneficiaryGrant18Factory(email="dory@example.com")
        expired_today_book_booking = booking_factories.IndividualBookingFactory(
            user=amnesiac_user, stock__offer__subcategoryId=subcategories.LIVRE_PAPIER.id
        )
        send_expired_bookings_recap_email_to_beneficiary(amnesiac_user, [expired_today_book_booking])

        assert len(mails_testing.outbox) == 1
        assert mails_testing.outbox[0].sent_data["Mj-TemplateID"] == 3095107
        assert mails_testing.outbox[0].sent_data["Vars"]["withdrawal_period"] == 10

    def test_should_send_email_to_beneficiary_when_expired_none_books_bookings_cancelled(self, app):
        amnesiac_user = users_factories.BeneficiaryGrant18Factory(email="dory@example.com")
        expired_today_dvd_booking = booking_factories.IndividualBookingFactory(
            user=amnesiac_user, stock__offer__subcategoryId=subcategories.SUPPORT_PHYSIQUE_FILM.id
        )
        expired_today_cd_booking = booking_factories.IndividualBookingFactory(
            user=amnesiac_user, stock__offer__subcategoryId=subcategories.SUPPORT_PHYSIQUE_FILM.id
        )
        send_expired_bookings_recap_email_to_beneficiary(
            amnesiac_user, [expired_today_cd_booking, expired_today_dvd_booking]
        )

        assert len(mails_testing.outbox) == 1
        assert mails_testing.outbox[0].sent_data["Mj-TemplateID"] == 3095107
        assert mails_testing.outbox[0].sent_data["Vars"]["withdrawal_period"] == 30

    def test_should_send_two_emails_to_beneficiary_when_expired_books_and_other_bookings_cancelled(self, app):
        amnesiac_user = users_factories.BeneficiaryGrant18Factory(email="dory@example.com")
        expired_today_book_booking = booking_factories.IndividualBookingFactory(
            user=amnesiac_user, stock__offer__subcategoryId=subcategories.LIVRE_PAPIER.id
        )
        expired_today_cd_booking = booking_factories.IndividualBookingFactory(
            user=amnesiac_user, stock__offer__subcategoryId=subcategories.SUPPORT_PHYSIQUE_FILM.id
        )
        send_expired_bookings_recap_email_to_beneficiary(
            amnesiac_user, [expired_today_cd_booking, expired_today_book_booking]
        )

        assert len(mails_testing.outbox) == 2
        assert mails_testing.outbox[0].sent_data["Mj-TemplateID"] == 3095107
        assert mails_testing.outbox[0].sent_data["Vars"]["withdrawal_period"] == 10
        assert mails_testing.outbox[1].sent_data["Mj-TemplateID"] == 3095107
        assert mails_testing.outbox[1].sent_data["Vars"]["withdrawal_period"] == 30


class SendExpiredBookingsRecapEmailToOffererTest:
    def test_should_send_email_to_offerer_when_expired_bookings_cancelled(self, app):
        offerer = OffererFactory()
        expired_today_dvd_booking = booking_factories.IndividualBookingFactory(
            stock__offer__bookingEmail="offerer.booking@example.com"
        )
        expired_today_cd_booking = booking_factories.IndividualBookingFactory(
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
        expired_today_dvd_booking = booking_factories.IndividualBookingFactory(
            stock__offer__name="Intouchables",
            stock__offer__bookingEmail="offerer.booking@example.com",
            stock__offer__subcategoryId=subcategories.SUPPORT_PHYSIQUE_FILM.id,
        )
        expired_today_book_booking = booking_factories.IndividualBookingFactory(
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


class SendSoonToBeExpiredBookingsRecapEmailToBeneficiaryTest:
    @patch(
        "pcapi.domain.user_emails.build_soon_to_be_expired_bookings_recap_email_data_for_beneficiary",
        return_value={"MJ-TemplateID": 12345},
    )
    def test_should_send_email_to_beneficiary_when_they_have_soon_to_be_expired_bookings(
        self, build_soon_to_be_expired_bookings_recap_email_data_for_beneficiary
    ):
        # given
        now = datetime.utcnow()
        user = users_factories.BeneficiaryGrant18Factory(email="isasimov@example.com")
        created_23_days_ago = now - timedelta(days=23)

        dvd = ProductFactory(subcategoryId=subcategories.SUPPORT_PHYSIQUE_FILM.id)
        soon_to_be_expired_dvd_booking = booking_factories.IndividualBookingFactory(
            stock__offer__product=dvd,
            stock__offer__name="Fondation",
            stock__offer__venue__name="Première Fondation",
            dateCreated=created_23_days_ago,
            user=user,
        )

        cd = ProductFactory(subcategoryId=subcategories.SUPPORT_PHYSIQUE_MUSIQUE.id)
        soon_to_be_expired_cd_booking = booking_factories.IndividualBookingFactory(
            stock__offer__product=cd,
            stock__offer__name="Fondation et Empire",
            stock__offer__venue__name="Seconde Fondation",
            dateCreated=created_23_days_ago,
            user=user,
        )

        # when
        send_soon_to_be_expired_individual_bookings_recap_email_to_beneficiary(
            user, [soon_to_be_expired_cd_booking, soon_to_be_expired_dvd_booking]
        )

        # then
        build_soon_to_be_expired_bookings_recap_email_data_for_beneficiary.assert_called_once_with(
            beneficiary=user,
            bookings=[soon_to_be_expired_cd_booking, soon_to_be_expired_dvd_booking],
            days_before_cancel=7,
            days_from_booking=23,
        )
        assert len(mails_testing.outbox) == 1  # test number of emails sent
        assert mails_testing.outbox[0].sent_data["MJ-TemplateID"] == 12345

    @patch(
        "pcapi.domain.user_emails.build_soon_to_be_expired_bookings_recap_email_data_for_beneficiary",
        return_value={"MJ-TemplateID": 12345},
    )
    def test_should_send_two_emails_to_beneficiary_when_they_book_and_other_things_have_soon_to_be_expired_bookings(
        self, build_soon_to_be_expired_bookings_recap_email_data_for_beneficiary
    ):
        # given
        now = datetime.utcnow()
        user = users_factories.BeneficiaryGrant18Factory(email="isasimov@example.com")
        created_5_days_ago = now - timedelta(days=5)
        created_23_days_ago = now - timedelta(days=23)

        book = ProductFactory(subcategoryId=subcategories.LIVRE_PAPIER.id)
        soon_to_be_expired_book_booking = booking_factories.IndividualBookingFactory(
            stock__offer__product=book,
            stock__offer__name="Fondation",
            stock__offer__venue__name="Première Fondation",
            dateCreated=created_5_days_ago,
            user=user,
        )

        cd = ProductFactory(subcategoryId=subcategories.SUPPORT_PHYSIQUE_MUSIQUE.id)
        soon_to_be_expired_cd_booking = booking_factories.IndividualBookingFactory(
            stock__offer__product=cd,
            stock__offer__name="Fondation et Empire",
            stock__offer__venue__name="Seconde Fondation",
            dateCreated=created_23_days_ago,
            user=user,
        )

        # when
        send_soon_to_be_expired_individual_bookings_recap_email_to_beneficiary(
            user, [soon_to_be_expired_book_booking, soon_to_be_expired_cd_booking]
        )

        # then
        call1 = call(
            beneficiary=user, bookings=[soon_to_be_expired_book_booking], days_before_cancel=5, days_from_booking=5
        )
        call2 = call(
            beneficiary=user, bookings=[soon_to_be_expired_cd_booking], days_before_cancel=7, days_from_booking=23
        )
        calls = [call1, call2]

        build_soon_to_be_expired_bookings_recap_email_data_for_beneficiary.assert_has_calls(calls, any_order=False)

        assert build_soon_to_be_expired_bookings_recap_email_data_for_beneficiary.call_count == 2
        assert len(mails_testing.outbox) == 2  # test number of emails sent
        assert mails_testing.outbox[0].sent_data["MJ-TemplateID"] == 12345
        assert mails_testing.outbox[1].sent_data["MJ-TemplateID"] == 12345


class SendNewlyEligibleUserEmailTest:
    def test_send_activation_email(self):
        # given
        user = users_factories.UserFactory(
            dateOfBirth=(datetime.now() - relativedelta(years=18, days=5)), departementCode="93"
        )

        # when
        send_newly_eligible_user_email(user)

        # then
        assert len(mails_testing.outbox) == 1  # test number of emails sent
        assert mails_testing.outbox[0].sent_data["Mj-TemplateID"] == 2030056
        assert (
            mails_testing.outbox[0].sent_data["Vars"]["nativeAppLink"][:118]
            == "https://passcultureapptestauto.page.link/?link=https%3A%2F%2F"
            "app-native.testing.internal-passculture.app%2Fid-check%3F"
        )
        assert "email" in mails_testing.outbox[0].sent_data["Vars"]["nativeAppLink"]
        assert mails_testing.outbox[0].sent_data["Vars"]["depositAmount"] == 300


class SendOfferValidationTest:
    def test_send_offer_approval_email(
        self,
    ):
        # Given
        venue = VenueFactory(name="Sibérie orientale")
        offer = OfferFactory(name="Michel Strogoff", venue=venue)

        # When
        send_offer_validation_status_update_email(offer, OfferValidationStatus.APPROVED, ["jules.verne@example.com"])

        # Then
        assert len(mails_testing.outbox) == 1  # test number of emails sent
        assert mails_testing.outbox[0].sent_data["MJ-TemplateID"] == 2613721
        assert mails_testing.outbox[0].sent_data["Vars"]["offer_name"] == "Michel Strogoff"
        assert mails_testing.outbox[0].sent_data["Vars"]["venue_name"] == "Sibérie orientale"
        assert humanize(offer.id) in mails_testing.outbox[0].sent_data["Vars"]["pc_pro_offer_link"]
        assert mails_testing.outbox[0].sent_data["To"] == "jules.verne@example.com"

    def test_send_offer_refusing_email(
        self,
    ):
        # Given
        venue = VenueFactory(name="Sibérie orientale")
        offer = OfferFactory(name="Michel Strogoff", venue=venue)

        # When
        send_offer_validation_status_update_email(offer, OfferValidationStatus.REJECTED, ["jules.verne@example.com"])

        # Then
        assert len(mails_testing.outbox) == 1  # test number of emails sent
        assert mails_testing.outbox[0].sent_data["MJ-TemplateID"] == 2613942
        assert mails_testing.outbox[0].sent_data["Vars"]["offer_name"] == "Michel Strogoff"
        assert mails_testing.outbox[0].sent_data["Vars"]["venue_name"] == "Sibérie orientale"
        assert mails_testing.outbox[0].sent_data["To"] == "jules.verne@example.com"
        assert humanize(offer.id) in mails_testing.outbox[0].sent_data["Vars"]["pc_pro_offer_link"]


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
