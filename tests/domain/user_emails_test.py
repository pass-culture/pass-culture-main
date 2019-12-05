from unittest.mock import patch, Mock, call

from domain.user_emails import send_beneficiary_booking_cancellation_email, \
    send_warning_to_beneficiary_after_pro_booking_cancellation, \
    send_offerer_driven_cancellation_email_to_offerer, \
    send_booking_confirmation_email_to_user, send_booking_recap_emails, send_final_booking_recap_email, \
    send_validation_confirmation_email, send_batch_cancellation_emails_to_users, \
    send_batch_cancellation_email_to_offerer, send_user_validation_email, send_venue_validation_confirmation_email, \
    send_reset_password_email_with_mailjet_template, send_activation_email, send_reset_password_email
from models import Offerer, UserOfferer, User, RightsType
from tests.test_utils import create_user, create_booking, create_stock_with_event_offer, create_offerer, create_venue, \
    create_offer_with_thing_product, create_stock_with_thing_offer, create_mocked_bookings, create_mediation, \
    create_recommendation, create_stock_from_offer


class SendResetPasswordEmailTest:
    @patch('utils.mailing.feature_send_mail_to_users_enabled', return_value=True)
    def when_feature_send_emails_enabled_sends_a_reset_password_email_to_user(self,
                                                                              feature_send_mail_to_users_enabled,
                                                                              app):
        # given
        user = create_user(public_name='bobby', email='bobby@test.com', reset_password_token='AZ45KNB99H')
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
    def when_feature_send_emails_disabled_sends_email_to_pass_culture_dev(self, feature_send_mail_to_users_enabled, app):
        # given
        user = create_user(public_name='bobby', email='bobby@test.com', reset_password_token='AZ45KNB99H')
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
    @patch('emails.beneficiary_booking_cancellation.SUPPORT_EMAIL_ADDRESS', 'support@example.com')
    def test_should_called_mocked_send_email_with_valid_data(self):
        # given
        beneficiary = create_user(first_name='Fabien', email='fabien@example.com')
        thing_offer = create_offer_with_thing_product(venue=None, thing_name='Test thing name', idx=123456)
        mediation = create_mediation(offer=thing_offer)
        mediation.id = 36
        recommendation = create_recommendation(offer=thing_offer, user=beneficiary, mediation=mediation)
        stock = create_stock_from_offer(offer=thing_offer, price=10)
        booking = create_booking(beneficiary, stock=stock, recommendation=recommendation, is_cancelled=1)
        mocked_send_email = Mock()

        # when
        send_beneficiary_booking_cancellation_email(booking, mocked_send_email)

        # then
        mocked_send_email.assert_called_once()
        args, kwargs = mocked_send_email.call_args
        assert kwargs['data'] == {
            'FromEmail': 'support@example.com',
            'Mj-TemplateID': 1091464,
            'Mj-TemplateLanguage': True,
            'To': 'fabien@example.com',
            'Vars': {
                'env': '-development',
                'event_date': '',
                'event_hour': '',
                'is_event': 0,
                'is_free_offer': '0',
                'mediation_id': '',
                'offer_id': 123456,
                'offer_name': 'Test thing name',
                'offer_price': '10',
                'user_first_name': 'Fabien',
            }
        }


class SendWarningToBeneficiaryAfterProBookingCancellationTest:
    @patch('emails.beneficiary_warning_after_pro_booking_cancellation.SUPPORT_EMAIL_ADDRESS', 'support@example.com')
    @patch('emails.beneficiary_warning_after_pro_booking_cancellation.DEV_EMAIL_ADDRESS', 'dev@example.com')
    def test_should_sends_email_to_beneficiary_when_pro_cancels_booking(self):
        # Given
        user = create_user(email='user@example.com')
        booking = create_booking(user)
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
                'is_free_offer': '1',
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
    @patch('utils.mailing.feature_send_mail_to_users_enabled',return_value=True)
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
        booking = create_booking(user, stock)
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
        booking = create_booking(user, stock)
        mocked_send_email = Mock()

        # When
        send_offerer_driven_cancellation_email_to_offerer(booking, mocked_send_email)

        # Then
        make_offerer_driven_cancellation_email_for_offerer.assert_called_once_with(booking)
        mocked_send_email.assert_called_once()
        args = mocked_send_email.call_args
        assert args[1]['data']['To'] == 'administration@passculture.app'


class SendBookingConfirmationEmailToUserTest:
    def when_called_calls_send_email(self):
        # Given
        user_email = 'test@email.com'
        user = create_user('Test', departement_code='93', email=user_email, can_book_free_offers=True)
        booking = create_booking(user)

        mocked_send_email = Mock()

        with patch('domain.user_emails.retrieve_data_for_user_booking_confirmation_email',
                   return_value={'To': user_email}) as email_data_retrieval:

            # When
            send_booking_confirmation_email_to_user(booking, mocked_send_email)

        # Then
        email_data_retrieval.assert_called_once_with(booking, [user_email])
        mocked_send_email.assert_called_once_with(data={'To': user_email})


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
        booking = create_booking(user, stock)
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
        stock = create_stock_with_thing_offer(offerer, venue, offer, booking_email='offer.booking.email@example.net')
        booking = create_booking(user, stock)
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
        booking = create_booking(user, stock)
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
    @patch('domain.user_emails.find_all_emails_of_user_offerers_admins', return_value=['admin1@example.com', 'admin2@example.com'])
    @patch('domain.user_emails.make_validation_confirmation_email', return_value={'Html-part': ''})
    @patch('utils.mailing.feature_send_mail_to_users_enabled', return_value=True)
    def when_feature_send_mail_to_users_enabled_sends_email_to_all_users_linked_to_offerer(self,
                                                                                           feature_send_mail_to_users_enabled,
                                                                                           make_validation_confirmation_email,
                                                                                           find_all_emails_of_user_offerers_admins):
        # Given
        offerer = Offerer()
        user_offerer = UserOfferer()
        user_offerer.rights = RightsType.editor
        user_offerer.user = User(email='test@example.com')
        mocked_send_email = Mock()

        # When
        send_validation_confirmation_email(user_offerer, offerer, mocked_send_email)

        # Then
        make_validation_confirmation_email.assert_called_once_with(user_offerer, offerer)

        mocked_send_email.assert_called_once()
        args = mocked_send_email.call_args
        assert args[1]['data']['To'] == 'admin1@example.com, admin2@example.com'


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


class SendBatchCancellationEmailToOffererTest:
    @patch('domain.user_emails.make_batch_cancellation_email', return_value={'Html-part': ''})
    @patch('utils.mailing.feature_send_mail_to_users_enabled', return_value=True)
    def when_feature_send_mail_to_users_enabled_and_offer_booking_email_sends_to_offerer_and_administration_stock_case(
            self, feature_send_mail_to_users_enabled, make_batch_cancellation_email):
        # Given
        num_bookings = 5
        bookings = create_mocked_bookings(num_bookings, 'offerer@example.com')
        mocked_send_email = Mock()

        # When
        send_batch_cancellation_email_to_offerer(bookings, 'stock', mocked_send_email)

        # Then
        make_batch_cancellation_email.assert_called_once_with(bookings, 'stock')

        mocked_send_email.assert_called_once()
        args = mocked_send_email.call_args
        assert args[1]['data']['To'] == 'offerer@example.com, administration@passculture.app'

    @patch('domain.user_emails.make_batch_cancellation_email', return_value={'Html-part': ''})
    @patch('utils.mailing.feature_send_mail_to_users_enabled', return_value=True)
    def when_feature_send_mail_to_users_enabled_and_offer_booking_email_sends_to_offerer_and_administration_event_occurrence_case(
            self, feature_send_mail_to_users_enabled, make_batch_cancellation_email):
        # Given
        num_bookings = 5
        bookings = create_mocked_bookings(num_bookings, 'offerer@example.com')
        mocked_send_email = Mock()

        # When
        send_batch_cancellation_email_to_offerer(bookings, 'event_occurrence', mocked_send_email)

        # Then
        make_batch_cancellation_email.assert_called_once_with(bookings, 'event_occurrence')

        mocked_send_email.assert_called_once()
        args = mocked_send_email.call_args
        assert args[1]['data']['To'] == 'offerer@example.com, administration@passculture.app'

    @patch('domain.user_emails.make_batch_cancellation_email', return_value={'Html-part': ''})
    @patch('utils.mailing.feature_send_mail_to_users_enabled', return_value=False)
    def when_feature_send_mail_to_users_disabled_sends_email_to_pass_culture_dev(self,
                                                                                 feature_send_mail_to_users_enabled,
                                                                                 make_batch_cancellation_email):
        # Given
        num_bookings = 5
        bookings = create_mocked_bookings(num_bookings, 'offerer@example.com')
        mocked_send_email = Mock()

        # When
        send_batch_cancellation_email_to_offerer(bookings, 'stock', mocked_send_email)

        # Then
        mocked_send_email.assert_called_once()
        args = mocked_send_email.call_args
        assert args[1]['data']['To'] == 'dev@passculture.app'
        assert 'This is a test' in args[1]['data']['Html-part']

    @patch('domain.user_emails.make_batch_cancellation_email', return_value={'Html-part': ''})
    @patch('utils.mailing.feature_send_mail_to_users_enabled',return_value=True)
    def when_feature_send_mail_to_users_enabled_and_not_offer_booking_email_sends_only_to_administration(self,
                                                                                                         feature_send_mail_to_users_enabled,
                                                                                                         make_batch_cancellation_email):
        # Given
        num_bookings = 5
        bookings = create_mocked_bookings(num_bookings, None)
        mocked_send_email = Mock()

        # When
        send_batch_cancellation_email_to_offerer(bookings, 'event_occurrence', mocked_send_email)

        # Then
        make_batch_cancellation_email.assert_called_once_with(bookings, 'event_occurrence')

        mocked_send_email.assert_called_once()
        args = mocked_send_email.call_args
        assert args[1]['data']['To'] == 'administration@passculture.app'


class SendVenueValidationConfirmationEmailTest:
    @patch('domain.user_emails.find_all_emails_of_user_offerers_admins', return_value=['admin1@example.com', 'admin2@example.com'])
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

    @patch('domain.user_emails.find_all_emails_of_user_offerers_admins', return_value=['admin1@example.com', 'admin2@example.com'])
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
        user = create_user(public_name='bobby', email='bobby@example.net', reset_password_token='AZ45KNB99H')
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
        user = create_user(public_name='bobby', email='bobby@example.net', reset_password_token='AZ45KNB99H')
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
        user = create_user(public_name='bobby', email='bobby@example.net', reset_password_token='AZ45KNB99H')
        mocked_send_email = Mock(return_value=True)

        # when
        activation_email = send_activation_email(user, mocked_send_email)

        # then
        assert activation_email is True

    def test_should_return_false_when_email_data_are_not_valid(self):
        # given
        user = create_user(public_name='bobby', email='bobby@example.net', reset_password_token='AZ45KNB99H')
        mocked_send_email = Mock(return_value=False)

        # when
        activation_email = send_activation_email(user, mocked_send_email)

        # then
        assert activation_email is False
