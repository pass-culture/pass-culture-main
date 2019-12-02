import re
import secrets
from datetime import datetime, timezone, timedelta
from unittest.mock import MagicMock, patch, Mock

from bs4 import BeautifulSoup
from freezegun import freeze_time

from models import PcObject, Offerer, ThingType, EventType, User
from models.db import db
from models.email import Email, EmailStatus
from tests.conftest import clean_database, mocked_mail
from tests.files.api_entreprise import MOCKED_SIREN_ENTREPRISES_API_RETURN
from tests.test_utils import create_stock_with_event_offer, create_stock_with_thing_offer, \
    create_user, create_booking, create_user_offerer, \
    create_offerer, create_venue, create_offer_with_thing_product, create_offer_with_event_product, \
    create_stock_from_offer, \
    create_stock_from_event_occurrence, create_event_occurrence, create_product_with_thing_type, create_mocked_bookings, \
    create_email, create_deposit
from utils.mailing import get_activation_email_data, make_batch_cancellation_email, \
    make_beneficiaries_import_email, \
    make_final_recap_email_for_stock_with_event, \
    make_offer_creation_notification_email, \
    make_offerer_driven_cancellation_email_for_offerer, \
    make_offerer_booking_recap_email_after_user_action, \
    make_offerer_driven_cancellation_email_for_user, \
    make_payment_details_email, \
    make_payment_message_email, \
    make_payments_report_email, \
    make_user_booking_recap_email, \
    make_user_validation_email, \
    make_pro_user_waiting_for_validation_by_admin_email, \
    make_validation_confirmation_email, \
    make_venue_validation_confirmation_email, \
    make_venue_validation_email, \
    make_wallet_balances_email, \
    parse_email_addresses, \
    send_raw_email, resend_email, \
    write_object_validation_email, compute_email_html_part_and_recipients, \
    get_offerer_booking_recap_email_data, make_reset_password_email_data, \
    ADMINISTRATION_EMAIL_ADDRESS, _get_users_information_from_bookings, make_reset_password_email

SUBJECT_USER_EVENT_BOOKING_CONFIRMATION_EMAIL = \
    'Confirmation de votre réservation pour Mains, sorts et papiers le 20 juillet 2019 à 14:00'

SUBJECT_USER_THING_BOOKING_CONFIRMATION_EMAIL = \
    'Confirmation de votre commande pour Test Book'

SUBJECT_USER_BOOKING_THING_CANCELLATION_EMAIL = \
    'Annulation de votre commande pour Test Book'

SUBJECT_USER_BOOKING_EVENT_CANCELLATION_EMAIL = \
    'Annulation de votre réservation pour Mains, sorts et papiers le 20 juillet 2019 à 14:00'


def get_mocked_response_status_200(entity):
    response = MagicMock(status_code=200, text='')
    response.json = MagicMock(return_value=MOCKED_SIREN_ENTREPRISES_API_RETURN)
    return response


@mocked_mail
@clean_database
def test_make_user_booking_event_recap_email_should_have_standard_subject_and_body(app):
    # Given
    beginning_datetime = datetime(2019, 7, 20, 12, 0, 0)
    end_datetime = beginning_datetime + timedelta(hours=1)
    booking_limit_datetime = beginning_datetime - timedelta(hours=1)
    offerer = create_offerer()
    venue = create_venue(offerer, 'Test offerer', 'reservations@test.fr', '123 rue test', '93000', 'Test city',
                         '93')
    stock = create_stock_with_event_offer(offerer=None, venue=venue, booking_limit_datetime=booking_limit_datetime,
                                          beginning_datetime=beginning_datetime, end_datetime=end_datetime)
    user = create_user('Test', departement_code='93', email='test@example.com', can_book_free_offers=True)
    booking = create_booking(user, stock, venue, None)
    booking.token = '56789'

    # When
    recap_email = make_user_booking_recap_email(booking, is_cancellation=False)

    # Then
    email_html = _remove_whitespaces(recap_email['Html-part'])
    recap_email_soup = BeautifulSoup(email_html, 'html.parser')
    mail_content = recap_email_soup.find("div", {"id": 'mail-content'}).text
    mail_greeting = recap_email_soup.find("p", {"id": 'mail-greeting'}).text
    mail_salutation = recap_email_soup.find("p", {"id": 'mail-salutation'}).text
    assert recap_email['Subject'] == SUBJECT_USER_EVENT_BOOKING_CONFIRMATION_EMAIL
    assert 'Bonjour Test,' in mail_greeting
    assert 'Nous vous confirmons votre réservation pour Mains, sorts et papiers' in recap_email_soup.find("div", {
        "id": 'mail-content'}).text
    assert 'le 20 juillet 2019 à 14:00' in mail_content
    assert 'proposé par Test offerer' in mail_content
    assert '(Adresse : 123 rue test, 93000 Test city).' in mail_content
    assert 'Votre code de réservation est le 56789.' in mail_content
    assert 'Cordialement,' in mail_salutation
    assert 'L\'équipe pass Culture' in mail_salutation


@mocked_mail
@clean_database
def test_make_user_booking_event_recap_email_should_have_standard_cancellation_body_and_subject(app):
    # Given
    beginning_datetime = datetime(2019, 7, 20, 12, 0, 0)
    end_datetime = beginning_datetime + timedelta(hours=1)
    booking_limit_datetime = beginning_datetime - timedelta(hours=1)
    offerer = create_offerer()
    venue = create_venue(offerer, 'Test offerer', 'reservations@test.fr', '123 rue test', '93000', 'Test city',
                         '93')
    stock = create_stock_with_event_offer(offerer=None, venue=venue, beginning_datetime=beginning_datetime,
                                          end_datetime=end_datetime, booking_limit_datetime=booking_limit_datetime)
    user = create_user('Test', departement_code='93', email='test@example.com', can_book_free_offers=True)
    booking = create_booking(user, stock, venue, None)

    # When
    recap_email = make_user_booking_recap_email(booking, is_cancellation=True)

    # Then
    email_html = _remove_whitespaces(recap_email['Html-part'])
    recap_email_soup = BeautifulSoup(email_html, 'html.parser')
    mail_content = recap_email_soup.find('div', {"id": 'mail-content'}).text
    assert 'Votre réservation pour Mains, sorts et papiers,' in mail_content
    assert 'proposé par Test offerer' in mail_content
    assert 'le 20 juillet 2019 à 14:00,' in mail_content
    assert 'a bien été annulée.' in mail_content
    assert recap_email['Subject'] == SUBJECT_USER_BOOKING_EVENT_CANCELLATION_EMAIL


@mocked_mail
@clean_database
def test_maker_user_booking_thing_recap_email_should_have_standard_body_and_subject(app):
    # Given
    offerer = create_offerer()
    venue = create_venue(offerer, 'Test offerer', 'reservations@test.fr', '123 rue test', '93000', 'Test city',
                         '93')
    thing_offer = create_offer_with_thing_product(venue=None)
    stock = create_stock_with_thing_offer(offerer=None, venue=venue, offer=thing_offer)
    stock.offer.product.idAtProviders = '12345'
    user = create_user('Test', departement_code='93', email='test@example.com', can_book_free_offers=True)
    booking = create_booking(user, stock, venue, None)
    booking.token = '56789'

    # When
    recap_email = make_user_booking_recap_email(booking, is_cancellation=False)

    # Then
    email_html = _remove_whitespaces(recap_email['Html-part'])
    recap_email_soup = BeautifulSoup(email_html, 'html.parser')
    mail_content = recap_email_soup.find("div", {"id": 'mail-content'}).text
    assert 'Nous vous confirmons votre commande pour Test Book (Ref: 12345),' in mail_content
    assert 'proposé par Test offerer.' in mail_content
    assert recap_email['Subject'] == SUBJECT_USER_THING_BOOKING_CONFIRMATION_EMAIL


@mocked_mail
@clean_database
def test_make_user_booking_thing_recap_email_should_have_standard_cancellation_body_and_subject(app):
    # Given
    offerer = create_offerer()
    venue = create_venue(offerer, 'Test offerer', 'reservations@test.fr', '123 rue test', '93000', 'Test city',
                         '93')
    thing_offer = create_offer_with_thing_product(venue=None)
    stock = create_stock_with_thing_offer(offerer=None, venue=venue, offer=thing_offer)
    stock.offer.product.idAtProviders = '12345'
    user = create_user('Test', departement_code='93', email='test@example.com', can_book_free_offers=True)
    booking = create_booking(user, stock, venue, None)

    # When
    recap_email = make_user_booking_recap_email(booking, is_cancellation=True)

    # Then
    html_email = _remove_whitespaces(recap_email['Html-part'])
    recap_email_soup = BeautifulSoup(html_email, 'html.parser')
    assert 'Votre commande pour Test Book (Ref: 12345),' in recap_email_soup.find("div",
                                                                                  {"id": 'mail-content'}).text
    assert recap_email['Subject'] == SUBJECT_USER_BOOKING_THING_CANCELLATION_EMAIL


@mocked_mail
@clean_database
def test_offerer_recap_email_past_offer_without_booking(app):
    # Given
    beginning_datetime = datetime(2017, 7, 20, 12, 0, 0)
    end_datetime = beginning_datetime + timedelta(hours=1)
    booking_limit_datetime = beginning_datetime - timedelta(days=1)

    expected_subject = '[Réservations] Récapitulatif pour Mains, sorts et papiers le 20 juillet 2017 à 14:00'
    offerer = create_offerer()
    venue = create_venue(offerer, 'Test offerer', 'reservations@test.fr', '123 rue test', '93000', 'Test city', '93')
    stock = create_stock_with_event_offer(offerer=None, venue=venue, beginning_datetime=beginning_datetime,
                                          end_datetime=end_datetime, booking_limit_datetime=booking_limit_datetime)

    # When
    with patch('utils.mailing.booking_queries.find_ongoing_bookings_by_stock', return_value=[]):
        recap_email = make_final_recap_email_for_stock_with_event(stock)

    # Then
    mail_html = _remove_whitespaces(recap_email['Html-part'])
    recap_email_soup = BeautifulSoup(mail_html, 'html.parser')
    recap = recap_email_soup.find("p", {"id": 'recap'}).text
    no_recap = recap_email_soup.find("p", {"id": 'no-recap'}).text
    assert recap_email['Subject'] == expected_subject
    assert 'Voici le récapitulatif final des réservations :' in recap
    assert '(total 0) pour Mains, sorts et papiers' in recap
    assert 'Aucune réservation' in no_recap


@mocked_mail
@clean_database
def test_offerer_recap_email_past_offer_with_booking(app):
    # Given
    beginning_datetime = datetime(2017, 7, 20, 12, 0, 0)
    end_datetime = beginning_datetime + timedelta(hours=1)
    booking_limit_datetime = beginning_datetime - timedelta(days=1)
    offerer = create_offerer()
    venue = create_venue(offerer, 'Test offerer', 'reservations@test.fr', '123 rue test', '93000', 'Test city', '93')
    stock = create_stock_with_event_offer(offerer=None, venue=venue, beginning_datetime=beginning_datetime,
                                          end_datetime=end_datetime, booking_limit_datetime=booking_limit_datetime)
    user = create_user('Test', first_name='Jean', last_name='Dupont', departement_code='93', email='test@example.com',
                       can_book_free_offers=True)
    booking = create_booking(user, stock, venue, None)
    booking.token = '56789'
    stock.bookings = [booking]

    # When
    with patch('utils.mailing.booking_queries.find_ongoing_bookings_by_stock', return_value=[booking]):
        recap_email = make_final_recap_email_for_stock_with_event(stock)

    # Then
    email_html = _remove_whitespaces(recap_email['Html-part'])
    recap_email_soup = BeautifulSoup(email_html, 'html.parser')
    recap_html = recap_email_soup.find('p', {'id': 'recap'}).text
    assert 'Voici le récapitulatif final des réservations :' in recap_html
    assert '(total 1) pour Mains, sorts et papiers' in recap_html
    assert 'le 20 juillet 2017 à 14:00,' in recap_html
    assert 'proposé par Test offerer (Adresse : 123 rue test, 93000 Test city).' in recap_html
    recap_table_html = recap_email_soup.find('table', {'id': 'recap-table'}).text
    assert 'Prénom' in recap_table_html
    assert 'Nom' in recap_table_html
    assert 'Email' in recap_table_html
    assert 'Code réservation' in recap_table_html
    assert 'Jean' in recap_table_html
    assert 'Dupont' in recap_table_html
    assert 'test@example.com' in recap_table_html
    assert '56789' in recap_table_html


@mocked_mail
@clean_database
def test_offerer_recap_email_does_not_send_cancelled_or_used_booking(app):
    # Given
    venue = create_venue(Offerer(), 'Test offerer', 'reservations@test.fr', '123 rue test', '93000', 'Test city', '93')
    stock = create_stock_with_event_offer(offerer=Offerer(), venue=venue)

    user1 = create_user('Test1', first_name='Lucie', last_name='Dubois', departement_code='93',
                        email='test@example.com',
                        can_book_free_offers=True)
    booking1 = create_booking(user1, stock)

    user2 = create_user('Test2', first_name='Jean', last_name='Dupont', departement_code='93', email='test@example.com',
                        can_book_free_offers=True)
    booking2 = create_booking(user2, stock)

    ongoing_bookings = [booking1, booking2]

    # When
    with patch('utils.mailing.booking_queries.find_ongoing_bookings_by_stock', return_value=ongoing_bookings):
        recap_email = make_final_recap_email_for_stock_with_event(stock)

    # Then
    email_html = BeautifulSoup(recap_email['Html-part'], 'html.parser')
    html_recap_table = str(email_html.find("table", {"id": "recap-table"}))
    assert '<td>Lucie</td>' in html_recap_table
    assert '<td>Jean</td>' in html_recap_table
    assert '<td>Cancelled</td>' not in html_recap_table
    assert '<td>Used</td>' not in html_recap_table


@mocked_mail
@clean_database
def test_offerer_recap_email_has_unsubscribe_options(app):
    # Given
    venue = create_venue(Offerer(), 'Test offerer', 'reservations@test.fr', '123 rue test', '93000', 'Test city', '93')
    stock = create_stock_with_event_offer(offerer=Offerer(), venue=venue)

    user1 = create_user('Test1', departement_code='93', email='test@example.com', can_book_free_offers=True)
    booking1 = create_booking(user1, stock)

    user2 = create_user('Test2', departement_code='93', email='test@example.com', can_book_free_offers=True)
    booking2 = create_booking(user2, stock)

    ongoing_bookings = [booking1, booking2]

    # When
    with patch('utils.mailing.booking_queries.find_ongoing_bookings_by_stock', return_value=ongoing_bookings):
        recap_email = make_final_recap_email_for_stock_with_event(stock)

    # Then
    email_html = _remove_whitespaces(recap_email['Html-part'])
    recap_email_soup = BeautifulSoup(email_html, 'html.parser')
    assert 'Vous recevez ce message parce que votre adresse e-mail est renseignée comme adresse de contact sur votre offre.' in recap_email_soup.find(
        'p', {'id': 'unsubscribe-option'}).text
    assert 'Si vous souhaitez modifier l’adresse de contact cliquez ici : être notifié des réservations à une autre adresse e-mail.' in recap_email_soup.find(
        'p', {'id': 'unsubscribe-option'}).text
    assert 'Si vous ne souhaitez plus recevoir de notifications de réservations par e-mail, cliquez ici : ne plus recevoir les notifications de réservations.' in recap_email_soup.find(
        'p', {'id': 'unsubscribe-option'}).text
    assert 'mailto:support@passculture.app?subject=Changer%20l%27adresse%20e-mail%20de%20notification%20des%20r%C3%A9servations' == \
           recap_email_soup.find('a', {'id': 'change-email'})['href']
    assert 'mailto:support@passculture.app?subject=Ne%20plus%20recevoir%20les%20notifications%20de%20r%C3%A9servations' == \
           recap_email_soup.find('a', {'id': 'remove-email'})['href']


@mocked_mail
@clean_database
def test_write_object_validation_email_should_have_some_specific_information(app):
    # Given
    validation_token = secrets.token_urlsafe(20)
    offerer = create_offerer(siren='732075312', address='122 AVENUE DE FRANCE', city='Paris', postal_code='75013',
                             name='Accenture', validation_token=validation_token)

    user = create_user(public_name='Test', departement_code='75', email='user@accenture.com',
                       can_book_free_offers=False, validation_token=validation_token)

    user_offerer = create_user_offerer(user, offerer, validation_token)

    # When
    email = write_object_validation_email(offerer, user_offerer, get_by_siren=get_mocked_response_status_200)

    # Then
    html = BeautifulSoup(email['Html-part'], features="html.parser")
    assert html.h1.text == 'Inscription ou rattachement PRO à valider'

    div_offerer = html.select('div.offerer')[0]
    assert div_offerer.h2.text == 'Nouvelle structure :'
    assert div_offerer.h3.text == 'Infos API entreprise :'
    assert div_offerer.strong.a['href'] == 'http://localhost/validate?modelNames=Offerer&token={}'.format(
        offerer.validationToken)
    assert div_offerer.strong.a.text == 'cliquez ici'

    div_user_offerer = html.select('div.user_offerer')[0]
    assert div_user_offerer.h2.text == 'Nouveau rattachement :'
    assert div_user_offerer.h3.text == 'Utilisateur :'
    assert div_user_offerer.strong.a['href'] == 'http://localhost/validate?modelNames=UserOfferer&token={}'.format(
        user_offerer.validationToken)
    assert div_user_offerer.strong.a.text == 'cliquez ici'

    offerer_data = div_offerer.select('pre.offerer-data')[0].text
    assert "'address': '122 AVENUE DE FRANCE'" in offerer_data
    assert "'city': 'Paris'" in offerer_data
    assert "'name': 'Accenture'" in offerer_data
    assert "'postalCode': '75013'" in offerer_data
    assert "'siren': '732075312'" in offerer_data
    assert "'validationToken': '{}'".format(validation_token) in offerer_data

    api_entreprise_data = div_offerer.select('pre.api-entreprise-data')[0].text
    assert "'numero_tva_intra': 'FR60732075312'" in api_entreprise_data
    assert "'other_etablissements_sirets': ['73207531200213', '73207531200197', '73207531200171']".replace(' ',
                                                                                                           '').replace(
        '\n', '') in api_entreprise_data.replace(' ', '').replace('\n', '')
    assert 'siege_social' in api_entreprise_data


@mocked_mail
@clean_database
def test_write_object_validation_email_does_not_include_validation_link_if_user_offerer_is_already_validated(app):
    # Given
    validation_token = secrets.token_urlsafe(20)
    offerer = create_offerer(siren='732075312', address='122 AVENUE DE FRANCE', city='Paris', postal_code='75013',
                             name='Accenture', validation_token=validation_token)

    user = create_user(public_name='Test', departement_code='75', email='user@accenture.com',
                       can_book_free_offers=False, validation_token=validation_token)

    user_offerer = create_user_offerer(user, offerer, validation_token=None)

    # When
    email = write_object_validation_email(offerer, user_offerer, get_by_siren=get_mocked_response_status_200)

    # Then
    html = BeautifulSoup(email['Html-part'], features="html.parser")
    assert not html.select('div.user_offerer strong.validation a')
    assert html.select('div.user_offerer h2')[0].text == 'Rattachement :'


@mocked_mail
@clean_database
def test_write_object_validation_email_does_not_include_validation_link_if_offerer_is_already_validated(app):
    # Given
    validation_token = secrets.token_urlsafe(20)
    offerer = create_offerer(siren='732075312', address='122 AVENUE DE FRANCE', city='Paris', postal_code='75013',
                             name='Accenture', validation_token=None)

    user = create_user(public_name='Test', departement_code='75', email='user@accenture.com',
                       can_book_free_offers=False, validation_token=validation_token)

    user_offerer = create_user_offerer(user, offerer, validation_token)

    # When
    email = write_object_validation_email(offerer, user_offerer, get_by_siren=get_mocked_response_status_200)

    # Then
    html = BeautifulSoup(email['Html-part'], features="html.parser")
    assert not html.select('div.offerer strong.validation a')
    assert html.select('div.offerer h2')[0].text == 'Structure :'


@mocked_mail
@clean_database
def test_validation_email_should_not_return_clearTextPassword(app):
    # Given
    validation_token = secrets.token_urlsafe(20)
    offerer = create_offerer(siren='732075312', address='122 AVENUE DE FRANCE', city='Paris', postal_code='75013',
                             name='Accenture', validation_token=validation_token)

    user = create_user(public_name='Test', departement_code='75', email='user@accenture.com',
                       can_book_free_offers=False, validation_token=validation_token)

    user_offerer = create_user_offerer(user, offerer, validation_token)

    mocked_api_entreprises = get_mocked_response_status_200

    # When
    email = write_object_validation_email(offerer, user_offerer, get_by_siren=mocked_api_entreprises)

    # Then
    email_html_soup = BeautifulSoup(email['Html-part'], features="html.parser")
    assert 'clearTextPassword' not in str(email_html_soup)
    assert 'totallysafepsswd' not in str(email_html_soup)


@clean_database
def test_make_offerer_driven_cancellation_email_for_user_event(app):
    # Given
    beginning_datetime = datetime(2019, 7, 20, 12, 0, 0, tzinfo=timezone.utc)
    end_datetime = beginning_datetime + timedelta(hours=1)
    booking_limit_datetime = beginning_datetime - timedelta(hours=1)

    user = create_user(public_name='John Doe')
    offerer = create_offerer(name='Test offerer')
    venue = create_venue(offerer)
    offer = create_offer_with_event_product(venue, event_name='Mains, sorts et papiers')
    event_occurrence = create_event_occurrence(offer, beginning_datetime=beginning_datetime, end_datetime=end_datetime)
    stock = create_stock_from_event_occurrence(event_occurrence, price=20, available=10,
                                               booking_limit_date=booking_limit_datetime)
    booking = create_booking(user, stock)

    # When
    with patch('utils.mailing.booking_queries.find_ongoing_bookings_by_stock', return_value=[]):
        email = make_offerer_driven_cancellation_email_for_user(booking)

    # Then
    email_html = BeautifulSoup(email['Html-part'], 'html.parser')
    mail_content = str(email_html.find("div", {"id": "mail-content"}))
    assert 'réservation' in mail_content
    assert 'pour Mains, sorts et papiers' in mail_content
    assert 'le 20 juillet 2019 à 14:00' in mail_content
    assert 'proposé par Test offerer' in mail_content
    assert 'recrédité de 20 euros' in mail_content
    assert email[
               'Subject'] == 'Votre réservation pour Mains, sorts et papiers, proposé par Test offerer a été annulée par l\'offreur'


@clean_database
def test_make_offerer_driven_cancellation_email_for_user_thing(app):
    # Given
    user = create_user(public_name='John Doe')
    offerer = create_offerer(name='Test offerer')
    venue = create_venue(offerer)
    offer = create_offer_with_thing_product(venue, thing_name='Test Book')
    stock = create_stock_from_offer(offer, price=15, available=10)
    booking = create_booking(user, stock, quantity=2)

    # When
    with patch('utils.mailing.booking_queries.find_ongoing_bookings_by_stock', return_value=[]):
        email = make_offerer_driven_cancellation_email_for_user(booking)

    # Then
    email_html = BeautifulSoup(email['Html-part'], 'html.parser')
    mail_content = str(email_html.find("div", {"id": "mail-content"}))
    assert 'commande' in mail_content
    assert 'pour Test Book' in mail_content
    assert 'proposé par Test offerer' in mail_content
    assert 'recrédité de 30 euros' in mail_content
    assert email[
               'Subject'] == 'Votre commande pour Test Book, proposé par Test offerer a été annulée par l\'offreur'


@clean_database
def test_make_offerer_driven_cancellation_email_for_offerer_event_when_no_other_booking(app):
    # Given
    beginning_datetime = datetime(2019, 7, 20, 12, 0, 0, tzinfo=timezone.utc)
    end_datetime = beginning_datetime + timedelta(hours=1)
    booking_limit_datetime = beginning_datetime - timedelta(hours=1)

    user = create_user(public_name='John Doe', email='john@doe.fr')
    offerer = create_offerer(name='Test offerer')
    venue = create_venue(offerer, name='Le petit théâtre', address='1 rue de la Libération', city='Montreuil',
                         postal_code='93100')
    offer = create_offer_with_event_product(venue, event_name='Le théâtre des ombres')
    event_occurrence = create_event_occurrence(offer, beginning_datetime=beginning_datetime, end_datetime=end_datetime)
    stock = create_stock_from_event_occurrence(event_occurrence, price=20, available=10,
                                               booking_limit_date=booking_limit_datetime)
    booking = create_booking(user, stock)

    # When
    with patch('utils.mailing.booking_queries.find_ongoing_bookings_by_stock', return_value=[]):
        email = make_offerer_driven_cancellation_email_for_offerer(booking)

    # Then
    email_html = BeautifulSoup(email['Html-part'], 'html.parser')
    html_action = str(email_html.find("p", {"id": "action"}))
    html_recap = str(email_html.find("p", {"id": "recap"}))
    html_no_recal = str(email_html.find("p", {"id": "no-recap"}))
    assert 'Vous venez d\'annuler' in html_action
    assert 'John Doe' in html_action
    assert 'john@doe.fr' in html_action
    assert 'pour Le théâtre des ombres' in html_recap
    assert 'proposé par Le petit théâtre' in html_recap
    assert 'le 20 juillet 2019 à 14:00' in html_recap
    assert '1 rue de la Libération' in html_recap
    assert 'Montreuil' in html_recap
    assert '93100' in html_recap
    assert 'Aucune réservation' in html_no_recal
    assert email[
               'Subject'] == 'Confirmation de votre annulation de réservation pour Le théâtre des ombres, proposé par Le petit théâtre'


@clean_database
def test_make_offerer_driven_cancellation_email_for_offerer_event_when_other_booking(app):
    # Given
    user1 = create_user(public_name='John Doe', first_name='John', last_name='Doe', email='john@doe.fr')
    user2 = create_user(public_name='Jane S.', first_name='Jane', last_name='Smith', email='jane@smith.fr')
    offerer = create_offerer(name='Test offerer')
    venue = create_venue(offerer, name='Le petit théâtre', address='1 rue de la Libération', city='Montreuil',
                         postal_code='93100')
    offer = create_offer_with_event_product(venue, event_name='Le théâtre des ombres')
    event_occurrence = create_event_occurrence(offer,
                                               beginning_datetime=datetime(2019, 7, 20, 12, 0, 0, tzinfo=timezone.utc))
    stock = create_stock_from_event_occurrence(event_occurrence, price=20, available=10)
    booking1 = create_booking(user1, stock, token='98765')
    booking2 = create_booking(user2, stock, token='12345')

    # When
    with patch('utils.mailing.booking_queries.find_ongoing_bookings_by_stock', return_value=[booking2]):
        email = make_offerer_driven_cancellation_email_for_offerer(booking1)

    # Then
    email_html = BeautifulSoup(email['Html-part'], 'html.parser')
    html_recap_table = email_html.find("table", {"id": "recap-table"}).text
    assert 'Prénom' in html_recap_table
    assert 'Nom' in html_recap_table
    assert 'Email' in html_recap_table
    assert 'Jane' in html_recap_table
    assert 'Smith' in html_recap_table
    assert 'jane@smith.fr' in html_recap_table
    assert '12345' in html_recap_table


@clean_database
def test_make_offerer_driven_cancellation_email_for_offerer_thing_and_already_existing_booking(app):
    # Given
    user = create_user(public_name='John Doe', first_name='John', last_name='Doe', email='john@doe.fr')
    offerer = create_offerer(name='Test offerer')
    venue = create_venue(offerer, name='La petite librairie', address='1 rue de la Libération', city='Montreuil',
                         postal_code='93100')
    thing_product = create_product_with_thing_type(thing_name='Le récit de voyage')
    offer = create_offer_with_thing_product(venue, thing_product)
    stock = create_stock_from_offer(offer, price=0, available=10)
    booking = create_booking(user, stock, token='12346')

    user2 = create_user(public_name='James Bond', first_name='James', last_name='Bond', email='bond@james.bond.uk')
    booking2 = create_booking(user2, stock, token='12345')
    ongoing_bookings = [booking2]

    # When
    with patch('utils.mailing.booking_queries.find_ongoing_bookings_by_stock', return_value=ongoing_bookings):
        email = make_offerer_driven_cancellation_email_for_offerer(booking)

    # Then
    email_html = BeautifulSoup(email['Html-part'], 'html.parser')
    html_action = str(email_html.find("p", {"id": "action"}))
    html_recap = email_html.find("p", {"id": "recap"}).text
    html_recap_table = email_html.find("table", {"id": "recap-table"}).text
    assert 'Vous venez d\'annuler' in html_action
    assert 'John Doe' in html_action
    assert 'john@doe.fr' in html_action
    assert 'pour Le récit de voyage' in html_recap
    assert 'proposé par La petite librairie' in html_recap
    assert '1 rue de la Libération' in html_recap
    assert 'Montreuil' in html_recap
    assert '93100' in html_recap
    assert 'James' in html_recap_table
    assert 'bond@james.bond.uk' in html_recap_table
    assert '12346' not in html_recap_table
    assert '12345' not in html_recap_table
    assert email[
               'Subject'] == 'Confirmation de votre annulation de réservation pour Le récit de voyage, proposé par La petite librairie'


@clean_database
def test_make_validation_confirmation_email_offerer_user_offerer_admin(app):
    # Given
    user = create_user(email='admin@letheatresas.com')
    offerer = create_offerer(name='Le Théâtre SAS')
    user_offerer = create_user_offerer(user, offerer, is_admin=True)
    # When
    with patch('utils.mailing.find_user_offerer_email', return_value='admin@letheatresas.com'):
        email = make_validation_confirmation_email(user_offerer, offerer)
    # Then
    email_html = BeautifulSoup(email['Html-part'], 'html.parser')
    html_validation_details = str(email_html.find('p', {'id': 'validation-details'}))
    assert 'Votre structure "Le Théâtre SAS"' in html_validation_details
    assert 'L\'utilisateur admin@letheatresas.com' in html_validation_details
    assert 'en tant qu\'administrateur' in html_validation_details
    assert email['FromName'] == 'pass Culture pro'
    assert email['Subject'] == 'Validation de votre structure et de compte administrateur rattaché'


@clean_database
def test_make_validation_confirmation_email_offerer_user_offerer_editor(app):
    # Given
    user = create_user(email='admin@letheatresas.com')
    offerer = create_offerer(name='Le Théâtre SAS')
    user_offerer = create_user_offerer(user, offerer)
    # When
    with patch('utils.mailing.find_user_offerer_email', return_value='editor@letheatresas.com'):
        email = make_validation_confirmation_email(user_offerer, offerer)
    # Then
    email_html = BeautifulSoup(email['Html-part'], 'html.parser')
    html_validation_details = str(email_html.find('p', {'id': 'validation-details'}))
    assert 'Votre structure "Le Théâtre SAS"' in html_validation_details
    assert 'L\'utilisateur editor@letheatresas.com' in html_validation_details
    assert 'en tant qu\'éditeur' in html_validation_details
    assert email['FromName'] == 'pass Culture pro'
    assert email['Subject'] == 'Validation de votre structure et de compte éditeur rattaché'


@clean_database
def test_make_validation_confirmation_email_user_offerer_editor(app):
    # Given
    user = create_user(email='admin@letheatresas.com')
    offerer = create_offerer(name='Le Théâtre SAS')
    user_offerer = create_user_offerer(user, offerer)
    # When
    with patch('utils.mailing.find_user_offerer_email', return_value='editor@letheatresas.com'):
        email = make_validation_confirmation_email(user_offerer, offerer=None)
    # Then
    email_html = BeautifulSoup(email['Html-part'], 'html.parser')
    html_validation_details = str(email_html.find('p', {'id': 'validation-details'}))
    assert 'Votre structure "Le Théâtre SAS"' not in html_validation_details
    assert 'L\'utilisateur editor@letheatresas.com a été validé' in html_validation_details
    assert 'en tant qu\'éditeur' in html_validation_details
    assert email['FromName'] == 'pass Culture pro'
    assert email['Subject'] == 'Validation de compte éditeur rattaché à votre structure'


@clean_database
def test_make_validation_confirmation_email_offerer(app):
    # Given
    offerer = create_offerer(name='Le Théâtre SAS')
    # When
    with patch('utils.mailing.find_user_offerer_email', return_value='admin@letheatresas.com'):
        email = make_validation_confirmation_email(user_offerer=None, offerer=offerer)
    # Then
    email_html = BeautifulSoup(email['Html-part'], 'html.parser')
    html_validation_details = str(email_html.find('p', {'id': 'validation-details'}))
    assert 'Votre structure "Le Théâtre SAS"' in html_validation_details
    assert 'L\'utilisateur' not in html_validation_details
    assert email['FromName'] == 'pass Culture pro'
    assert email['Subject'] == 'Validation de votre structure'


@clean_database
def test_make_make_batch_cancellation_email_for_case_event_occurrence(app):
    # Given
    bookings = create_mocked_bookings(num_bookings=4, venue_email='venue@email.com', name='Le récit de voyage')
    # When
    email = make_batch_cancellation_email(bookings, cancellation_case='event_occurrence')
    # Then
    email_html = _remove_whitespaces(email['Html-part'])
    parsed_email = BeautifulSoup(email_html, 'html.parser')
    html_action = str(parsed_email.find('p', {'id': 'action'}))
    html_recap = str(parsed_email.find('table', {'id': 'recap-table'}))
    assert 'Suite à votre suppression de date' in html_action
    assert 'Le récit de voyage' in html_action
    assert 'automatiquement annulées' in html_action
    for booking in bookings:
        assert '<td>%s</td>' % booking.user.email in html_recap
        assert '<td>%s</td>' % booking.user.firstName in html_recap
        assert '<td>%s</td>' % booking.user.lastName in html_recap
    assert email['FromEmail'] == 'support@passculture.app'
    assert email['FromName'] == 'pass Culture pro'
    assert email['Subject'] == 'Annulation de réservations pour Le récit de voyage'


@clean_database
def test_make_make_batch_cancellation_email_for_case_stock(app):
    # Given
    bookings = create_mocked_bookings(num_bookings=4, venue_email='venue@email.com', name='Le récit de voyage')
    # When
    email = make_batch_cancellation_email(bookings, cancellation_case='stock')
    # Then
    email_html = _remove_whitespaces(email['Html-part'])
    parsed_email = BeautifulSoup(email_html, 'html.parser')
    html_action = str(parsed_email.find('p', {'id': 'action'}))
    html_recap = str(parsed_email.find('table', {'id': 'recap-table'}))
    assert 'Suite à votre suppression de stock' in html_action
    assert 'Le récit de voyage' in html_action
    assert 'automatiquement annulées' in html_action
    for booking in bookings:
        assert '<td>%s</td>' % booking.user.email in html_recap
        assert '<td>%s</td>' % booking.user.firstName in html_recap
        assert '<td>%s</td>' % booking.user.lastName in html_recap
    assert email['FromEmail'] == 'support@passculture.app'
    assert email['FromName'] == 'pass Culture pro'
    assert email['Subject'] == 'Annulation de réservations pour Le récit de voyage'


@freeze_time('2018-10-15 09:21:34')
def test_make_payment_message_email_sends_a_xml_file_with_its_checksum_in_email_body(app):
    # Given
    xml = '<?xml version="1.0" encoding="UTF-8"?><Document xmlns="urn:iso:std:iso:20022:tech:xsd:pain.001.001.03"></Document>'
    checksum = b'\x16\x91\x0c\x11~Hs\xc5\x1a\xa3W1\x13\xbf!jq@\xea  <h&\xef\x1f\xaf\xfc\x7fO\xc8\x82'

    # When
    email = make_payment_message_email(xml, checksum)

    # Then
    assert email["FromEmail"] == 'support@passculture.app'
    assert email["FromName"] == "pass Culture Pro"
    assert email["Subject"] == "Virements XML pass Culture Pro - 2018-10-15"
    assert email["Attachments"] == [{"ContentType": "text/xml",
                                     "Filename": "message_banque_de_france_20181015.xml",
                                     "Content": 'PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iVVRGLTgiPz48RG9j'
                                                'dW1lbnQgeG1sbnM9InVybjppc286c3RkOmlzbzoyMDAyMjp0ZWNoOnhz'
                                                'ZDpwYWluLjAwMS4wMDEuMDMiPjwvRG9jdW1lbnQ+'}]
    email_html = BeautifulSoup(email['Html-part'], 'html.parser')
    assert 'message_banque_de_france_20181015.xml' in email_html.find('p', {'id': 'file_name'}).find('strong').text
    assert '16910c117e4873c51aa3573113bf216a7140ea20203c6826ef1faffc7f4fc882' \
           in email_html.find('p', {'id': 'checksum'}).find('strong').text


@freeze_time('2018-10-15 09:21:34')
def test_make_payment_details_email():
    # Given
    csv = '"header A","header B","header C","header D"\n"part A","part B","part C","part D"\n'

    # When
    email = make_payment_details_email(csv)

    # Then
    assert email["FromEmail"] == 'support@passculture.app'
    assert email["FromName"] == "pass Culture Pro"
    assert email["Subject"] == "Détails des paiements pass Culture Pro - 2018-10-15"
    assert email["Html-part"] == ""
    assert email["Attachments"] == [{"ContentType": "text/csv",
                                     "Filename": "details_des_paiements_20181015.csv",
                                     "Content": 'ImhlYWRlciBBIiwiaGVhZGVyIEIiLCJoZWFkZXIgQyIsImhlYWRlciBE'
                                                'IgoicGFydCBBIiwicGFydCBCIiwicGFydCBDIiwicGFydCBEIgo='}]


@freeze_time('2018-10-15 09:21:34')
def test_make_wallet_balances_email():
    # Given
    csv = '"header A","header B","header C","header D"\n"part A","part B","part C","part D"\n'

    # When
    email = make_wallet_balances_email(csv)

    # Then
    assert email["FromEmail"] == 'support@passculture.app'
    assert email["FromName"] == "pass Culture Pro"
    assert email["Subject"] == "Soldes des utilisateurs pass Culture - 2018-10-15"
    assert email["Html-part"] == ""
    assert email["Attachments"] == [{"ContentType": "text/csv",
                                     "Filename": "soldes_des_utilisateurs_20181015.csv",
                                     "Content": 'ImhlYWRlciBBIiwiaGVhZGVyIEIiLCJoZWFkZXIgQyIsImhlYWRlciBE'
                                                'IgoicGFydCBBIiwicGFydCBCIiwicGFydCBDIiwicGFydCBEIgo='}]


def test_make_venue_validation_email(app):
    # Given
    offerer = create_offerer(name='La Structure', siren='123456789')
    venue = create_venue(offerer, name='Le Lieu', comment='Ceci est mon commentaire')
    venue.generate_validation_token()

    # When
    email = make_venue_validation_email(venue)

    # Then
    assert email["FromEmail"] == 'support@passculture.app'
    assert email["FromName"] == "pass Culture"
    assert email["Subject"] == "{} - rattachement de lieu pro à valider : {}".format(venue.departementCode, venue.name)
    email_html = _remove_whitespaces(email['Html-part'])
    parsed_email = BeautifulSoup(email_html, 'html.parser')
    html_validation = parsed_email.find('p', {'id': 'validation'}).text
    html_validation_link = parsed_email.find('a', {'id': 'validation-link'}).text
    assert 'La structure "La Structure" (SIREN : 123456789)' in html_validation
    assert 'a rattaché le lieu suivant sans renseigner de SIRET' in html_validation
    assert 'Nom : "Le Lieu"' in html_validation
    assert 'Commentaire de la structure : "Ceci est mon commentaire".' in html_validation
    assert 'localhost/validate/venue?token={}'.format(venue.validationToken) in html_validation
    assert 'localhost/validate/venue?token={}'.format(venue.validationToken) in html_validation_link


def test_make_venue_validation_confirmation_email(app):
    # Given
    offerer = create_offerer(name='La Structure', siren='123456789')
    venue = create_venue(offerer, name='Le Lieu', comment='Ceci est mon commentaire')

    # When
    email = make_venue_validation_confirmation_email(venue)

    # Then
    assert email['Subject'] == 'Validation du rattachement du lieu "Le Lieu" à votre structure "La Structure"'
    assert email["FromEmail"] == 'support@passculture.app'
    assert email["FromName"] == "pass Culture pro"
    email_html = _remove_whitespaces(email['Html-part'])
    parsed_email = BeautifulSoup(email_html, 'html.parser')
    html_validation = str(parsed_email.find('p', {'id': 'validation-details'}))
    html_greeting = str(parsed_email.find('p', {'id': 'mail-greeting'}))
    html_salutation = str(parsed_email.find('p', {'id': 'mail-salutation'}))
    assert 'Cher partenaire pass Culture,' in html_greeting
    assert 'Le rattachement du lieu "Le Lieu"' in html_validation
    assert 'à votre structure "La Structure"' in html_validation
    assert 'Cordialement,' in html_salutation
    assert 'L\'équipe pass Culture' in html_salutation


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


@freeze_time('2019-05-20 12:00:00')
class MakeBeneficiariesImportEmailTest:
    def test_sends_date_in_subject(self, app):
        # given
        new_beneficiaries = [User(), User()]
        error_messages = ['erreur import 1', 'erreur import 2']

        # when
        email = make_beneficiaries_import_email(new_beneficiaries, error_messages)

        # then
        assert email["FromEmail"] == 'dev@passculture.app'
        assert email["FromName"] == 'pass Culture'
        assert email["Subject"] == 'Import des utilisateurs depuis Démarches Simplifiées 2019-05-20'

    def test_sends_number_of_newly_created_beneficiaries(self, app):
        # given
        new_beneficiaries = [User(), User()]
        error_messages = ['erreur import 1', 'erreur import 2']

        # when
        email = make_beneficiaries_import_email(new_beneficiaries, error_messages)

        # then
        email_html = _remove_whitespaces(email['Html-part'])
        parsed_email = BeautifulSoup(email_html, 'html.parser')
        assert parsed_email.find("p", {"id": 'total'}).text == "Nombre total d'utilisateurs créés : 2"

    def test_sends_list_of_import_errors(self, app):
        # given
        new_beneficiaries = [User(), User()]
        error_messages = ['erreur import 1', 'erreur import 2']

        # when
        email = make_beneficiaries_import_email(new_beneficiaries, error_messages)

        # then
        email_html = _remove_whitespaces(email['Html-part'])
        parsed_email = BeautifulSoup(email_html, 'html.parser')
        assert parsed_email.find("p", {"id": 'errors'}).text.strip() == "erreur import 1 erreur import 2"


class MakeOffererBookingRecapEmailAfterUserActionTest:
    @mocked_mail
    @clean_database
    def test_booking_recap_email_html_should_contain_all_bookings_information(app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer, 'Test offerer', 'reservations@test.fr', '123 rue test', '93000', 'Test city',
                             '93')
        beginning_datetime = datetime(2019, 7, 20, 12, 0, 0)
        end_datetime = beginning_datetime + timedelta(hours=1)
        booking_limit_datetime = beginning_datetime - timedelta(hours=1)

        stock = create_stock_with_event_offer(offerer=None, venue=venue, event_type=EventType.SPECTACLE_VIVANT,
                                              offer_id=1,
                                              beginning_datetime=beginning_datetime, end_datetime=end_datetime,
                                              booking_limit_datetime=booking_limit_datetime)
        user = create_user(public_name='Test', first_name='First', last_name='Last', departement_code='93',
                           email='test@example.com', can_book_free_offers=True)
        booking = create_booking(user, stock, venue, None)
        booking.token = '56789'

        # When
        with patch('utils.mailing.booking_queries.find_ongoing_bookings_by_stock', return_value=[booking]):
            recap_email = make_offerer_booking_recap_email_after_user_action(booking)

        # Then
        email_html = _remove_whitespaces(recap_email['Html-part'])
        recap_email_soup = BeautifulSoup(email_html, 'html.parser')
        mail_greeting = recap_email_soup.find('p', {'id': 'mail-greeting'}).text
        action = recap_email_soup.find('p', {'id': 'action'}).text
        recap_table = recap_email_soup.find('table', {'id': 'recap-table'}).text
        recap = recap_email_soup.find('p', {'id': 'recap'}).text
        assert 'Cher partenaire pass Culture,' in mail_greeting
        assert 'First Last (test@example.com) vient de faire une nouvelle réservation.' in action
        assert 'Voici le récapitulatif des réservations à ce jour :' in recap
        assert '(total 1) pour Mains, sorts et papiers (Spectacle vivant) http://localhost:3001/offres/AE' in recap
        assert 'le 20 juillet 2019 à 14:00,' in recap
        assert 'proposé par Test offerer (Adresse : 123 rue test, 93000 Test city).' in recap
        assert 'Prénom' in recap_table
        assert 'Nom' in recap_table
        assert 'Email' in recap_table
        assert 'Code réservation' in recap_table
        assert 'First' in recap_table
        assert 'Last' in recap_table
        assert 'test@example.com' in recap_table
        assert '56789' in recap_table
        assert recap_email[
                   'Subject'] == '[Réservations 93] Nouvelle réservation pour Mains, sorts et papiers - 20 juillet 2019 à 14:00'

    @mocked_mail
    @clean_database
    def test_booking_recap_email_html_should_have_unsubscribe_option(app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer, 'Test offerer', 'reservations@test.fr', '123 rue test', '93000', 'Test city',
                             '93')
        stock = create_stock_with_event_offer(offerer=None, venue=venue)
        user = create_user('Test', departement_code='93', email='test@example.com', can_book_free_offers=True)
        booking = create_booking(user, stock, venue, None)
        booking.token = '56789'

        # When
        with patch('utils.mailing.booking_queries.find_ongoing_bookings_by_stock', return_value=[booking]):
            recap_email = make_offerer_booking_recap_email_after_user_action(booking)

        # Then
        email_html = _remove_whitespaces(recap_email['Html-part'])
        recap_email_soup = BeautifulSoup(email_html, 'html.parser')
        unsubscribe_option = recap_email_soup.find('p', {'id': 'unsubscribe-option'}).text
        change_email = recap_email_soup.find('a', {'id': 'change-email'})['href']
        remove_email = recap_email_soup.find('a', {'id': 'remove-email'})['href']
        assert 'Vous recevez ce message parce que votre adresse e-mail est renseignée comme adresse de contact sur votre offre.' in unsubscribe_option
        assert 'Si vous souhaitez modifier l’adresse de contact cliquez ici : être notifié des réservations à une autre adresse e-mail.' in unsubscribe_option
        assert 'Si vous ne souhaitez plus recevoir de notifications de réservations par e-mail, cliquez ici : ne plus recevoir les notifications de réservations.' in unsubscribe_option
        assert 'mailto:support@passculture.app?subject=Changer%20l%27adresse%20e-mail%20de%20notification%20des%20r%C3%A9servations' == \
               change_email
        assert 'mailto:support@passculture.app?subject=Ne%20plus%20recevoir%20les%20notifications%20de%20r%C3%A9servations' == \
               remove_email

    @mocked_mail
    @clean_database
    def test_booking_recap_email_html_should_not_have_cancelled_or_used_bookings(app):
        # Given
        venue = create_venue(Offerer(), 'Test offerer', 'reservations@test.fr', '123 rue test', '93000', 'Test city',
                             '93')
        stock = create_stock_with_event_offer(offerer=Offerer(), venue=venue)

        user1 = create_user(public_name='Test1', first_name='First1', last_name='Last1', departement_code='93',
                            email='test@example.com', can_book_free_offers=True)
        booking1 = create_booking(user1, stock)

        user2 = create_user(public_name='Test2', first_name='First2', last_name='Last2', departement_code='93',
                            email='test@example.com', can_book_free_offers=True)
        booking2 = create_booking(user2, stock)

        ongoing_bookings = [booking1, booking2]

        # When
        with patch('utils.mailing.booking_queries.find_ongoing_bookings_by_stock', return_value=ongoing_bookings):
            recap_email = make_offerer_booking_recap_email_after_user_action(booking1)

        # Then
        email_html = BeautifulSoup(recap_email['Html-part'], 'html.parser')
        html_recap_table = str(email_html.find("table", {"id": "recap-table"}))
        assert '<td>First1</td>' in html_recap_table
        assert '<td>First2</td>' in html_recap_table
        assert '<td>Cancelled</td>' not in html_recap_table
        assert '<td>Used</td>' not in html_recap_table

    @mocked_mail
    @clean_database
    def test_offerer_recap_email_future_offer_when_new_booking_with_old_booking(app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer, 'Test offerer', 'reservations@test.fr', '123 rue test', '93000', 'Test city',
                             '93')
        stock = create_stock_with_event_offer(offerer=None, venue=venue)
        user_1 = create_user('Test', first_name='John', last_name='Doe', departement_code='93',
                             email='test@example.com',
                             can_book_free_offers=True)
        user_2 = create_user('Test 2', first_name='Jane', last_name='Doe', departement_code='93',
                             email='test@example.com',
                             can_book_free_offers=True)
        user_2.email = 'other_test@example.com'
        booking_1 = create_booking(user_1, stock, venue, None)
        booking_1.token = '56789'
        booking_2 = create_booking(user_2, stock, venue, None)
        booking_2.token = '67890'

        # When
        with patch('utils.mailing.booking_queries.find_ongoing_bookings_by_stock', return_value=[booking_1, booking_2]):
            recap_email = make_offerer_booking_recap_email_after_user_action(booking_2)

        # Then
        email_html = _remove_whitespaces(recap_email['Html-part'])
        recap_email_soup = BeautifulSoup(email_html, 'html.parser')
        action_html = recap_email_soup.find('p', {'id': 'action'}).text
        recap_table_html = recap_email_soup.find('table', {'id': 'recap-table'}).text
        recap_html = recap_email_soup.find('p', {'id': 'recap'}).text
        assert 'Jane Doe (other_test@example.com) vient de faire une nouvelle réservation.' in action_html
        assert '(total 2) pour Mains, sorts et papiers' in recap_html
        assert 'John' in recap_table_html
        assert 'Jane' in recap_table_html
        assert 'test@example.com' in recap_table_html
        assert 'other_test@example.com' in recap_table_html
        assert '56789' in recap_table_html
        assert '67890' in recap_table_html

    @mocked_mail
    @clean_database
    def test_offerer_booking_recap_email_for_a_thing_offer_has_action_and_recap_html(app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer, 'Test offerer', 'reservations@test.fr', '123 rue test', '93000', 'Test city',
                             '93')
        thing_offer = create_offer_with_thing_product(venue=None, thing_type=ThingType.AUDIOVISUEL)
        stock = create_stock_with_thing_offer(offerer=None, venue=venue, offer=thing_offer)
        stock.offer.id = 1
        user1 = create_user('Test', first_name='Joe', last_name='Dalton', departement_code='93',
                            email='test1@email.com',
                            can_book_free_offers=True)
        user2 = create_user('Test', first_name='Averell', last_name='Dalton', departement_code='93',
                            email='test2@email.com', can_book_free_offers=True)
        booking1 = create_booking(user1, stock, venue, token='56789')
        booking2 = create_booking(user2, stock, venue, token='12345')

        # When
        with patch('utils.mailing.booking_queries.find_ongoing_bookings_by_stock', return_value=[booking1, booking2]):
            recap_email = make_offerer_booking_recap_email_after_user_action(booking1)

        # Then

        email_html = _remove_whitespaces(recap_email['Html-part'])
        recap_email_soup = BeautifulSoup(email_html, 'html.parser')
        recap_html = recap_email_soup.find("p", {"id": 'recap'}).text
        action_html = recap_email_soup.find("p", {"id": 'action'}).text
        assert 'Joe Dalton (test1@email.com) vient de faire une nouvelle réservation' in action_html
        assert 'Voici le récapitulatif des réservations à ce jour :' in recap_html
        assert '(total 2) pour Test Book' in recap_html
        assert '(Audiovisuel - films sur supports physiques et VOD)' in recap_html
        assert 'http://localhost:3001/offres/AE' in recap_html
        assert 'proposé par Test offerer (Adresse : 123 rue test, 93000 Test city).' in recap_html

    @mocked_mail
    @clean_database
    def test_offerer_booking_recap_email_thing_offer_has_recap_table(app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer, 'Test offerer', 'reservations@test.fr', '123 rue test', '93000', 'Test city',
                             '93')
        thing_offer = create_offer_with_thing_product(venue=None, thing_type=ThingType.AUDIOVISUEL)
        stock = create_stock_with_thing_offer(offerer=None, venue=venue, offer=thing_offer)
        stock.offer.id = 1
        user1 = create_user('Test', first_name='Joe', last_name='Dalton', departement_code='93',
                            email='test1@email.com',
                            can_book_free_offers=True)
        user2 = create_user('Test', first_name='Averell', last_name='Dalton', departement_code='93',
                            email='test2@email.com', can_book_free_offers=True)
        booking1 = create_booking(user1, stock, venue, token='56789')
        booking2 = create_booking(user2, stock, venue, token='12345')

        # When
        with patch('utils.mailing.booking_queries.find_ongoing_bookings_by_stock', return_value=[booking1, booking2]):
            recap_email = make_offerer_booking_recap_email_after_user_action(booking1)

        # Then

        email_html = _remove_whitespaces(recap_email['Html-part'])
        recap_email_soup = BeautifulSoup(email_html, 'html.parser')
        recap_table_html = recap_email_soup.find("table", {"id": 'recap-table'}).text
        assert 'Joe' in recap_table_html
        assert 'Averell' in recap_table_html
        assert 'test1@email.com' in recap_table_html
        assert 'test2@email.com' in recap_table_html

    @mocked_mail
    @clean_database
    def test_offerer_booking_recap_email_thing_offer_does_not_have_validation_tokens(app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer, 'Test offerer', 'reservations@test.fr', '123 rue test', '93000', 'Test city',
                             '93')
        thing_offer = create_offer_with_thing_product(venue=None, thing_type=ThingType.AUDIOVISUEL)
        stock = create_stock_with_thing_offer(offerer=None, venue=venue, offer=thing_offer)
        stock.offer.id = 1
        user1 = create_user('Test', first_name='Joe', last_name='Dalton', departement_code='93',
                            email='test1@email.com',
                            can_book_free_offers=True)
        user2 = create_user('Test', first_name='Averell', last_name='Dalton', departement_code='93',
                            email='test2@email.com', can_book_free_offers=True)
        booking1 = create_booking(user1, stock, venue, token='56789')
        booking2 = create_booking(user2, stock, venue, token='12345')

        # When
        with patch('utils.mailing.booking_queries.find_ongoing_bookings_by_stock', return_value=[booking1, booking2]):
            recap_email = make_offerer_booking_recap_email_after_user_action(booking1)

        # Then

        email_html = _remove_whitespaces(recap_email['Html-part'])
        recap_email_soup = BeautifulSoup(email_html, 'html.parser')
        recap_table_html = recap_email_soup.find("table", {"id": 'recap-table'}).text
        assert '12345' not in recap_table_html
        assert '56789' not in recap_table_html

    @freeze_time('2018-10-15 09:21:34')
    @clean_database
    def test_make_offerer_booking_recap_email_after_user_cancellation_for_physical_venue(app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer, 'Test offerer', 'reservations@test.fr', '123 rue test', '93000', 'Test city',
                             '93')
        event_offer = create_offer_with_event_product(venue, event_name='Test Event')
        now = datetime.utcnow() + timedelta()
        event_occurrence = create_event_occurrence(event_offer, beginning_datetime=now)
        stock = create_stock_from_event_occurrence(event_occurrence, price=0)
        user_1 = create_user('Test1', first_name='John', last_name='Doe', departement_code='93',
                             email='test1@email.com')
        user_2 = create_user('Test2', first_name='Jane', last_name='Doe', departement_code='93',
                             email='test2@email.com')
        booking_1 = create_booking(user_1, stock, venue)
        booking_2 = create_booking(user_2, stock, venue)
        booking_2.isCancelled = True
        PcObject.save(booking_1, booking_2)

        # When
        with patch('utils.mailing.booking_queries.find_ongoing_bookings_by_stock', return_value=[booking_1]):
            recap_email = make_offerer_booking_recap_email_after_user_action(booking_2, is_cancellation=True)

        # Then
        email_html = _remove_whitespaces(recap_email['Html-part'])
        parsed_email = BeautifulSoup(email_html, 'html.parser')
        assert "<strong>Jane Doe</strong> (test2@email.com) vient d'annuler sa réservation." in str(
            parsed_email.find("p", {"id": "action"}))
        assert "Voici le récapitulatif des réservations à ce jour :" in str(parsed_email.find("p", {"id": "recap"}))
        assert "(total 1) pour Test Event" in str(parsed_email.find("p", {"id": "recap"}))
        assert "le 15 octobre 2018 à 11:21," in str(parsed_email.find("p", {"id": "recap"}))
        assert "proposé par Test offerer (Adresse : 123 rue test, 93000 Test city)." in str(
            parsed_email.find("p", {"id": "recap"}))
        assert "<td>John</td>" in str(parsed_email.find("table", {"id": "recap-table"}))
        assert "<td>Jane</td>" not in str(parsed_email.find("table", {"id": "recap-table"}))
        assert "<td>test1@email.com</td>" in str(parsed_email.find("table", {"id": "recap-table"}))
        assert "<td>{token}</td>".format(token=booking_1.token) in str(
            parsed_email.find("table", {"id": "recap-table"}))

    @freeze_time('2018-10-15 09:21:34')
    @clean_database
    def test_make_offerer_booking_recap_email_after_user_cancellation_should_have_unsubscribe_option(app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer, 'Test offerer', 'reservations@test.fr', '123 rue test', '93000', 'Test city',
                             '93')
        event_offer = create_offer_with_event_product(venue, event_name='Test Event')
        now = datetime.utcnow() + timedelta()
        event_occurrence = create_event_occurrence(event_offer, beginning_datetime=now)
        stock = create_stock_from_event_occurrence(event_occurrence, price=0)
        user_1 = create_user('Test1', departement_code='93', email='test1@email.com')
        user_2 = create_user('Test2', departement_code='93', email='test2@email.com')
        booking_1 = create_booking(user_1, stock, venue)
        booking_2 = create_booking(user_2, stock, venue)
        booking_2.isCancelled = True
        PcObject.save(booking_1, booking_2)

        # When
        with patch('utils.mailing.booking_queries.find_ongoing_bookings_by_stock', return_value=[booking_1]):
            recap_email = make_offerer_booking_recap_email_after_user_action(booking_2, is_cancellation=True)

        # Then
        email_html = _remove_whitespaces(recap_email['Html-part'])
        parsed_email = BeautifulSoup(email_html, 'html.parser')

        # Then
        email_html = _remove_whitespaces(recap_email['Html-part'])
        recap_email_soup = BeautifulSoup(email_html, 'html.parser')
        assert 'Vous recevez ce message parce que votre adresse e-mail est renseignée comme adresse de contact sur votre offre.' in recap_email_soup.find(
            'p', {'id': 'unsubscribe-option'}).text
        assert 'Si vous souhaitez modifier l’adresse de contact cliquez ici : être notifié des réservations à une autre adresse e-mail.' in recap_email_soup.find(
            'p', {'id': 'unsubscribe-option'}).text
        assert 'Si vous ne souhaitez plus recevoir de notifications de réservations par e-mail, cliquez ici : ne plus recevoir les notifications de réservations.' in recap_email_soup.find(
            'p', {'id': 'unsubscribe-option'}).text
        assert 'mailto:support@passculture.app?subject=Changer%20l%27adresse%20e-mail%20de%20notification%20des%20r%C3%A9servations' == \
               recap_email_soup.find('a', {'id': 'change-email'})['href']
        assert 'mailto:support@passculture.app?subject=Ne%20plus%20recevoir%20les%20notifications%20de%20r%C3%A9servations' == \
               recap_email_soup.find('a', {'id': 'remove-email'})['href']

    @clean_database
    def test_booking_cancellation_email_of_thing_for_offerer_does_not_show_address_when_virtual_venue(app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer, 'Test offerer', 'reservations@test.fr', is_virtual=True, siret=None,
                             postal_code=None,
                             departement_code=None, address=None)
        thing_offer = create_offer_with_thing_product(venue, thing_name='Test')
        stock = create_stock_from_offer(thing_offer, price=0)
        user_1 = create_user('Test1', departement_code='93', email='test1@email.com')
        user_2 = create_user('Test2', departement_code='93', email='test2@email.com')
        booking_1 = create_booking(user_1, stock, venue)
        booking_2 = create_booking(user_2, stock, venue)
        booking_2.isCancelled = True
        PcObject.save(booking_1, booking_2)

        # When
        with patch('utils.mailing.booking_queries.find_ongoing_bookings_by_stock', return_value=[booking_1]):
            recap_email = make_offerer_booking_recap_email_after_user_action(booking_2, is_cancellation=True)

            # Then
            email_html = BeautifulSoup(recap_email['Html-part'], 'html.parser')
        email_racap_html = email_html.find('p', {'id': 'recap'}).text
        assert 'Offre numérique proposée par Test offerer' in email_racap_html
        assert '(Adresse:' not in email_racap_html

    @clean_database
    def test_make_offerer_booking_user_cancellation_for_event_email_when_virtual_venue_does_not_show_address(app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer, 'Test offerer', 'reservations@test.fr', is_virtual=True, siret=None,
                             postal_code=None,
                             departement_code=None, address=None)
        event_offer = create_offer_with_event_product(venue, event_name='Test')
        event_occurrence = create_event_occurrence(event_offer, beginning_datetime=datetime.utcnow())
        stock = create_stock_from_event_occurrence(event_occurrence, price=0)
        user_1 = create_user('Test1', departement_code='93', email='test1@email.com')
        user_2 = create_user('Test2', departement_code='93', email='test2@email.com')
        booking_1 = create_booking(user_1, stock, venue)
        booking_2 = create_booking(user_2, stock, venue)
        booking_2.isCancelled = True
        PcObject.save(booking_1, booking_2)

        # When
        with patch('utils.mailing.booking_queries.find_ongoing_bookings_by_stock', return_value=[booking_1]):
            recap_email = make_offerer_booking_recap_email_after_user_action(booking_2, is_cancellation=True)

            # Then
            email_html = BeautifulSoup(recap_email['Html-part'], 'html.parser')
        assert 'Offre numérique proposée par Test offerer.' in str(email_html.find('p', {'id': 'recap'}))
        assert 'annuler sa réservation' in str(email_html.find('p', {'id': 'action'}))
        assert '(Adresse:' not in str(email_html.find('p', {'id': 'action'}))

    @clean_database
    def test_booking_cancellation_email_of_thing_for_offerer_contains_cancellation_subject_without_date(app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer, 'Test offerer')
        thing_offer = create_offer_with_thing_product(venue, thing_name='Test')
        stock = create_stock_from_offer(thing_offer, price=0)
        user_1 = create_user('Test1', departement_code='93', email='test1@email.com')
        user_2 = create_user('Test2', departement_code='93', email='test2@email.com')
        booking_1 = create_booking(user_1, stock, venue)
        booking_2 = create_booking(user_2, stock, venue)
        booking_2.isCancelled = True
        PcObject.save(booking_1, booking_2)

        # When
        with patch('utils.mailing.booking_queries.find_ongoing_bookings_by_stock', return_value=[booking_1]):
            recap_email = make_offerer_booking_recap_email_after_user_action(booking_2, is_cancellation=True)

        # Then
        assert recap_email['Subject'] == '[Réservations] Annulation de réservation pour Test'

    @freeze_time('2018-10-15 09:21:34')
    @clean_database
    def test_make_offerer_booking_user_cancellation_email_for_event_has_cancellation_subject_with_date(app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer, 'Test offerer')
        event_offer = create_offer_with_event_product(venue, event_name='Test')
        event_occurrence = create_event_occurrence(event_offer, beginning_datetime=datetime.utcnow())
        stock = create_stock_from_event_occurrence(event_occurrence, price=0)
        user_1 = create_user('Test1', departement_code='93', email='test1@email.com')
        user_2 = create_user('Test2', departement_code='93', email='test2@email.com')
        booking_1 = create_booking(user_1, stock, venue)
        booking_2 = create_booking(user_2, stock, venue)
        booking_2.isCancelled = True
        PcObject.save(booking_1, booking_2)

        # When
        with patch('utils.mailing.booking_queries.find_ongoing_bookings_by_stock', return_value=[booking_1]):
            recap_email = make_offerer_booking_recap_email_after_user_action(booking_2, is_cancellation=True)

        # Then
        assert recap_email['Subject'] == '[Réservations] Annulation de réservation pour Test - 15 octobre 2018 à 11:21'

    @clean_database
    def test_make_offerer_booking_user_cancellation_has_recap_information_but_no_token(app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer, 'Test offerer', 'reservations@test.fr', is_virtual=True, siret=None)
        thing_offer = create_offer_with_thing_product(venue)
        stock = create_stock_from_offer(thing_offer, price=0)
        user_1 = create_user('Test1', first_name='Jane', last_name='Doe', departement_code='93',
                             email='test1@email.com')
        user_2 = create_user('Test2', first_name='Lucy', last_name='Smith', departement_code='93',
                             email='test2@email.com')
        booking_1 = create_booking(user_1, stock, venue, token='12345')
        booking_2 = create_booking(user_2, stock, venue, token='56789')
        booking_2.isCancelled = True
        PcObject.save(booking_1, booking_2)

        # When
        with patch('utils.mailing.booking_queries.find_ongoing_bookings_by_stock', return_value=[booking_1]):
            recap_email = make_offerer_booking_recap_email_after_user_action(booking_2, is_cancellation=True)

        # Then
        email_html = BeautifulSoup(recap_email['Html-part'], 'html.parser')
        recap_table_html = email_html.find('table', {'id': 'recap-table'}).text
        assert 'Jane' in recap_table_html
        assert 'Lucy' not in recap_table_html
        assert 'test1@email.com' in recap_table_html
        assert 'test2@email.com' not in recap_table_html
        assert '12345' not in recap_table_html
        assert '56789' not in recap_table_html


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


class MakeOffererBookingRecapEmailWithMailjetTemplateTest:
    @clean_database
    def test_should_write_email_with_right_data_when_offer_is_an_event(self, app):
        # Given
        user = create_user(email='test@example.com')
        offerer = create_offerer(idx=1)
        venue = create_venue(offerer, 'Test offerer', 'reservations@example.com', siret='89765389057043', idx=1,
                             departement_code='75', postal_code='75000')
        event_offer = create_offer_with_event_product(venue, idx=1)
        beginning_datetime = datetime(2019, 11, 6, 14, 59, 5, tzinfo=timezone.utc)
        stock = create_stock_from_offer(event_offer, beginning_datetime=beginning_datetime, price=0, available=10)
        booking = create_booking(user, stock, venue, token='ABC123')
        recipient = ['dev@passculture.app']
        stock.bookings = [booking]

        PcObject.save(stock)

        # When
        email = get_offerer_booking_recap_email_data(booking, recipient)

        # Then
        assert email == {
            'FromEmail': 'support@passculture.app',
            'MJ-TemplateID': 1095029,
            'MJ-TemplateLanguage': True,
            'To': 'dev@passculture.app',
            'Vars':
                {
                    'nom_offre': 'Test event',
                    'nom_lieu': 'Test offerer',
                    'prix': 'Gratuit',
                    'date': '06-Nov-2019',
                    'heure': '15h59',
                    'quantity': 1,
                    'user_firstName': 'John',
                    'user_lastName': 'Doe',
                    'user_email': 'test@example.com',
                    'is_event': 1,
                    'nombre_resa': 1,
                    'contremarque': 'ABC123',
                    'env': '-development',
                    'ISBN': '',
                    'lien_offre_pcpro': 'http://localhost:3001/offres/AE?lieu=AE&structure=AE',
                    'offer_type': 'EventType.SPECTACLE_VIVANT',
                    'departement': '75',
                    'users': [{'firstName': 'John',
                               'lastName': 'Doe',
                               'email': 'test@example.com',
                               'contremarque': 'ABC123'}]
                }
        }

    @clean_database
    def test_should_write_email_with_right_data_when_offer_is_a_book(self, app):
        # Given
        user = create_user(email='test@example.com')
        offerer = create_offerer(idx=1)
        extra_data = {'isbn': '123456789'}
        venue = create_venue(offerer, 'Test offerer', 'reservations@example.com', is_virtual=True, siret=None, idx=1)

        thing_product = create_product_with_thing_type(thing_name='Le récit de voyage', extra_data=extra_data)
        event_offer = create_offer_with_thing_product(venue, thing_product, idx=1)
        stock = create_stock_from_offer(event_offer, price=0)
        booking = create_booking(user, stock, venue, quantity=3, token='ABC123')
        recipient = ['dev@passculture.app']
        stock.bookings = [booking]

        PcObject.save(stock)

        # When
        email = get_offerer_booking_recap_email_data(booking, recipient)

        # Then
        assert email == {
            'FromEmail': 'support@passculture.app',
            'MJ-TemplateID': 1095029,
            'MJ-TemplateLanguage': True,
            'To': 'dev@passculture.app',
            'Vars':
                {
                    'nom_offre': 'Le récit de voyage',
                    'nom_lieu': 'Test offerer',
                    'prix': 'Gratuit',
                    'ISBN': '123456789',
                    'nombre_resa': 1,
                    'contremarque': 'ABC123',
                    'env': '-development',
                    'lien_offre_pcpro': 'http://localhost:3001/offres/AE?lieu=AE&structure=AE',

                    'user_firstName': 'John',
                    'user_lastName': 'Doe',
                    'user_email': 'test@example.com',
                    'is_event': 0,
                    'date': '',
                    'heure': '',
                    'quantity': 3,
                    'offer_type': 'book',
                    'departement': 'numérique',
                    'users': [{'firstName': 'John',
                               'lastName': 'Doe',
                               'email': 'test@example.com',
                               'contremarque': 'ABC123'}]
                }
        }

    @clean_database
    def test_should_not_truncate_price(self, app):
        # Given
        user = create_user(email='test@example.com')
        offerer = create_offerer(idx=1)
        deposit = create_deposit(user, amount=50, source='public')
        venue = create_venue(offerer, 'Test offerer', 'reservations@example.com', siret='89765389057043', idx=1,
                             departement_code='75', postal_code='75000')
        event_offer = create_offer_with_event_product(venue, is_duo=True, idx=1)
        beginning_datetime = datetime(2019, 11, 6, 14, 00, 0, tzinfo=timezone.utc)
        stock = create_stock_from_offer(event_offer, beginning_datetime=beginning_datetime, price=5.86, available=10)
        booking = create_booking(user, stock, venue, token='ABC123')
        stock.bookings = [booking]
        recipient = ['dev@passculture.app']

        PcObject.save(deposit, stock)

        # When
        email = get_offerer_booking_recap_email_data(booking, recipient)

        # Then
        assert email == {
            'FromEmail': 'support@passculture.app',
            'MJ-TemplateID': 1095029,
            'MJ-TemplateLanguage': True,
            'To': 'dev@passculture.app',
            'Vars':
                {
                    'nom_offre': 'Test event',
                    'nom_lieu': 'Test offerer',
                    'prix': '5.86',
                    'date': '06-Nov-2019',
                    'heure': '15h',
                    'quantity': 1,
                    'user_firstName': 'John',
                    'user_lastName': 'Doe',
                    'user_email': 'test@example.com',
                    'is_event': 1,
                    'ISBN': '',
                    'offer_type': 'EventType.SPECTACLE_VIVANT',
                    'departement': '75',
                    'nombre_resa': 1,
                    'contremarque': 'ABC123',
                    'env': '-development',
                    'lien_offre_pcpro': 'http://localhost:3001/offres/AE?lieu=AE&structure=AE',
                    'users': [{'firstName': 'John',
                               'lastName': 'Doe',
                               'email': 'test@example.com',
                               'contremarque': 'ABC123'}]
                }
        }

    @clean_database
    def test_returns_empty_ISBN_when_no_extra_data(self, app):
        # Given
        user = create_user(email='test@example.com')
        offerer = create_offerer(idx=1)
        venue = create_venue(offerer, 'Test offerer', 'reservations@example.com', is_virtual=True, siret=None, idx=1)
        thing_offer = create_offer_with_thing_product(venue, thing_type=ThingType.LIVRE_EDITION, idx=1)
        beginning_datetime = datetime(2019, 11, 6, 14, 00, 0, tzinfo=timezone.utc)
        stock = create_stock_from_offer(thing_offer, beginning_datetime=beginning_datetime, price=0, available=10)
        booking = create_booking(user, stock, venue, token='ABC123')
        recipient = ['dev@passculture.app']
        stock.bookings = [booking]

        PcObject.save(stock)

        # When
        thing_offer.extraData = None
        email_data_template = get_offerer_booking_recap_email_data(booking, recipient)

        # Then
        assert email_data_template == {
            'FromEmail': 'support@passculture.app',
            'MJ-TemplateID': 1095029,
            'MJ-TemplateLanguage': True,
            'To': 'dev@passculture.app',
            'Vars':
                {
                    'nom_offre': 'Test Book',
                    'nom_lieu': 'Test offerer',
                    'prix': 'Gratuit',
                    'date': '',
                    'heure': '',
                    'quantity': 1,
                    'user_firstName': 'John',
                    'user_lastName': 'Doe',
                    'user_email': 'test@example.com',
                    'is_event': 0,
                    'ISBN': '',
                    'offer_type': 'book',
                    'departement': 'numérique',
                    'nombre_resa': 1,
                    'contremarque': 'ABC123',
                    'env': '-development',
                    'lien_offre_pcpro': 'http://localhost:3001/offres/AE?lieu=AE&structure=AE',
                    'users': [{'firstName': 'John',
                               'lastName': 'Doe',
                               'email': 'test@example.com',
                               'contremarque': 'ABC123'}]
                }
        }

    @clean_database
    def test_returns_empty_ISBN_when_extra_data_has_no_key_isbn(self, app):
        # Given
        user = create_user(email="test@example.com")
        offerer = create_offerer(idx=1)
        venue = create_venue(offerer, 'Test offerer', 'reservations@example.com', is_virtual=True, siret=None, idx=1)
        thing_offer = create_offer_with_thing_product(venue, thing_type=ThingType.LIVRE_EDITION, idx=1)
        beginning_datetime = datetime(2019, 11, 6, 14, 00, 0, tzinfo=timezone.utc)
        stock = create_stock_from_offer(thing_offer, beginning_datetime=beginning_datetime, price=0, available=10)
        booking = create_booking(user, stock, venue, token='ABC123')
        stock.bookings = [booking]
        recipient = ['dev@passculture.app']

        PcObject.save(stock)

        # When
        thing_offer.extraData = {}
        email_data_template = get_offerer_booking_recap_email_data(booking, recipient)

        # Then
        assert email_data_template == {
            'FromEmail': 'support@passculture.app',
            'MJ-TemplateID': 1095029,
            'MJ-TemplateLanguage': True,
            'To': 'dev@passculture.app',
            'Vars':
                {
                    'nom_offre': 'Test Book',
                    'nom_lieu': 'Test offerer',
                    'prix': 'Gratuit',
                    'date': '',
                    'heure': '',
                    'quantity': 1,
                    'user_firstName': 'John',
                    'user_lastName': 'Doe',
                    'user_email': 'test@example.com',
                    'is_event': 0,
                    'ISBN': '',
                    'departement': 'numérique',
                    'offer_type': 'book',
                    'lien_offre_pcpro': 'http://localhost:3001/offres/AE?lieu=AE&structure=AE',
                    'nombre_resa': 1,
                    'env': '-development',
                    'contremarque': 'ABC123',
                    'users': [{'firstName': 'John',
                               'lastName': 'Doe',
                               'email': 'test@example.com',
                               'contremarque': 'ABC123'}]
                }
        }

    @patch('utils.mailing.feature_send_mail_to_users_enabled', return_value=True)
    @clean_database
    def test_returns_multiple_offer_email_when_production_environment(self, app):
        # Given
        user = create_user(email='test@example.com')
        offerer = create_offerer(idx=1)
        venue = create_venue(offerer, 'Test offerer', 'reservations@example.com', siret='89765389057043', idx=1,
                     departement_code='75', postal_code='75000')
        thing_offer = create_offer_with_thing_product(venue, thing_type=ThingType.LIVRE_EDITION,
                                                      booking_email='dev@passculture.app', idx=1)
        beginning_datetime = datetime(2019, 11, 6, 14, 00, 0, tzinfo=timezone.utc)
        stock = create_stock_from_offer(thing_offer, beginning_datetime=beginning_datetime, price=0, available=10)
        booking = create_booking(user, stock, venue, token='ABC123')
        stock.bookings = [booking]
        recipient = ['dev@passculture.app', ADMINISTRATION_EMAIL_ADDRESS]

        PcObject.save(stock)

        # When
        thing_offer.extraData = None

        email_data_template = get_offerer_booking_recap_email_data(booking, recipient)

        # Then
        assert email_data_template == {
            'FromEmail': 'support@passculture.app',
            'MJ-TemplateID': 1095029,
            'MJ-TemplateLanguage': True,
            'To': f'dev@passculture.app, {ADMINISTRATION_EMAIL_ADDRESS}',
            'Vars':
                {
                    'nom_offre': 'Test Book',
                    'nom_lieu': 'Test offerer',
                    'prix': 'Gratuit',
                    'date': '',
                    'heure': '',
                    'quantity': 1,
                    'user_firstName': 'John',
                    'user_lastName': 'Doe',
                    'user_email': 'test@example.com',
                    'is_event': 0,
                    'ISBN': '',
                    'offer_type': 'book',
                    'departement': '75',
                    'nombre_resa': 1,
                    'contremarque': 'ABC123',
                    'env': '-development',
                    'lien_offre_pcpro': 'http://localhost:3001/offres/AE?lieu=AE&structure=AE',
                    'users': [{'firstName': 'John',
                               'lastName': 'Doe',
                               'email': 'test@example.com',
                               'contremarque': 'ABC123'}]
                }
        }

    @patch('utils.mailing.IS_PROD', False)
    @patch('utils.mailing.feature_send_mail_to_users_enabled', return_value=True)
    @clean_database
    def test_returns_email_with_correct_data_when_two_users_made_reservations_on_same_offer(self, app):
        # Given
        user_1 = create_user('Test', first_name='Jean', last_name='Dupont', departement_code='93',
                             email='test@example.com',
                             can_book_free_offers=True)
        user_2 = create_user('Test', first_name='Jaja', last_name='Dudu', departement_code='93',
                             email='mail@example.com',
                             can_book_free_offers=True)
        offerer = create_offerer(idx=1)
        venue = create_venue(offerer, 'Test offerer', 'reservations@example.com', siret='89765389057043', idx=1,
                     departement_code='75', postal_code='75000')
        thing_offer = create_offer_with_thing_product(venue, thing_type=ThingType.LIVRE_EDITION,
                                                      booking_email='dev@passculture.app', idx=1)
        beginning_datetime = datetime(2019, 11, 6, 14, 00, 0, tzinfo=timezone.utc)
        stock = create_stock_from_offer(thing_offer, beginning_datetime=beginning_datetime, price=0, available=10)
        booking_1 = create_booking(user_1, stock, venue, token='ACVSDC')
        booking_2 = create_booking(user_2, stock, venue, token='TEST95')
        stock.bookings = [booking_1, booking_2]
        recipient = ['dev@passculture.app', ADMINISTRATION_EMAIL_ADDRESS]

        PcObject.save(stock)

        # When
        thing_offer.extraData = None

        email_data_template = get_offerer_booking_recap_email_data(booking_1, recipient)

        # Then
        assert email_data_template == {
            'FromEmail': 'support@passculture.app',
            'MJ-TemplateID': 1095029,
            'MJ-TemplateLanguage': True,
            'To': f'dev@passculture.app, {ADMINISTRATION_EMAIL_ADDRESS}',
            'Vars':
                {
                    'nom_offre': 'Test Book',
                    'nom_lieu': 'Test offerer',
                    'prix': 'Gratuit',
                    'date': '',
                    'heure': '',
                    'quantity': 1,
                    'user_firstName': 'Jean',
                    'user_lastName': 'Dupont',
                    'user_email': 'test@example.com',
                    'is_event': 0,
                    'ISBN': '',
                    'offer_type': 'book',
                    'lien_offre_pcpro': 'http://localhost:3001/offres/AE?lieu=AE&structure=AE',
                    'departement': '75',
                    'nombre_resa': 2,
                    'env': '-development',
                    'contremarque': 'ACVSDC',
                    'users': [{'firstName': 'Jean',
                               'lastName': 'Dupont',
                               'email': 'test@example.com',
                               'contremarque': 'ACVSDC'},
                              {'firstName': 'Jaja',
                               'lastName': 'Dudu',
                               'email': 'mail@example.com',
                               'contremarque': 'TEST95'}
                              ]
                }
        }

    @patch('utils.mailing.IS_PROD', True)
    @clean_database
    def test_returns_right_email_with_correct_link_to_the_corresponding_offer(self, app):
        # Given
        user = create_user('Test', first_name='Jean', last_name='Dupont', departement_code='93',
                           email='test@example.com',
                           can_book_free_offers=True)

        offerer = create_offerer(idx=1)
        venue = create_venue(offerer, 'Test offerer', 'reservations@example.com', siret='89765389057043', idx=1,
                             departement_code='75', postal_code='75000')
        thing_offer = create_offer_with_thing_product(venue, thing_type=ThingType.LIVRE_EDITION,
                                                      booking_email='dev@passculture.app', idx=3)
        beginning_datetime = datetime(2019, 11, 6, 14, 00, 0, tzinfo=timezone.utc)
        stock = create_stock_from_offer(thing_offer, beginning_datetime=beginning_datetime, price=0, available=10)
        booking = create_booking(user, stock, venue, token='ACVSDC')
        stock.bookings = [booking]
        recipient = ['dev@passculture.app', ADMINISTRATION_EMAIL_ADDRESS]

        PcObject.save(stock)

        # When
        thing_offer.extraData = None

        email_data_template = get_offerer_booking_recap_email_data(booking, recipient)

        # Then
        assert email_data_template == {
            'FromEmail': 'support@passculture.app',
            'MJ-TemplateID': 1095029,
            'MJ-TemplateLanguage': True,
            'To': f'dev@passculture.app',
            'Vars':
                {
                    'nom_offre': 'Test Book',
                    'nom_lieu': 'Test offerer',
                    'prix': 'Gratuit',
                    'date': '',
                    'heure': '',
                    'quantity': 1,
                    'user_firstName': 'Jean',
                    'user_lastName': 'Dupont',
                    'user_email': 'test@example.com',
                    'is_event': 0,
                    'ISBN': '',
                    'offer_type': 'book',
                    'lien_offre_pcpro': 'http://localhost:3001/offres/AM?lieu=AE&structure=AE',
                    'departement': '75',
                    'nombre_resa': 1,
                    'env': '',
                    'contremarque': 'ACVSDC',
                    'users': [{'firstName': 'Jean',
                               'lastName': 'Dupont',
                               'email': 'test@example.com',
                               'contremarque': 'ACVSDC'}]
                }
        }


class MakeOfferCreationNotificationEmailTest:
    @classmethod
    def setup_class(self):
        self.offerer = create_offerer(siren='123456789', postal_code='93100', name='Cinéma de Montreuil')

        siret = self.offerer.siren + '12345'

        self.virtual_venue = create_venue(self.offerer, siret=None, is_virtual=True, postal_code=None,
                                          departement_code=None, address=None)
        self.venue93 = create_venue(self.offerer, siret=siret, is_virtual=False, departement_code='93',
                                    postal_code='93100')

        self.physical_offer93 = create_offer_with_thing_product(self.venue93, thing_type=ThingType.AUDIOVISUEL,
                                                                thing_name='Le vent se lève', idx=1)
        self.virtual_offer = create_offer_with_thing_product(self.virtual_venue, thing_type=ThingType.JEUX_VIDEO,
                                                             thing_name='Les lapins crétins', idx=2)

    def test_when_physical_offer_returns_subject_with_departement_information_and_dictionary_with_given_content(self,
                                                                                                                app):
        # When
        author = create_user(email='user@email.com')
        email = make_offer_creation_notification_email(self.physical_offer93, author, 'test.url')
        # Then
        assert email["FromEmail"] == 'support@passculture.app'
        assert email["FromName"] == "pass Culture"
        assert email["Subject"] == "[Création d’offre - 93] Le vent se lève"

        email_html = _remove_whitespaces(email['Html-part'])
        parsed_email = BeautifulSoup(email_html, 'html.parser')

        offer_html = str(parsed_email.find('p', {'id': 'offer'}))
        assert 'Une nouvelle offre "Le vent se lève"' in offer_html

        offerer_html = str(parsed_email.find('p', {'id': 'offerer'}))
        assert "Vient d'être créée par Cinéma de Montreuil" in offerer_html

        link_html = str(parsed_email.find('p', {'id': 'give_link'}))
        assert "Lien pour y accéder : " in link_html
        assert "Cette offre a été créée par user@email.com." in str(parsed_email.find('p', {'id': 'author'}))
        link = str(parsed_email.find('a', {'id': 'link'}))
        assert "test.url/offres/AE" in link
        assert 'href="test.url/offres/AE"' in link

    def test_when_virtual_offer_returns_subject_with_virtual_information_and_dictionary_with_given_content(self, app):
        # When
        author = create_user('author@email.com')
        email = make_offer_creation_notification_email(self.virtual_offer, author, 'test.url')
        # Then
        assert email["FromEmail"] == 'support@passculture.app'
        assert email["FromName"] == "pass Culture"
        assert email["Subject"] == "[Création d’offre - numérique] Les lapins crétins"


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


@freeze_time('2018-10-15 09:21:34')
class MakePaymentsReportEmailTest:
    @classmethod
    def setup_class(self):
        self.grouped_payments = {
            'ERROR': [Mock(), Mock()],
            'SENT': [Mock()],
            'PENDING': [Mock(), Mock(), Mock()]
        }

        self.not_processable_csv = '"header A","header B","header C","header D"\n"part A","part B","part C","part D"\n'
        self.error_csv = '"header 1","header 2","header 3","header 4"\n"part 1","part 2","part 3","part 4"\n'

    def test_it_contains_the_two_csv_files_as_attachment(self, app):
        # Given

        # When
        email = make_payments_report_email(self.not_processable_csv, self.error_csv, self.grouped_payments)

        # Then
        assert email["Attachments"] == [
            {
                "ContentType": "text/csv",
                "Filename": "paiements_non_traitables_2018-10-15.csv",
                "Content": 'ImhlYWRlciBBIiwiaGVhZGVyIEIiLCJoZWFkZXIgQyIsImhlYWRlciBE'
                           'IgoicGFydCBBIiwicGFydCBCIiwicGFydCBDIiwicGFydCBEIgo='
            },
            {
                "ContentType": "text/csv",
                "Filename": "paiements_en_erreur_2018-10-15.csv",
                "Content": 'ImhlYWRlciAxIiwiaGVhZGVyIDIiLCJoZWFkZXIgMyIsImhlYWRlciA0'
                           'IgoicGFydCAxIiwicGFydCAyIiwicGFydCAzIiwicGFydCA0Igo='
            }
        ]

    def test_it_contains_from_and_subject_info(self, app):
        # When
        email = make_payments_report_email(self.not_processable_csv, self.error_csv, self.grouped_payments)

        # Then
        assert email["FromEmail"] == 'support@passculture.app'
        assert email["FromName"] == "pass Culture Pro"
        assert email["Subject"] == "Récapitulatif des paiements pass Culture Pro - 2018-10-15"

    def test_it_contains_the_total_count_of_payments(self, app):
        # When
        email = make_payments_report_email(self.not_processable_csv, self.error_csv, self.grouped_payments)

        # Then
        email_html = BeautifulSoup(email['Html-part'], 'html.parser')
        assert email_html.find('p', {'id': 'total'}).text == 'Nombre total de paiements : 6'

    def test_it_contains_a_count_of_payments_by_status_in_html_part(self, app):
        # When
        email = make_payments_report_email(self.not_processable_csv, self.error_csv, self.grouped_payments)

        # Then
        email_html = BeautifulSoup(email['Html-part'], 'html.parser')
        assert email_html.find('ul').text == '\nERROR : 2\nSENT : 1\nPENDING : 3\n'


class UserValidationEmailsTest:
    def test_make_webapp_user_validation_email_includes_validation_url_with_token_and_user_email(self, app):
        # Given
        user = create_user(email="test@example.com")
        user.generate_validation_token()
        app_origin_url = 'portail-pro'

        # When
        with patch('utils.mailing.feature_send_mail_to_users_enabled', return_value=True):
            email = make_user_validation_email(user, app_origin_url, is_webapp=True)

        # Then
        email_html = BeautifulSoup(email['Html-part'], 'html.parser')
        mail_content = email_html.find("div", {"id": 'mail-content'}).text
        assert 'Bonjour {},'.format(user.publicName) in email_html.find("p", {"id": 'mail-greeting'}).text
        assert "Vous venez de créer un compte pass Culture avec votre adresse test@example.com." in mail_content
        assert 'localhost/validate/user/{}'.format(user.validationToken) in \
               email_html.find('a', href=True)['href']
        assert 'Vous pouvez valider votre adresse email en suivant ce lien :' in mail_content
        assert 'localhost/validate/user/{}'.format(user.validationToken) in mail_content
        assert email['To'] == user.email
        assert email['FromName'] == 'pass Culture'
        assert email['Subject'] == 'Validation de votre adresse email pour le pass Culture'
        assert email['FromEmail'] == 'support@passculture.app'

    def test_make_pro_user_validation_email_includes_validation_url_with_token_and_user_email(self, app):
        # Given
        user = create_user(email="test@example.com")
        user.generate_validation_token()
        app_origin_url = 'portail-pro'

        # When
        email = make_user_validation_email(user, app_origin_url, is_webapp=False)
        expected = {
            'FromEmail': 'dev@passculture.app',
            'FromName': 'pass Culture pro',
            'Subject': '[pass Culture pro] Validation de votre adresse email pour le pass Culture',
            'MJ-TemplateID': 778688,
            'MJ-TemplateLanguage': True,
            'Recipients': [
                {
                    'Email': 'test@example.com',
                    'Name': 'John Doe'
                }
            ],
            'Vars':
                {
                    'nom_structure': 'John Doe',
                    'lien_validation_mail': f'{app_origin_url}/inscription/validation/{user.validationToken}'
                }
        }

        # Then
        assert email == expected

    def test_make_pro_user_waiting_for_validation_by_admin_email(self, app):
        # Given
        user = create_user(email="test@example.com")
        user.generate_validation_token()
        offerer = create_offerer(name='Bar des amis')

        # When
        email = make_pro_user_waiting_for_validation_by_admin_email(user, offerer)
        expected = {
            'FromEmail': 'dev@passculture.app',
            'FromName': 'pass Culture pro',
            'Subject': f'[pass Culture pro] Votre structure {offerer.name} est en cours de validation',
            'MJ-TemplateID': 778329,
            'MJ-TemplateLanguage': True,
            'Recipients': [
                {
                    'Email': 'test@example.com',
                    'Name': 'John Doe'
                }
            ],
            'Vars':
                {
                    'nom_structure': 'Bar des amis'
                }
        }

        # Then
        assert email == expected


class MakeResetPasswordEmailDataTest:
    @patch('utils.mailing.ENV', 'testing')
    @patch('utils.mailing.IS_PROD', False)
    @patch('utils.mailing.SUPPORT_EMAIL_ADDRESS', 'john.doe@example.com')
    @patch('utils.mailing.feature_send_mail_to_users_enabled', return_value=False)
    def test_should_write_email_with_right_data_when_not_production_environment(self, app):
        # Given
        user = create_user(email="johnny.wick@example.com", first_name="Johnny", reset_password_token='ABCDEFG')

        # When
        reset_password_email_data = make_reset_password_email_data(user=user)

        # Then
        assert reset_password_email_data == {
            'FromEmail': 'john.doe@example.com',
            'MJ-TemplateID': 912168,
            'MJ-TemplateLanguage': True,
            'To': 'dev@passculture.app',
            'Vars':
                {
                    'prenom_user': 'Johnny',
                    'token': 'ABCDEFG',
                    'env': '-testing'
                }
        }

    @patch('utils.mailing.ENV', 'production')
    @patch('utils.mailing.IS_PROD', True)
    @patch('utils.mailing.SUPPORT_EMAIL_ADDRESS', 'john.doe@example.com')
    @patch('utils.mailing.feature_send_mail_to_users_enabled', return_value=True)
    def test_should_write_email_with_right_data_when_production_environment(self, app):
        # Given
        user = create_user(email="johnny.wick@example.com", first_name="Johnny", reset_password_token='ABCDEFG')

        # When
        reset_password_email_data = make_reset_password_email_data(user=user)

        # Then
        assert reset_password_email_data == {
            'FromEmail': 'john.doe@example.com',
            'MJ-TemplateID': 912168,
            'MJ-TemplateLanguage': True,
            'To': 'johnny.wick@example.com',
            'Vars':
                {
                    'prenom_user': 'Johnny',
                    'token': 'ABCDEFG',
                    'env': ''
                }
        }


class GetActivationEmailTest:
    @patch('utils.mailing.IS_PROD', True)
    def test_should_return_dict_when_environment_is_production(self):
        # Given
        user = create_user(first_name='Fabien', email='fabien+test@example.net', reset_password_token='ABCD123')

        # When
        activation_email_data = get_activation_email_data(user)

        # Then
        assert activation_email_data == {
            'FromEmail': 'support@passculture.app',
            'Mj-TemplateID': 994771,
            'Mj-TemplateLanguage': True,
            'To': 'fabien+test@example.net',
            'Vars': {
                'prenom_user': 'Fabien',
                'token': 'ABCD123',
                'email': 'fabien%2Btest%40example.net',
                'env': ''
            },
        }

    @patch('utils.mailing.IS_PROD', False)
    def test_should_return_dict_when_environment_is_development(self):
        # Given
        user = create_user(first_name='Fabien', email='fabien+test@example.net', reset_password_token='ABCD123')

        # When
        activation_email_data = get_activation_email_data(user)

        # Then
        assert activation_email_data['Vars'] == {
            'prenom_user': 'Fabien',
            'token': 'ABCD123',
            'email': 'fabien%2Btest%40example.net',
            'env': '-development'
        }


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
