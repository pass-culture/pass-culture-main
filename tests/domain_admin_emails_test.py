import secrets
from unittest.mock import Mock, patch

import pytest

from domain.admin_emails import maybe_send_offerer_validation_email, send_venue_validation_email, \
    send_payment_details_email, send_wallet_balances_email, send_payments_report_emails, \
    send_offer_creation_notification_to_support
from utils.mailing import MailServiceException
from tests.test_utils import create_offerer, create_user, \
    create_user_offerer, create_venue, create_thing_offer


@pytest.mark.standalone
def test_maybe_send_offerer_validation_email_sends_email_to_pass_culture_when_objects_to_validate_and_send_email_enabled(
        app):
    # Given
    offerer = create_offerer(siren='732075312', address='122 AVENUE DE FRANCE', city='Paris', postal_code='75013',
                             name='Accenture', validation_token='12345')

    user = create_user(public_name='Test', departement_code='75', email='user@accenture.com',
                       can_book_free_offers=False, validation_token='98765')

    user_offerer = create_user_offerer(user, offerer, validation_token=None)

    mocked_send_create_email = Mock()
    return_value = Mock()
    return_value.status_code = 200
    mocked_send_create_email.return_value = return_value

    # When
    with patch('utils.mailing.feature_send_mail_to_users_enabled', return_value=True):
        maybe_send_offerer_validation_email(offerer, user_offerer, mocked_send_create_email)

    # Then
    mocked_send_create_email.assert_called_once()
    args = mocked_send_create_email.call_args
    email = args[1]['data']
    assert email['To'] == 'support.passculture@beta.gouv.fr'
    assert 'This is a test' not in email['Html-part']


@pytest.mark.standalone
def test_maybe_send_offerer_validation_email_sends_email_to_pass_culture_dev_when_objects_to_validate_and_send_email_disabled(
        app):
    # Given
    offerer = create_offerer(siren='732075312', address='122 AVENUE DE FRANCE', city='Paris', postal_code='75013',
                             name='Accenture', validation_token='12345')

    user = create_user(public_name='Test', departement_code='75', email='user@accenture.com',
                       can_book_free_offers=False, validation_token='98765')

    user_offerer = create_user_offerer(user, offerer, validation_token=None)

    mocked_send_create_email = Mock()
    return_value = Mock()
    return_value.status_code = 200
    mocked_send_create_email.return_value = return_value

    # When
    with patch('utils.mailing.feature_send_mail_to_users_enabled', return_value=False):
        maybe_send_offerer_validation_email(offerer, user_offerer, mocked_send_create_email)

    # Then
    mocked_send_create_email.assert_called_once()
    args = mocked_send_create_email.call_args
    email = args[1]['data']
    assert email['To'] == 'passculture-dev@beta.gouv.fr'
    assert 'This is a test' in email['Html-part']


@pytest.mark.standalone
def test_maybe_send_offerer_validation_email_does_not_send_email_if_all_validated(app):
    # Given
    offerer = create_offerer(siren='732075312', address='122 AVENUE DE FRANCE', city='Paris', postal_code='75013',
                             name='Accenture', validation_token=None)

    user = create_user(public_name='Test', departement_code='75', email='user@accenture.com',
                       can_book_free_offers=False, validation_token=None)

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

    user = create_user(public_name='Test', departement_code='75', email='user@accenture.com',
                       can_book_free_offers=False, validation_token=validation_token)

    user_offerer = create_user_offerer(user, offerer, validation_token)

    mocked_send_create_email = Mock()
    return_value = Mock()
    return_value.status_code = 400
    mocked_send_create_email.return_value = return_value

    # When
    with pytest.raises(MailServiceException):
        maybe_send_offerer_validation_email(offerer, user_offerer, mocked_send_create_email)


@pytest.mark.standalone
def test_send_venue_validation_email_when_mailjet_status_code_200_sends_email_to_pass_culture(app):
    # Given
    offerer = create_offerer()
    venue = create_venue(offerer)

    mocked_send_create_email = Mock()
    return_value = Mock()
    return_value.status_code = 200
    mocked_send_create_email.return_value = return_value

    # When
    with patch('utils.mailing.feature_send_mail_to_users_enabled', return_value=True):
        send_venue_validation_email(venue, mocked_send_create_email)

    # Then
    mocked_send_create_email.assert_called_once()
    args = mocked_send_create_email.call_args
    email = args[1]['data']
    assert email['To'] == 'support.passculture@beta.gouv.fr'
    assert 'This is a test' not in email['Html-part']


@pytest.mark.standalone
def test_send_venue_validation_email_has_pass_culture_dev_as_recipient_when_send_email_disabled(app):
    # Given
    offerer = create_offerer()
    venue = create_venue(offerer)

    mocked_send_create_email = Mock()
    return_value = Mock()
    return_value.status_code = 200
    mocked_send_create_email.return_value = return_value

    # When
    with patch('utils.mailing.feature_send_mail_to_users_enabled', return_value=False):
        send_venue_validation_email(venue, mocked_send_create_email)

    # Then
    mocked_send_create_email.assert_called_once()
    args = mocked_send_create_email.call_args
    email = args[1]['data']
    assert email['To'] == 'passculture-dev@beta.gouv.fr'
    assert 'This is a test' in email['Html-part']


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
        send_venue_validation_email(venue, mocked_send_create_email)


@pytest.mark.standalone
def test_send_payment_details_email_when_mailjet_status_code_200_sends_email_to_pass_culture(app):
    # Given
    csv = '"header A","header B","header C","header D"\n"part A","part B","part C","part D"\n'
    recipients = ['comptable1@culture.fr', 'comptable2@culture.fr']

    mocked_send_create_email = Mock()
    return_value = Mock()
    return_value.status_code = 200
    mocked_send_create_email.return_value = return_value

    # When
    with patch('utils.mailing.feature_send_mail_to_users_enabled', return_value=True):
        send_payment_details_email(csv, recipients, mocked_send_create_email)

    # Then
    mocked_send_create_email.assert_called_once()
    args = mocked_send_create_email.call_args
    email = args[1]['data']
    assert email['To'] == 'comptable1@culture.fr, comptable2@culture.fr'


@pytest.mark.standalone
def test_send_payment_details_email_has_pass_culture_dev_as_recipient_when_send_email_disabled(app):
    # Given
    csv = '"header A","header B","header C","header D"\n"part A","part B","part C","part D"\n'
    recipients = ['comptable1@culture.fr', 'comptable2@culture.fr']

    mocked_send_create_email = Mock()
    return_value = Mock()
    return_value.status_code = 200
    mocked_send_create_email.return_value = return_value

    # When
    with patch('utils.mailing.feature_send_mail_to_users_enabled', return_value=False):
        send_payment_details_email(csv, recipients, mocked_send_create_email)

    # Then
    mocked_send_create_email.assert_called_once()
    args = mocked_send_create_email.call_args
    email = args[1]['data']
    assert email['To'] == 'passculture-dev@beta.gouv.fr'


@pytest.mark.standalone
def test_send_payment_details_email_when_mailjet_status_code_400_raises_MailServiceException(app):
    # Given
    csv = '"header A","header B","header C","header D"\n"part A","part B","part C","part D"\n'
    recipients = ['comptable1@culture.fr', 'comptable2@culture.fr']

    mocked_send_create_email = Mock()
    return_value = Mock()
    return_value.status_code = 400
    mocked_send_create_email.return_value = return_value

    # When
    with pytest.raises(MailServiceException):
        send_payment_details_email(csv, recipients, mocked_send_create_email)


@pytest.mark.standalone
def test_send_wallet_balances_email_when_mailjet_status_code_200_sends_email_to_recipients(app):
    # Given
    csv = '"header A","header B","header C","header D"\n"part A","part B","part C","part D"\n'
    recipients = ['comptable1@culture.fr', 'comptable2@culture.fr']

    mocked_send_create_email = Mock()
    return_value = Mock()
    return_value.status_code = 200
    mocked_send_create_email.return_value = return_value

    # When
    with patch('utils.mailing.feature_send_mail_to_users_enabled', return_value=True):
        send_wallet_balances_email(csv, recipients, mocked_send_create_email)

    # Then
    mocked_send_create_email.assert_called_once()
    args = mocked_send_create_email.call_args
    email = args[1]['data']
    assert email['To'] == 'comptable1@culture.fr, comptable2@culture.fr'


@pytest.mark.standalone
def test_send_wallet_balances_email_has_pass_culture_dev_as_recipient_when_send_email_disabled(app):
    # Given
    csv = '"header A","header B","header C","header D"\n"part A","part B","part C","part D"\n'
    recipients = ['comptable1@culture.fr', 'comptable2@culture.fr']

    mocked_send_create_email = Mock()
    return_value = Mock()
    return_value.status_code = 200
    mocked_send_create_email.return_value = return_value

    # When
    with patch('utils.mailing.feature_send_mail_to_users_enabled', return_value=False):
        send_wallet_balances_email(csv, recipients, mocked_send_create_email)

    # Then
    mocked_send_create_email.assert_called_once()
    args = mocked_send_create_email.call_args
    email = args[1]['data']
    assert email['To'] == 'passculture-dev@beta.gouv.fr'


@pytest.mark.standalone
def test_send_wallet_balances_email_when_mailjet_status_code_400_raises_MailServiceException(app):
    # Given
    csv = '"header A","header B","header C","header D"\n"part A","part B","part C","part D"\n'
    recipients = ['comptable1@culture.fr', 'comptable2@culture.fr']

    mocked_send_create_email = Mock()
    return_value = Mock()
    return_value.status_code = 400
    mocked_send_create_email.return_value = return_value

    # When
    with pytest.raises(MailServiceException):
        send_wallet_balances_email(csv, recipients, mocked_send_create_email)


@pytest.mark.standalone
def test_send_payments_report_emails_when_mailjet_status_code_200_sends_email_to_recipients(app):
    # Given
    not_processable_csv = '"header A","header B","header C","header D"\n"part A","part B","part C","part D"\n'
    error_csv = '"header 1","header 2","header 3","header 4"\n"part 1","part 2","part 3","part 4"\n'
    grouped_payments = {
        'ERROR': [Mock(), Mock()],
        'SENT': [Mock()],
        'PENDING': [Mock(), Mock(), Mock()]
    }

    mocked_send_create_email = Mock()
    return_value = Mock()
    return_value.status_code = 200
    mocked_send_create_email.return_value = return_value

    # When
    with patch('utils.mailing.feature_send_mail_to_users_enabled', return_value=True):
        send_payments_report_emails(not_processable_csv, error_csv, grouped_payments, ['dev.team@test.com'],
                                    mocked_send_create_email)

    # Then
    mocked_send_create_email.assert_called_once()
    args = mocked_send_create_email.call_args
    email = args[1]['data']
    assert email['To'] == 'dev.team@test.com'


@pytest.mark.standalone
def test_send_payments_report_emails_email_has_pass_culture_dev_as_recipient_when_send_email_disabled(app):
    # Given
    not_processable_csv = '"header A","header B","header C","header D"\n"part A","part B","part C","part D"\n'
    error_csv = '"header 1","header 2","header 3","header 4"\n"part 1","part 2","part 3","part 4"\n'
    grouped_payments = {
        'ERROR': [Mock(), Mock()],
        'SENT': [Mock()],
        'PENDING': [Mock(), Mock(), Mock()]
    }

    mocked_send_create_email = Mock()
    return_value = Mock()
    return_value.status_code = 200
    mocked_send_create_email.return_value = return_value

    # When
    with patch('utils.mailing.feature_send_mail_to_users_enabled', return_value=False):
        send_payments_report_emails(not_processable_csv, error_csv, grouped_payments, ['dev.team@test.com'],
                                    mocked_send_create_email)

    # Then
    mocked_send_create_email.assert_called_once()
    args = mocked_send_create_email.call_args
    email = args[1]['data']
    assert email['To'] == 'passculture-dev@beta.gouv.fr'


@pytest.mark.standalone
def test_send_payments_report_emails_when_mailjet_status_code_400_raises_MailServiceException(app):
    # Given
    not_processable_csv = '"header A","header B","header C","header D"\n"part A","part B","part C","part D"\n'
    error_csv = '"header 1","header 2","header 3","header 4"\n"part 1","part 2","part 3","part 4"\n'
    grouped_payments = {
        'ERROR': [Mock(), Mock()],
        'SENT': [Mock()],
        'PENDING': [Mock(), Mock(), Mock()]
    }

    mocked_send_create_email = Mock()
    return_value = Mock()
    return_value.status_code = 400
    mocked_send_create_email.return_value = return_value

    # When
    with pytest.raises(MailServiceException):
        send_payments_report_emails(not_processable_csv, error_csv, grouped_payments, ['dev.team@test.com'],
                                    mocked_send_create_email)


@pytest.mark.standalone
class SendOfferCreationNotificationToSupportTest:
    def test_when_mailjet_status_code_200_sends_email_to_support_email(self, app):
        mocked_send_create_email = Mock()
        return_value = Mock()
        return_value.status_code = 200
        mocked_send_create_email.return_value = return_value
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_thing_offer(venue)
        author = create_user(email='author@email.com')
        # When
        with patch('utils.mailing.feature_send_mail_to_users_enabled', return_value=True):
            send_offer_creation_notification_to_support(offer, author, 'http://test.url', mocked_send_create_email)

        # Then
        mocked_send_create_email.assert_called_once()
        args = mocked_send_create_email.call_args
        email = args[1]['data']
        assert email['To'] == 'support.passculture@beta.gouv.fr'

    def test_when_send_email_disabled_has_pass_culture_dev_as_recipient(self, app):
        # Given
        mocked_send_create_email = Mock()
        return_value = Mock()
        return_value.status_code = 200
        mocked_send_create_email.return_value = return_value
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_thing_offer(venue)
        author = create_user(email='author@email.com')
        # When
        with patch('utils.mailing.feature_send_mail_to_users_enabled', return_value=False):
            send_offer_creation_notification_to_support(offer, author, 'http://test.url', mocked_send_create_email)

        # Then
        mocked_send_create_email.assert_called_once()
        args = mocked_send_create_email.call_args
        email = args[1]['data']
        assert email['To'] == 'passculture-dev@beta.gouv.fr'

    def test_when_mailjet_status_code_400_raises_MailServiceException(self, app):
        # Given
        mocked_send_create_email = Mock()
        return_value = Mock()
        return_value.status_code = 400
        mocked_send_create_email.return_value = return_value
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_thing_offer(venue)
        author = create_user(email='author@email.com')
        # When
        with pytest.raises(MailServiceException):
            send_offer_creation_notification_to_support(offer, author, 'http://test.url', mocked_send_create_email)
