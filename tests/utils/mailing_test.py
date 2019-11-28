import re
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

from freezegun import freeze_time

from models import PcObject, ThingType
from models.db import db
from models.email import Email, EmailStatus
from tests.conftest import clean_database, mocked_mail
from tests.files.api_entreprise import MOCKED_SIREN_ENTREPRISES_API_RETURN
from tests.test_utils import create_user, create_booking, create_offerer, create_venue, create_offer_with_thing_product, \
    create_stock_from_offer, \
    create_email
from utils.mailing import parse_email_addresses, \
    send_raw_email, resend_email, \
    compute_email_html_part_and_recipients, \
    _get_users_information_from_bookings, make_reset_password_email


def get_mocked_response_status_200(entity):
    response = MagicMock(status_code=200, text='')
    response.json = MagicMock(return_value=MOCKED_SIREN_ENTREPRISES_API_RETURN)
    return response


@mocked_mail
@clean_database
@freeze_time('2019-01-01 12:00:00')
def test_save_and_send_creates_an_entry_in_email_with_status_sent_when_send_mail_successful(app):
    # given
    email_content = {
        'FromEmail': 'test@email.fr',
        'FromName': 'Test From',
        'Subject': 'Test subject',
        'Text-Part': 'Hello world',
        'Html-part': '<html><body>Hello World</body></html>'
    }
    mocked_response = MagicMock()
    mocked_response.status_code = 200
    app.mailjet_client.send.create.return_value = mocked_response

    # when
    successfully_sent_email = send_raw_email(email_content)

    # then
    assert successfully_sent_email
    emails = Email.query.all()
    assert app.mailjet_client.send.create.called_once_with(email_content)
    assert len(emails) == 1
    email = emails[0]
    assert email.content == email_content
    assert email.status == EmailStatus.SENT
    assert email.datetime == datetime(2019, 1, 1, 12, 0, 0)


@mocked_mail
@clean_database
@freeze_time('2019-01-01 12:00:00')
def test_save_and_send_creates_an_entry_in_email_with_status_error_when_send_mail_unsuccessful(app):
    # given
    email_content = {
        'FromEmail': 'test@email.fr',
        'FromName': 'Test From',
        'Subject': 'Test subject',
        'Text-Part': 'Hello world',
        'Html-part': '<html><body>Hello World</body></html>'
    }
    mocked_response = MagicMock()
    mocked_response.status_code = 500
    app.mailjet_client.send.create.return_value = mocked_response

    # when
    successfully_sent_email = send_raw_email(email_content)

    # then
    assert not successfully_sent_email
    assert app.mailjet_client.send.create.called_once_with(email_content)
    emails = Email.query.all()
    assert len(emails) == 1
    email = emails[0]
    assert email.content == email_content
    assert email.status == EmailStatus.ERROR
    assert email.datetime == datetime(2019, 1, 1, 12, 0, 0)


@mocked_mail
@clean_database
@freeze_time('2019-01-01 12:00:00')
def test_send_content_and_update_updates_email_when_send_mail_successful(app):
    # given
    email_content = {
        'FromEmail': 'test@email.fr',
        'FromName': 'Test From',
        'Subject': 'Test subject',
        'Text-Part': 'Hello world',
        'Html-part': '<html><body>Hello World</body></html>'
    }
    email = create_email(email_content, status='ERROR', time=datetime(2018, 12, 1, 12, 0, 0))
    PcObject.save(email)
    mocked_response = MagicMock()
    mocked_response.status_code = 200
    app.mailjet_client.send.create.return_value = mocked_response

    # when
    successfully_sent = resend_email(email)

    # then
    db.session.refresh(email)
    assert successfully_sent
    assert email.status == EmailStatus.SENT
    assert email.datetime == datetime(2019, 1, 1, 12, 0, 0)
    app.mailjet_client.send.create.assert_called_once_with(data=email_content)


@mocked_mail
@clean_database
@freeze_time('2019-01-01 12:00:00')
def test_send_content_and_update_does_not_update_email_when_send_mail_unsuccessful(app):
    # given
    email_content = {
        'FromEmail': 'test@email.fr',
        'FromName': 'Test From',
        'Subject': 'Test subject',
        'Text-Part': 'Hello world',
        'Html-part': '<html><body>Hello World</body></html>'
    }
    email = create_email(email_content, status='ERROR', time=datetime(2018, 12, 1, 12, 0, 0))
    PcObject.save(email)
    mocked_response = MagicMock()
    mocked_response.status_code = 500
    app.mailjet_client.send.create.return_value = mocked_response

    # when
    successfully_sent = resend_email(email)

    # then
    assert not successfully_sent
    db.session.refresh(email)
    assert email.status == EmailStatus.ERROR
    assert email.datetime == datetime(2018, 12, 1, 12, 0, 0)
    app.mailjet_client.send.create.assert_called_once_with(data=email_content)


class ParseEmailAddressesTest:
    def test_returns_an_empty_list(self):
        assert parse_email_addresses('') == []
        assert parse_email_addresses(None) == []

    def test_returns_one_address_when_a_single_one_is_given(self):
        assert parse_email_addresses('recipient@test.com') == ['recipient@test.com']
        assert parse_email_addresses('recipient@test.com  ;  ') == ['recipient@test.com']
        assert parse_email_addresses(' , recipient@test.com') == ['recipient@test.com']

    def test_returns_two_addresses_when_given_addresses_are_separated_by_comma(self):
        assert parse_email_addresses('one@test.com,two@test.com') == ['one@test.com', 'two@test.com']
        assert parse_email_addresses('one@test.com, two@test.com') == ['one@test.com', 'two@test.com']
        assert parse_email_addresses('  one@test.com  , two@test.com   ') == ['one@test.com', 'two@test.com']

    def test_returns_two_addresses_when_given_addresses_are_separated_by_semicolon(self):
        assert parse_email_addresses('one@test.com;two@test.com') == ['one@test.com', 'two@test.com']
        assert parse_email_addresses('one@test.com; two@test.com') == ['one@test.com', 'two@test.com']
        assert parse_email_addresses('  one@test.com  ; two@test.com   ') == ['one@test.com', 'two@test.com']


class ComputeEmailHtmlPartAndRecipientsTest:
    def test_accepts_string_as_to(self, app):
        # when
        with patch('utils.mailing.feature_send_mail_to_users_enabled', return_value=True):
            html, to = compute_email_html_part_and_recipients("my_html", "plop@plop.com")

        # then
        assert html == "my_html"
        assert to == "plop@plop.com"

    def test_accepts_list_of_strings_as_to(self, app):
        # when
        with patch('utils.mailing.feature_send_mail_to_users_enabled', return_value=True):
            html, to = compute_email_html_part_and_recipients("my_html", ["plop@plop.com", "plip@plip.com"])

        # then
        assert html == "my_html"
        assert to == "plop@plop.com, plip@plip.com"


class GetUsersInformationFromStockBookingsTest:
    def test_returns_correct_users_information_from_bookings_stock(self):
        # Given
        user_1 = create_user('Test', first_name='Jean', last_name='Dupont', departement_code='93',
                             email='test@example.com',
                             can_book_free_offers=True)
        user_2 = create_user('Test', first_name='Jaja', last_name='Dudu', departement_code='93',
                             email='mail@example.com',
                             can_book_free_offers=True)
        user_3 = create_user('Test', first_name='Toto', last_name='Titi', departement_code='93',
                             email='mail@example.com',
                             can_book_free_offers=True)
        offerer = create_offerer()
        venue = create_venue(offerer, 'Test offerer', 'reservations@test.fr', is_virtual=True, siret=None)
        thing_offer = create_offer_with_thing_product(venue, thing_type=ThingType.LIVRE_EDITION,
                                                      booking_email='dev@passculture.app')
        beginning_datetime = datetime(2019, 11, 6, 14, 00, 0, tzinfo=timezone.utc)
        stock = create_stock_from_offer(thing_offer, beginning_datetime=beginning_datetime, price=0, available=10)
        booking_1 = create_booking(user_1, stock, venue, token='HELLO0')
        booking_2 = create_booking(user_2, stock, venue, token='HELLO1')
        booking_3 = create_booking(user_3, stock, venue, token='HELLO2')

        stock.bookings = [booking_1, booking_2, booking_3]

        # When
        users_informations = _get_users_information_from_bookings(stock.bookings)

        # Then
        assert users_informations == [
            {'firstName': 'Jean', 'lastName': 'Dupont', 'email': 'test@example.com', 'contremarque': 'HELLO0'},
            {'firstName': 'Jaja', 'lastName': 'Dudu', 'email': 'mail@example.com', 'contremarque': 'HELLO1'},
            {'firstName': 'Toto', 'lastName': 'Titi', 'email': 'mail@example.com', 'contremarque': 'HELLO2'}
        ]


def _remove_whitespaces(text):
    text = re.sub('\n\s+', ' ', text)
    text = re.sub('\n', '', text)
    return text
