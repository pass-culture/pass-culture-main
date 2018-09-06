from unittest.mock import patch, Mock

import pytest

from domain.booking_emails import send_user_driven_cancellation_email_to_user, \
    send_user_driven_cancellation_email_to_offerer, send_offerer_driven_cancellation_email_to_user
from utils.mailing import MailServiceException
from utils.test_utils import create_user, create_booking, create_stock_with_event_offer, create_offerer, create_venue


@pytest.mark.standalone
def test_send_user_driven_cancellation_email_to_user_when_feature_send_mail_to_users_enabled(app):
    # Given
    user = create_user(email='user@email.fr')
    booking = create_booking(user)
    mocked_send_create_email = Mock()
    return_value = Mock()
    return_value.status_code = 200
    mocked_send_create_email.return_value = return_value

    with patch('domain.booking_emails.feature_send_mail_to_users_enabled', return_value=True), patch(
            'domain.booking_emails.make_user_booking_recap_email', return_value={'Html-part': ''}) as make_user_recap_email:
        # When
        send_user_driven_cancellation_email_to_user(booking, mocked_send_create_email)

        # Then
        make_user_recap_email.assert_called_once_with(booking, is_cancellation=True)
    mocked_send_create_email.assert_called_once()
    args = mocked_send_create_email.call_args
    assert args[1]['data']['To'] == 'user@email.fr'
    mocked_send_create_email.reset_mock()
    make_user_recap_email.reset_mock()


@pytest.mark.standalone
def test_send_user_driven_cancellation_email_to_user_when_feature_send_mail_to_users_disabled(app):
    # Given
    user = create_user(email='user@email.fr')
    booking = create_booking(user)
    mocked_send_create_email = Mock()
    return_value = Mock()
    return_value.status_code = 200
    mocked_send_create_email.return_value = return_value

    with patch('domain.booking_emails.feature_send_mail_to_users_enabled', return_value=False), patch(
            'domain.booking_emails.make_user_booking_recap_email',
            return_value={'Html-part': ''}) as make_user_recap_email:
        # When
        send_user_driven_cancellation_email_to_user(booking, mocked_send_create_email)

        # Then
        make_user_recap_email.assert_called_once_with(booking, is_cancellation=True)
    mocked_send_create_email.assert_called_once()
    args = mocked_send_create_email.call_args
    assert args[1]['data']['To'] == 'passculture-dev@beta.gouv.fr'
    assert 'This is a test' in args[1]['data']['Html-part']
    mocked_send_create_email.reset_mock()
    make_user_recap_email.reset_mock()


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
    with patch('domain.booking_emails.feature_send_mail_to_users_enabled', return_value=False), patch(
            'domain.booking_emails.make_offerer_booking_recap_email_after_user_action',
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

    with patch('domain.booking_emails.feature_send_mail_to_users_enabled', return_value=True), patch(
            'domain.booking_emails.make_offerer_booking_recap_email_after_user_action',
            return_value={'Html-part': ''}) as make_offerer_recap_email:
        # When
        send_user_driven_cancellation_email_to_offerer(booking, mocked_send_create_email)

        # Then
        make_offerer_recap_email.assert_called_once_with(booking, is_cancellation=True)
    mocked_send_create_email.assert_called_once()
    args = mocked_send_create_email.call_args
    assert args[1]['data']['To'] == 'booking@email.fr'
    mocked_send_create_email.reset_mock()
    make_offerer_recap_email.reset_mock()


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

    with patch('domain.booking_emails.feature_send_mail_to_users_enabled', return_value=False), patch(
            'domain.booking_emails.make_offerer_booking_recap_email_after_user_action',
            return_value={'Html-part': ''}) as make_offerer_recap_email:
        # When
        send_user_driven_cancellation_email_to_offerer(booking, mocked_send_create_email)

        # Then
        make_offerer_recap_email.assert_called_once_with(booking, is_cancellation=True)
    mocked_send_create_email.assert_called_once()
    args = mocked_send_create_email.call_args
    assert args[1]['data']['To'] == 'passculture-dev@beta.gouv.fr'
    assert 'This is a test' in args[1]['data']['Html-part']
    mocked_send_create_email.reset_mock()
    make_offerer_recap_email.reset_mock()


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
    with patch('domain.booking_emails.feature_send_mail_to_users_enabled', return_value=False), patch(
            'domain.booking_emails.make_offerer_booking_recap_email_after_user_action',
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

    with patch('domain.booking_emails.feature_send_mail_to_users_enabled', return_value=True), patch(
            'domain.booking_emails.make_offerer_driven_cancellation_email_for_user', return_value={'Html-part': ''}) as make_cancellation_email:
        # When
        send_offerer_driven_cancellation_email_to_user(booking, mocked_send_create_email)

        # Then
        make_cancellation_email.assert_called_once_with(booking)
    mocked_send_create_email.assert_called_once()
    args = mocked_send_create_email.call_args
    assert args[1]['data']['To'] == 'user@email.fr'
    mocked_send_create_email.reset_mock()
    make_cancellation_email.reset_mock()
