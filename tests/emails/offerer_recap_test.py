from datetime import datetime, timedelta
from unittest.mock import patch

from bs4 import BeautifulSoup

from models import Offerer
from tests.conftest import mocked_mail, clean_database
from tests.model_creators.generic_creators import create_booking, create_user, create_offerer, create_venue
from tests.model_creators.specific_creators import create_stock_with_event_offer
from tests.utils.mailing_test import _remove_whitespaces
from utils.mailing import make_final_recap_email_for_stock_with_event


@mocked_mail
@clean_database
def test_offerer_recap_email_does_not_contain_past_offer_without_booking(app):
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
def test_offerer_recap_email_contains_past_offer_with_booking(app):
    # Given
    beginning_datetime = datetime(2017, 7, 20, 12, 0, 0)
    end_datetime = beginning_datetime + timedelta(hours=1)
    booking_limit_datetime = beginning_datetime - timedelta(days=1)
    offerer = create_offerer()
    venue = create_venue(offerer, 'Test offerer', 'reservations@test.fr', '123 rue test', '93000', 'Test city', '93')
    stock = create_stock_with_event_offer(offerer=None, venue=venue, beginning_datetime=beginning_datetime,
                                          end_datetime=end_datetime, booking_limit_datetime=booking_limit_datetime)
    user = create_user(can_book_free_offers=True, departement_code='93', email='test@example.com',
                       first_name='Jean', last_name='Dupont', public_name='Test')
    booking = create_booking(user=user, stock=stock, venue=venue)
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
def test_offerer_recap_email_does_not_retrieve_cancelled_or_used_booking(app):
    # Given
    venue = create_venue(Offerer(), 'Test offerer', 'reservations@test.fr', '123 rue test', '93000', 'Test city', '93')
    stock = create_stock_with_event_offer(offerer=Offerer(), venue=venue)

    user1 = create_user(can_book_free_offers=True, departement_code='93', email='test@example.com',
                        first_name='Lucie', last_name='Dubois', public_name='Test1')
    booking1 = create_booking(user=user1, stock=stock)

    user2 = create_user(can_book_free_offers=True, departement_code='93', email='test@example.com',
                        first_name='Jean', last_name='Dupont', public_name='Test2')
    booking2 = create_booking(user=user2, stock=stock)

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

    user1 = create_user(can_book_free_offers=True, departement_code='93', email='test@example.com',
                        public_name='Test1')
    booking1 = create_booking(user=user1, stock=stock)

    user2 = create_user(can_book_free_offers=True, departement_code='93', email='test@example.com',
                        public_name='Test2')
    booking2 = create_booking(user=user2, stock=stock)

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
