import secrets
from unittest.mock import Mock

import pytest

from domain.user_emails import send_reset_password_email
from domain.admin_emails import maybe_send_offerer_validation_email, send_venue_validation_email
from utils.mailing import MailServiceException
from utils.test_utils import create_offerer, create_user, \
    create_user_offerer, create_venue


@pytest.mark.standalone
def test_send_reset_password_email_sends_a_reset_password_email_to_the_recipient(app):
    # given
    user = create_user(public_name='bobby', email='bobby@test.com', reset_password_token='AZ45KNB99H')
    mocked_send_create_email = Mock()
    return_value = Mock()
    return_value.status_code = 200
    mocked_send_create_email.return_value = return_value

    # when
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


@pytest.mark.standalone
def test_maybe_send_offerer_validation_email_does_not_send_email_if_all_validated(app):
    # Given
    offerer = create_offerer(siren='732075312', address='122 AVENUE DE FRANCE', city='Paris', postal_code='75013',
                             name='Accenture', validation_token=None)

    user = create_user(public_name='Test', departement_code='75', email='user@accenture.com', can_book_free_offers=False,
                       validation_token=None)

    user_offerer = create_user_offerer(user, offerer, validation_token=None)

    mocked_send_create_email = Mock()
    return_value = Mock()
    return_value.status_code = 200
    mocked_send_create_email.return_value = return_value

    # When
    try:
        maybe_send_offerer_validation_email(offerer, user_offerer, mocked_send_create_email)
    except MailServiceException as e:
        app.logger.error('Mail service failure', e) 

    # Then
    assert not mocked_send_create_email.called


@pytest.mark.standalone
def test_maybe_send_offerer_validation_email_raises_exception_if_status_code_400(app):
    # Given
    validation_token = secrets.token_urlsafe(20)
    offerer = create_offerer(siren='732075312', address='122 AVENUE DE FRANCE', city='Paris', postal_code='75013',
                             name='Accenture', validation_token=validation_token)

    user = create_user(public_name='Test', departement_code='75', email='user@accenture.com', can_book_free_offers=False,
                       validation_token=validation_token)

    user_offerer = create_user_offerer(user, offerer, validation_token)

    mocked_send_create_email = Mock()
    return_value = Mock()
    return_value.status_code = 400
    mocked_send_create_email.return_value = return_value

    # When
    with pytest.raises(MailServiceException):
        maybe_send_offerer_validation_email(offerer, user_offerer, mocked_send_create_email)



@pytest.mark.standalone
def test_send_venue_validation_email_when_mailjet_status_code_200_calls_send_create_email_and_returns_nothing(app):
    # Given
    offerer = create_offerer()
    venue = create_venue(offerer)

    mocked_send_create_email = Mock()
    return_value = Mock()
    return_value.status_code = 200
    mocked_send_create_email.return_value = return_value

    # When
    try:
        send_venue_validation_email(venue, mocked_send_create_email)
    except MailServiceException:
        assert False

    # Then
    mocked_send_create_email.assert_called_once()


@pytest.mark.standalone
def test_send_venue_validation_email_when_mailjet_status_code_400_raises_MailServiceException(app):
    # Given
    offerer = create_offerer()
    venue = create_venue(offerer)

    mocked_send_create_email = Mock()
    return_value = Mock()
    return_value.status_code = 400
    mocked_send_create_email.return_value = return_value

    # When
    with pytest.raises(MailServiceException):
        send_venue_validation_email(venue,mocked_send_create_email)
