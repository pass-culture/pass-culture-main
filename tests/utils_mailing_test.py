import re
import secrets
from datetime import datetime, timezone, timedelta
from unittest.mock import MagicMock, patch

import pytest
from bs4 import BeautifulSoup
from freezegun import freeze_time

from models import PcObject, Offerer
from tests.conftest import clean_database, mocked_mail
from tests.files.api_entreprise import MOCKED_SIREN_ENTREPRISES_API_RETURN
from utils.mailing import make_user_booking_recap_email, \
    make_offerer_booking_recap_email_after_user_action, make_final_recap_email_for_stock_with_event, \
    write_object_validation_email, make_offerer_driven_cancellation_email_for_user, \
    make_reset_password_email, \
    make_offerer_driven_cancellation_email_for_offerer, make_validation_confirmation_email, \
    make_venue_validation_email, \
    make_venue_validation_confirmation_email, \
    make_batch_cancellation_email, make_payment_transaction_email, make_user_validation_email, \
    make_payment_details_email, make_wallet_balances_email
from utils.test_utils import create_stock_with_event_offer, create_stock_with_thing_offer, \
    create_user, create_booking, create_user_offerer, \
    create_offerer, create_venue, create_thing_offer, create_event_offer, create_stock_from_offer, \
    create_stock_from_event_occurrence, create_event_occurrence, create_thing, create_mocked_bookings

SUBJECT_USER_EVENT_BOOKING_CONFIRMATION_EMAIL = \
    'Confirmation de votre réservation pour Mains, sorts et papiers le 20 juillet 2019 à 14:00'

SUBJECT_USER_THING_BOOKING_CONFIRMATION_EMAIL = \
    'Confirmation de votre commande pour Test Book'

SUBJECT_USER_BOOKING_THING_CANCELLATION_EMAIL = \
    'Annulation de votre commande pour Test Book'

SUBJECT_USER_BOOKING_EVENT_CANCELLATION_EMAIL = \
    'Annulation de votre réservation pour Mains, sorts et papiers le 20 juillet 2019 à 14:00'

SUBJECT_OFFERER_BOOKING_CONFIRMATION_EMAIL = \
    '[Réservations] Nouvelle réservation pour Mains, sorts et papiers - 20 juillet 2019 à 14:00'


def get_mocked_response_status_200(entity):
    response = MagicMock(status_code=200, text='')
    response.json = MagicMock(return_value=MOCKED_SIREN_ENTREPRISES_API_RETURN)
    return response


@mocked_mail
@clean_database
@pytest.mark.standalone
def test_make_user_booking_event_recap_email_should_have_standard_subject_and_body(app):
    # Given
    venue = create_venue(None, 'Test offerer', 'reservations@test.fr', '123 rue test', '93000', 'Test city', '93')
    stock = create_stock_with_event_offer(offerer=None, venue=venue)
    user = create_user('Test', departement_code='93', email='test@email.com', can_book_free_offers=True)
    booking = create_booking(user, stock, venue, None)
    booking.token = '56789'

    # When
    recap_email = make_user_booking_recap_email(booking, is_cancellation=False)

    # Then
    email_html = remove_whitespaces(recap_email['Html-part'])
    recap_email_soup = BeautifulSoup(email_html, 'html.parser')
    assert recap_email['Subject'] == SUBJECT_USER_EVENT_BOOKING_CONFIRMATION_EMAIL
    assert 'Bonjour Test,' in recap_email_soup.find("p", {"id": 'mail-greeting'}).text
    assert 'Nous vous confirmons votre réservation pour Mains, sorts et papiers' in recap_email_soup.find("div", {
        "id": 'mail-content'}).text
    assert 'le 20 juillet 2019 à 14:00' in recap_email_soup.find("div", {"id": 'mail-content'}).text
    assert 'proposé par Test offerer' in recap_email_soup.find("div", {"id": 'mail-content'}).text
    assert '(Adresse : 123 rue test, 93000 Test city).' in recap_email_soup.find("div", {"id": 'mail-content'}).text
    assert 'Votre code de réservation est le 56789.' in recap_email_soup.find("div", {"id": 'mail-content'}).text
    assert 'Cordialement,' in recap_email_soup.find("p", {"id": 'mail-salutation'}).text
    assert 'L\'équipe pass Culture' in recap_email_soup.find("p", {"id": 'mail-salutation'}).text


@mocked_mail
@clean_database
@pytest.mark.standalone
def test_make_user_booking_event_recap_email_should_have_standard_cancellation_body_and_subject(app):
    # Given
    venue = create_venue(None, 'Test offerer', 'reservations@test.fr', '123 rue test', '93000', 'Test city', '93')
    stock = create_stock_with_event_offer(offerer=None,
                                          venue=venue)
    user = create_user('Test', departement_code='93', email='test@email.com', can_book_free_offers=True)
    booking = create_booking(user, stock, venue, None)

    # When
    recap_email = make_user_booking_recap_email(booking, is_cancellation=True)

    # Then
    email_html = remove_whitespaces(recap_email['Html-part'])
    recap_email_soup = BeautifulSoup(email_html, 'html.parser')
    mail_content = recap_email_soup.find('div', {"id": 'mail-content'}).text
    assert 'Votre réservation pour Mains, sorts et papiers,' in mail_content
    assert 'proposé par Test offerer' in mail_content
    assert 'le 20 juillet 2019 à 14:00,' in mail_content
    assert 'a bien été annulée.' in mail_content
    assert recap_email['Subject'] == SUBJECT_USER_BOOKING_EVENT_CANCELLATION_EMAIL


@mocked_mail
@clean_database
@pytest.mark.standalone
def test_maker_user_booking_thing_recap_email_should_have_standard_body_and_subject(app):
    # Given
    venue = create_venue(None, 'Test offerer', 'reservations@test.fr', '123 rue test', '93000', 'Test city', '93')
    thing_offer = create_thing_offer(venue=None)
    stock = create_stock_with_thing_offer(offerer=None, venue=venue, thing_offer=thing_offer)
    stock.offer.thing.idAtProviders = '12345'
    user = create_user('Test', departement_code='93', email='test@email.com', can_book_free_offers=True)
    booking = create_booking(user, stock, venue, None)
    booking.token = '56789'

    # When
    recap_email = make_user_booking_recap_email(booking, is_cancellation=False)

    # Then
    email_html = remove_whitespaces(recap_email['Html-part'])
    recap_email_soup = BeautifulSoup(email_html, 'html.parser')
    mail_content = recap_email_soup.find("div", {"id": 'mail-content'}).text
    assert 'Nous vous confirmons votre commande pour Test Book (Ref: 12345),' in mail_content
    assert 'proposé par Test offerer.' in mail_content
    assert recap_email['Subject'] == SUBJECT_USER_THING_BOOKING_CONFIRMATION_EMAIL


@mocked_mail
@clean_database
@pytest.mark.standalone
def test_make_user_booking_thing_recap_email_should_have_standard_cancellation_body_and_subject(app):
    # Given
    venue = create_venue(None, 'Test offerer', 'reservations@test.fr', '123 rue test', '93000', 'Test city', '93')
    thing_offer = create_thing_offer(venue=None)
    stock = create_stock_with_thing_offer(offerer=None, venue=venue, thing_offer=thing_offer)
    stock.offer.thing.idAtProviders = '12345'
    user = create_user('Test', departement_code='93', email='test@email.com', can_book_free_offers=True)
    booking = create_booking(user, stock, venue, None)

    # When
    recap_email = make_user_booking_recap_email(booking, is_cancellation=True)

    # Then
    html_email = remove_whitespaces(recap_email['Html-part'])
    recap_email_soup = BeautifulSoup(html_email, 'html.parser')
    assert 'Votre commande pour Test Book (Ref: 12345),' in recap_email_soup.find("div", {"id": 'mail-content'}).text
    assert recap_email['Subject'] == SUBJECT_USER_BOOKING_THING_CANCELLATION_EMAIL


@mocked_mail
@clean_database
@pytest.mark.standalone
def test_booking_recap_email_html_should_have_place_and_structure(app):
    # Given
    venue = create_venue(None, 'Test offerer', 'reservations@test.fr', '123 rue test', '93000', 'Test city', '93')
    stock = create_stock_with_event_offer(offerer=None,
                                          venue=venue)
    user = create_user('Test', departement_code='93', email='test@email.com', can_book_free_offers=True)
    booking = create_booking(user, stock, venue, None)
    booking.token = '56789'

    # When
    with patch('utils.mailing.find_all_ongoing_bookings_by_stock', return_value=[booking]):
        recap_email = make_offerer_booking_recap_email_after_user_action(booking)

    # Then
    email_html = remove_whitespaces(recap_email['Html-part'])
    recap_email_soup = BeautifulSoup(email_html, 'html.parser')
    assert 'Cher partenaire pass Culture,' in recap_email_soup.find('p', {'id': 'mail-greeting'}).text
    assert 'Test (test@email.com) vient de faire une nouvelle réservation.' in recap_email_soup.find('p', {
        'id': 'action'}).text
    assert 'Voici le récapitulatif des réservations à ce jour :' in recap_email_soup.find('p', {'id': 'recap'}).text
    assert '(total 1) pour Mains, sorts et papiers' in recap_email_soup.find('p', {'id': 'recap'}).text
    assert 'le 20 juillet 2019 à 14:00,' in recap_email_soup.find('p', {'id': 'recap'}).text
    assert 'proposé par Test offerer (Adresse : 123 rue test, 93000 Test city).' in recap_email_soup.find('p', {
        'id': 'recap'}).text
    assert 'Nom ou pseudo' in recap_email_soup.find('table', {'id': 'recap-table'}).text
    assert 'Email' in recap_email_soup.find('table', {'id': 'recap-table'}).text
    assert 'Code réservation' in recap_email_soup.find('table', {'id': 'recap-table'}).text
    assert 'Test' in recap_email_soup.find('table', {'id': 'recap-table'}).text
    assert 'test@email.com' in recap_email_soup.find('table', {'id': 'recap-table'}).text
    assert '56789' in recap_email_soup.find('table', {'id': 'recap-table'}).text
    assert recap_email['Subject'] == SUBJECT_OFFERER_BOOKING_CONFIRMATION_EMAIL


@mocked_mail
@clean_database
@pytest.mark.standalone
def test_booking_recap_email_html_should_not_have_cancelled_or_used_bookings(app):
    # Given
    venue = create_venue(Offerer(), 'Test offerer', 'reservations@test.fr', '123 rue test', '93000', 'Test city', '93')
    stock = create_stock_with_event_offer(offerer=Offerer(),
                                          venue=venue)

    user1 = create_user('Test1', departement_code='93', email='test@email.com', can_book_free_offers=True)
    booking1 = create_booking(user1, stock)

    user2 = create_user('Test2', departement_code='93', email='test@email.com', can_book_free_offers=True)
    booking2 = create_booking(user2, stock)

    ongoing_bookings = [booking1, booking2]

    # When
    with patch('utils.mailing.find_all_ongoing_bookings_by_stock', return_value=ongoing_bookings):
        recap_email = make_offerer_booking_recap_email_after_user_action(booking1)

    # Then
    email_html = BeautifulSoup(recap_email['Html-part'], 'html.parser')
    html_recap_table = str(email_html.find("table", {"id": "recap-table"}))
    assert '<td>Test1</td>' in html_recap_table
    assert '<td>Test2</td>' in html_recap_table
    assert '<td>Cancelled</td>' not in html_recap_table
    assert '<td>Used</td>' not in html_recap_table


@mocked_mail
@clean_database
@pytest.mark.standalone
def test_offerer_recap_email_past_offer_without_booking(app):
    # Given
    expected_subject = '[Réservations] Récapitulatif pour Mains, sorts et papiers le 20 juillet 2017 à 14:00'
    venue = create_venue(None, 'Test offerer', 'reservations@test.fr', '123 rue test', '93000', 'Test city', '93')
    stock = create_stock_with_event_offer(offerer=None,
                                          venue=venue,
                                          beginning_datetime_future=False)

    # When
    with patch('utils.mailing.find_all_ongoing_bookings_by_stock', return_value=[]):
        recap_email = make_final_recap_email_for_stock_with_event(stock)

    # Then
    mail_html = remove_whitespaces(recap_email['Html-part'])
    recap_email_soup = BeautifulSoup(mail_html, 'html.parser')
    assert recap_email['Subject'] == expected_subject
    assert 'Voici le récapitulatif final des réservations :' in recap_email_soup.find("p", {"id": 'recap'}).text
    assert '(total 0) pour Mains, sorts et papiers' in recap_email_soup.find("p", {"id": 'recap'}).text
    assert 'Aucune réservation' in recap_email_soup.find("p", {"id": 'no-recap'}).text


@mocked_mail
@clean_database
@pytest.mark.standalone
def test_offerer_recap_email_past_offer_with_booking(app):
    # Given
    venue = create_venue(None, 'Test offerer', 'reservations@test.fr', '123 rue test', '93000', 'Test city', '93')
    stock = create_stock_with_event_offer(offerer=None,
                                          venue=venue,
                                          beginning_datetime_future=False)
    user = create_user('Test', departement_code='93', email='test@email.com', can_book_free_offers=True)
    booking = create_booking(user, stock, venue, None)
    booking.token = '56789'
    stock.bookings = [booking]

    # When
    with patch('utils.mailing.find_all_ongoing_bookings_by_stock', return_value=[booking]):
        recap_email = make_final_recap_email_for_stock_with_event(stock)

    # Then
    email_html = remove_whitespaces(recap_email['Html-part'])
    recap_email_soup = BeautifulSoup(email_html, 'html.parser')
    recap_html = recap_email_soup.find('p', {'id': 'recap'}).text
    assert 'Voici le récapitulatif final des réservations :' in recap_html
    assert '(total 1) pour Mains, sorts et papiers' in recap_html
    assert 'le 20 juillet 2017 à 14:00,' in recap_html
    assert 'proposé par Test offerer (Adresse : 123 rue test, 93000 Test city).' in recap_html
    recap_table_html = recap_email_soup.find('table', {'id': 'recap-table'}).text
    assert 'Test' in recap_table_html
    assert 'test@email.com' in recap_table_html
    assert '56789' in recap_table_html


@mocked_mail
@clean_database
@pytest.mark.standalone
def test_offerer_recap_email_does_not_send_cancelled_or_used_booking(app):
    # Given
    venue = create_venue(Offerer(), 'Test offerer', 'reservations@test.fr', '123 rue test', '93000', 'Test city', '93')
    stock = create_stock_with_event_offer(offerer=Offerer(),
                                          venue=venue)

    user1 = create_user('Test1', departement_code='93', email='test@email.com', can_book_free_offers=True)
    booking1 = create_booking(user1, stock)

    user2 = create_user('Test2', departement_code='93', email='test@email.com', can_book_free_offers=True)
    booking2 = create_booking(user2, stock)

    ongoing_bookings = [booking1, booking2]

    # When
    with patch('utils.mailing.find_all_ongoing_bookings_by_stock', return_value=ongoing_bookings):
        recap_email = make_final_recap_email_for_stock_with_event(stock)

    # Then
    email_html = BeautifulSoup(recap_email['Html-part'], 'html.parser')
    html_recap_table = str(email_html.find("table", {"id": "recap-table"}))
    assert '<td>Test1</td>' in html_recap_table
    assert '<td>Test2</td>' in html_recap_table
    assert '<td>Cancelled</td>' not in html_recap_table
    assert '<td>Used</td>' not in html_recap_table


@mocked_mail
@clean_database
@pytest.mark.standalone
def test_offerer_recap_email_future_offer_when_new_booking_with_old_booking(app):
    # Given
    venue = create_venue(None, 'Test offerer', 'reservations@test.fr', '123 rue test', '93000', 'Test city', '93')
    stock = create_stock_with_event_offer(offerer=None,
                                          venue=venue,
                                          beginning_datetime_future=True)
    user_1 = create_user('Test', departement_code='93', email='test@email.com', can_book_free_offers=True)
    user_2 = create_user('Test', departement_code='93', email='test@email.com', can_book_free_offers=True)
    user_2.publicName = 'Test 2'
    user_2.email = 'other_test@email.com'
    booking_1 = create_booking(user_1, stock, venue, None)
    booking_1.token = '56789'
    booking_2 = create_booking(user_2, stock, venue, None)
    booking_2.token = '67890'

    # When
    with patch('utils.mailing.find_all_ongoing_bookings_by_stock', return_value=[booking_1, booking_2]):
        recap_email = make_offerer_booking_recap_email_after_user_action(booking_2)

    # Then
    email_html = remove_whitespaces(recap_email['Html-part'])
    recap_email_soup = BeautifulSoup(email_html, 'html.parser')
    action_html = recap_email_soup.find('p', {'id': 'action'}).text
    recap_table_html = recap_email_soup.find('table', {'id': 'recap-table'}).text
    recap_html = recap_email_soup.find('p', {'id': 'recap'}).text
    assert 'Test 2 (other_test@email.com) vient de faire une nouvelle réservation.' in action_html
    assert '(total 2) pour Mains, sorts et papiers' in recap_html
    assert 'Test' in recap_table_html
    assert 'Test 2' in recap_table_html
    assert 'test@email.com' in recap_table_html
    assert 'other_test@email.com' in recap_table_html
    assert '56789' in recap_table_html
    assert '67890' in recap_table_html


@mocked_mail
@clean_database
@pytest.mark.standalone
def test_offerer_booking_recap_email_thing_offer(app):
    # Given
    venue = create_venue(None, 'Test offerer', 'reservations@test.fr', '123 rue test', '93000', 'Test city', '93')
    thing_offer = create_thing_offer(venue=None)
    stock = create_stock_with_thing_offer(offerer=None, venue=venue, thing_offer=thing_offer)
    user = create_user('Test', departement_code='93', email='test@email.com', can_book_free_offers=True)
    booking = create_booking(user, stock, venue, None)
    booking.token = '56789'

    # When
    with patch('utils.mailing.find_all_ongoing_bookings_by_stock', return_value=[booking]):
        recap_email = make_offerer_booking_recap_email_after_user_action(booking)

    # Then

    email_html = remove_whitespaces(recap_email['Html-part'])
    recap_email_soup = BeautifulSoup(email_html, 'html.parser')
    recap_html = recap_email_soup.find("p", {"id": 'recap'})
    action_html = recap_email_soup.find("p", {"id": 'action'}).text
    assert 'Test (test@email.com) vient de faire une nouvelle réservation' in action_html
    assert 'pour Test Book,' in action_html
    assert 'proposé par Test offerer (Adresse : 123 rue test, 93000 Test city).' in action_html
    assert recap_html is None
    action_table_html = recap_email_soup.find("table", {"id": 'recap-table'})
    assert action_table_html is None


@mocked_mail
@clean_database
@pytest.mark.standalone
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
    assert div_offerer.strong.a['href'] == 'localhost/validate?modelNames=Offerer&token={}'.format(
        offerer.validationToken)
    assert div_offerer.strong.a.text == 'cliquez ici'

    div_user_offerer = html.select('div.user_offerer')[0]
    assert div_user_offerer.h2.text == 'Nouveau rattachement :'
    assert div_user_offerer.h3.text == 'Utilisateur :'
    assert div_user_offerer.strong.a['href'] == 'localhost/validate?modelNames=UserOfferer&token={}'.format(
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
@pytest.mark.standalone
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
@pytest.mark.standalone
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
@pytest.mark.standalone
def test_validation_email_should_not_return_clearTextPassword(app):
    # Given
    validation_token = secrets.token_urlsafe(20)
    offerer = create_offerer(siren='732075312', address='122 AVENUE DE FRANCE', city='Paris', postal_code='75013',
                             name='Accenture', validation_token=validation_token)

    user = create_user(public_name='Test', departement_code='75', email='user@accenture.com',
                       can_book_free_offers=False, password='totallysafepsswd', validation_token=validation_token)

    user_offerer = create_user_offerer(user, offerer, validation_token)

    mocked_api_entreprises = get_mocked_response_status_200

    # When
    email = write_object_validation_email(offerer, user_offerer, get_by_siren=mocked_api_entreprises)

    # Then
    email_html_soup = BeautifulSoup(email['Html-part'], features="html.parser")
    assert 'clearTextPassword' not in str(email_html_soup)
    assert 'totallysafepsswd' not in str(email_html_soup)


@pytest.mark.standalone
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
@clean_database
@pytest.mark.standalone
def test_make_offerer_booking_user_cancellation_email_for_physical_venue(app):
    # Given
    offerer = create_offerer()
    venue = create_venue(offerer, 'Test offerer', 'reservations@test.fr', '123 rue test', '93000', 'Test city', '93')
    event_offer = create_event_offer(venue, event_name='Test Event')
    now = datetime.utcnow() + timedelta()
    event_occurrence = create_event_occurrence(event_offer, beginning_datetime=now)
    stock = create_stock_from_event_occurrence(event_occurrence, price=0)
    user_1 = create_user('Test1', departement_code='93', email='test1@email.com')
    user_2 = create_user('Test2', departement_code='93', email='test2@email.com')
    booking_1 = create_booking(user_1, stock, venue)
    booking_2 = create_booking(user_2, stock, venue)
    booking_2.isCancelled = True
    PcObject.check_and_save(booking_1, booking_2)

    # When
    with patch('utils.mailing.find_all_ongoing_bookings_by_stock', return_value=[booking_1]):
        recap_email = make_offerer_booking_recap_email_after_user_action(booking_2, is_cancellation=True)

    # Then
    email_html = remove_whitespaces(recap_email['Html-part'])
    parsed_email = BeautifulSoup(email_html, 'html.parser')
    assert "<strong>Test2</strong> (test2@email.com) vient d'annuler sa réservation." in str(
        parsed_email.find("p", {"id": "action"}))
    assert "Voici le récapitulatif des réservations à ce jour :" in str(parsed_email.find("p", {"id": "recap"}))
    assert "(total 1) pour Test Event" in str(parsed_email.find("p", {"id": "recap"}))
    assert "le 15 octobre 2018 à 11:21," in str(parsed_email.find("p", {"id": "recap"}))
    assert "proposé par Test offerer (Adresse : 123 rue test, 93000 Test city)." in str(
        parsed_email.find("p", {"id": "recap"}))
    assert "<td>Test1</td>" in str(parsed_email.find("table", {"id": "recap-table"}))
    assert "<td>Test2</td>" not in str(parsed_email.find("table", {"id": "recap-table"}))
    assert "<td>test1@email.com</td>" in str(parsed_email.find("table", {"id": "recap-table"}))
    assert "<td>{token}</td>".format(token=booking_1.token) in str(parsed_email.find("table", {"id": "recap-table"}))


@clean_database
@pytest.mark.standalone
@pytest.mark.offerer_driven_cancellation
def test_make_offerer_driven_cancellation_email_for_user_event(app):
    # Given
    user = create_user(public_name='John Doe')
    offerer = create_offerer(name='Test offerer')
    venue = create_venue(offerer)
    offer = create_event_offer(venue, event_name='Mains, sorts et papiers')
    event_occurrence = create_event_occurrence(offer,
                                               beginning_datetime=datetime(2019, 7, 20, 12, 0, 0, tzinfo=timezone.utc))
    stock = create_stock_from_event_occurrence(event_occurrence, price=20, available=10)
    booking = create_booking(user, stock)

    # When
    with patch('utils.mailing.find_all_ongoing_bookings_by_stock', return_value=[]):
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
@pytest.mark.standalone
@pytest.mark.offerer_driven_cancellation
def test_make_offerer_driven_cancellation_email_for_user_thing(app):
    # Given
    user = create_user(public_name='John Doe')
    offerer = create_offerer(name='Test offerer')
    venue = create_venue(offerer)
    offer = create_thing_offer(venue, thing_name='Test Book')
    stock = create_stock_from_offer(offer, price=15, available=10)
    booking = create_booking(user, stock, quantity=2)

    # When
    with patch('utils.mailing.find_all_ongoing_bookings_by_stock', return_value=[]):
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
@pytest.mark.standalone
@pytest.mark.offerer_driven_cancellation
def test_make_offerer_driven_cancellation_email_for_offerer_event(app):
    # Given
    user = create_user(public_name='John Doe', email='john@doe.fr')
    offerer = create_offerer(name='Test offerer')
    venue = create_venue(offerer, name='Le petit théâtre', address='1 rue de la Libération', city='Montreuil',
                         postal_code='93100')
    offer = create_event_offer(venue, event_name='Le théâtre des ombres')
    event_occurrence = create_event_occurrence(offer,
                                               beginning_datetime=datetime(2019, 7, 20, 12, 0, 0, tzinfo=timezone.utc))
    stock = create_stock_from_event_occurrence(event_occurrence, price=20, available=10)
    booking = create_booking(user, stock)

    # When
    with patch('utils.mailing.find_all_ongoing_bookings_by_stock', return_value=[]):
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
@pytest.mark.standalone
@pytest.mark.offerer_driven_cancellation
def test_make_offerer_driven_cancellation_email_for_offerer_thing_and_already_existing_booking(app):
    # Given
    user = create_user(public_name='John Doe', email='john@doe.fr')
    offerer = create_offerer(name='Test offerer')
    venue = create_venue(offerer, name='La petite librairie', address='1 rue de la Libération', city='Montreuil',
                         postal_code='93100')
    thing = create_thing(thing_name='Le récit de voyage')
    offer = create_thing_offer(venue, thing)
    stock = create_stock_from_offer(offer, price=0, available=10)
    booking = create_booking(user, stock)

    user2 = create_user(public_name='James Bond', email='bond@james.bond.uk')
    booking2 = create_booking(user2, stock)
    ongoing_bookings = [booking2]

    # When
    with patch('utils.mailing.find_all_ongoing_bookings_by_stock', return_value=ongoing_bookings):
        email = make_offerer_driven_cancellation_email_for_offerer(booking)

    # Then
    email_html = BeautifulSoup(email['Html-part'], 'html.parser')
    html_action = str(email_html.find("p", {"id": "action"}))
    html_recap = email_html.find("p", {"id": "recap"})
    html_recap_table = email_html.find("table", {"id": "recap-table"})
    assert 'Vous venez d\'annuler' in html_action
    assert 'John Doe' in html_action
    assert 'john@doe.fr' in html_action
    assert 'pour Le récit de voyage' in html_recap.text
    assert 'proposé par La petite librairie' in html_recap.text
    assert '1 rue de la Libération' in html_recap.text
    assert 'Montreuil' in html_recap.text
    assert '93100' in html_recap.text
    assert html_recap_table is None
    assert email[
               'Subject'] == 'Confirmation de votre annulation de réservation pour Le récit de voyage, proposé par La petite librairie'


@clean_database
@pytest.mark.standalone
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
@pytest.mark.standalone
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
@pytest.mark.standalone
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
@pytest.mark.standalone
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
@pytest.mark.standalone
def test_make_make_batch_cancellation_email_for_case_event_occurrence(app):
    # Given
    bookings = create_mocked_bookings(num_bookings=4, venue_email='venue@email.com', name='Le récit de voyage')
    # When
    email = make_batch_cancellation_email(bookings, cancellation_case='event_occurrence')
    # Then
    email_html = remove_whitespaces(email['Html-part'])
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
    assert email['FromEmail'] == 'passculture@beta.gouv.fr'
    assert email['FromName'] == 'pass Culture pro'
    assert email['Subject'] == 'Annulation de réservations pour Le récit de voyage'


@clean_database
@pytest.mark.standalone
def test_make_make_batch_cancellation_email_for_case_stock(app):
    # Given
    bookings = create_mocked_bookings(num_bookings=4, venue_email='venue@email.com', name='Le récit de voyage')
    # When
    email = make_batch_cancellation_email(bookings, cancellation_case='stock')
    # Then
    email_html = remove_whitespaces(email['Html-part'])
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
    assert email['FromEmail'] == 'passculture@beta.gouv.fr'
    assert email['FromName'] == 'pass Culture pro'
    assert email['Subject'] == 'Annulation de réservations pour Le récit de voyage'


@clean_database
@pytest.mark.standalone
def test_make_offerer_booking_user_cancellation_email_when_virtual_venue_does_not_show_address(app):
    # Given
    offerer = create_offerer()
    venue = create_venue(offerer, 'Test offerer', 'reservations@test.fr', is_virtual=True, siret=None)
    thing_offer = create_thing_offer(venue)
    stock = create_stock_from_offer(thing_offer, price=0)
    user_1 = create_user('Test1', departement_code='93', email='test1@email.com')
    user_2 = create_user('Test2', departement_code='93', email='test2@email.com')
    booking_1 = create_booking(user_1, stock, venue)
    booking_2 = create_booking(user_2, stock, venue)
    booking_2.isCancelled = True
    PcObject.check_and_save(booking_1, booking_2)

    # When
    with patch('utils.mailing.find_all_ongoing_bookings_by_stock', return_value=[booking_1]):
        recap_email = make_offerer_booking_recap_email_after_user_action(booking_2, is_cancellation=True)

        # Then
        email_html = BeautifulSoup(recap_email['Html-part'], 'html.parser')
    assert 'offre numérique proposée par Test offerer' in str(email_html.find('p', {'id': 'action'}))
    assert '(Adresse:' not in str(email_html.find('p', {'id': 'action'}))


@clean_database
@pytest.mark.standalone
def test_make_offerer_booking_user_cancellation_does_not_have_recap_information(app):
    # Given
    offerer = create_offerer()
    venue = create_venue(offerer, 'Test offerer', 'reservations@test.fr', is_virtual=True, siret=None)
    thing_offer = create_thing_offer(venue)
    stock = create_stock_from_offer(thing_offer, price=0)
    user_1 = create_user('Test1', departement_code='93', email='test1@email.com')
    user_2 = create_user('Test2', departement_code='93', email='test2@email.com')
    booking_1 = create_booking(user_1, stock, venue)
    booking_2 = create_booking(user_2, stock, venue)
    booking_2.isCancelled = True
    PcObject.check_and_save(booking_1, booking_2)

    # When
    with patch('utils.mailing.find_all_ongoing_bookings_by_stock', return_value=[booking_1]):
        recap_email = make_offerer_booking_recap_email_after_user_action(booking_2, is_cancellation=True)

    # Then
    email_html = BeautifulSoup(recap_email['Html-part'], 'html.parser')
    assert email_html.find('table', {'id': 'recap-table'}) is None


@pytest.mark.standalone
@freeze_time('2018-10-15 09:21:34')
def test_make_payment_transaction_email_sends_a_xml_file_with_its_checksum_in_email_body(app):
    # Given
    xml = '<?xml version="1.0" encoding="UTF-8"?><Document xmlns="urn:iso:std:iso:20022:tech:xsd:pain.001.001.03"></Document>'
    file_hash = '12345678AZERTYU'

    # When
    email = make_payment_transaction_email(xml, file_hash)

    # Then
    assert email["From"] == {"Email": "passculture@beta.gouv.fr",
                             "Name": "pass Culture Pro"}
    assert email["Subject"] == "Virements pass Culture Pro - 2018-10-15"
    assert email["Attachments"] == [{"ContentType": "text/xml",
                                     "Filename": "transaction_banque_de_france_20181015.xml",
                                     "Base64Content": b'PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iVVRGLTgiPz48RG9j'
                                                      b'dW1lbnQgeG1sbnM9InVybjppc286c3RkOmlzbzoyMDAyMjp0ZWNoOnhz'
                                                      b'ZDpwYWluLjAwMS4wMDEuMDMiPjwvRG9jdW1lbnQ+'}]
    email_html = BeautifulSoup(email['Html-part'], 'html.parser')
    assert 'transaction_banque_de_france_20181015.xml' in email_html.find('p', {'id': 'file_name'}).find('strong').text
    assert '12345678AZERTYU' in email_html.find('p', {'id': 'file_hash'}).find('strong').text


@pytest.mark.standalone
@freeze_time('2018-10-15 09:21:34')
def test_make_payment_details_email():
    # Given
    csv = '"header A","header B","header C","header D"\n"part A","part B","part C","part D"\n'

    # When
    email = make_payment_details_email(csv)

    # Then
    assert email["From"] == {"Email": "passculture@beta.gouv.fr",
                             "Name": "pass Culture Pro"}
    assert email["Subject"] == "Détails des paiements pass Culture Pro - 2018-10-15"
    assert email["Html-part"] == ""
    assert email["Attachments"] == [{"ContentType": "text/csv",
                                     "Filename": "details_des_paiements_20181015.csv",
                                     "Base64Content": b'ImhlYWRlciBBIiwiaGVhZGVyIEIiLCJoZWFkZXIgQyIsImhlYWRlciBE'
                                                      b'IgoicGFydCBBIiwicGFydCBCIiwicGFydCBDIiwicGFydCBEIgo='}]


@pytest.mark.standalone
@freeze_time('2018-10-15 09:21:34')
def test_make_wallet_balances_email():
    # Given
    csv = '"header A","header B","header C","header D"\n"part A","part B","part C","part D"\n'

    # When
    email = make_wallet_balances_email(csv)

    # Then
    assert email["From"] == {"Email": "passculture@beta.gouv.fr",
                             "Name": "pass Culture Pro"}
    assert email["Subject"] == "Soldes des utilisateurs pass Culture - 2018-10-15"
    assert email["Html-part"] == ""
    assert email["Attachments"] == [{"ContentType": "text/csv",
                                     "Filename": "soldes_des_utilisateurs_20181015.csv",
                                     "Base64Content": b'ImhlYWRlciBBIiwiaGVhZGVyIEIiLCJoZWFkZXIgQyIsImhlYWRlciBE'
                                                      b'IgoicGFydCBBIiwicGFydCBCIiwicGFydCBDIiwicGFydCBEIgo='}]


class UserValidationEmailsTest:
    @pytest.mark.standalone
    def test_make_webapp_user_validation_email_includes_validation_url_with_token_and_user_email(self, app):
        # Given
        user = create_user(email="test@email.com")
        user.generate_validation_token()
        app_origin_url = 'portail-pro'

        # When
        with patch('utils.mailing.feature_send_mail_to_users_enabled', return_value=True):
            email = make_user_validation_email(user, app_origin_url, is_webapp=True)

        # Then
        email_html = BeautifulSoup(email['Html-part'], 'html.parser')
        mail_content = email_html.find("div", {"id": 'mail-content'}).text
        assert 'Bonjour {},'.format(user.publicName) in email_html.find("p", {"id": 'mail-greeting'}).text
        assert "Vous venez de créer un compte pass Culture avec votre adresse test@email.com." in mail_content
        assert 'localhost/validate/user/{}'.format(user.validationToken) in \
               email_html.find('a', href=True)['href']
        assert 'Vous pouvez valider votre adresse email en suivant ce lien :' in mail_content
        assert 'localhost/validate/user/{}'.format(user.validationToken) in mail_content
        assert email['To'] == user.email
        assert email['FromName'] == 'pass Culture'
        assert email['Subject'] == 'Validation de votre adresse email pour le pass Culture'
        assert email['FromEmail'] == 'passculture@beta.gouv.fr'

    @pytest.mark.standalone
    def test_make_pro_user_validation_email_includes_validation_url_with_token_and_user_email(self, app):
        # Given
        user = create_user(email="test@email.com")
        user.generate_validation_token()
        app_origin_url = 'portail-pro'

        # When
        email = make_user_validation_email(user, app_origin_url, is_webapp=False)

        # Then
        email_html = BeautifulSoup(email['Html-part'], 'html.parser')
        mail_content = email_html.find("div", {"id": 'mail-content'}).text
        assert 'Cher partenaire pass Culture,'.format(user.publicName) in email_html.find("p",
                                                                                          {"id": 'mail-greeting'}).text
        assert "Vous venez de créer un compte pass Culture pro avec votre adresse test@email.com." in mail_content

        assert 'portail-pro/inscription/validation/{}'.format(user.validationToken) in \
               email_html.find('a', href=True)['href']
        assert 'Vous pouvez valider votre adresse email en suivant ce lien :' in mail_content
        assert 'portail-pro/inscription/validation/{}'.format(user.validationToken) in mail_content
        assert email['FromName'] == 'pass Culture pro'


def remove_whitespaces(text):
    text = re.sub('\n\s+', ' ', text)
    text = re.sub('\n', '', text)
    return text


@pytest.mark.standalone
def test_make_venue_validation_email(app):
    # Given
    offerer = create_offerer(name='La Structure', siren='123456789')
    venue = create_venue(offerer, name='Le Lieu', comment='Ceci est mon commentaire')
    venue.generate_validation_token()

    # When
    email = make_venue_validation_email(venue)

    # Then
    assert email["FromEmail"] == "passculture@beta.gouv.fr"
    assert email["FromName"] == "pass Culture"
    assert email["Subject"] == "{} - rattachement de lieu pro à valider : {}".format(venue.departementCode, venue.name)
    email_html = remove_whitespaces(email['Html-part'])
    parsed_email = BeautifulSoup(email_html, 'html.parser')
    html_validation = parsed_email.find('p', {'id': 'validation'}).text
    html_validation_link = parsed_email.find('a', {'id': 'validation-link'}).text
    assert 'La structure "La Structure" (SIREN : 123456789)' in html_validation
    assert 'a rattaché le lieu suivant sans renseigner de SIRET' in html_validation
    assert 'Nom : "Le Lieu"' in html_validation
    assert 'Commentaire de la structure : "Ceci est mon commentaire".' in html_validation
    assert 'localhost/validate/venue?token={}'.format(venue.validationToken) in html_validation
    assert 'localhost/validate/venue?token={}'.format(venue.validationToken) in html_validation_link


@pytest.mark.standalone
def test_make_venue_validation_confirmation_email(app):
    # Given
    offerer = create_offerer(name='La Structure', siren='123456789')
    venue = create_venue(offerer, name='Le Lieu', comment='Ceci est mon commentaire')

    # When
    email = make_venue_validation_confirmation_email(venue)

    # Then
    assert email['Subject'] == 'Validation du rattachement du lieu "Le Lieu" à votre structure "La Structure"'
    assert email["FromEmail"] == "passculture@beta.gouv.fr"
    assert email["FromName"] == "pass Culture pro"
    email_html = remove_whitespaces(email['Html-part'])
    parsed_email = BeautifulSoup(email_html, 'html.parser')
    html_validation = str(parsed_email.find('p', {'id': 'validation-details'}))
    html_greeting = str(parsed_email.find('p', {'id': 'mail-greeting'}))
    html_salutation = str(parsed_email.find('p', {'id': 'mail-salutation'}))
    assert 'Cher partenaire pass Culture,' in html_greeting
    assert 'Le rattachement du lieu "Le Lieu"' in html_validation
    assert 'à votre structure "La Structure"' in html_validation
    assert 'Cordialement,' in html_salutation
    assert 'L\'équipe pass Culture' in html_salutation
