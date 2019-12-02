from unittest.mock import patch, Mock, call

from domain.user_emails import send_user_driven_cancellation_email_to_user, \
    send_user_driven_cancellation_email_to_offerer, send_offerer_driven_cancellation_email_to_user, \
    send_offerer_driven_cancellation_email_to_offerer, \
    send_booking_confirmation_email_to_user, send_booking_recap_emails, send_final_booking_recap_email, \
    send_validation_confirmation_email, send_batch_cancellation_emails_to_users, \
    send_batch_cancellation_email_to_offerer, send_user_validation_email, send_venue_validation_confirmation_email, \
    send_reset_password_email_with_mailjet_template, send_activation_email, \
    send_pro_user_waiting_for_validation_by_admin_email, send_reset_password_email
from models import Offerer, UserOfferer, User, RightsType
from tests.test_utils import create_user, create_booking, create_stock_with_event_offer, create_offerer, create_venue, \
    create_offer_with_thing_product, create_stock_with_thing_offer, create_mocked_bookings


class SendResetPasswordEmailTest:
    def when_feature_send_emails_enabled_sends_a_reset_password_email_to_user(self, app):
        # given
        user = create_user(public_name='bobby', email='bobby@test.com', reset_password_token='AZ45KNB99H')
        mocked_send_email = Mock()
        return_value = Mock()
        return_value.status_code = 200
        mocked_send_email.return_value = return_value

        # when
        with patch('utils.mailing.feature_send_mail_to_users_enabled', return_value=True):
            send_reset_password_email(user, mocked_send_email, 'localhost')

        # then
        mocked_send_email.assert_called_once()
        args = mocked_send_email.call_args
        data = args[1]['data']
        assert data['FromName'] == 'pass Culture'
        assert data['FromEmail'] == 'support@passculture.app'
        assert data['Subject'] == 'Réinitialisation de votre mot de passe'
        assert data['To'] == 'bobby@test.com'

    def when_feature_send_emails_disabled_sends_email_to_pass_culture_dev(self, app):
        # given
        user = create_user(public_name='bobby', email='bobby@test.com', reset_password_token='AZ45KNB99H')
        mocked_send_email = Mock()
        return_value = Mock()
        return_value.status_code = 200
        mocked_send_email.return_value = return_value

        # when
        with patch('utils.mailing.feature_send_mail_to_users_enabled', return_value=False):
            send_reset_password_email(user, mocked_send_email, 'localhost')

        # then
        mocked_send_email.assert_called_once()
        args = mocked_send_email.call_args
        email = args[1]['data']
        assert email['To'] == 'dev@passculture.app'
        assert 'This is a test' in email['Html-part']


class SendUserDrivenCancellationEmailToUserTest:
    def when_feature_send_mail_to_users_enabled_sends_email_to_user(self):
        # Given
        user = create_user(email='user@email.fr')
        booking = create_booking(user)
        mocked_send_email = Mock()
        return_value = Mock()
        return_value.status_code = 200
        mocked_send_email.return_value = return_value

        with patch('utils.mailing.feature_send_mail_to_users_enabled', return_value=True), patch(
                'domain.user_emails.make_user_booking_recap_email',
                return_value={'Html-part': ''}) as make_user_recap_email:
            # When
            send_user_driven_cancellation_email_to_user(booking, mocked_send_email)

            # Then
            make_user_recap_email.assert_called_once_with(booking, is_cancellation=True)
        mocked_send_email.assert_called_once()
        args = mocked_send_email.call_args
        assert args[1]['data']['To'] == 'user@email.fr'

    def when_feature_send_mail_to_users_disabled_sends_email_to_pass_culture_dev(self, app):
        # Given
        user = create_user(email='user@email.fr')
        booking = create_booking(user)
        mocked_send_email = Mock()
        return_value = Mock()
        return_value.status_code = 200
        mocked_send_email.return_value = return_value

        with patch('utils.mailing.feature_send_mail_to_users_enabled', return_value=False), patch(
                'domain.user_emails.make_user_booking_recap_email',
                return_value={'Html-part': ''}) as make_user_recap_email:
            # When
            send_user_driven_cancellation_email_to_user(booking, mocked_send_email)

            # Then
            make_user_recap_email.assert_called_once_with(booking, is_cancellation=True)
        mocked_send_email.assert_called_once()
        args = mocked_send_email.call_args
        assert args[1]['data']['To'] == 'dev@passculture.app'
        assert 'This is a test' in args[1]['data']['Html-part']


class SendUserDrivenCancellationEmailToOffererTest:

    def when_feature_send_mail_to_users_enabled_and_offer_booking_email_sends_to_offerer_and_administration(self, app):
        # Given
        user = create_user(email='user@email.fr')
        offerer = create_offerer()
        venue = create_venue(offerer)
        stock = create_stock_with_event_offer(offerer, venue)
        stock.resolvedOffer.bookingEmail = 'offer@email.fr'
        booking = create_booking(user, stock, venue)
        mocked_send_email = Mock()
        return_value = Mock()
        return_value.status_code = 200
        mocked_send_email.return_value = return_value

        with patch('utils.mailing.feature_send_mail_to_users_enabled', return_value=True), patch(
                'domain.user_emails.make_offerer_booking_recap_email_after_user_action',
                return_value={'Html-part': ''}) as make_offerer_recap_email:
            # When
            send_user_driven_cancellation_email_to_offerer(booking, mocked_send_email)

            # Then
            make_offerer_recap_email.assert_called_once_with(booking, is_cancellation=True)
        mocked_send_email.assert_called_once()
        args = mocked_send_email.call_args
        assert args[1]['data']['To'] == 'offer@email.fr, administration@passculture.app'

    def when_feature_send_mail_to_users_enabled_and_not_offer_booking_email_sends_only_to_administration(self, app):
        # Given
        user = create_user(email='user@email.fr')
        offerer = create_offerer()
        venue = create_venue(offerer)
        stock = create_stock_with_event_offer(offerer, venue)
        stock.resolvedOffer.bookingEmail = None
        booking = create_booking(user, stock, venue)
        mocked_send_email = Mock()
        return_value = Mock()
        return_value.status_code = 200
        mocked_send_email.return_value = return_value

        with patch('utils.mailing.feature_send_mail_to_users_enabled', return_value=True), patch(
                'domain.user_emails.make_offerer_booking_recap_email_after_user_action',
                return_value={'Html-part': ''}) as make_offerer_recap_email:
            # When
            send_user_driven_cancellation_email_to_offerer(booking, mocked_send_email)

            # Then
            make_offerer_recap_email.assert_called_once_with(booking, is_cancellation=True)
        mocked_send_email.assert_called_once()
        args = mocked_send_email.call_args
        assert args[1]['data']['To'] == 'administration@passculture.app'

    def when_feature_send_mail_to_users_disabled_sends_to_pass_culture_dev(self, app):
        # Given
        user = create_user(email='user@email.fr')
        offerer = create_offerer()
        venue = create_venue(offerer, booking_email='booking@email.fr')
        stock = create_stock_with_event_offer(offerer, venue)
        booking = create_booking(user, stock, venue)
        mocked_send_email = Mock()
        return_value = Mock()
        return_value.status_code = 200
        mocked_send_email.return_value = return_value

        with patch('utils.mailing.feature_send_mail_to_users_enabled', return_value=False), patch(
                'domain.user_emails.make_offerer_booking_recap_email_after_user_action',
                return_value={'Html-part': ''}) as make_offerer_recap_email:
            # When
            send_user_driven_cancellation_email_to_offerer(booking, mocked_send_email)

            # Then
            make_offerer_recap_email.assert_called_once_with(booking, is_cancellation=True)
        mocked_send_email.assert_called_once()
        args = mocked_send_email.call_args
        assert args[1]['data']['To'] == 'dev@passculture.app'
        assert 'This is a test' in args[1]['data']['Html-part']


class SendOffererDrivenCancellationEmailToUserTest:
    def when_feature_send_mail_to_users_enabled_sends_email_to_user(self, app):
        # Given
        user = create_user(email='user@email.fr')
        booking = create_booking(user)
        mocked_send_email = Mock()
        return_value = Mock()
        return_value.status_code = 200
        mocked_send_email.return_value = return_value

        with patch('utils.mailing.feature_send_mail_to_users_enabled', return_value=True), patch(
                'domain.user_emails.make_offerer_driven_cancellation_email_for_user',
                return_value={'Html-part': ''}) as make_cancellation_email:
            # When
            send_offerer_driven_cancellation_email_to_user(booking, mocked_send_email)

            # Then
            make_cancellation_email.assert_called_once_with(booking)
        mocked_send_email.assert_called_once()
        args = mocked_send_email.call_args
        assert args[1]['data']['To'] == 'user@email.fr'


class SendOffererDrivenCancellationEmailToOffererTest:
    def when_feature_send_mail_to_users_enabled_and_offer_booking_email_sends_to_offerer_and_administration(self, app):
        # Given
        user = create_user(email='user@email.fr')
        offerer = create_offerer()
        venue = create_venue(offerer)
        venue.bookingEmail = 'booking@email.fr'
        stock = create_stock_with_event_offer(offerer, venue)
        stock.resolvedOffer.bookingEmail = 'offer@email.com'
        booking = create_booking(user, stock)
        mocked_send_email = Mock()
        return_value = Mock()
        return_value.status_code = 200
        mocked_send_email.return_value = return_value

        with patch('utils.mailing.feature_send_mail_to_users_enabled', return_value=True), patch(
                'domain.user_emails.make_offerer_driven_cancellation_email_for_offerer',
                return_value={'Html-part': ''}) as make_cancellation_email:
            # When
            send_offerer_driven_cancellation_email_to_offerer(booking, mocked_send_email)

            # Then
            make_cancellation_email.assert_called_once_with(booking)
        mocked_send_email.assert_called_once()
        args = mocked_send_email.call_args
        assert args[1]['data']['To'] == 'offer@email.com, administration@passculture.app'

    def when_feature_send_mail_to_users_enabled_and_not_offer_booking_email_sends_only_to_administration(self, app):
        # Given
        user = create_user(email='user@email.fr')
        offerer = create_offerer()
        venue = create_venue(offerer)
        stock = create_stock_with_event_offer(offerer, venue)
        stock.resolvedOffer.bookingEmail = None
        booking = create_booking(user, stock)
        mocked_send_email = Mock()
        return_value = Mock()
        return_value.status_code = 200
        mocked_send_email.return_value = return_value

        with patch('utils.mailing.feature_send_mail_to_users_enabled', return_value=True), patch(
                'domain.user_emails.make_offerer_driven_cancellation_email_for_offerer',
                return_value={'Html-part': ''}) as make_cancellation_email:
            # When
            send_offerer_driven_cancellation_email_to_offerer(booking, mocked_send_email)

            # Then
            make_cancellation_email.assert_called_once_with(booking)
        mocked_send_email.assert_called_once()
        args = mocked_send_email.call_args
        assert args[1]['data']['To'] == 'administration@passculture.app'


class SendBookingConfirmationEmailToUserTest:
    def when_called_calls_send_email(self, app):
        # Given
        venue = create_venue(None, 'Test offerer', 'reservations@test.fr', '123 rue test', '93000', 'Test city', '93')
        stock = create_stock_with_event_offer(offerer=None, venue=venue)
        user = create_user('Test', departement_code='93', email='test@email.com', can_book_free_offers=True)
        booking = create_booking(user, stock, venue, None)
        booking.token = '56789'

        mocked_send_email = Mock()
        return_value = Mock()
        return_value.status_code = 200
        mocked_send_email.return_value = return_value

        # When
        send_booking_confirmation_email_to_user(booking, mocked_send_email)

        # Then
        mocked_send_email.assert_called_once()
        called_with_args = mocked_send_email.call_args[1]['data']
        assert 'This is a test (ENV=development). In production, email would have been sent to : test@email.com' in called_with_args['Html-part']
        assert called_with_args['To'] == 'dev@passculture.app'
        assert called_with_args['FromName'] == 'pass Culture'
        assert called_with_args['FromEmail'] == 'dev@passculture.app'


class SendBookingRecapEmailsTest:
    def when_feature_send_mail_to_users_disabled_sends_email_to_pass_culture_dev(self, app):
        # given
        user = create_user()
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue, booking_email='offer.booking.email@example.net')
        stock = create_stock_with_thing_offer(offerer, venue, offer)
        booking = create_booking(user, stock)
        mocked_send_email = Mock()
        return_value = Mock()
        return_value.status_code = 200
        mocked_send_email.return_value = return_value

        with patch('utils.mailing.feature_send_mail_to_users_enabled') as send_mail_to_users:
            send_mail_to_users.return_value = False
            # when
            send_booking_recap_emails(booking, mocked_send_email)

        # then
        mocked_send_email.assert_called_once()
        args = mocked_send_email.call_args
        data = args[1]['data']
        assert data['To'] == 'dev@passculture.app'

    def when_feature_send_mail_to_users_enabled_and_offer_booking_email_sends_to_offerer_and_administration(self, app):
        # given
        user = create_user()
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue, booking_email='offer.booking.email@example.net')
        stock = create_stock_with_thing_offer(offerer, venue, offer, booking_email='offer.booking.email@example.net')
        booking = create_booking(user, stock)
        mocked_send_email = Mock()
        return_value = Mock()
        return_value.status_code = 200
        mocked_send_email.return_value = return_value

        with patch('utils.mailing.feature_send_mail_to_users_enabled') as send_mail_to_users:
            send_mail_to_users.return_value = True
            # when
            send_booking_recap_emails(booking, mocked_send_email)

        # then
        mocked_send_email.assert_called_once()
        args = mocked_send_email.call_args
        data = args[1]['data']
        assert data['To'] == 'administration@passculture.app, offer.booking.email@example.net'

    def when_feature_send_mail_to_users_enabled_and_not_offer_booking_email_sends_only_to_administration(
            self, app):
        # given
        user = create_user()
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue, booking_email=None)
        stock = create_stock_with_thing_offer(offerer, venue, offer, booking_email=None)
        booking = create_booking(user, stock)
        mocked_send_email = Mock()
        return_value = Mock()
        return_value.status_code = 200
        mocked_send_email.return_value = return_value

        with patch('utils.mailing.feature_send_mail_to_users_enabled') as send_mail_to_users:
            send_mail_to_users.return_value = True
            # when
            send_booking_recap_emails(booking, mocked_send_email)

        # then
        mocked_send_email.assert_called_once()
        args = mocked_send_email.call_args
        data = args[1]['data']
        assert data['To'] == 'administration@passculture.app'


class SendFinalBookingRecapEmailTest:
    def when_feature_send_mail_to_users_disabled_sends_email_to_pass_culture_dev(self, app):
        # given
        offerer = create_offerer()
        venue = create_venue(offerer)
        stock = create_stock_with_event_offer(offerer, venue, booking_email='offer.booking.email@example.net')
        mocked_send_email = Mock()
        return_value = Mock()
        return_value.status_code = 200
        mocked_send_email.return_value = return_value

        with patch('utils.mailing.feature_send_mail_to_users_enabled') as send_mail_to_users, patch(
                'domain.user_emails.set_booking_recap_sent_and_save') as set_booking_recap_sent_and_save:
            send_mail_to_users.return_value = False
            # when
            send_final_booking_recap_email(stock, mocked_send_email)

        # then
        mocked_send_email.assert_called_once()
        args = mocked_send_email.call_args
        assert args[1]['data']['To'] == 'dev@passculture.app'
        set_booking_recap_sent_and_save.assert_called_once_with(stock)

    def when_feature_send_mail_to_users_enabled_and_offer_booking_email_sends_to_offerer_and_support(self, app):
        # given
        offerer = create_offerer()
        venue = create_venue(offerer)
        stock = create_stock_with_event_offer(offerer, venue, booking_email='offer.booking.email@example.net')
        mocked_send_email = Mock()
        return_value = Mock()
        return_value.status_code = 200
        mocked_send_email.return_value = return_value

        with patch('utils.mailing.feature_send_mail_to_users_enabled') as send_mail_to_users, patch(
                'domain.user_emails.set_booking_recap_sent_and_save') as set_booking_recap_sent_and_save:
            send_mail_to_users.return_value = True
            # when
            send_final_booking_recap_email(stock, mocked_send_email)

        # then
        mocked_send_email.assert_called_once()
        args = mocked_send_email.call_args
        assert 'offer.booking.email@example.net' in args[1]['data']['To']
        assert 'administration@passculture.app' in args[1]['data']['To']
        set_booking_recap_sent_and_save.assert_called_once_with(stock)

    def when_feature_send_mail_to_users_enabled_and_not_offer_booking_email_sends_only_to_administration(
            self, app):
        # given
        offerer = create_offerer()
        venue = create_venue(offerer)
        stock = create_stock_with_event_offer(offerer, venue, booking_email=None)
        mocked_send_email = Mock()
        return_value = Mock()
        return_value.status_code = 200
        mocked_send_email.return_value = return_value

        with patch('utils.mailing.feature_send_mail_to_users_enabled') as send_mail_to_users, patch(
                'domain.user_emails.set_booking_recap_sent_and_save') as set_booking_recap_sent_and_save:
            send_mail_to_users.return_value = True
            # when
            send_final_booking_recap_email(stock, mocked_send_email)

            # then
            mocked_send_email.assert_called_once()
        args = mocked_send_email.call_args
        assert args[1]['data']['To'] == 'administration@passculture.app'
        set_booking_recap_sent_and_save.assert_called_once_with(stock)


class SendValidationConfirmationEmailTest:
    def when_feature_send_mail_to_users_enabled_sends_email_to_all_users_linked_to_offerer(self, app):
        # Given
        offerer = Offerer()
        user_offerer = UserOfferer()
        user_offerer.rights = RightsType.editor
        user_offerer.user = User(email='test@email.com')
        mocked_send_email = Mock()
        return_value = Mock()
        return_value.status_code = 200
        mocked_send_email.return_value = return_value

        with patch('utils.mailing.feature_send_mail_to_users_enabled', return_value=True), patch(
                'domain.user_emails.make_validation_confirmation_email',
                return_value={'Html-part': ''}) as make_cancellation_email, patch(
            'domain.user_emails.find_all_emails_of_user_offerers_admins',
                return_value=['admin1@email.com', 'admin2@email.com']):
            # When
            send_validation_confirmation_email(user_offerer, offerer, mocked_send_email)

        # Then
        make_cancellation_email.assert_called_once_with(user_offerer, offerer)

        mocked_send_email.assert_called_once()
        args = mocked_send_email.call_args
        assert args[1]['data']['To'] == 'admin1@email.com, admin2@email.com'


class SendCancellationEmailOneUserTest:
    def when_called_calls_send_offerer_driven_cancellation_email_to_user_for_every_booking(self):
        # Given
        mocked_send_email = Mock()
        return_value = Mock()
        return_value.status_code = 200
        mocked_send_email.return_value = return_value
        num_bookings = 6
        bookings = create_mocked_bookings(num_bookings, 'offerer@email.com')
        calls = [call(booking, mocked_send_email) for booking in bookings]

        # When
        with patch(
                'domain.user_emails.send_offerer_driven_cancellation_email_to_user') as send_cancellation_email_one_user, patch(
            'domain.user_emails.make_offerer_driven_cancellation_email_for_user',
            return_value={'Html-part': ''}), patch('utils.mailing.feature_send_mail_to_users_enabled', return_value=True):
            send_batch_cancellation_emails_to_users(bookings, mocked_send_email)

        # Then
        send_cancellation_email_one_user.assert_has_calls(calls)


class SendBatchCancellationEmailToOffererTest:
    def when_feature_send_mail_to_users_enabled_and_offer_booking_email_sends_to_offerer_and_administration_stock_case(
            self):
        # Given
        num_bookings = 5
        bookings = create_mocked_bookings(num_bookings, 'offerer@email.com')
        mocked_send_email = Mock()
        return_value = Mock()
        return_value.status_code = 200
        mocked_send_email.return_value = return_value

        # When
        with patch('utils.mailing.feature_send_mail_to_users_enabled', return_value=True), patch(
                'domain.user_emails.make_batch_cancellation_email',
                return_value={'Html-part': ''}) as make_cancellation_email:
            # When
            send_batch_cancellation_email_to_offerer(bookings, 'stock', mocked_send_email)

        # Then
        make_cancellation_email.assert_called_once_with(bookings, 'stock')

        mocked_send_email.assert_called_once()
        args = mocked_send_email.call_args
        assert args[1]['data']['To'] == 'offerer@email.com, administration@passculture.app'

    def when_feature_send_mail_to_users_enabled_and_offer_booking_email_sends_to_offerer_and_administration_event_occurrence_case(
            self):
        # Given
        num_bookings = 5
        bookings = create_mocked_bookings(num_bookings, 'offerer@email.com')
        mocked_send_email = Mock()
        return_value = Mock()
        return_value.status_code = 200
        mocked_send_email.return_value = return_value

        # When
        with patch('utils.mailing.feature_send_mail_to_users_enabled', return_value=True), patch(
                'domain.user_emails.make_batch_cancellation_email',
                return_value={'Html-part': ''}) as make_cancellation_email:
            # When
            send_batch_cancellation_email_to_offerer(bookings, 'event_occurrence', mocked_send_email)

        # Then
        make_cancellation_email.assert_called_once_with(bookings, 'event_occurrence')

        mocked_send_email.assert_called_once()
        args = mocked_send_email.call_args
        assert args[1]['data']['To'] == 'offerer@email.com, administration@passculture.app'

    def when_feature_send_mail_to_users_disabled_sends_email_to_pass_culture_dev(self):
        # Given
        num_bookings = 5
        bookings = create_mocked_bookings(num_bookings, 'offerer@email.com')
        mocked_send_email = Mock()
        return_value = Mock()
        return_value.status_code = 200
        mocked_send_email.return_value = return_value

        # When
        with patch('utils.mailing.feature_send_mail_to_users_enabled', return_value=False), patch(
                'domain.user_emails.make_batch_cancellation_email',
                return_value={'Html-part': ''}) as make_cancellation_email:
            # When
            send_batch_cancellation_email_to_offerer(bookings, 'stock', mocked_send_email)

        # Then
        mocked_send_email.assert_called_once()
        args = mocked_send_email.call_args
        assert args[1]['data']['To'] == 'dev@passculture.app'
        assert 'This is a test' in args[1]['data']['Html-part']

    def when_feature_send_mail_to_users_enabled_and_not_offer_booking_email_sends_only_to_administration(self):
        # Given
        num_bookings = 5
        bookings = create_mocked_bookings(num_bookings, None)
        mocked_send_email = Mock()
        return_value = Mock()
        return_value.status_code = 200
        mocked_send_email.return_value = return_value

        # When
        with patch('utils.mailing.feature_send_mail_to_users_enabled', return_value=True), patch(
                'domain.user_emails.make_batch_cancellation_email',
                return_value={'Html-part': ''}) as make_cancellation_email:
            # When
            send_batch_cancellation_email_to_offerer(bookings, 'event_occurrence', mocked_send_email)

        # Then
        make_cancellation_email.assert_called_once_with(bookings, 'event_occurrence')

        mocked_send_email.assert_called_once()
        args = mocked_send_email.call_args
        assert args[1]['data']['To'] == 'administration@passculture.app'


class SendVenueValidationConfirmationEmailTest:
    def when_feature_send_mail_to_users_enabled_sends_email_to_all_users_linked_to_offerer(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer)
        mocked_send_email = Mock()
        return_value = Mock()
        return_value.status_code = 200
        mocked_send_email.return_value = return_value

        with patch('utils.mailing.feature_send_mail_to_users_enabled', return_value=True), patch(
                'domain.user_emails.make_venue_validation_confirmation_email',
                return_value={'Html-part': ''}) as make_cancellation_email, patch(
            'domain.user_emails.find_all_emails_of_user_offerers_admins',
                return_value=['admin1@email.com', 'admin2@email.com']):
            # When
            send_venue_validation_confirmation_email(venue, mocked_send_email)

        # Then
        make_cancellation_email.assert_called_once_with(venue)

        mocked_send_email.assert_called_once()
        args = mocked_send_email.call_args
        assert args[1]['data']['To'] == 'admin1@email.com, admin2@email.com'

    def when_feature_send_mail_to_users_enabled_sends_email_to_pass_culutre_dev(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer)
        mocked_send_email = Mock()
        return_value = Mock()
        return_value.status_code = 200
        mocked_send_email.return_value = return_value

        with patch('utils.mailing.feature_send_mail_to_users_enabled', return_value=False), patch(
                'domain.user_emails.make_venue_validation_confirmation_email',
                return_value={'Html-part': ''}) as make_cancellation_email, patch(
            'domain.user_emails.find_all_emails_of_user_offerers_admins',
                return_value=['admin1@email.com', 'admin2@email.com']):
            # When
            send_venue_validation_confirmation_email(venue, mocked_send_email)

        # Then
        make_cancellation_email.assert_called_once_with(venue)

        mocked_send_email.assert_called_once()
        args = mocked_send_email.call_args
        assert args[1]['data']['To'] == 'dev@passculture.app'


class SendUserValidationEmailTest:
    def when_feature_send_mail_to_users_enabled_sends_email_to_user(self):
        # Given
        user = create_user()
        user.generate_validation_token()
        mocked_send_email = Mock()
        return_value = Mock()
        return_value.status_code = 200
        mocked_send_email.return_value = return_value

        # When
        with patch('domain.user_emails.make_user_validation_email', return_value={'Html-part': ''}) as make_email, patch(
                'utils.mailing.feature_send_mail_to_users_enabled', return_value=True):
            send_user_validation_email(user, mocked_send_email, 'localhost-test', True)
        # Then
        mocked_send_email.assert_called_once()
        make_email.assert_called_once()
        mocked_send_email.call_args[1]['To'] = user.email


class SendUserWaitingForValidationByAdminEmailTest:
    def when_feature_send_mail_to_users_enabled_sends_email_to_user_with_offerer_name_in_subject(self):
        # Given
        user = create_user()
        user.generate_validation_token()
        offerer = create_offerer(name='Bar des amis')
        mocked_send_email = Mock()
        return_value = Mock()
        return_value.status_code = 200
        mocked_send_email.return_value = return_value

        # When
        with patch('domain.user_emails.make_user_validation_email', return_value={'Html-part': ''}) as make_email, patch(
                'utils.mailing.feature_send_mail_to_users_enabled', return_value=True):
            send_pro_user_waiting_for_validation_by_admin_email(user, mocked_send_email, offerer)

        # Then
        mocked_send_email.assert_called_once()
        args = mocked_send_email.call_args
        data = args[1]['data']
        assert data['Subject'] == '[pass Culture pro] Votre structure Bar des amis est en cours de validation'


class SendResetPasswordEmailWithMailjetTemplateTest:
    def when_feature_send_emails_enabled_sends_a_reset_password_email_to_user(self, app):
        # given
        user = create_user(public_name='bobby', email='bobby@example.net', reset_password_token='AZ45KNB99H')
        mocked_send_email = Mock()
        return_value = Mock()
        return_value.status_code = 200
        mocked_send_email.return_value = return_value

        # when
        with patch('utils.mailing.feature_send_mail_to_users_enabled', return_value=True):
            send_reset_password_email_with_mailjet_template(user, mocked_send_email)

        # then
        mocked_send_email.assert_called_once()
        args = mocked_send_email.call_args
        data = args[1]['data']
        assert data['FromEmail'] == 'support@passculture.app'
        assert data['To'] == 'bobby@example.net'

    def when_feature_send_emails_disabled_sends_email_to_pass_culture_dev(self, app):
        # given
        user = create_user(public_name='bobby', email='bobby@example.net', reset_password_token='AZ45KNB99H')
        mocked_send_email = Mock()
        return_value = Mock()
        return_value.status_code = 200
        mocked_send_email.return_value = return_value

        # when
        with patch('utils.mailing.feature_send_mail_to_users_enabled', return_value=False):
            send_reset_password_email_with_mailjet_template(user, mocked_send_email)

        # then
        mocked_send_email.assert_called_once()
        args = mocked_send_email.call_args
        email = args[1]['data']
        assert email['To'] == 'dev@passculture.app'


class SendActivationEmailTest:
    def test_should_return_true_when_email_data_are_good(self):
        # given
        user = create_user(public_name='bobby', email='bobby@example.net', reset_password_token='AZ45KNB99H')
        mocked_send_email = Mock(return_value=True)

        # when
        activation_email = send_activation_email(user, mocked_send_email)

        # then
        assert activation_email == True

    def test_should_return_false_when_email_data_are_not_valid(self):
        # given
        user = create_user(public_name='bobby', email='bobby@example.net', reset_password_token='AZ45KNB99H')
        mocked_send_email = Mock(return_value=False)

        # when
        activation_email = send_activation_email(user, mocked_send_email)

        # then
        assert activation_email == False
