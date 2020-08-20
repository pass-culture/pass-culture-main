from unittest.mock import Mock, call, patch

from tests.conftest import clean_database
from tests.domain_creators.generic_creators import create_domain_beneficiary, \
    create_domain_beneficiary_pre_subcription
from tests.model_creators.generic_creators import create_booking, \
    create_deposit, create_offerer, create_user, create_user_offerer, \
    create_venue
from tests.model_creators.specific_creators import create_offer_with_thing_product, \
    create_stock_with_event_offer
from tests.test_utils import create_mocked_bookings

from domain.beneficiary_pre_subscription.beneficiary_pre_subscription_exceptions import \
    BeneficiaryIsADupplicate, BeneficiaryIsNotEligible
from domain.booking.booking import Booking
from domain.stock.stock import Stock
from domain.user_emails import send_activation_email, \
    send_attachment_validation_email_to_pro_offerer, \
    send_batch_cancellation_emails_to_users, \
    send_beneficiary_booking_cancellation_email, \
    send_booking_confirmation_email_to_beneficiary, \
    send_booking_recap_emails, \
    send_offerer_bookings_recap_email_after_offerer_cancellation, \
    send_offerer_driven_cancellation_email_to_offerer, \
    send_ongoing_offerer_attachment_information_email_to_pro, \
    send_rejection_email_to_beneficiary_pre_subscription, \
    send_reset_password_email_to_pro, send_reset_password_email_to_user, \
    send_user_driven_cancellation_email_to_offerer, \
    send_user_validation_email, send_validation_confirmation_email_to_pro, \
    send_venue_validation_confirmation_email, \
    send_warning_to_beneficiary_after_pro_booking_cancellation
from models import Offerer
from repository import repository


class SendBeneficiaryBookingCancellationEmailTest:
    @patch('domain.user_emails.make_beneficiary_booking_cancellation_email_data',
           return_value={'Mj-TemplateID': 1091464})
    def test_should_called_mocked_send_email_with_valid_data(self,
                                                             mocked_make_beneficiary_booking_cancellation_email_data):
        # given
        beneficiary = create_user()
        booking = create_booking(beneficiary, idx=23)
        mocked_send_email = Mock()

        # when
        send_beneficiary_booking_cancellation_email(booking, mocked_send_email)

        # then
        mocked_make_beneficiary_booking_cancellation_email_data.assert_called_once_with(booking)
        mocked_send_email.assert_called_once_with(data={'Mj-TemplateID': 1091464})


class SendOffererDrivenCancellationEmailToOffererTest:
    @patch('domain.user_emails.ADMINISTRATION_EMAIL_ADDRESS', 'administration@example.com')
    @patch('domain.user_emails.make_offerer_driven_cancellation_email_for_offerer', return_value={'Html-part': ''})
    @patch('utils.mailing.feature_send_mail_to_users_enabled', return_value=True)
    def test_should_send_cancellation_by_offerer_email_to_offerer_and_administration_when_booking_email_provided(self,
                                                                                                                 feature_send_mail_to_users_enabled,
                                                                                                                 make_offerer_driven_cancellation_email_for_offerer):
        # Given
        user = create_user(email='user@example.com')
        offerer = create_offerer()
        venue = create_venue(offerer)
        venue.bookingEmail = 'booking@example.com'
        stock = create_stock_with_event_offer(offerer, venue)
        stock.offer.bookingEmail = 'offer@example.com'
        booking = create_booking(user=user, stock=stock)
        mocked_send_email = Mock()

        # When
        send_offerer_driven_cancellation_email_to_offerer(booking, mocked_send_email)

        # Then
        make_offerer_driven_cancellation_email_for_offerer.assert_called_once_with(booking)
        mocked_send_email.assert_called_once()
        args = mocked_send_email.call_args
        assert args[1]['data']['To'] == 'offer@example.com, administration@example.com'

    @patch('domain.user_emails.ADMINISTRATION_EMAIL_ADDRESS', 'administration@example.com')
    @patch('domain.user_emails.make_offerer_driven_cancellation_email_for_offerer', return_value={'Html-part': ''})
    @patch('utils.mailing.feature_send_mail_to_users_enabled', return_value=True)
    def test_should_send_cancellation_by_offerer_email_only_to_administration_when_no_booking_email_provided(self,
                                                                                                             feature_send_mail_to_users_enabled,
                                                                                                             make_offerer_driven_cancellation_email_for_offerer):
        # Given
        user = create_user(email='user@example.com')
        offerer = create_offerer()
        venue = create_venue(offerer)
        stock = create_stock_with_event_offer(offerer, venue)
        stock.offer.bookingEmail = None
        booking = create_booking(user=user, stock=stock)
        mocked_send_email = Mock()

        # When
        send_offerer_driven_cancellation_email_to_offerer(booking, mocked_send_email)

        # Then
        make_offerer_driven_cancellation_email_for_offerer.assert_called_once_with(booking)
        mocked_send_email.assert_called_once()
        args = mocked_send_email.call_args
        assert args[1]['data']['To'] == 'administration@example.com'


class SendBeneficiaryUserDrivenCancellationEmailToOffererTest:
    @clean_database
    @patch('domain.user_emails.ADMINISTRATION_EMAIL_ADDRESS', 'administration@example.com')
    @patch('emails.beneficiary_offer_cancellation.feature_send_mail_to_users_enabled', return_value=True)
    def test_should_send_booking_cancellation_email_to_offerer_and_administration_when_booking_email_provided(self,
                                                                                                              mock_feature_send_mail_to_users_enabled,
                                                                                                              app):
        # Given
        user = create_user(email='user@example.com')
        offerer = create_offerer()
        deposit = create_deposit(user, amount=500)
        venue = create_venue(offerer)
        stock = create_stock_with_event_offer(offerer, venue)
        stock.offer.bookingEmail = 'booking@example.com'
        booking = create_booking(user=user, stock=stock)
        mocked_send_email = Mock()

        repository.save(deposit, stock)

        # When
        send_user_driven_cancellation_email_to_offerer(booking, mocked_send_email)

        # Then
        mocked_send_email.assert_called_once()
        args = mocked_send_email.call_args
        assert args[1]['data']['To'] == 'booking@example.com, administration@example.com'

    @clean_database
    @patch('domain.user_emails.ADMINISTRATION_EMAIL_ADDRESS', 'administration@example.com')
    @patch('emails.beneficiary_offer_cancellation.feature_send_mail_to_users_enabled', return_value=True)
    def test_should_send_booking_cancellation_email_only_to_administration_when_no_booking_email_provided(self,
                                                                                                          mock_feature_send_mail_to_users_enabled,
                                                                                                          app):
        # Given
        user = create_user(email='user@example.com')
        offerer = create_offerer()
        deposit = create_deposit(user, amount=500)
        venue = create_venue(offerer)
        stock = create_stock_with_event_offer(offerer, venue)
        stock.offer.bookingEmail = None
        booking = create_booking(user=user, stock=stock)
        mocked_send_email = Mock()

        repository.save(deposit, stock)

        # When
        send_user_driven_cancellation_email_to_offerer(booking, mocked_send_email)

        # Then
        mocked_send_email.assert_called_once()
        args = mocked_send_email.call_args
        assert args[1]['data']['To'] == 'administration@example.com'


class SendWarningToBeneficiaryAfterProBookingCancellationTest:
    @patch('emails.beneficiary_warning_after_pro_booking_cancellation.SUPPORT_EMAIL_ADDRESS', 'support@example.com')
    @patch('emails.beneficiary_warning_after_pro_booking_cancellation.DEV_EMAIL_ADDRESS', 'dev@example.com')
    @patch('emails.beneficiary_warning_after_pro_booking_cancellation.feature_send_mail_to_users_enabled',
           return_value=True)
    def test_should_sends_email_to_beneficiary_when_pro_cancels_booking(self, mock_feature_send_mail_to_users_enabled):
        # Given
        user = create_user(email='user@example.com')
        booking = create_booking(user=user)
        mocked_send_email = Mock()

        # When
        send_warning_to_beneficiary_after_pro_booking_cancellation(booking, mocked_send_email)

        # Then
        mocked_send_email.assert_called_once()
        args, kwargs = mocked_send_email.call_args
        assert kwargs['data'] == {
            'FromEmail': 'support@example.com',
            'MJ-TemplateID': 1116690,
            'MJ-TemplateLanguage': True,
            'To': 'user@example.com',
            'Vars': {
                'event_date': '',
                'event_hour': '',
                'is_event': 0,
                'is_free_offer': 0,
                'is_thing': 1,
                'is_online': 0,
                'offer_name': booking.stock.offer.name,
                'offer_price': '10',
                'offerer_name': booking.stock.offer.venue.managingOfferer.name,
                'user_first_name': user.firstName,
                'venue_name': booking.stock.offer.venue.name
            }
        }


class SendBookingConfirmationEmailToBeneficiaryTest:
    @patch('utils.mailing.feature_send_mail_to_users_enabled', return_value=True)
    @patch('domain.user_emails.retrieve_data_for_beneficiary_booking_confirmation_email',
           return_value={'MJ-TemplateID': 1163067})
    def when_called_calls_send_email(self,
                                     mocked_retrieve_data_for_beneficiary_booking_confirmation_email,
                                     mock_feature_send_mail_to_users_enabled
                                     ):
        # Given
        user = create_user()
        booking = create_booking(user=user, idx=23)
        mocked_send_email = Mock()

        # When
        send_booking_confirmation_email_to_beneficiary(booking, mocked_send_email)

        # Then
        mocked_retrieve_data_for_beneficiary_booking_confirmation_email.assert_called_once_with(booking)
        mocked_send_email.assert_called_once_with(data={'MJ-TemplateID': 1163067})


class SendBookingRecapEmailsTest:
    @patch('utils.mailing.DEV_EMAIL_ADDRESS', 'dev@example.com')
    @patch('utils.mailing.feature_send_mail_to_users_enabled', return_value=False)
    def when_feature_send_mail_to_users_disabled_sends_email_to_pass_culture_dev(self,
                                                                                 mock_feature_send_mail_to_users_enabled,
                                                                                 app):
        # given
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue, booking_email='offer.booking.email@example.net')

        user = create_domain_beneficiary(identifier=1)
        stock = Stock(
            identifier=1,
            quantity=None,
            offer=offer,
            price=10
        )
        booking = Booking(beneficiary=user, stock=stock, amount=1, quantity=10)
        mocked_send_email = Mock()

        # when
        send_booking_recap_emails(booking, mocked_send_email)

        # then
        mocked_send_email.assert_called_once()
        args = mocked_send_email.call_args
        data = args[1]['data']
        assert data['To'] == 'dev@example.com'

    @patch('domain.user_emails.ADMINISTRATION_EMAIL_ADDRESS', 'administration@example.com')
    @patch('utils.mailing.feature_send_mail_to_users_enabled', return_value=True)
    def when_feature_send_mail_to_users_enabled_and_offer_booking_email_sends_to_offerer_and_administration(self,
                                                                                                            mock_feature_send_mail_to_users_enabled,
                                                                                                            app):
        # given
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue, booking_email='offer.booking.email@example.net')

        user = create_domain_beneficiary(identifier=1)
        stock = Stock(
            identifier=1,
            quantity=None,
            offer=offer,
            price=10
        )
        booking = Booking(beneficiary=user, stock=stock, amount=1, quantity=10)

        mocked_send_email = Mock()

        # when
        send_booking_recap_emails(booking, mocked_send_email)

        # then
        mocked_send_email.assert_called_once()
        args = mocked_send_email.call_args
        data = args[1]['data']
        assert data['To'] == 'administration@example.com, offer.booking.email@example.net'

    @patch('domain.user_emails.ADMINISTRATION_EMAIL_ADDRESS', 'administration@example.com')
    @patch('utils.mailing.feature_send_mail_to_users_enabled', return_value=True)
    def when_feature_send_mail_to_users_enabled_and_not_offer_booking_email_sends_only_to_administration(
            self,
            feature_send_mail_to_users_enabled):
        # given
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue, booking_email=None)

        user = create_domain_beneficiary(identifier=1)
        stock = Stock(
            identifier=1,
            quantity=None,
            offer=offer,
            price=10
        )
        booking = Booking(beneficiary=user, stock=stock, amount=1, quantity=10)

        mocked_send_email = Mock()

        # when
        send_booking_recap_emails(booking, mocked_send_email)

        # then
        mocked_send_email.assert_called_once()
        args = mocked_send_email.call_args
        data = args[1]['data']
        assert data['To'] == 'administration@example.com'


class SendValidationConfirmationEmailTest:
    @patch('domain.user_emails.retrieve_data_for_new_offerer_validation_email',
           return_value={'Mj-TemplateID': 778723})
    def when_feature_send_mail_to_users_is_enabled_sends_email_to_all_users_linked_to_offerer(self,
                                                                                              mock_retrieve_data_for_new_offerer_validation_email):
        # Given
        offerer = Offerer()
        mocked_send_email = Mock()

        # When
        send_validation_confirmation_email_to_pro(offerer, mocked_send_email)

        # Then
        mock_retrieve_data_for_new_offerer_validation_email.assert_called_once_with(offerer)
        mocked_send_email.assert_called_once_with(data={'Mj-TemplateID': 778723})


class SendCancellationEmailOneUserTest:
    @patch('domain.user_emails.send_warning_to_beneficiary_after_pro_booking_cancellation')
    @patch('utils.mailing.feature_send_mail_to_users_enabled', return_value=True)
    def when_called_calls_send_offerer_driven_cancellation_email_to_user_for_every_booking(self,
                                                                                           feature_send_mail_to_users_enabled,
                                                                                           mocked_send_warning_to_beneficiary_after_pro_booking_cancellation):
        # Given
        mocked_send_email = Mock()
        num_bookings = 6
        bookings = create_mocked_bookings(num_bookings, 'offerer@example.com')
        calls = [call(booking, mocked_send_email) for booking in bookings]

        # When
        send_batch_cancellation_emails_to_users(bookings, mocked_send_email)

        # Then
        mocked_send_warning_to_beneficiary_after_pro_booking_cancellation.assert_has_calls(calls)


class SendOffererBookingsRecapEmailAfterOffererCancellationTest:
    @patch('domain.user_emails.retrieve_offerer_bookings_recap_email_data_after_offerer_cancellation',
           return_value={'Mj-TemplateID': 1116333})
    @patch('domain.user_emails.ADMINISTRATION_EMAIL_ADDRESS', 'administration@example.com')
    @patch('utils.mailing.feature_send_mail_to_users_enabled', return_value=True)
    def when_feature_send_mail_to_users_enabled_sends_to_offerer_administration(self,
                                                                                feature_send_mail_to_users_enabled,
                                                                                retrieve_offerer_bookings_recap_email_data_after_offerer_cancellation):
        # Given
        num_bookings = 5
        bookings = create_mocked_bookings(num_bookings, 'offerer@example.com')
        recipients = 'offerer@example.com, administration@example.com'
        mocked_send_email = Mock()

        # When
        send_offerer_bookings_recap_email_after_offerer_cancellation(bookings, mocked_send_email)

        # Then
        retrieve_offerer_bookings_recap_email_data_after_offerer_cancellation.assert_called_once_with(bookings,
                                                                                                      recipients)
        mocked_send_email.assert_called_once_with(data={'Mj-TemplateID': 1116333})

    @patch('domain.user_emails.ADMINISTRATION_EMAIL_ADDRESS', 'administration@example.com')
    @patch('domain.user_emails.retrieve_offerer_bookings_recap_email_data_after_offerer_cancellation',
           return_value={'Mj-TemplateID': 1116333})
    @patch('utils.mailing.feature_send_mail_to_users_enabled', return_value=True)
    def when_feature_send_mail_to_users_enabled_and_offerer_email_is_missing_sends_only_to_administration(self,
                                                                                                          feature_send_mail_to_users_enabled,
                                                                                                          retrieve_offerer_bookings_recap_email_data_after_offerer_cancellation):
        # Given
        num_bookings = 5
        bookings = create_mocked_bookings(num_bookings, None)
        recipients = 'administration@example.com'
        mocked_send_email = Mock()

        # When
        send_offerer_bookings_recap_email_after_offerer_cancellation(bookings, mocked_send_email)

        # Then
        retrieve_offerer_bookings_recap_email_data_after_offerer_cancellation.assert_called_once_with(bookings,
                                                                                                      recipients)
        mocked_send_email.assert_called_once_with(data={'Mj-TemplateID': 1116333})


class SendVenueValidationConfirmationEmailTest:
    @patch('domain.user_emails.find_all_emails_of_user_offerers_admins',
           return_value=['admin1@example.com', 'admin2@example.com'])
    @patch('domain.user_emails.make_venue_validated_email', return_value={'Html-part': ''})
    @patch('utils.mailing.feature_send_mail_to_users_enabled', return_value=True)
    def when_feature_send_mail_to_users_enabled_sends_email_to_all_users_linked_to_offerer(self,
                                                                                           mock_feature_send_mail_to_users_enabled,
                                                                                           mock_make_venue_validated_email,
                                                                                           mock_find_all_emails_of_user_offerers_admins,
                                                                                           app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer)
        mocked_send_email = Mock()

        # When
        send_venue_validation_confirmation_email(venue, mocked_send_email)

        # Then
        mock_make_venue_validated_email.assert_called_once_with(venue)

        mocked_send_email.assert_called_once()
        args = mocked_send_email.call_args
        assert args[1]['data']['To'] == 'admin1@example.com, admin2@example.com'

    @patch('domain.user_emails.find_all_emails_of_user_offerers_admins',
           return_value=['admin1@example.com', 'admin2@example.com'])
    @patch('domain.user_emails.make_venue_validated_email', return_value={'Html-part': ''})
    @patch('utils.mailing.feature_send_mail_to_users_enabled', return_value=False)
    @patch('utils.mailing.DEV_EMAIL_ADDRESS', 'dev@example.com')
    def when_feature_send_mail_to_users_enabled_sends_email_to_pass_culutre_dev(self,
                                                                                mock_feature_send_mail_to_users_enabled,
                                                                                mock_make_venue_validated_email,
                                                                                mock_find_all_emails_of_user_offerers_admins,
                                                                                app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer)
        mocked_send_email = Mock()

        # When
        send_venue_validation_confirmation_email(venue, mocked_send_email)

        # Then
        mock_make_venue_validated_email.assert_called_once_with(venue)

        mocked_send_email.assert_called_once()
        args = mocked_send_email.call_args
        assert args[1]['data']['To'] == 'dev@example.com'


class SendUserValidationEmailTest:
    @patch('domain.user_emails.make_user_validation_email', return_value={'Html-part': ''})
    @patch('utils.mailing.feature_send_mail_to_users_enabled', return_value=True)
    def when_feature_send_mail_to_users_enabled_sends_email_to_user(self,
                                                                    feature_send_mail_to_users_enabled,
                                                                    make_user_validation_email):
        # Given
        user = create_user()
        user.generate_validation_token()
        mocked_send_email = Mock()

        # When
        send_user_validation_email(user, mocked_send_email, 'localhost-test', True)

        # Then
        mocked_send_email.assert_called_once()
        make_user_validation_email.assert_called_once()
        mocked_send_email.call_args[1]['To'] = user.email


class SendActivationEmailTest:
    @patch('domain.user_emails.get_activation_email_data')
    def test_send_activation_email(self, mocked_get_activation_email_data):
        # given
        beneficiary = create_domain_beneficiary()
        mocked_send_email = Mock()
        mocked_get_activation_email_data.return_value = {'Html-part': ''}

        # when
        send_activation_email(beneficiary, mocked_send_email)

        # then
        mocked_get_activation_email_data.assert_called_once_with(user=beneficiary)
        mocked_send_email.assert_called_once_with(data={'Html-part': ''})


class SendAttachmentValidationEmailToProOffererTest:
    @patch('domain.user_emails.retrieve_data_for_offerer_attachment_validation_email')
    @clean_database
    def test_send_attachment_validation_email_to_pro_offerer(self,
                                                             mocked_retrieve_data_for_offerer_attachment_validation_email,
                                                             app):
        # given
        user = create_user()
        offerer = create_offerer()
        user_offerer = create_user_offerer(user, offerer)
        mocked_send_email = Mock()
        mocked_retrieve_data_for_offerer_attachment_validation_email.return_value = {'Html-part': ''}

        # when
        send_attachment_validation_email_to_pro_offerer(user_offerer, mocked_send_email)

        # then
        mocked_retrieve_data_for_offerer_attachment_validation_email.assert_called_once_with(user_offerer=user_offerer)
        mocked_send_email.assert_called_once_with(data={'Html-part': ''})


class SendOngoingOffererAttachmentInformationEmailTest:
    @patch('domain.user_emails.retrieve_data_for_offerer_ongoing_attachment_email',
           return_value={'Mj-TemplateID': 778749})
    @clean_database
    def test_should_return_true_when_email_data_are_valid(self,
                                                          mock_retrieve_data_for_offerer_ongoing_attachment_email,
                                                          app):
        # given
        pro = create_user()
        offerer = create_offerer()
        offerer2 = create_offerer(siren='123456788')
        user_offerer_1 = create_user_offerer(pro, offerer)
        user_offerer_2 = create_user_offerer(pro, offerer2)

        repository.save(user_offerer_1, user_offerer_2)

        mocked_send_email = Mock()

        # when
        send_ongoing_offerer_attachment_information_email_to_pro(user_offerer_2, mocked_send_email)

        # then
        mock_retrieve_data_for_offerer_ongoing_attachment_email.assert_called_once_with(user_offerer_2)
        mocked_send_email.assert_called_once_with(data={'Mj-TemplateID': 778749})


class SendResetPasswordProEmailTest:
    @patch('domain.user_emails.retrieve_data_for_reset_password_pro_email',
           return_value={'MJ-TemplateID': 779295})
    def when_feature_send_emails_enabled_sends_a_reset_password_email_to_pro_user(self,
                                                                                  mock_retrieve_data_for_reset_password_pro_email,
                                                                                  app):
        # given
        user = create_user(email='pro@example.com', reset_password_token='AZ45KNB99H')
        mocked_send_email = Mock()

        # when
        send_reset_password_email_to_pro(user, mocked_send_email)

        # then
        mock_retrieve_data_for_reset_password_pro_email.assert_called_once_with(user)
        mocked_send_email.assert_called_once_with(data={'MJ-TemplateID': 779295})


class SendResetPasswordUserEmailTest:
    @patch('domain.user_emails.retrieve_data_for_reset_password_user_email',
           return_value={'MJ-TemplateID': 912168})
    def when_feature_send_emails_enabled_sends_a_reset_password_email_to_user(self,
                                                                              mock_retrieve_data_for_reset_password_user_email,
                                                                              app):
        # given
        user = create_user(email='bobby@example.com', first_name='Bobby', reset_password_token='AZ45KNB99H')
        mocked_send_email = Mock()

        # when
        send_reset_password_email_to_user(user, mocked_send_email)

        # then
        mock_retrieve_data_for_reset_password_user_email.assert_called_once_with(user)
        mocked_send_email.assert_called_once_with(data={'MJ-TemplateID': 912168})


class SendRejectionEmailToBeneficiaryPreSubscriptionTest:
    @patch('domain.user_emails.make_dupplicate_beneficiary_pre_subscription_rejected_data',
           return_value={'MJ-TemplateID': 1530996})
    def when_beneficiary_is_a_dupplicate_sends_correct_template(self,
                                                                mocked_make_data,
                                                                app):
        # given
        beneficiary_pre_subscription = create_domain_beneficiary_pre_subcription()
        mocked_send_email = Mock()
        error = BeneficiaryIsADupplicate("Dupplicate")

        # when
        send_rejection_email_to_beneficiary_pre_subscription(beneficiary_pre_subscription, error, mocked_send_email)

        # then
        mocked_make_data.assert_called_once_with(beneficiary_pre_subscription)
        mocked_send_email.assert_called_once_with(data={'MJ-TemplateID': 1530996})


class SendRejectionEmailToBeneficiaryPreSubscriptionTest:
    @patch('domain.user_emails.make_not_eligible_beneficiary_pre_subscription_rejected_data',
           return_value={'MJ-TemplateID': 1619528})
    def when_beneficiary_is_not_eligible_sends_correct_template(self,
                                                                mocked_make_data,
                                                                app):
        # given
        beneficiary_pre_subscription = create_domain_beneficiary_pre_subcription()
        mocked_send_email = Mock()
        error = BeneficiaryIsNotEligible("Dupplicate")

        # when
        send_rejection_email_to_beneficiary_pre_subscription(beneficiary_pre_subscription, error, mocked_send_email)

        # then
        mocked_make_data.assert_called_once_with(beneficiary_pre_subscription)
        mocked_send_email.assert_called_once_with(data={'MJ-TemplateID': 1619528})
