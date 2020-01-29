from unittest.mock import patch, Mock, call

from domain.user_emails import send_beneficiary_booking_cancellation_email, \
    send_warning_to_beneficiary_after_pro_booking_cancellation, \
    send_offerer_driven_cancellation_email_to_offerer, \
    send_booking_confirmation_email_to_beneficiary, send_booking_recap_emails, send_final_booking_recap_email, \
    send_validation_confirmation_email_to_pro, send_batch_cancellation_emails_to_users, \
    send_offerer_bookings_recap_email_after_offerer_cancellation, send_user_validation_email, \
    send_venue_validation_confirmation_email, \
    send_reset_password_email_with_mailjet_template, send_activation_email, send_reset_password_email, \
    send_attachment_validation_email_to_pro_offerer, send_ongoing_offerer_attachment_information_email_to_pro

from repository import repository
from models import Offerer
from tests.model_creators.generic_creators import create_booking, create_user, create_offerer, create_venue, create_user_offerer
from tests.model_creators.specific_creators import create_stock_with_event_offer, create_stock_with_thing_offer, \
    create_offer_with_thing_product
from tests.test_utils import create_mocked_bookings
from tests.conftest import clean_database


class SendResetPasswordEmailTest:
    @patch('utils.mailing.feature_send_mail_to_users_enabled', return_value=True)
    def when_feature_send_emails_enabled_sends_a_reset_password_email_to_user(self,
                                                                              feature_send_mail_to_users_enabled,
                                                                              app):
        # given
        user = create_user(email='bobby@test.com', public_name='bobby', reset_password_token='AZ45KNB99H')
        mocked_send_email = Mock()

        # when
        send_reset_password_email(user, mocked_send_email, 'localhost')

        # then
        mocked_send_email.assert_called_once()
        args = mocked_send_email.call_args
        data = args[1]['data']
        assert data['FromName'] == 'pass Culture'
        assert data['FromEmail'] == 'support@passculture.app'
        assert data['Subject'] == 'Réinitialisation de votre mot de passe'
        assert data['To'] == 'bobby@test.com'

    @patch('utils.mailing.feature_send_mail_to_users_enabled', return_value=False)
    def when_feature_send_emails_disabled_sends_email_to_pass_culture_dev(self, feature_send_mail_to_users_enabled,
                                                                          app):
        # given
        user = create_user(email='bobby@test.com', public_name='bobby', reset_password_token='AZ45KNB99H')
        mocked_send_email = Mock()

        # when
        send_reset_password_email(user, mocked_send_email, 'localhost')

        # then
        mocked_send_email.assert_called_once()
        args = mocked_send_email.call_args
        email = args[1]['data']
        assert email['To'] == 'dev@passculture.app'
        assert 'This is a test' in email['Html-part']


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


class SendWarningToBeneficiaryAfterProBookingCancellationTest:
    @patch('emails.beneficiary_warning_after_pro_booking_cancellation.SUPPORT_EMAIL_ADDRESS', 'support@example.com')
    @patch('emails.beneficiary_warning_after_pro_booking_cancellation.DEV_EMAIL_ADDRESS', 'dev@example.com')
    def test_should_sends_email_to_beneficiary_when_pro_cancels_booking(self):
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
            'To': 'dev@example.com',
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


class SendOffererDrivenCancellationEmailToOffererTest:
    @patch('domain.user_emails.make_offerer_driven_cancellation_email_for_offerer', return_value={'Html-part': ''})
    @patch('utils.mailing.feature_send_mail_to_users_enabled', return_value=True)
    def when_feature_send_mail_to_users_enabled_and_offer_booking_email_sends_to_offerer_and_administration(self,
                                                                                                            feature_send_mail_to_users_enabled,
                                                                                                            make_offerer_driven_cancellation_email_for_offerer):
        # Given
        user = create_user(email='user@example.com')
        offerer = create_offerer()
        venue = create_venue(offerer)
        venue.bookingEmail = 'booking@example.com'
        stock = create_stock_with_event_offer(offerer, venue)
        stock.resolvedOffer.bookingEmail = 'offer@example.com'
        booking = create_booking(user=user, stock=stock)
        mocked_send_email = Mock()

        # When
        send_offerer_driven_cancellation_email_to_offerer(booking, mocked_send_email)

        # Then
        make_offerer_driven_cancellation_email_for_offerer.assert_called_once_with(booking)
        mocked_send_email.assert_called_once()
        args = mocked_send_email.call_args
        assert args[1]['data']['To'] == 'offer@example.com, administration@passculture.app'

    @patch('domain.user_emails.make_offerer_driven_cancellation_email_for_offerer', return_value={'Html-part': ''})
    @patch('utils.mailing.feature_send_mail_to_users_enabled', return_value=True)
    def when_feature_send_mail_to_users_enabled_and_not_offer_booking_email_sends_only_to_administration(self,
                                                                                                         feature_send_mail_to_users_enabled,
                                                                                                         make_offerer_driven_cancellation_email_for_offerer):
        # Given
        user = create_user(email='user@example.com')
        offerer = create_offerer()
        venue = create_venue(offerer)
        stock = create_stock_with_event_offer(offerer, venue)
        stock.resolvedOffer.bookingEmail = None
        booking = create_booking(user=user, stock=stock)
        mocked_send_email = Mock()

        # When
        send_offerer_driven_cancellation_email_to_offerer(booking, mocked_send_email)

        # Then
        make_offerer_driven_cancellation_email_for_offerer.assert_called_once_with(booking)
        mocked_send_email.assert_called_once()
        args = mocked_send_email.call_args
        assert args[1]['data']['To'] == 'administration@passculture.app'


class SendBookingConfirmationEmailToBeneficiaryTest:
    @patch('domain.user_emails.retrieve_data_for_beneficiary_booking_confirmation_email',
           return_value={'MJ-TemplateID': 1163067})
    def when_called_calls_send_email(self, mocked_retrieve_data_for_beneficiary_booking_confirmation_email):
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
    @patch('utils.mailing.feature_send_mail_to_users_enabled', return_value=False)
    def when_feature_send_mail_to_users_disabled_sends_email_to_pass_culture_dev(self,
                                                                                 feature_send_mail_to_users_enabled):
        # given
        user = create_user()
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue, booking_email='offer.booking.email@example.net')
        stock = create_stock_with_thing_offer(offerer, venue, offer)
        booking = create_booking(user=user, stock=stock)
        mocked_send_email = Mock()

        # when
        send_booking_recap_emails(booking, mocked_send_email)

        # then
        mocked_send_email.assert_called_once()
        args = mocked_send_email.call_args
        data = args[1]['data']
        assert data['To'] == 'dev@passculture.app'

    @patch('utils.mailing.feature_send_mail_to_users_enabled', return_value=True)
    def when_feature_send_mail_to_users_enabled_and_offer_booking_email_sends_to_offerer_and_administration(self,
                                                                                                            feature_send_mail_to_users_enabled):
        # given
        user = create_user()
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue, booking_email='offer.booking.email@example.net')
        stock = create_stock_with_thing_offer(offerer, venue, offer,
                                              booking_email='offer.booking.email@example.net')
        booking = create_booking(user=user, stock=stock)
        mocked_send_email = Mock()

        # when
        send_booking_recap_emails(booking, mocked_send_email)

        # then
        mocked_send_email.assert_called_once()
        args = mocked_send_email.call_args
        data = args[1]['data']
        assert data['To'] == 'administration@passculture.app, offer.booking.email@example.net'

    @patch('utils.mailing.feature_send_mail_to_users_enabled', return_value=True)
    def when_feature_send_mail_to_users_enabled_and_not_offer_booking_email_sends_only_to_administration(
            self, feature_send_mail_to_users_enabled):
        # given
        user = create_user()
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue, booking_email=None)
        stock = create_stock_with_thing_offer(offerer, venue, offer, booking_email=None)
        booking = create_booking(user=user, stock=stock)
        mocked_send_email = Mock()

        # when
        send_booking_recap_emails(booking, mocked_send_email)

        # then
        mocked_send_email.assert_called_once()
        args = mocked_send_email.call_args
        data = args[1]['data']
        assert data['To'] == 'administration@passculture.app'


class SendFinalBookingRecapEmailTest:
    @patch('domain.user_emails.set_booking_recap_sent_and_save')
    @patch('utils.mailing.feature_send_mail_to_users_enabled', return_value=False)
    def when_feature_send_mail_to_users_disabled_sends_email_to_pass_culture_dev(self,
                                                                                 feature_send_mail_to_users_enabled,
                                                                                 set_booking_recap_sent_and_save):
        # given
        offerer = create_offerer()
        venue = create_venue(offerer)
        stock = create_stock_with_event_offer(offerer, venue, booking_email='offer.booking.email@example.net')
        mocked_send_email = Mock()

        # when
        send_final_booking_recap_email(stock, mocked_send_email)

        # then
        mocked_send_email.assert_called_once()
        args = mocked_send_email.call_args
        assert args[1]['data']['To'] == 'dev@passculture.app'
        set_booking_recap_sent_and_save.assert_called_once_with(stock)

    @patch('domain.user_emails.set_booking_recap_sent_and_save')
    @patch('utils.mailing.feature_send_mail_to_users_enabled', return_value=True)
    def when_feature_send_mail_to_users_enabled_and_offer_booking_email_sends_to_offerer_and_support(self,
                                                                                                     feature_send_mail_to_users_enabled,
                                                                                                     set_booking_recap_sent_and_save):
        # given
        offerer = create_offerer()
        venue = create_venue(offerer)
        stock = create_stock_with_event_offer(offerer, venue, booking_email='offer.booking.email@example.net')
        mocked_send_email = Mock()

        # when
        send_final_booking_recap_email(stock, mocked_send_email)

        # then
        mocked_send_email.assert_called_once()
        args = mocked_send_email.call_args
        assert 'offer.booking.email@example.net' in args[1]['data']['To']
        assert 'administration@passculture.app' in args[1]['data']['To']
        set_booking_recap_sent_and_save.assert_called_once_with(stock)

    @patch('domain.user_emails.set_booking_recap_sent_and_save')
    @patch('utils.mailing.feature_send_mail_to_users_enabled', return_value=True)
    def when_feature_send_mail_to_users_enabled_and_not_offer_booking_email_sends_only_to_administration(
            self, feature_send_mail_to_users_enabled, set_booking_recap_sent_and_save):
        # given
        offerer = create_offerer()
        venue = create_venue(offerer)
        stock = create_stock_with_event_offer(offerer, venue, booking_email=None)
        mocked_send_email = Mock()

        # when
        send_final_booking_recap_email(stock, mocked_send_email)

        # then
        mocked_send_email.assert_called_once()
        args = mocked_send_email.call_args
        assert args[1]['data']['To'] == 'administration@passculture.app'
        set_booking_recap_sent_and_save.assert_called_once_with(stock)


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
                                                                                           send_warning_to_beneficiary_after_pro_booking_cancellation):
        # Given
        mocked_send_email = Mock()
        num_bookings = 6
        bookings = create_mocked_bookings(num_bookings, 'offerer@example.com')
        calls = [call(booking, mocked_send_email) for booking in bookings]

        # When
        send_batch_cancellation_emails_to_users(bookings, mocked_send_email)

        # Then
        send_warning_to_beneficiary_after_pro_booking_cancellation.assert_has_calls(calls)


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
                                                                                           feature_send_mail_to_users_enabled,
                                                                                           make_venue_validated_email,
                                                                                           find_all_emails_of_user_offerers_admins):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer)
        mocked_send_email = Mock()

        # When
        send_venue_validation_confirmation_email(venue, mocked_send_email)

        # Then
        make_venue_validated_email.assert_called_once_with(venue)

        mocked_send_email.assert_called_once()
        args = mocked_send_email.call_args
        assert args[1]['data']['To'] == 'admin1@example.com, admin2@example.com'

    @patch('domain.user_emails.find_all_emails_of_user_offerers_admins',
           return_value=['admin1@example.com', 'admin2@example.com'])
    @patch('domain.user_emails.make_venue_validated_email', return_value={'Html-part': ''})
    @patch('utils.mailing.feature_send_mail_to_users_enabled', return_value=False)
    def when_feature_send_mail_to_users_enabled_sends_email_to_pass_culutre_dev(self,
                                                                                feature_send_mail_to_users_enabled,
                                                                                make_venue_validated_email,
                                                                                find_all_emails_of_user_offerers_admins):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer)
        mocked_send_email = Mock()

        # When
        send_venue_validation_confirmation_email(venue, mocked_send_email)

        # Then
        make_venue_validated_email.assert_called_once_with(venue)

        mocked_send_email.assert_called_once()
        args = mocked_send_email.call_args
        assert args[1]['data']['To'] == 'dev@passculture.app'


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


class SendResetPasswordEmailWithMailjetTemplateTest:
    @patch('emails.user_reset_password.feature_send_mail_to_users_enabled', return_value=True)
    def when_feature_send_emails_enabled_sends_a_reset_password_email_to_user(self,
                                                                              feature_send_mail_to_users_enabled):
        # given
        user = create_user(email='bobby@example.net', public_name='bobby', reset_password_token='AZ45KNB99H')
        mocked_send_email = Mock()

        # when
        send_reset_password_email_with_mailjet_template(user, mocked_send_email)

        # then
        mocked_send_email.assert_called_once()
        args = mocked_send_email.call_args
        data = args[1]['data']
        assert data['FromEmail'] == 'support@passculture.app'
        assert data['To'] == 'bobby@example.net'

    @patch('emails.user_reset_password.feature_send_mail_to_users_enabled', return_value=False)
    def when_feature_send_emails_disabled_sends_email_to_pass_culture_dev(self,
                                                                          feature_send_mail_to_users_enabled):
        # given
        user = create_user(email='bobby@example.net', public_name='bobby', reset_password_token='AZ45KNB99H')
        mocked_send_email = Mock()

        # when
        send_reset_password_email_with_mailjet_template(user, mocked_send_email)

        # then
        mocked_send_email.assert_called_once()
        args = mocked_send_email.call_args
        email = args[1]['data']
        assert email['To'] == 'dev@passculture.app'


class SendActivationEmailTest:
    def test_should_return_true_when_email_data_are_valid(self):
        # given
        user = create_user(email='bobby@example.net', public_name='bobby', reset_password_token='AZ45KNB99H',
                           first_name='John')
        mocked_send_email = Mock(return_value=True)

        # when
        activation_email = send_activation_email(user, mocked_send_email)

        # then
        assert activation_email is True

    def test_should_return_false_when_email_data_are_not_valid(self):
        # given
        user = create_user(email='bobby@example.net', public_name='bobby', reset_password_token='AZ45KNB99H',
                           first_name='John')
        mocked_send_email = Mock(return_value=False)

        # when
        activation_email = send_activation_email(user, mocked_send_email)

        # then
        assert activation_email is False


class SendAttachmentValidationEmailToProOffererTest:
    @patch('emails.offerer_attachment_validation.feature_send_mail_to_users_enabled', return_value=True)
    @patch('emails.offerer_attachment_validation.format_environment_for_email', return_value='')
    @patch('emails.offerer_attachment_validation.find_user_offerer_email',
           return_value='pro@example.com')
    @patch('emails.offerer_attachment_validation.SUPPORT_EMAIL_ADDRESS', 'support@passculture.app')
    @clean_database
    def test_should_return_true_when_email_data_are_valid(self,
                                                          feature_send_mail_to_users_enabled,
                                                          format_environment_for_email,
                                                          find_user_offerer_email,
                                                          app):

        # given
        user = create_user(email='pro@example.com')
        offerer = create_offerer()
        user_offerer = create_user_offerer(user, offerer)

        repository.save(user_offerer)

        mocked_send_email = Mock(return_value=True)

        # when
        attachment_validation_email = send_attachment_validation_email_to_pro_offerer(user_offerer, mocked_send_email)


        # then
        assert attachment_validation_email is True
        mocked_send_email.assert_called_once()
        args = mocked_send_email.call_args
        data = args[1]['data']
        assert data['MJ-TemplateID'] == 778756
        assert data['FromEmail'] == 'support@passculture.app'
        assert data['To'] == 'pro@example.com'
        assert data['Vars']['nom_structure'] == 'Test Offerer'


    @clean_database
    def test_should_return_false_when_email_data_are_not_valid(self):
        # given
        user = create_user(email='bobby@example.net')
        offerer = create_offerer()
        user_offerer = create_user_offerer(user, offerer)

        repository.save(offerer, user_offerer)

        mocked_send_email = Mock(return_value=False)

        # when
        attachment_validation_email = send_attachment_validation_email_to_pro_offerer(user_offerer, mocked_send_email)

        # then
        assert attachment_validation_email is False


class SendOngoingOffererAttachmentInformationEmailTest:
    @patch('emails.offerer_ongoing_attachment.feature_send_mail_to_users_enabled', return_value=True)
    @patch('emails.offerer_ongoing_attachment.format_environment_for_email', return_value='')
    @patch('emails.offerer_ongoing_attachment.find_user_offerer_email',
           return_value='pro@example.com')
    @patch('emails.offerer_ongoing_attachment.SUPPORT_EMAIL_ADDRESS', 'support@passculture.app')
    @clean_database
    def test_should_return_true_when_email_data_are_valid(self,
                                                          feature_send_mail_to_users_enabled,
                                                          format_environment_for_email,
                                                          find_user_offerer_email,
                                                          app):

        # given
        user = create_user(email='pro@example.com')
        offerer = create_offerer()
        offerer2 = create_offerer(siren='123456788')
        user_offerer_1 = create_user_offerer(user, offerer)
        user_offerer_2 = create_user_offerer(user, offerer2)

        repository.save(offerer, offerer2, user_offerer_1, user_offerer_2)

        mocked_send_email = Mock(return_value=True)

        # when
        ongoing_attachment_email = send_ongoing_offerer_attachment_information_email_to_pro(user_offerer_2, mocked_send_email)

        # then
        assert ongoing_attachment_email is True
        mocked_send_email.assert_called_once()
        args = mocked_send_email.call_args
        data = args[1]['data']
        assert data['MJ-TemplateID'] == 778749
        assert data['FromEmail'] == 'support@passculture.app'
        assert data['To'] == 'pro@example.com'
        assert data['Vars']['nom_structure'] == 'Test Offerer'

    @clean_database
    def test_should_return_false_when_email_data_are_not_valid(self):
        # given
        user = create_user(email='pro@example.com')
        offerer = create_offerer()
        user_offerer = create_user_offerer(user, offerer)

        repository.save(offerer, user_offerer)

        mocked_send_email = Mock(return_value=False)

        # when
        ongoing_attachment_email = send_ongoing_offerer_attachment_information_email_to_pro(user_offerer, mocked_send_email)

        # then
        assert ongoing_attachment_email is False

