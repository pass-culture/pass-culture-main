import secrets
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest
from bs4 import BeautifulSoup

from models import PcObject, Offerer
from tests.conftest import clean_database, mocked_mail
from utils.mailing import make_user_booking_recap_email, \
    make_offerer_booking_recap_email_after_user_action, make_final_recap_email_for_stock_with_event, \
    write_object_validation_email, make_offerer_driven_cancellation_email_for_user, \
    make_reset_password_email, \
    make_offerer_driven_cancellation_email_for_offerer
from utils.test_utils import create_stock_with_event_offer, create_stock_with_thing_offer, \
    create_user, create_booking, MOCKED_SIREN_ENTREPRISES_API_RETURN, create_user_offerer, \
    create_offerer, create_venue, create_thing_offer, create_event_offer, create_stock_from_offer, \
    create_stock_from_event_occurrence, create_event_occurrence, create_thing


def get_mocked_response_status_200(entity):
    response = MagicMock(status_code=200, text='')
    response.json = MagicMock(return_value=MOCKED_SIREN_ENTREPRISES_API_RETURN)
    return response


SUBJECT_USER_EVENT_BOOKING_CONFIRMATION_EMAIL = \
    'Confirmation de votre réservation pour Mains, sorts et papiers le 20 juillet 2019 à 14:00'

HTML_USER_BOOKING_EVENT_CONFIRMATION_EMAIL = \
    '''<html>
    <body>
        <p id="mail-greeting">Bonjour Test,</p>

        <div id="mail-content">
            Nous vous confirmons votre réservation pour Mains, sorts et papiers le 20 juillet 2019 à 14:00, proposé par Test offerer (Adresse : 123 rue test, 93000 Test city). Votre code de réservation est le 56789.
        </div>

        <p id="mail-salutation">
            Cordialement,
            <br>L\'équipe pass Culture
        </p>

    </body>
</html>'''

SUBJECT_USER_THING_BOOKING_CONFIRMATION_EMAIL = \
    'Confirmation de votre commande pour Test Book'

HTML_USER_BOOKING_THING_CONFIRMATION_EMAIL = '<html><body>' + \
                                             '<p id="mail-greeting">Bonjour Test,</p>' + \
                                             '<div id="mail-content">Nous vous confirmons votre commande pour Test Book (Ref: 12345),' + \
                                             ' proposé par Test offerer.' + \
                                             ' Votre code de réservation est le 56789.</div>' + \
                                             '<p id="mail-salutation">Cordialement,' + \
                                             '<br>L\'équipe pass Culture</p>' + \
                                             '</body></html>'

SUBJECT_USER_BOOKING_THING_CANCELLATION_EMAIL = \
    'Annulation de votre commande pour Test Book'

HTML_USER_BOOKING_THING_CANCELLATION_EMAIL = '<html><body>' + \
                                             '<p id="mail-greeting">Bonjour Test,</p>' + \
                                             '<div id="mail-content">Votre commande pour Test Book (Ref: 12345), ' + \
                                             'proposé par Test offerer ' + \
                                             'a bien été annulée.</div>' + \
                                             '<p id="mail-salutation">Cordialement,' + \
                                             '<br>L\'équipe pass Culture</p>' + \
                                             '</body></html>'

SUBJECT_USER_BOOKING_EVENT_CANCELLATION_EMAIL = \
    'Annulation de votre réservation pour Mains, sorts et papiers le 20 juillet 2019 à 14:00'

HTML_USER_BOOKING_EVENT_CANCELLATION_EMAIL = '<html><body>' + \
                                             '<p id="mail-greeting">Bonjour Test,</p>' + \
                                             '<div id="mail-content">Votre réservation pour Mains, sorts et papiers, ' + \
                                             'proposé par Test offerer ' + \
                                             'le 20 juillet 2019 à 14:00, ' + \
                                             'a bien été annulée.</div>' + \
                                             '<p id="mail-salutation">Cordialement,' + \
                                             '<br>L\'équipe pass Culture</p>' + \
                                             '</body></html>'

SUBJECT_OFFERER_BOOKING_CONFIRMATION_EMAIL = \
    '[Reservations] Nouvelle reservation pour Mains, sorts et papiers - 20 juillet 2019 à 14:00'
HTML_OFFERER_BOOKING_CONFIRMATION_EMAIL = \
    '<html><body>' + \
    '<p id="mail-greeting">Cher partenaire pass Culture,</p>' + \
    '<p id="action"><strong>Test</strong> (test@email.com) vient de faire une nouvelle réservation.</p>' + \
    '<p id="recap">Voici le récapitulatif des réservations à ce jour (total 1)' + \
    ' pour Mains, sorts et papiers le 20 juillet 2019 à 14:00,' + \
    ' proposé par Test offerer (Adresse : 123 rue test, 93000 Test city).</p>' + \
    '<table id="recap-table"><tr><th>Nom ou pseudo</th><th>Email</th><th>Code réservation</th></tr>' + \
    '<tr><td>Test</td><td>test@email.com</td><td>56789</td></tr></table>' + \
    '</body></html>'


@mocked_mail
@clean_database
@pytest.mark.standalone
def test_make_user_booking_event_recap_email_should_have_standard_subject(app):
    # Given
    venue = create_venue(None, 'Test offerer', 'reservations@test.fr', '123 rue test', '93000', 'Test city', '93')
    stock = create_stock_with_event_offer(offerer=None, venue=venue)
    user = create_user('Test', 93, 'test@email.com', True)
    booking = create_booking(user, stock, venue, None)

    # When
    recap_email = make_user_booking_recap_email(booking, is_cancellation=False)

    # Then
    assert recap_email['Subject'] == SUBJECT_USER_EVENT_BOOKING_CONFIRMATION_EMAIL


@mocked_mail
@clean_database
@pytest.mark.standalone
def test_make_user_booking_event_recap_email_should_have_standard_body(app):
    # Given
    venue = create_venue(None, 'Test offerer', 'reservations@test.fr', '123 rue test', '93000', 'Test city', '93')
    stock = create_stock_with_event_offer(offerer=None, venue=venue)
    user = create_user('Test', 93, 'test@email.com', True)
    booking = create_booking(user, stock, venue, None)
    booking.token = '56789'
    expected_email_soup = BeautifulSoup(HTML_USER_BOOKING_EVENT_CONFIRMATION_EMAIL, 'html.parser')

    # When
    recap_email = make_user_booking_recap_email(booking, is_cancellation=False)

    # Then
    recap_email_soup = BeautifulSoup(recap_email['Html-part'], 'html.parser')
    assert recap_email_soup.prettify() == expected_email_soup.prettify()


@mocked_mail
@clean_database
@pytest.mark.standalone
def test_make_user_booking_event_recap_email_should_have_standard_subject_cancellation(app):
    # Given
    venue = create_venue(None, 'Test offerer', 'reservations@test.fr', '123 rue test', '93000', 'Test city', '93')
    stock = create_stock_with_event_offer(offerer=None, venue=venue)
    user = create_user('Test', 93, 'test@email.com', True)
    booking = create_booking(user, stock, venue, None)

    # When
    recap_email = make_user_booking_recap_email(booking, is_cancellation=True)

    # Then
    assert recap_email['Subject'] == SUBJECT_USER_BOOKING_EVENT_CANCELLATION_EMAIL


@mocked_mail
@clean_database
@pytest.mark.standalone
def test_make_user_booking_event_recap_email_should_have_standard_body_cancellation(app):
    # Given
    venue = create_venue(None, 'Test offerer', 'reservations@test.fr', '123 rue test', '93000', 'Test city', '93')
    stock = create_stock_with_event_offer(offerer=None,
                                          venue=venue)
    user = create_user('Test', 93, 'test@email.com', True)
    booking = create_booking(user, stock, venue, None)
    expected_email_soup = BeautifulSoup(HTML_USER_BOOKING_EVENT_CANCELLATION_EMAIL, 'html.parser')

    # When
    recap_email = make_user_booking_recap_email(booking, is_cancellation=True)

    # Then
    recap_email_soup = BeautifulSoup(recap_email['Html-part'], 'html.parser')
    assert recap_email_soup.prettify() == expected_email_soup.prettify()


@mocked_mail
@clean_database
@pytest.mark.standalone
def test_maker_user_booking_thing_recap_email_should_have_standard_body(app):
    # Given
    venue = create_venue(None, 'Test offerer', 'reservations@test.fr', '123 rue test', '93000', 'Test city', '93')
    thing_offer = create_thing_offer(venue=None)
    stock = create_stock_with_thing_offer(offerer=None, venue=venue, thing_offer=thing_offer)
    stock.offer.thing.idAtProviders = '12345'
    user = create_user('Test', 93, 'test@email.com', True)
    booking = create_booking(user, stock, venue, None)
    booking.token = '56789'
    expected_email_soup = BeautifulSoup(HTML_USER_BOOKING_THING_CONFIRMATION_EMAIL, 'html.parser')

    # When
    recap_email = make_user_booking_recap_email(booking, is_cancellation=False)

    # Then
    recap_email_soup = BeautifulSoup(recap_email['Html-part'], 'html.parser')
    assert recap_email_soup.prettify() == expected_email_soup.prettify()


@mocked_mail
@clean_database
@pytest.mark.standalone
def test_maker_user_booking_thing_recap_email_should_have_standard_subject(app):
    # Given
    venue = create_venue(None, 'Test offerer', 'reservations@test.fr', '123 rue test', '93000', 'Test city', '93')
    thing_offer = create_thing_offer(venue=None)
    stock = create_stock_with_thing_offer(offerer=None, venue=venue, thing_offer=thing_offer)
    stock.offer.thing.idAtProviders = '12345'
    user = create_user('Test', 93, 'test@email.com', True)
    booking = create_booking(user, stock, venue, None)

    # When
    recap_email = make_user_booking_recap_email(booking, is_cancellation=False)

    # Then
    assert recap_email['Subject'] == SUBJECT_USER_THING_BOOKING_CONFIRMATION_EMAIL


@mocked_mail
@clean_database
@pytest.mark.standalone
def test_make_user_booking_thing_recap_email_should_have_standard_subject_cancellation(app):
    # Given
    venue = create_venue(None, 'Test offerer', 'reservations@test.fr', '123 rue test', '93000', 'Test city', '93')
    thing_offer = create_thing_offer(venue=None)
    stock = create_stock_with_thing_offer(offerer=None, venue=venue, thing_offer=thing_offer)
    stock.offer.thing.idAtProviders = '12345'
    user = create_user('Test', 93, 'test@email.com', True)
    booking = create_booking(user, stock, venue, None)

    # When
    recap_email = make_user_booking_recap_email(booking, is_cancellation=True)

    # Then
    assert recap_email['Subject'] == SUBJECT_USER_BOOKING_THING_CANCELLATION_EMAIL


@mocked_mail
@clean_database
@pytest.mark.standalone
def test_make_user_booking_thing_recap_email_should_have_standard_body_cancellation(app):
    # Given
    venue = create_venue(None, 'Test offerer', 'reservations@test.fr', '123 rue test', '93000', 'Test city', '93')
    thing_offer = create_thing_offer(venue=None)
    stock = create_stock_with_thing_offer(offerer=None, venue=venue, thing_offer=thing_offer)
    stock.offer.thing.idAtProviders = '12345'
    user = create_user('Test', 93, 'test@email.com', True)
    booking = create_booking(user, stock, venue, None)
    expected_email_soup = BeautifulSoup(HTML_USER_BOOKING_THING_CANCELLATION_EMAIL, 'html.parser')

    # When
    recap_email = make_user_booking_recap_email(booking, is_cancellation=True)

    # Then
    recap_email_soup = BeautifulSoup(recap_email['Html-part'], 'html.parser')
    assert recap_email_soup.prettify() == expected_email_soup.prettify()


@mocked_mail
@clean_database
@pytest.mark.standalone
def test_booking_recap_email_html_should_have_place_and_structure(app):
    # Given
    venue = create_venue(None, 'Test offerer', 'reservations@test.fr', '123 rue test', '93000', 'Test city', '93')
    stock = create_stock_with_event_offer(offerer=None,
                                          venue=venue)
    user = create_user('Test', 93, 'test@email.com', True)
    booking = create_booking(user, stock, venue, None)
    booking.token = '56789'
    expected_email_soup = BeautifulSoup(HTML_OFFERER_BOOKING_CONFIRMATION_EMAIL, 'html.parser')

    # When
    with patch('utils.mailing.find_all_ongoing_bookings_by_stock', return_value=[booking]):
        recap_email = make_offerer_booking_recap_email_after_user_action(booking)

    # Then
    recap_email_soup = BeautifulSoup(recap_email['Html-part'], 'html.parser')
    assert recap_email_soup.prettify() == expected_email_soup.prettify()


@mocked_mail
@clean_database
@pytest.mark.standalone
def test_booking_recap_email_subject_should_have_defined_structure(app):
    # Given
    venue = create_venue(None, 'Test offerer', 'reservations@test.fr', '123 rue test', '93000', 'Test city', '93')
    stock = create_stock_with_event_offer(offerer=None,
                                          venue=venue)
    user = create_user('Test', 93, 'test@email.com', True)
    booking = create_booking(user, stock, venue, None)

    # When
    with patch('utils.mailing.find_all_ongoing_bookings_by_stock', return_value=[booking]):
        recap_email = make_offerer_booking_recap_email_after_user_action(booking)

    # Then
    assert recap_email['Subject'] == SUBJECT_OFFERER_BOOKING_CONFIRMATION_EMAIL


@mocked_mail
@clean_database
@pytest.mark.standalone
def test_booking_recap_email_html_should_not_have_cancelled_or_used_bookings(app):
    # Given
    venue = create_venue(Offerer(), 'Test offerer', 'reservations@test.fr', '123 rue test', '93000', 'Test city', '93')
    stock = create_stock_with_event_offer(offerer=Offerer(),
                                          venue=venue)

    user1 = create_user('Test1', 93, 'test@email.com', True)
    booking1 = create_booking(user1, stock)

    user2 = create_user('Test2', 93, 'test@email.com', True)
    booking2 = create_booking(user2, stock)

    user_cancelled = create_user('Cancelled')
    cancelled_booking = create_booking(user_cancelled, stock, is_cancelled=True)

    user_used = create_user('Used')
    used_booking = create_booking(user_used, stock, is_used=True)

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
def test_offerer_recap_email_subject_past_offer_without_booking(app):
    # Given
    expected_subject = '[Reservations] Récapitulatif pour Mains, sorts et papiers le 20 juillet 2017 à 14:00'
    venue = create_venue(None, 'Test offerer', 'reservations@test.fr', '123 rue test', '93000', 'Test city', '93')
    stock = create_stock_with_event_offer(offerer=None,
                                          venue=venue,
                                          beginning_datetime_future=False)

    # When
    with patch('utils.mailing.find_all_ongoing_bookings_by_stock', return_value=[]):
        recap_email = make_final_recap_email_for_stock_with_event(stock)

    # Then
    assert recap_email['Subject'] == expected_subject


@mocked_mail
@clean_database
@pytest.mark.standalone
def test_offerer_recap_email_past_offer_without_booking(app):
    # Given
    expected_html = '''
        <html>
            <body>
                <p id="mail-greeting">Cher partenaire pass Culture,</p>
                <p id="recap">
                    Voici le récapitulatif final des réservations (total 0) pour Mains, sorts et papiers le 20 juillet 2017 à 14:00, proposé par Test offerer (Adresse : 123 rue test, 93000 Test city).
                </p>
                <p>Aucune réservation</p>
            </body>
        </html>
        '''
    expected_html_soup = BeautifulSoup(expected_html, 'html.parser')
    venue = create_venue(None, 'Test offerer', 'reservations@test.fr', '123 rue test', '93000', 'Test city', '93')
    stock = create_stock_with_event_offer(offerer=None,
                                          venue=venue,
                                          beginning_datetime_future=False)

    # When
    with patch('utils.mailing.find_all_ongoing_bookings_by_stock', return_value=[]):
        recap_email = make_final_recap_email_for_stock_with_event(stock)

    # Then
    recap_email_soup = BeautifulSoup(recap_email['Html-part'], 'html.parser')
    assert expected_html_soup.prettify() == recap_email_soup.prettify()


@mocked_mail
@clean_database
@pytest.mark.standalone
def test_offerer_recap_email_past_offer_with_booking(app):
    # Given
    expected_html = '''
        <html>
            <body>
                <p id="mail-greeting">Cher partenaire pass Culture,</p>
                <p id="recap">
                    Voici le récapitulatif final des réservations (total 1) pour Mains, sorts et papiers le 20 juillet 2017 à 14:00, proposé par Test offerer (Adresse : 123 rue test, 93000 Test city).
                </p>
                <table id="recap-table">
                    <tr>
                        <th>Nom ou pseudo</th>
                        <th>Email</th>
                        <th>Code réservation</th>
                    </tr>
                    <tr>
                        <td>Test</td>
                        <td>test@email.com</td>
                        <td>56789</td>
                    </tr>
                </table>
            </body>
        </html>'''
    expected_html_soup = BeautifulSoup(expected_html, 'html.parser')
    venue = create_venue(None, 'Test offerer', 'reservations@test.fr', '123 rue test', '93000', 'Test city', '93')
    stock = create_stock_with_event_offer(offerer=None,
                                          venue=venue,
                                          beginning_datetime_future=False)
    user = create_user('Test', 93, 'test@email.com', True)
    booking = create_booking(user, stock, venue, None)
    booking.token = '56789'
    stock.bookings = [booking]

    # When
    with patch('utils.mailing.find_all_ongoing_bookings_by_stock', return_value=[booking]):
        recap_email = make_final_recap_email_for_stock_with_event(stock)

    # Then
    recap_email_soup = BeautifulSoup(recap_email['Html-part'], 'html.parser')
    assert recap_email_soup.prettify() == expected_html_soup.prettify()


@mocked_mail
@clean_database
@pytest.mark.standalone
def test_offerer_recap_email_does_not_send_cancelled_or_used_booking(app):
    # Given
    venue = create_venue(Offerer(), 'Test offerer', 'reservations@test.fr', '123 rue test', '93000', 'Test city', '93')
    stock = create_stock_with_event_offer(offerer=Offerer(),
                                          venue=venue)

    user1 = create_user('Test1', 93, 'test@email.com', True)
    booking1 = create_booking(user1, stock)

    user2 = create_user('Test2', 93, 'test@email.com', True)
    booking2 = create_booking(user2, stock)

    user_cancelled = create_user('Cancelled')
    cancelled_booking = create_booking(user_cancelled, stock, is_cancelled=True)

    user_used = create_user('Used')
    used_booking = create_booking(user_used, stock, is_used=True)

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
    expected_html = '''
        <html>
            <body>
                <p id="mail-greeting">Cher partenaire pass Culture,</p>
                <p id="action"><strong>Test 2</strong> (other_test@email.com) vient de faire une nouvelle réservation.</p>
                <p id="recap">
                    Voici le récapitulatif des réservations à ce jour (total 2) pour Mains, sorts et papiers le 20 juillet 2019 à 14:00, proposé par Test offerer (Adresse : 123 rue test, 93000 Test city).
                </p>
                <table id= "recap-table">
                    <tr>
                        <th>Nom ou pseudo</th>
                        <th>Email</th>
                        <th>Code réservation</th>
                    </tr>
                    <tr>
                        <td>Test</td>
                        <td>test@email.com</td>
                        <td>56789</td>
                    </tr>
                    <tr>
                        <td>Test 2</td>
                        <td>other_test@email.com</td>
                        <td>67890</td>
                    </tr>
                </table>
            </body>
        </html>'''
    expected_html_soup = BeautifulSoup(expected_html, 'html.parser')
    venue = create_venue(None, 'Test offerer', 'reservations@test.fr', '123 rue test', '93000', 'Test city', '93')
    stock = create_stock_with_event_offer(offerer=None,
                                          venue=venue,
                                          beginning_datetime_future=True)
    user_1 = create_user('Test', 93, 'test@email.com', True)
    user_2 = create_user('Test', 93, 'test@email.com', True)
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
    recap_email_soup = BeautifulSoup(recap_email['Html-part'], 'html.parser')
    assert recap_email_soup.prettify() == expected_html_soup.prettify()


@mocked_mail
@clean_database
@pytest.mark.standalone
def test_offerer_booking_recap_email_book(app):
    # Given
    expected_html = '''
    <html>
        <body>
            <p id="mail-greeting">Cher partenaire pass Culture,</p>
            <p id="action"><strong>Test</strong> (test@email.com) vient de faire une nouvelle réservation.</p>
            <p id="recap">
            Voici le récapitulatif des réservations à ce jour (total 1) pour Test Book, proposé par Test offerer (Adresse : 123 rue test, 93000 Test city).
            </p>
            <table id="recap-table">
                <tr>
                    <th>Nom ou pseudo</th>
                    <th>Email</th>
                    <th>Code réservation</th>
                </tr> 
                 
                <tr>
                    <td>Test</td>
                    <td>test@email.com</td>
                    <td>56789</td>
                </tr>
                 
            </table>
 
        </body>
    </html>'''
    venue = create_venue(None, 'Test offerer', 'reservations@test.fr', '123 rue test', '93000', 'Test city', '93')
    thing_offer = create_thing_offer(venue=None)
    expected_html_soup = BeautifulSoup(expected_html, 'html.parser')
    stock = create_stock_with_thing_offer(offerer=None, venue=venue, thing_offer=thing_offer)
    user = create_user('Test', 93, 'test@email.com', True)
    booking = create_booking(user, stock, venue, None)
    booking.token = '56789'

    # When
    with patch('utils.mailing.find_all_ongoing_bookings_by_stock', return_value=[booking]):
        recap_email = make_offerer_booking_recap_email_after_user_action(booking)

    # Then
    recap_email_soup = BeautifulSoup(recap_email['Html-part'], 'html.parser')
    assert recap_email_soup.prettify() == expected_html_soup.prettify()


@mocked_mail
@clean_database
@pytest.mark.standalone
def test_write_object_validation_email_should_have_some_specific_information(app):
    # Given
    validation_token = secrets.token_urlsafe(20)
    offerer = create_offerer(siren='732075312', address='122 AVENUE DE FRANCE', city='Paris', postal_code='75013',
                             name='Accenture', validation_token=validation_token)

    user = create_user(public_name='Test', departement_code=75, email='user@accenture.com', can_book_free_offers=False,
                       validation_token=validation_token)

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

    user = create_user(public_name='Test', departement_code=75, email='user@accenture.com', can_book_free_offers=False,
                       validation_token=validation_token)

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

    user = create_user(public_name='Test', departement_code=75, email='user@accenture.com', can_book_free_offers=False,
                       validation_token=validation_token)

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

    user = create_user(public_name='Test', departement_code=75, email='user@accenture.com', can_book_free_offers=False,
                       password='totallysafepsswd', validation_token=validation_token)

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


@clean_database
@pytest.mark.standalone
def test_make_offerer_booking_user_cancellation_email(app):
    # Given
    offerer = create_offerer()
    venue = create_venue(offerer, 'Test offerer', 'reservations@test.fr', '123 rue test', '93000', 'Test city', '93')
    thing_offer = create_thing_offer(venue)
    stock = create_stock_with_thing_offer(offerer, venue, thing_offer, price=0)
    user_1 = create_user('Test1', 93, 'test1@email.com')
    user_2 = create_user('Test2', 93, 'test2@email.com')
    booking_1 = create_booking(user_1, stock, venue)
    booking_2 = create_booking(user_2, stock, venue)
    booking_2.isCancelled = True
    PcObject.check_and_save(booking_1, booking_2)
    expected_html = '''
        <html>
            <body>
                <p id="mail-greeting">Cher partenaire pass Culture,</p>
                <p id="action"><strong>Test2</strong> (test2@email.com) vient d'annuler sa réservation.</p>
                <p id="recap">
                Voici le récapitulatif des réservations à ce jour (total 1) pour Test Book, proposé par Test offerer (Adresse : 123 rue test, 93000 Test city).
                </p>
                <table id="recap-table">
                    <tr>
                        <th>Nom ou pseudo</th>
                        <th>Email</th>
                        <th>Code réservation</th>
                    </tr> 

                    <tr>
                        <td>Test1</td>
                        <td>test1@email.com</td>
                        <td>{token}</td>
                    </tr>

                </table>

            </body>
        </html>'''.format(token=booking_1.token)
    expected_html_soup = BeautifulSoup(expected_html, 'html.parser')

    # When
    with patch('utils.mailing.find_all_ongoing_bookings_by_stock', return_value=[booking_1]):
        recap_email = make_offerer_booking_recap_email_after_user_action(booking_2, is_cancellation=True)

    # Then
    recap_email_soup = BeautifulSoup(recap_email['Html-part'], 'html.parser')
    assert recap_email_soup.prettify() == expected_html_soup.prettify()


@clean_database
@pytest.mark.standalone
@pytest.mark.offerer_driven_cancellation
def test_make_offerer_driven_cancellation_email_for_user_event(app):
    # Given
    user = create_user(public_name='John Doe')
    offerer = create_offerer(name='Test offerer')
    venue = create_venue(offerer)
    offer = create_event_offer(venue, 'Mains, sorts et papiers')
    event_occurrence = create_event_occurrence(offer,
                                               beginning_datetime=datetime(2019, 7, 20, 12, 0, 0, tzinfo=timezone.utc))
    stock = create_stock_from_event_occurrence(event_occurrence, price=20, available=10)
    booking = create_booking(user, stock)

    # When
    with patch('utils.mailing.find_all_ongoing_bookings_by_stock', return_value=[]):
        email = make_offerer_driven_cancellation_email_for_user(booking)

    # Then
    email_html = BeautifulSoup(email['Html-part'], 'html.parser')
    print(email_html.find("div", {"id": "mail-content"}))
    print(type(email_html.find("div", {"id": "mail-content"})))
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
    print(email_html.find("div", {"id": "mail-content"}))
    print(type(email_html.find("div", {"id": "mail-content"})))
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
    html_recap = str(email_html.find("p", {"id": "recap"}))
    html_recap_table = str(email_html.find("table", {"id": "recap-table"}))
    assert 'Vous venez d\'annuler' in html_action
    assert 'John Doe' in html_action
    assert 'john@doe.fr' in html_action
    assert 'pour Le récit de voyage' in html_recap
    assert 'proposé par La petite librairie' in html_recap
    assert '1 rue de la Libération' in html_recap
    assert 'Montreuil' in html_recap
    assert '93100' in html_recap
    assert '<td>James Bond</td>' in html_recap_table
    assert '<td>John Doe</td>' not in html_recap_table
    assert email[
               'Subject'] == 'Confirmation de votre annulation de réservation pour Le récit de voyage, proposé par La petite librairie'
