from unittest.mock import Mock, patch

import pytest

from domain.booking_emails import send_final_booking_recap_email, send_reset_password_email
from utils.mailing import MailServiceException
from utils.test_utils import create_offerer, create_venue, create_stock_with_event_offer, create_user


@pytest.mark.standalone
def test_send_reset_password_email_sends_a_reset_password_email_to_the_recipient(app):
    # given
    user = create_user(public_name='bobby', email='bobby@test.com', reset_password_token='AZ45KNB99H')
    mocked_send_create_email = Mock()
    return_value = Mock()
    return_value.status_code = 200
    mocked_send_create_email.return_value = return_value

    # when
    send_reset_password_email(user, mocked_send_create_email)

    # then
    mocked_send_create_email.assert_called_once()
    args = mocked_send_create_email.call_args
    data = args[1]['data']
    assert data['FromName'] == 'Pass Culture'
    assert data['FromEmail'] == 'passculture-dev@beta.gouv.fr'
    assert data['Subject'] == 'Réinitialisation de votre mot de passe'
    assert data['To'] == 'bobby@test.com'


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
        send_reset_password_email(user, mocked_send_create_email)