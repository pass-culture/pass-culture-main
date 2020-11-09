from datetime import datetime
from datetime import timezone
import re
from unittest.mock import MagicMock
from unittest.mock import patch

from freezegun import freeze_time
import pytest
from requests import Timeout

from pcapi.domain.user_emails import _build_recipients_list
from pcapi.model_creators.generic_creators import create_booking
from pcapi.model_creators.generic_creators import create_offerer
from pcapi.model_creators.generic_creators import create_user
from pcapi.model_creators.generic_creators import create_user_offerer
from pcapi.model_creators.generic_creators import create_venue
from pcapi.model_creators.specific_creators import create_offer_with_event_product
from pcapi.model_creators.specific_creators import create_offer_with_thing_product
from pcapi.model_creators.specific_creators import create_stock_from_offer
from pcapi.models import ThingType
from pcapi.models.email import Email
from pcapi.models.email import EmailStatus
from pcapi.repository import repository
from pcapi.utils.human_ids import humanize
from pcapi.utils.mailing import add_contact_informations
from pcapi.utils.mailing import add_contact_to_list
from pcapi.utils.mailing import build_pc_pro_offer_link
from pcapi.utils.mailing import compute_email_html_part_and_recipients
from pcapi.utils.mailing import create_contact
from pcapi.utils.mailing import extract_users_information_from_bookings
from pcapi.utils.mailing import format_booking_date_for_email
from pcapi.utils.mailing import format_booking_hours_for_email
from pcapi.utils.mailing import make_validation_email_object
from pcapi.utils.mailing import parse_email_addresses
from pcapi.utils.mailing import send_raw_email

from tests.conftest import mocked_mail
from tests.files.api_entreprise import MOCKED_SIREN_ENTREPRISES_API_RETURN


def get_mocked_response_status_200(entity):
    response = MagicMock(status_code=200, text='')
    response.json = MagicMock(return_value=MOCKED_SIREN_ENTREPRISES_API_RETURN)
    return response


def get_by_siren_stub(offerer):
    return {
        "unite_legale": {
            "siren": "395251440",
            "etablissement_siege": {
                "siren": "395251440",
                "siret": "39525144000016",
                "etablissement_siege": "true",
            },
        },
        "other_etablissements_sirets": ["39525144000032", "39525144000065"]
    }


@mocked_mail
@pytest.mark.usefixtures("db_session")
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
@pytest.mark.usefixtures("db_session")
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
        with patch('pcapi.utils.mailing.feature_send_mail_to_users_enabled', return_value=True):
            html, to = compute_email_html_part_and_recipients("my_html", "plop@plop.com")

        # then
        assert html == "my_html"
        assert to == "plop@plop.com"

    def test_accepts_list_of_strings_as_to(self, app):
        # when
        with patch('pcapi.utils.mailing.feature_send_mail_to_users_enabled', return_value=True):
            html, to = compute_email_html_part_and_recipients("my_html", ["plop@plop.com", "plip@plip.com"])

        # then
        assert html == "my_html"
        assert to == "plop@plop.com, plip@plip.com"


class GetUsersInformationFromStockBookingsTest:
    def test_returns_correct_users_information_from_bookings_stock(self):
        # Given
        user_1 = create_user(can_book_free_offers=True, departement_code='93', email='test@example.com',
                             first_name='Jean', last_name='Dupont', public_name='Test')
        user_2 = create_user(can_book_free_offers=True, departement_code='93', email='mail@example.com',
                             first_name='Jaja', last_name='Dudu', public_name='Test')
        user_3 = create_user(can_book_free_offers=True, departement_code='93', email='mail@example.com',
                             first_name='Toto', last_name='Titi', public_name='Test')
        offerer = create_offerer()
        venue = create_venue(offerer=offerer, name='Test offerer', booking_email='reservations@test.fr',
                             is_virtual=True, siret=None)
        thing_offer = create_offer_with_thing_product(venue, thing_type=ThingType.LIVRE_EDITION)
        beginning_datetime = datetime(2019, 11, 6, 14, 00, 0, tzinfo=timezone.utc)
        stock = create_stock_from_offer(thing_offer, price=0, quantity=10, beginning_datetime=beginning_datetime)
        booking_1 = create_booking(user=user_1, stock=stock, venue=venue, token='HELLO0')
        booking_2 = create_booking(user=user_2, stock=stock, venue=venue, token='HELLO1')
        booking_3 = create_booking(user=user_3, stock=stock, venue=venue, token='HELLO2')

        stock.bookings = [booking_1, booking_2, booking_3]

        # When
        users_informations = extract_users_information_from_bookings(stock.bookings)

        # Then
        assert users_informations == [
            {'firstName': 'Jean', 'lastName': 'Dupont', 'email': 'test@example.com', 'contremarque': 'HELLO0'},
            {'firstName': 'Jaja', 'lastName': 'Dudu', 'email': 'mail@example.com', 'contremarque': 'HELLO1'},
            {'firstName': 'Toto', 'lastName': 'Titi', 'email': 'mail@example.com', 'contremarque': 'HELLO2'}
        ]


class BuildPcProOfferLinkTest:
    @patch('pcapi.utils.mailing.PRO_URL', 'http://pcpro.com')
    @pytest.mark.usefixtures("db_session")
    def test_should_return_pc_pro_offer_link(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        repository.save(offer)
        offer_id = humanize(offer.id)
        venue_id = humanize(venue.id)
        offerer_id = humanize(offerer.id)

        # When
        pc_pro_url = build_pc_pro_offer_link(offer)

        # Then
        assert pc_pro_url == f'http://pcpro.com/offres/{offer_id}?lieu={venue_id}&structure={offerer_id}'


class BuildRecipientsListTest:
    def test_should_return_admin_email_and_booking_email_when_booking_email_on_offer_exists(self):
        # Given
        user = create_user()
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue=venue, booking_email='booking.email@example.com')
        stock = create_stock_from_offer(offer)
        booking = create_booking(user=user, stock=stock)

        # When
        recipients = _build_recipients_list(booking)

        # Then
        assert recipients == 'booking.email@example.com, administration@example.com'

    def test_should_return_only_admin_email_when_offer_has_no_booking_email(self):
        # Given
        user = create_user()
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue, booking_email=None)
        stock = create_stock_from_offer(offer)
        booking = create_booking(user=user, stock=stock)

        # When
        recipients = _build_recipients_list(booking)

        # Then
        assert recipients == 'administration@example.com'


class FormatDateAndHourForEmailTest:
    def test_should_return_formatted_event_beginningDatetime_when_offer_is_an_event(self):
        # Given
        user = create_user()
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_event_product(venue)
        stock = create_stock_from_offer(offer, beginning_datetime=datetime(2019, 10, 9, 10, 20, 00))
        booking = create_booking(user=user, stock=stock)

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
        booking = create_booking(user=user, stock=stock)

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
        booking = create_booking(user=user, stock=stock)

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
        booking = create_booking(user=user, stock=stock)

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
        booking = create_booking(user=user, stock=stock)

        # When
        formatted_date = format_booking_hours_for_email(booking)

        # Then
        assert formatted_date == ''


class MakeValidationEmailObjectTest:
    def test_should_return_subject_with_correct_departement_code(self):
        # Given
        user = create_user(departement_code='93')
        offerer = create_offerer(postal_code='95490')
        user_offerer = create_user_offerer(user=user, offerer=offerer)

        # When
        email_object = make_validation_email_object(user_offerer=user_offerer, offerer=offerer,
                                                    get_by_siren=get_by_siren_stub)

        # Then
        assert email_object.get("Subject") == '95 - inscription / rattachement PRO à valider : Test Offerer'


def _remove_whitespaces(text):
    text = re.sub(r'\n\s+', ' ', text)
    text = re.sub(r'\n', '', text)
    return text


class SendRawEmailTest:
    def test_should_call_mailjet_api_to_send_emails(self, app):
        # Given
        data = {'data': {}}
        app.mailjet_client.send.create = MagicMock()
        app.mailjet_client.send.create.return_value = MagicMock(status_code=200)

        # When
        result = send_raw_email(data)

        # Then
        app.mailjet_client.send.create.assert_called_once_with(data=data)
        assert result is True

    def test_should_return_false_when_mailjet_status_code_is_not_200(self, app):
        # Given
        data = {'data': {}}
        app.mailjet_client.send.create = MagicMock()
        app.mailjet_client.send.create.return_value = MagicMock(status_code=400)

        # When
        result = send_raw_email(data)

        # Then
        app.mailjet_client.send.create.assert_called_once_with(data=data)
        assert result is False

    def test_should_catch_errors_when_mailjet_api_is_not_reachable(self, app):
        # Given
        data = {'data': {}}
        app.mailjet_client.send.create = MagicMock()
        app.mailjet_client.send.create.side_effect = Timeout

        # When
        result = send_raw_email(data)

        # Then
        app.mailjet_client.send.create.assert_called_once_with(data=data)
        assert result is False


class CreateContactTest:
    def test_should_call_mailjet_api_to_create_contact(self, app):
        # Given
        data = {'Email': 'beneficiary@example.com'}
        create_contact_response = {
            'Data': [{
                'ID': '123',
                'Name': 'BeneficiaryName',
                'Email': 'beneficiary@example.com'
            }]
        }

        app.mailjet_client.contact.create = MagicMock()
        app.mailjet_client.contact.create.return_value = create_contact_response

        # When
        result = create_contact('beneficiary@example.com')

        # Then
        app.mailjet_client.contact.create.assert_called_once_with(data=data)
        assert result == create_contact_response


class AddContactInformationsTest:
    def test_should_call_mailjet_api_to_add_contact_informations(self, app):
        # Given
        data = {
            'Data': [
                {
                    "Name": "date_de_naissance",
                    "Value": 1046822400
                },
                {
                    "Name": "département",
                    "Value": "93"
                }
            ]
        }
        add_contact_infos_response = {
            'Data': [{
                'ID': '123',
                'Name': 'BeneficiaryName',
                'Email': 'beneficiary@example.com'
            }]
        }
        app.mailjet_client.contactdata.update = MagicMock()
        app.mailjet_client.contactdata.update.return_value = add_contact_infos_response

        # When
        result = add_contact_informations('beneficiary@example.com', 1046822400, '93')

        # Then
        app.mailjet_client.contactdata.update.assert_called_once_with(id='beneficiary@example.com', data=data)
        assert result == add_contact_infos_response

class AddContactToListTest:
    def test_should_call_mailjet_api_to_add_contact_to_list(self, app):
        # Given
        data = {
            'IsUnsubscribed': "false",
            'ContactAlt': 'beneficiary@example.com',
            'ListID': '12345',
        }

        add_to_list_response = {
            'Data': [{
                'ID': '123',
                'ListID': 'mailjetListId',
                'ListName': 'mailjetListName'
            }]
        }

        app.mailjet_client.listrecipient.create = MagicMock()
        app.mailjet_client.listrecipient.create.return_value = add_to_list_response

        # When
        result = add_contact_to_list('beneficiary@example.com', '12345')

        # Then
        app.mailjet_client.listrecipient.create.assert_called_once_with(data=data)
        assert result == add_to_list_response

