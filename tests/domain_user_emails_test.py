from unittest.mock import patch, Mock, call

import pytest

from domain.user_emails import send_user_driven_cancellation_email_to_user, \
    send_user_driven_cancellation_email_to_offerer, send_offerer_driven_cancellation_email_to_user, \
    send_offerer_driven_cancellation_email_to_offerer, \
    send_booking_confirmation_email_to_user, send_booking_recap_emails, send_final_booking_recap_email, \
    send_validation_confirmation_email, send_batch_cancellation_emails_to_users, \
    send_batch_cancellation_email_to_offerer, send_user_validation_email, send_venue_validation_confirmation_email, \
    send_reset_password_email
from models import Offerer, UserOfferer, User, RightsType
from utils.mailing import MailServiceException
from utils.test_utils import create_user, create_booking, create_stock_with_event_offer, create_offerer, create_venue, \
    create_thing_offer, create_stock_with_thing_offer, create_mocked_bookings


@pytest.mark.standalone
def test_send_user_driven_cancellation_email_to_user_when_feature_send_mail_to_users_enabled(app):
    # Given
    user = create_user(email='user@email.fr')
    booking = create_booking(user)
    mocked_send_create_email = Mock()
    return_value = Mock()
    return_value.status_code = 200
    mocked_send_create_email.return_value = return_value

    with patch('domain.user_emails.feature_send_mail_to_users_enabled', return_value=True), patch(
            'domain.user_emails.make_user_booking_recap_email',
            return_value={'Html-part': ''}) as make_user_recap_email:
        # When
        send_user_driven_cancellation_email_to_user(booking, mocked_send_create_email)

        # Then
        make_user_recap_email.assert_called_once_with(booking, is_cancellation=True)
    mocked_send_create_email.assert_called_once()
    args = mocked_send_create_email.call_args
    assert args[1]['data']['To'] == 'user@email.fr'


@pytest.mark.standalone
def test_send_user_driven_cancellation_email_to_user_when_feature_send_mail_to_users_disabled(app):
    # Given
    user = create_user(email='user@email.fr')
    booking = create_booking(user)
    mocked_send_create_email = Mock()
    return_value = Mock()
    return_value.status_code = 200
    mocked_send_create_email.return_value = return_value

    with patch('domain.user_emails.feature_send_mail_to_users_enabled', return_value=False), patch(
            'domain.user_emails.make_user_booking_recap_email',
            return_value={'Html-part': ''}) as make_user_recap_email:
        # When
        send_user_driven_cancellation_email_to_user(booking, mocked_send_create_email)

        # Then
        make_user_recap_email.assert_called_once_with(booking, is_cancellation=True)
    mocked_send_create_email.assert_called_once()
    args = mocked_send_create_email.call_args
    assert args[1]['data']['To'] == 'passculture-dev@beta.gouv.fr'
    assert 'This is a test' in args[1]['data']['Html-part']


@pytest.mark.standalone
def test_send_user_driven_cancellation_email_to_user_when_status_code_400(app):
    # Given
    user = create_user(email='user@email.fr')
    offerer = create_offerer()
    venue = create_venue(offerer, booking_email='booking@email.fr')
    stock = create_stock_with_event_offer(offerer, venue)
    booking = create_booking(user, stock, venue)
    mocked_send_create_email = Mock()
    return_value = Mock()
    return_value.status_code = 400
    mocked_send_create_email.return_value = return_value

    # When
    with patch('domain.user_emails.feature_send_mail_to_users_enabled', return_value=False), patch(
            'domain.user_emails.make_offerer_booking_recap_email_after_user_action',
            return_value={'Html-part': ''}), pytest.raises(MailServiceException):
        send_user_driven_cancellation_email_to_user(booking, mocked_send_create_email)


@pytest.mark.standalone
def test_send_user_driven_cancellation_email_to_offerer_when_feature_send_mail_to_users_enabled(app):
    # Given
    user = create_user(email='user@email.fr')
    offerer = create_offerer()
    venue = create_venue(offerer, booking_email='booking@email.fr')
    stock = create_stock_with_event_offer(offerer, venue)
    booking = create_booking(user, stock, venue)
    mocked_send_create_email = Mock()
    return_value = Mock()
    return_value.status_code = 200
    mocked_send_create_email.return_value = return_value

    with patch('domain.user_emails.feature_send_mail_to_users_enabled', return_value=True), patch(
            'domain.user_emails.make_offerer_booking_recap_email_after_user_action',
            return_value={'Html-part': ''}) as make_offerer_recap_email:
        # When
        send_user_driven_cancellation_email_to_offerer(booking, mocked_send_create_email)

        # Then
        make_offerer_recap_email.assert_called_once_with(booking, is_cancellation=True)
    mocked_send_create_email.assert_called_once()
    args = mocked_send_create_email.call_args
    assert args[1]['data']['To'] == 'booking@email.fr'


@pytest.mark.standalone
def test_send_user_driven_cancellation_email_to_offerer_when_feature_send_mail_to_users_disabled(app):
    # Given
    user = create_user(email='user@email.fr')
    offerer = create_offerer()
    venue = create_venue(offerer, booking_email='booking@email.fr')
    stock = create_stock_with_event_offer(offerer, venue)
    booking = create_booking(user, stock, venue)
    mocked_send_create_email = Mock()
    return_value = Mock()
    return_value.status_code = 200
    mocked_send_create_email.return_value = return_value

    with patch('domain.user_emails.feature_send_mail_to_users_enabled', return_value=False), patch(
            'domain.user_emails.make_offerer_booking_recap_email_after_user_action',
            return_value={'Html-part': ''}) as make_offerer_recap_email:
        # When
        send_user_driven_cancellation_email_to_offerer(booking, mocked_send_create_email)

        # Then
        make_offerer_recap_email.assert_called_once_with(booking, is_cancellation=True)
    mocked_send_create_email.assert_called_once()
    args = mocked_send_create_email.call_args
    assert args[1]['data']['To'] == 'passculture-dev@beta.gouv.fr'
    assert 'This is a test' in args[1]['data']['Html-part']


@pytest.mark.standalone
def test_send_user_driven_cancellation_email_to_offerer_when_status_code_400(app):
    # Given
    user = create_user(email='user@email.fr')
    offerer = create_offerer()
    venue = create_venue(offerer, booking_email='booking@email.fr')
    stock = create_stock_with_event_offer(offerer, venue)
    booking = create_booking(user, stock, venue)
    mocked_send_create_email = Mock()
    return_value = Mock()
    return_value.status_code = 400
    mocked_send_create_email.return_value = return_value

    # When
    with patch('domain.user_emails.feature_send_mail_to_users_enabled', return_value=False), patch(
            'domain.user_emails.make_offerer_booking_recap_email_after_user_action',
            return_value={'Html-part': ''}), pytest.raises(MailServiceException):
        send_user_driven_cancellation_email_to_offerer(booking, mocked_send_create_email)


@pytest.mark.standalone
def test_send_offerer_driven_cancellation_email_to_user_when_feature_send_mail_to_users_enabled(app):
    # Given
    user = create_user(email='user@email.fr')
    booking = create_booking(user)
    mocked_send_create_email = Mock()
    return_value = Mock()
    return_value.status_code = 200
    mocked_send_create_email.return_value = return_value

    with patch('domain.user_emails.feature_send_mail_to_users_enabled', return_value=True), patch(
            'domain.user_emails.make_offerer_driven_cancellation_email_for_user',
            return_value={'Html-part': ''}) as make_cancellation_email:
        # When
        send_offerer_driven_cancellation_email_to_user(booking, mocked_send_create_email)

        # Then
        make_cancellation_email.assert_called_once_with(booking)
    mocked_send_create_email.assert_called_once()
    args = mocked_send_create_email.call_args
    assert args[1]['data']['To'] == 'user@email.fr'


@pytest.mark.standalone
def test_send_offerer_driven_cancellation_email_to_user_when_status_code_400(app):
    # Given
    user = create_user(email='user@email.fr')
    booking = create_booking(user)
    mocked_send_create_email = Mock()
    return_value = Mock()
    return_value.status_code = 400
    mocked_send_create_email.return_value = return_value

    # When
    with patch('domain.user_emails.feature_send_mail_to_users_enabled', return_value=True), patch(
            'domain.user_emails.make_offerer_driven_cancellation_email_for_user',
            return_value={'Html-part': ''}), pytest.raises(MailServiceException):
        send_offerer_driven_cancellation_email_to_user(booking, mocked_send_create_email)


@pytest.mark.standalone
def test_send_offerer_driven_cancellation_email_to_offerer_when_booking_email(app):
    # Given
    user = create_user(email='user@email.fr')
    offerer = create_offerer()
    venue = create_venue(offerer)
    venue.bookingEmail = 'booking@email.fr'
    stock = create_stock_with_event_offer(offerer, venue)
    booking = create_booking(user, stock)
    mocked_send_create_email = Mock()
    return_value = Mock()
    return_value.status_code = 200
    mocked_send_create_email.return_value = return_value

    with patch('domain.user_emails.feature_send_mail_to_users_enabled', return_value=True), patch(
            'domain.user_emails.make_offerer_driven_cancellation_email_for_offerer',
            return_value={'Html-part': ''}) as make_cancellation_email:
        # When
        send_offerer_driven_cancellation_email_to_offerer(booking, mocked_send_create_email)

        # Then
        make_cancellation_email.assert_called_once_with(booking)
    mocked_send_create_email.assert_called_once()
    args = mocked_send_create_email.call_args
    assert args[1]['data']['To'] == 'booking@email.fr'


@pytest.mark.standalone
def test_send_offerer_driven_cancellation_email_to_offerer_when_no_booking_email(app):
    # Given
    user = create_user(email='user@email.fr')
    offerer = create_offerer()
    venue = create_venue(offerer)
    venue.bookingEmail = None
    stock = create_stock_with_event_offer(offerer, venue)
    booking = create_booking(user, stock)
    mocked_send_create_email = Mock()
    return_value = Mock()
    return_value.status_code = 200
    mocked_send_create_email.return_value = return_value

    with patch('domain.user_emails.feature_send_mail_to_users_enabled', return_value=True), patch(
            'domain.user_emails.make_offerer_driven_cancellation_email_for_offerer',
            return_value={'Html-part': ''}) as make_cancellation_email:
        # When
        send_offerer_driven_cancellation_email_to_offerer(booking, mocked_send_create_email)

        # Then
        make_cancellation_email.assert_not_called()
    mocked_send_create_email.assert_not_called()


@pytest.mark.standalone
def test_send_offerer_driven_cancellation_email_to_offerer_when_status_code_400(app):
    # Given
    user = create_user(email='user@email.fr')
    booking = create_booking(user)
    mocked_send_create_email = Mock()
    return_value = Mock()
    return_value.status_code = 400
    mocked_send_create_email.return_value = return_value

    # When
    with patch('domain.user_emails.feature_send_mail_to_users_enabled', return_value=True), patch(
            'domain.user_emails.make_offerer_driven_cancellation_email_for_offerer',
            return_value={'Html-part': ''}), pytest.raises(MailServiceException):
        send_offerer_driven_cancellation_email_to_offerer(booking, mocked_send_create_email)


@pytest.mark.standalone
def test_send_booking_confirmation_email_to_user_should_call_mailjet_send_create(app):
    # Given
    venue = create_venue(None, 'Test offerer', 'reservations@test.fr', '123 rue test', '93000', 'Test city', '93')
    stock = create_stock_with_event_offer(offerer=None,
                                          venue=venue)
    user = create_user('Test', departement_code='93', email='test@email.com', can_book_free_offers=True)
    booking = create_booking(user, stock, venue, None)
    booking.token = '56789'

    mocked_send_create_email = Mock()
    return_value = Mock()
    return_value.status_code = 200
    mocked_send_create_email.return_value = return_value

    # When
    send_booking_confirmation_email_to_user(booking, mocked_send_create_email)

    # Then
    mocked_send_create_email.assert_called_once()
    called_with_args = mocked_send_create_email.call_args[1]['data']
    assert 'This is a test (ENV=development). In production, email would have been sent to : test@email.com' in \
           called_with_args[
               'Html-part']
    assert called_with_args['To'] == 'passculture-dev@beta.gouv.fr'
    assert called_with_args['FromName'] == 'Pass Culture'
    assert called_with_args['FromEmail'] == 'passculture-dev@beta.gouv.fr'


@pytest.mark.standalone
def test_send_booking_recap_emails_does_not_send_email_to_offer_booking_email_if_feature_is_disabled(app):
    # given
    user = create_user()
    offerer = create_offerer()
    venue = create_venue(offerer)
    offer = create_thing_offer(venue, booking_email='offer.booking.email@test.com')
    stock = create_stock_with_thing_offer(offerer, venue, offer)
    booking = create_booking(user, stock)
    mocked_send_create_email = Mock()
    return_value = Mock()
    return_value.status_code = 200
    mocked_send_create_email.return_value = return_value

    with patch('domain.user_emails.feature_send_mail_to_users_enabled') as send_mail_to_users:
        send_mail_to_users.return_value = False
        # when
        send_booking_recap_emails(booking, mocked_send_create_email)

        # then
        mocked_send_create_email.assert_called_once()
    args = mocked_send_create_email.call_args
    assert args[1]['data']['To'] == 'passculture-dev@beta.gouv.fr'


@pytest.mark.standalone
def test_send_booking_recap_emails_sends_email_to_offer_booking_email_if_feature_is_enabled(app):
    # given
    user = create_user()
    offerer = create_offerer()
    venue = create_venue(offerer)
    offer = create_thing_offer(venue, booking_email='offer.booking.email@test.com')
    stock = create_stock_with_thing_offer(offerer, venue, offer)
    booking = create_booking(user, stock)
    mocked_send_create_email = Mock()
    return_value = Mock()
    return_value.status_code = 200
    mocked_send_create_email.return_value = return_value

    with patch('domain.user_emails.feature_send_mail_to_users_enabled') as send_mail_to_users:
        send_mail_to_users.return_value = True
        # when
        send_booking_recap_emails(booking, mocked_send_create_email)

    # then
    mocked_send_create_email.assert_called_once()
    args = mocked_send_create_email.call_args
    assert 'offer.booking.email@test.com' in args[1]['data']['To']
    assert 'passculture@beta.gouv.fr' in args[1]['data']['To']


@pytest.mark.standalone
def test_send_booking_recap_emails_email_sends_email_only_to_passculture_if_feature_is_enabled_but_no_offer_booking_email(
        app):
    # given
    user = create_user()
    offerer = create_offerer()
    venue = create_venue(offerer)
    offer = create_thing_offer(venue, booking_email=None)
    stock = create_stock_with_thing_offer(offerer, venue, offer, booking_email=None)
    booking = create_booking(user, stock)
    mocked_send_create_email = Mock()
    return_value = Mock()
    return_value.status_code = 200
    mocked_send_create_email.return_value = return_value

    with patch('domain.user_emails.feature_send_mail_to_users_enabled') as send_mail_to_users:
        send_mail_to_users.return_value = True
        # when
        send_booking_recap_emails(booking, mocked_send_create_email)

    # then
    mocked_send_create_email.assert_called_once()
    args = mocked_send_create_email.call_args
    assert args[1]['data']['To'] == 'passculture@beta.gouv.fr'


@pytest.mark.standalone
def test_send_final_booking_recap_email_does_not_send_email_to_offer_booking_email_if_feature_is_disabled(app):
    # given
    offerer = create_offerer()
    venue = create_venue(offerer)
    stock = create_stock_with_event_offer(offerer, venue, booking_email='offer.booking.email@test.com')
    mocked_send_create_email = Mock()
    return_value = Mock()
    return_value.status_code = 200
    mocked_send_create_email.return_value = return_value

    with patch('domain.user_emails.feature_send_mail_to_users_enabled') as send_mail_to_users, patch(
            'domain.user_emails.set_booking_recap_sent_and_save') as set_booking_recap_sent_and_save:
        send_mail_to_users.return_value = False
        # when
        send_final_booking_recap_email(stock, mocked_send_create_email)

    # then
    mocked_send_create_email.assert_called_once()
    args = mocked_send_create_email.call_args
    assert args[1]['data']['To'] == 'passculture-dev@beta.gouv.fr'
    set_booking_recap_sent_and_save.assert_called_once_with(stock)


@pytest.mark.standalone
def test_send_final_booking_recap_email_sends_email_to_offer_booking_email_if_feature_is_enabled(app):
    # given
    offerer = create_offerer()
    venue = create_venue(offerer)
    stock = create_stock_with_event_offer(offerer, venue, booking_email='offer.booking.email@test.com')
    mocked_send_create_email = Mock()
    return_value = Mock()
    return_value.status_code = 200
    mocked_send_create_email.return_value = return_value

    with patch('domain.user_emails.feature_send_mail_to_users_enabled') as send_mail_to_users, patch(
            'domain.user_emails.set_booking_recap_sent_and_save') as set_booking_recap_sent_and_save:
        send_mail_to_users.return_value = True
        # when
        send_final_booking_recap_email(stock, mocked_send_create_email)

    # then
    mocked_send_create_email.assert_called_once()
    args = mocked_send_create_email.call_args
    assert 'offer.booking.email@test.com' in args[1]['data']['To']
    assert 'passculture@beta.gouv.fr' in args[1]['data']['To']
    set_booking_recap_sent_and_save.assert_called_once_with(stock)


@pytest.mark.standalone
def test_send_final_booking_recap_email_sends_email_only_to_passculture_if_feature_is_enabled_but_no_offer_booking_email(
        app):
    # given
    offerer = create_offerer()
    venue = create_venue(offerer)
    stock = create_stock_with_event_offer(offerer, venue, booking_email=None)
    mocked_send_create_email = Mock()
    return_value = Mock()
    return_value.status_code = 200
    mocked_send_create_email.return_value = return_value

    with patch('domain.user_emails.feature_send_mail_to_users_enabled') as send_mail_to_users, patch(
            'domain.user_emails.set_booking_recap_sent_and_save') as set_booking_recap_sent_and_save:
        send_mail_to_users.return_value = True
        # when
        send_final_booking_recap_email(stock, mocked_send_create_email)

        # then
        mocked_send_create_email.assert_called_once()
    args = mocked_send_create_email.call_args
    assert args[1]['data']['To'] == 'passculture@beta.gouv.fr'
    set_booking_recap_sent_and_save.assert_called_once_with(stock)


@pytest.mark.standalone
def test_send_validation_confirmation_email(app):
    # Given
    offerer = Offerer()
    user_offerer = UserOfferer()
    user_offerer.rights = RightsType.editor
    user_offerer.user = User(email='test@email.com')
    mocked_send_create_email = Mock()
    return_value = Mock()
    return_value.status_code = 200
    mocked_send_create_email.return_value = return_value

    with patch('domain.user_emails.feature_send_mail_to_users_enabled', return_value=True), patch(
            'domain.user_emails.make_validation_confirmation_email',
            return_value={'Html-part': ''}) as make_cancellation_email, patch(
        'domain.user_emails.find_all_emails_of_user_offerers_admins',
        return_value=['admin1@email.com', 'admin2@email.com']):
        # When
        send_validation_confirmation_email(user_offerer, offerer, mocked_send_create_email)

    # Then
    make_cancellation_email.assert_called_once_with(user_offerer, offerer)

    mocked_send_create_email.assert_called_once()
    args = mocked_send_create_email.call_args
    assert args[1]['data']['To'] == 'admin1@email.com, admin2@email.com'


@pytest.mark.standalone
def test_send_validation_confirmation_email_when_status_code_400(app):
    # Given
    offerer = Offerer()
    user_offerer = UserOfferer()
    user_offerer.user = User(email='test@email.com')
    mocked_send_create_email = Mock()
    return_value = Mock()
    return_value.status_code = 400
    mocked_send_create_email.return_value = return_value

    with patch('domain.user_emails.feature_send_mail_to_users_enabled', return_value=True), patch(
            'domain.user_emails.make_validation_confirmation_email', return_value={'Html-part': ''}), patch(
        'domain.user_emails.find_all_emails_of_user_offerers_admins', return_value=['test@email.com']), pytest.raises(
        MailServiceException):
        # When
        send_validation_confirmation_email(user_offerer, offerer, mocked_send_create_email)


@pytest.mark.standalone
def test_send_cancellation_emails_to_users_calls_send_offerer_driven_cancellation_email_to_user_for_every_booking():
    # Given
    mocked_send_create_email = Mock()
    return_value = Mock()
    return_value.status_code = 200
    mocked_send_create_email.return_value = return_value
    num_bookings = 6
    bookings = create_mocked_bookings(num_bookings, 'offerer@email.com')
    calls = [call(booking, mocked_send_create_email) for booking in bookings]

    # When
    with patch(
            'domain.user_emails.send_offerer_driven_cancellation_email_to_user') as send_cancellation_email_one_user, patch(
        'domain.user_emails.make_offerer_driven_cancellation_email_for_user',
        return_value={'Html-part': ''}), patch('domain.user_emails.feature_send_mail_to_users_enabled',
                                               return_value=True):
        send_batch_cancellation_emails_to_users(bookings, mocked_send_create_email)

    # Then
    send_cancellation_email_one_user.assert_has_calls(calls)


@pytest.mark.standalone
def test_send_batch_cancellation_email_to_offerer():
    # Given
    num_bookings = 5
    bookings = create_mocked_bookings(num_bookings, 'offerer@email.com')
    mocked_send_create_email = Mock()
    return_value = Mock()
    return_value.status_code = 200
    mocked_send_create_email.return_value = return_value

    # When
    with patch('domain.user_emails.feature_send_mail_to_users_enabled', return_value=True), patch(
            'domain.user_emails.make_batch_cancellation_email',
            return_value={'Html-part': ''}) as make_cancellation_email:
        # When
        send_batch_cancellation_email_to_offerer(bookings, 'stock', mocked_send_create_email)

    # Then
    make_cancellation_email.assert_called_once_with(bookings, 'stock')

    mocked_send_create_email.assert_called_once()
    args = mocked_send_create_email.call_args
    assert args[1]['data']['To'] == 'offerer@email.com'


@pytest.mark.standalone
def test_send_batch_cancellation_email_to_offerer_event_occurrence_case():
    # Given
    num_bookings = 5
    bookings = create_mocked_bookings(num_bookings, 'offerer@email.com')
    mocked_send_create_email = Mock()
    return_value = Mock()
    return_value.status_code = 200
    mocked_send_create_email.return_value = return_value

    # When
    with patch('domain.user_emails.feature_send_mail_to_users_enabled', return_value=True), patch(
            'domain.user_emails.make_batch_cancellation_email',
            return_value={'Html-part': ''}) as make_cancellation_email:
        # When
        send_batch_cancellation_email_to_offerer(bookings, 'event_occurrence', mocked_send_create_email)

    # Then
    make_cancellation_email.assert_called_once_with(bookings, 'event_occurrence')

    mocked_send_create_email.assert_called_once()
    args = mocked_send_create_email.call_args
    assert args[1]['data']['To'] == 'offerer@email.com'


@pytest.mark.standalone
def test_send_batch_cancellation_email_to_offerer_email_status_code_500():
    # Given
    num_bookings = 5
    bookings = create_mocked_bookings(num_bookings, 'offerer@email.com')
    mocked_send_create_email = Mock()
    return_value = Mock()
    return_value.status_code = 500
    mocked_send_create_email.return_value = return_value

    # When
    with pytest.raises(MailServiceException), patch('domain.user_emails.feature_send_mail_to_users_enabled',
                                                    return_value=True), patch(
        'domain.user_emails.make_batch_cancellation_email',
        return_value={'Html-part': ''}):
        # When
        send_batch_cancellation_email_to_offerer(bookings, 'stock', mocked_send_create_email)


@pytest.mark.standalone
def test_send_batch_cancellation_email_to_offerer_feature_send_mail_to_users_enabled_False():
    # Given
    num_bookings = 5
    bookings = create_mocked_bookings(num_bookings, 'offerer@email.com')
    mocked_send_create_email = Mock()
    return_value = Mock()
    return_value.status_code = 200
    mocked_send_create_email.return_value = return_value

    # When
    with patch('domain.user_emails.feature_send_mail_to_users_enabled', return_value=False), patch(
            'domain.user_emails.make_batch_cancellation_email',
            return_value={'Html-part': ''}) as make_cancellation_email:
        # When
        send_batch_cancellation_email_to_offerer(bookings, 'stock', mocked_send_create_email)

    # Then
    mocked_send_create_email.assert_called_once()
    args = mocked_send_create_email.call_args
    assert args[1]['data']['To'] == 'passculture-dev@beta.gouv.fr'
    assert 'This is a test' in args[1]['data']['Html-part']


@pytest.mark.standalone
def test_send_batch_cancellation_email_to_offerer_no_venue_email():
    # Given
    num_bookings = 5
    bookings = create_mocked_bookings(num_bookings, None)
    mocked_send_create_email = Mock()
    return_value = Mock()
    return_value.status_code = 200
    mocked_send_create_email.return_value = return_value

    # When
    with patch('domain.user_emails.feature_send_mail_to_users_enabled', return_value=True), patch(
            'domain.user_emails.make_batch_cancellation_email',
            return_value={'Html-part': ''}):
        # When
        send_batch_cancellation_email_to_offerer(bookings, 'stock', mocked_send_create_email)

    # Then
    mocked_send_create_email.assert_not_called()


@pytest.mark.standalone
def test_send_venue_validation_confirmation_email(app):
    # Given
    offerer = create_offerer()
    venue = create_venue(offerer)
    mocked_send_create_email = Mock()
    return_value = Mock()
    return_value.status_code = 200
    mocked_send_create_email.return_value = return_value

    with patch('domain.user_emails.feature_send_mail_to_users_enabled', return_value=True), patch(
            'domain.user_emails.make_venue_validation_confirmation_email',
            return_value={'Html-part': ''}) as make_cancellation_email, patch(
        'domain.user_emails.find_all_emails_of_user_offerers_admins',
        return_value=['admin1@email.com', 'admin2@email.com']):
        # When
        send_venue_validation_confirmation_email(venue, mocked_send_create_email)

    # Then
    make_cancellation_email.assert_called_once_with(venue)

    mocked_send_create_email.assert_called_once()
    args = mocked_send_create_email.call_args
    assert args[1]['data']['To'] == 'admin1@email.com, admin2@email.com'


@pytest.mark.standalone
def test_send_venue_validation_confirmation_email_has_pass_culutre_dev_as_recipient_when_send_email_disabled(
        app):
    # Given
    offerer = create_offerer()
    venue = create_venue(offerer)
    mocked_send_create_email = Mock()
    return_value = Mock()
    return_value.status_code = 200
    mocked_send_create_email.return_value = return_value

    with patch('domain.user_emails.feature_send_mail_to_users_enabled', return_value=False), patch(
            'domain.user_emails.make_venue_validation_confirmation_email',
            return_value={'Html-part': ''}) as make_cancellation_email, patch(
        'domain.user_emails.find_all_emails_of_user_offerers_admins',
        return_value=['admin1@email.com', 'admin2@email.com']):
        # When
        send_venue_validation_confirmation_email(venue, mocked_send_create_email)

    # Then
    make_cancellation_email.assert_called_once_with(venue)

    mocked_send_create_email.assert_called_once()
    args = mocked_send_create_email.call_args
    assert args[1]['data']['To'] == 'passculture-dev@beta.gouv.fr'


@pytest.mark.standalone
def test_send_venue_validation_confirmation_email_when_status_code_400(app):
    # Given
    offerer = create_offerer()
    venue = create_venue(offerer)
    mocked_send_create_email = Mock()
    return_value = Mock()
    return_value.status_code = 400
    mocked_send_create_email.return_value = return_value

    with patch('domain.user_emails.feature_send_mail_to_users_enabled', return_value=True), patch(
            'domain.user_emails.make_venue_validation_confirmation_email', return_value={'Html-part': ''}), patch(
        'domain.user_emails.find_all_emails_of_user_offerers_admins', return_value=['test@email.com']), pytest.raises(
        MailServiceException):
        # When
        send_venue_validation_confirmation_email(venue, mocked_send_create_email)


@pytest.mark.standalone
def test_send_user_validation_email_when_send_create_status_code_200():
    # Given
    user = create_user()
    user.generate_validation_token()
    mocked_send_create_email = Mock()
    return_value = Mock()
    return_value.status_code = 200
    mocked_send_create_email.return_value = return_value

    # When
    with patch('domain.user_emails.make_user_validation_email', return_value={'Html-part': ''}) as make_email, patch(
            'domain.user_emails.feature_send_mail_to_users_enabled', return_value=True):
        send_user_validation_email(user, mocked_send_create_email, True)
    # Then
    mocked_send_create_email.assert_called_once()
    make_email.assert_called_once()
    mocked_send_create_email.call_args[1]['To'] = user.email


@pytest.mark.standalone
def test_send_user_validation_email_when_send_create_status_code_400():
    # Given
    user = create_user()
    user.generate_validation_token()
    mocked_send_create_email = Mock()
    return_value = Mock()
    return_value.status_code = 400
    mocked_send_create_email.return_value = return_value

    # When
    with pytest.raises(MailServiceException), patch('domain.user_emails.make_user_validation_email',
                                                    return_value={'Html-part': ''}) as make_email, patch(
        'domain.user_emails.feature_send_mail_to_users_enabled', return_value=True):
        send_user_validation_email(user, mocked_send_create_email, True)
    # Then
    mocked_send_create_email.assert_called_once()
    make_email.assert_called_once()


@pytest.mark.standalone
def test_send_reset_password_email_sends_a_reset_password_email_to_the_recipient_when_send_emails_enabled(app):
    # given
    user = create_user(public_name='bobby', email='bobby@test.com', reset_password_token='AZ45KNB99H')
    mocked_send_create_email = Mock()
    return_value = Mock()
    return_value.status_code = 200
    mocked_send_create_email.return_value = return_value

    # when
    with patch('domain.user_emails.feature_send_mail_to_users_enabled', return_value=True):
        send_reset_password_email(user, mocked_send_create_email, 'localhost')

    # then
    mocked_send_create_email.assert_called_once()
    args = mocked_send_create_email.call_args
    data = args[1]['data']
    assert data['FromName'] == 'Pass Culture'
    assert data['FromEmail'] == 'passculture-dev@beta.gouv.fr'
    assert data['Subject'] == 'Réinitialisation de votre mot de passe'
    assert data['To'] == 'bobby@test.com'


@pytest.mark.standalone
def test_send_reset_password_email_sends_a_reset_password_email_to_the_pass_culture_dev_when_send_emails_disabled(app):
    # given
    user = create_user(public_name='bobby', email='bobby@test.com', reset_password_token='AZ45KNB99H')
    mocked_send_create_email = Mock()
    return_value = Mock()
    return_value.status_code = 200
    mocked_send_create_email.return_value = return_value

    # when
    with patch('domain.user_emails.feature_send_mail_to_users_enabled', return_value=False):
        send_reset_password_email(user, mocked_send_create_email, 'localhost')

    # then
    mocked_send_create_email.assert_called_once()
    args = mocked_send_create_email.call_args
    email = args[1]['data']
    assert email['To'] == 'passculture-dev@beta.gouv.fr'
    assert 'This is a test' in email['Html-part']


@pytest.mark.standalone
def test_send_reset_password_email_raises_an_exception_if_mailjet_failed(app):
    # given
    user = create_user(public_name='bobby', email='bobby@test.com', reset_password_token='AZ45KNB99H')
    mocked_send_create_email = Mock()
    return_value = Mock()
    return_value.status_code = 400
    mocked_send_create_email.return_value = return_value

    # when
    with pytest.raises(MailServiceException):
        send_reset_password_email(user, mocked_send_create_email, 'localhost')
