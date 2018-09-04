from unittest.mock import patch, Mock

import pytest

from domain.booking_emails import send_user_driven_cancellation_email_to_user
from utils.test_utils import create_user, create_booking


@pytest.mark.standalone
def test_send_user_driven_cancellation_email_to_user_calls_mailjet(app):
    # Given
    user = create_user(email='user@email.fr')
    booking = create_booking(user)
    mocked_send_create_email = Mock()
    return_value = Mock()
    return_value.status_code = 200
    mocked_send_create_email.return_value = return_value

    with patch('domain.booking_emails.feature_send_mail_to_users_enabled') as send_mail_to_users:
        send_mail_to_users.return_value = True
        # When
        send_user_driven_cancellation_email_to_user(booking, mocked_send_create_email)

    # Then
    mocked_send_create_email.assert_called_once()
    args = mocked_send_create_email.call_args
    assert args[1]['data']['To'] == 'user@email.fr'