import re
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

from bs4 import BeautifulSoup
from freezegun import freeze_time

from domain.user_emails import build_recipients_list
from models import PcObject, ThingType
from models.db import db
from models.email import Email, EmailStatus
from tests.conftest import clean_database, mocked_mail
from tests.files.api_entreprise import MOCKED_SIREN_ENTREPRISES_API_RETURN
from tests.test_utils import create_user, create_booking, create_offerer, create_venue, create_offer_with_thing_product, \
    create_stock_from_offer, \
    create_email, create_offer_with_event_product
from utils.human_ids import humanize
from utils.mailing import parse_email_addresses, \
    send_raw_email, resend_email, \
    compute_email_html_part_and_recipients, \
    extract_users_information_from_bookings, build_pc_pro_offer_link, format_booking_date_for_email, \
    format_booking_hours_for_email, make_reset_password_email


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
        users_informations = extract_users_information_from_bookings(stock.bookings)

        # Then
        assert users_informations == [
            {'firstName': 'Jean', 'lastName': 'Dupont', 'email': 'test%40example.com', 'contremarque': 'HELLO0'},
            {'firstName': 'Jaja', 'lastName': 'Dudu', 'email': 'mail%40example.com', 'contremarque': 'HELLO1'},
            {'firstName': 'Toto', 'lastName': 'Titi', 'email': 'mail%40example.com', 'contremarque': 'HELLO2'}
        ]


class BuildPcProOfferLinkTest:
    @patch('utils.mailing.PRO_URL', 'http://pcpro.com')
    @clean_database
    def test_should_return_pc_pro_offer_link(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        PcObject.save(offer)
        offer_id = humanize(offer.id)
        venue_id = humanize(venue.id)
        offerer_id = humanize(offerer.id)

        # When
        pc_pro_url = build_pc_pro_offer_link(offer)

        # Then
        assert pc_pro_url == f'http://pcpro.com/offres/{offer_id}?lieu={venue_id}&structure={offerer_id}'


class BuildRecipientsListTest:
    @patch('domain.user_emails.ADMINISTRATION_EMAIL_ADDRESS', 'admin@pass.com')
    def test_should_return_admin_email_and_booking_email_when_booking_email_on_offer_exists(self):
        # Given
        user = create_user()
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock = create_stock_from_offer(offer)
        booking = create_booking(user, stock)

        # When
        recipients = build_recipients_list(booking)

        # Then
        assert recipients == 'booking.email@test.com, admin@pass.com'

    @patch('domain.user_emails.ADMINISTRATION_EMAIL_ADDRESS', 'admin@pass.com')
    def test_should_return_only_admin_email_when_offer_has_no_booking_email(self):
        # Given
        user = create_user()
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue, booking_email=None)
        stock = create_stock_from_offer(offer)
        booking = create_booking(user, stock)

        # When
        recipients = build_recipients_list(booking)

        # Then
        assert recipients == 'admin@pass.com'


class FormatDateAndHourForEmailTest:
    def test_should_return_formatted_event_beginningDatetime_when_offer_is_an_event(self):
        # Given
        user = create_user()
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_event_product(venue)
        stock = create_stock_from_offer(offer, beginning_datetime=datetime(2019, 10, 9, 10, 20, 00))
        booking = create_booking(user, stock)

        # When
        formatted_date = format_booking_date_for_email(booking)

        # Then
        assert formatted_date == '09-Oct-2019'

    def test_should_return_empty_string_when_offer_is_not_an_event(self):
        # Given
        user = create_user()
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock = create_stock_from_offer(offer, beginning_datetime=None)
        booking = create_booking(user, stock)

        # When
        formatted_date = format_booking_date_for_email(booking)

        # Then
        assert formatted_date == ''


class FormatBookingHoursForEmailTest:
    def test_should_return_hours_and_minutes_from_beginningDatetime_when_contains_hours(self):
        # Given
        user = create_user()
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_event_product(venue)
        stock = create_stock_from_offer(offer, beginning_datetime=datetime(2019, 10, 9, 10, 20, 00))
        booking = create_booking(user, stock)

        # When
        formatted_date = format_booking_hours_for_email(booking)

        # Then
        assert formatted_date == '12h20'

    def test_should_return_only_hours_from_event_beginningDatetime_when_oclock(self):
        # Given
        user = create_user()
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_event_product(venue)
        stock = create_stock_from_offer(offer, beginning_datetime=datetime(2019, 10, 9, 13, 00, 00))
        booking = create_booking(user, stock)

        # When
        formatted_date = format_booking_hours_for_email(booking)

        # Then
        assert formatted_date == '15h'

    def test_should_return_empty_string_when_offer_is_not_an_event(self):
        # Given
        user = create_user()
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock = create_stock_from_offer(offer)
        booking = create_booking(user, stock)

        # When
        formatted_date = format_booking_hours_for_email(booking)

        # Then
        assert formatted_date == ''


class MakeResetPasswordTest:
    def test_make_reset_password_email_generates_an_html_email_with_a_reset_link(app):
        # given
        user = create_user(public_name='bobby', email='bobby@test.com', reset_password_token='AZ45KNB99H')

        # when
        email = make_reset_password_email(user, 'app-jeune')

        # then
        html = BeautifulSoup(email['Html-part'], features="html.parser")
        assert html.select('a.reset-password-link')[
                   0].text.strip() == 'app-jeune/mot-de-passe-perdu?token=AZ45KNB99H'
        assert html.select('div.validity-info')[
                   0].text.strip() == 'Le lien est valable 24h. Au delà de ce délai, vous devrez demander une nouvelle réinitialisation.'


def _remove_whitespaces(text):
    text = re.sub('\n\s+', ' ', text)
    text = re.sub('\n', '', text)
    return text
