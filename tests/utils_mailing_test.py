import secrets
from unittest.mock import Mock, MagicMock, patch

import pytest
from bs4 import BeautifulSoup

from tests.conftest import clean_database, mocked_mail
from utils.config import IS_DEV, IS_STAGING, ENV
from utils.mailing import make_user_booking_recap_email, send_booking_confirmation_email_to_user, \
    make_booking_recap_email, make_final_recap_email_for_stock_with_event, write_object_validation_email, \
    maybe_send_offerer_validation_email, MailServiceException, send_booking_recap_emails, send_final_booking_recap_email
from utils.test_utils import create_stock_with_event_offer, create_stock_with_thing_offer, \
    create_user, create_booking, MOCKED_SIREN_ENTREPRISES_API_RETURN, create_user_offerer, \
    create_offerer, create_venue, create_thing_offer


def get_mocked_response_status_200(entity):
    response = MagicMock(status_code=200, text='')
    response.json = MagicMock(return_value=MOCKED_SIREN_ENTREPRISES_API_RETURN)
    return response


SUBJECT_USER_EVENT_BOOKING_CONFIRMATION_EMAIL = \
    'Confirmation de votre réservation pour Mains, sorts et papiers le 20 juillet 2019 à 14:00'

HTML_USER_BOOKING_EVENT_CONFIRMATION_EMAIL = \
'''<html>
    <body>
        <p id="mail-greeting">Cher Test,</p>

        <div id="mail-content">
            Nous vous confirmons votre réservation pour Mains, sorts et papiers le 20 juillet 2019 à 14:00, proposé par Test offerer (Adresse : 123 rue test, 93000 Test city). Votre code de réservation est le 56789.
        </div>

        <p id="mail-salutation">
            Cordialement,
            <br>L\'équipe pass culture
        </p>

    </body>
</html>'''

SUBJECT_USER_THING_BOOKING_CONFIRMATION_EMAIL = \
    'Confirmation de votre commande pour Test Book'

HTML_USER_BOOKING_THING_CONFIRMATION_EMAIL = '<html><body>' + \
                                             '<p id="mail-greeting">Cher Test,</p>' + \
                                             '<div id="mail-content">Nous vous confirmons votre commande pour Test Book (Ref: 12345),' + \
                                             ' proposé par Test offerer.' + \
                                             ' Votre code de réservation est le 56789.</div>' + \
                                             '<p id="mail-salutation">Cordialement,' + \
                                             '<br>L\'équipe pass culture</p>' + \
                                             '</body></html>'

SUBJECT_USER_BOOKING_THING_CANCELLATION_EMAIL = \
    'Annulation de votre commande pour Test Book'

HTML_USER_BOOKING_THING_CANCELLATION_EMAIL = '<html><body>' + \
                                             '<p id="mail-greeting">Cher Test,</p>' + \
                                             '<div id="mail-content">Votre commande pour Test Book (Ref: 12345), ' + \
                                             'proposé par Test offerer ' + \
                                             'a bien été annulée.</div>' + \
                                             '<p id="mail-salutation">Cordialement,' + \
                                             '<br>L\'équipe pass culture</p>' + \
                                             '</body></html>'

SUBJECT_USER_BOOKING_EVENT_CANCELLATION_EMAIL = \
    'Annulation de votre réservation pour Mains, sorts et papiers le 20 juillet 2019 à 14:00'

HTML_USER_BOOKING_EVENT_CANCELLATION_EMAIL = '<html><body>' + \
                                             '<p id="mail-greeting">Cher Test,</p>' + \
                                             '<div id="mail-content">Votre réservation pour Mains, sorts et papiers, ' + \
                                             'proposé par Test offerer ' + \
                                             'le 20 juillet 2019 à 14:00, ' + \
                                             'a bien été annulée.</div>' + \
                                             '<p id="mail-salutation">Cordialement,' + \
                                             '<br>L\'équipe pass culture</p>' + \
                                             '</body></html>'

SUBJECT_OFFERER_BOOKING_CONFIRMATION_EMAIL = \
    '[Reservations] Nouvelle reservation pour Mains, sorts et papiers le 20 juillet 2019 à 14:00'
HTML_OFFERER_BOOKING_CONFIRMATION_EMAIL = \
    '<html><body>' + \
    '<p>Cher partenaire Pass Culture,</p>' + \
    '<p>Test (test@email.com) vient de faire une nouvelle réservation.</p>' + \
    '<p>Voici le récapitulatif des réservations à ce jour (total 1)' + \
    ' pour Mains, sorts et papiers le 20 juillet 2019 à 14:00,' + \
    ' proposé par Test offerer (Adresse : 123 rue test, 93000 Test city).</p>' + \
    '<table><tr><th>Nom ou pseudo</th><th>Email</th><th>Code réservation</th></tr>' + \
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
def test_send_booking_confirmation_email_to_user_should_call_mailjet_send_create(app):
    # Given
    venue = create_venue(None, 'Test offerer', 'reservations@test.fr', '123 rue test', '93000', 'Test city', '93')
    stock = create_stock_with_event_offer(offerer=None,
                                          venue=venue)
    user = create_user('Test', 93, 'test@email.com', True)
    booking = create_booking(user, stock, venue, None)
    booking.token = '56789'
    mail_html = HTML_USER_BOOKING_EVENT_CONFIRMATION_EMAIL

    if IS_DEV or IS_STAGING:
        beginning_email = \
            '<p>This is a test (ENV={}). In production, email would have been sent to : test@email.com</p>'.format(ENV)
        recipients = 'passculture-dev@beta.gouv.fr'
        mail_html = beginning_email + mail_html
    else:
        recipients = 'test@email.com'

    expected_email = {
        "FromName": 'Pass Culture',
        'FromEmail': 'passculture-dev@beta.gouv.fr',
        'To': recipients,
        'Subject': SUBJECT_USER_EVENT_BOOKING_CONFIRMATION_EMAIL,
        'Html-part': mail_html
    }

    app.mailjet_client.send.create.return_value = Mock(status_code=200)

    # When
    send_booking_confirmation_email_to_user(booking)

    # Then
    app.mailjet_client.send.create.assert_called_once_with(data=expected_email)


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
    recap_email = make_booking_recap_email(stock, booking)

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
    recap_email = make_booking_recap_email(stock, booking)

    # Then
    assert recap_email['Subject'] == SUBJECT_OFFERER_BOOKING_CONFIRMATION_EMAIL


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
                <p>Cher partenaire Pass Culture,</p>
                <p>
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
                <p>Cher partenaire Pass Culture,</p>
                <p>
                    Voici le récapitulatif final des réservations (total 1) pour Mains, sorts et papiers le 20 juillet 2017 à 14:00, proposé par Test offerer (Adresse : 123 rue test, 93000 Test city).
                </p>
                <table>
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
    offer = create_stock_with_event_offer(offerer=None,
                                          venue=venue,
                                          beginning_datetime_future=False)
    user = create_user('Test', 93, 'test@email.com', True)
    booking = create_booking(user, offer, venue, None)
    booking.token = '56789'
    offer.bookings = [booking]

    # When
    recap_email = make_final_recap_email_for_stock_with_event(offer)

    # Then
    recap_email_soup = BeautifulSoup(recap_email['Html-part'], 'html.parser')
    assert recap_email_soup.prettify() == expected_html_soup.prettify()


@mocked_mail
@clean_database
@pytest.mark.standalone
def test_offerer_recap_email_future_offer_when_new_booking_with_old_booking(app):
    # Given
    expected_html = '''
        <html>
            <body>
                <p>Cher partenaire Pass Culture,</p>
                <p>Test 2 (other_test@email.com) vient de faire une nouvelle réservation.</p>
                <p>
                    Voici le récapitulatif des réservations à ce jour (total 2) pour Mains, sorts et papiers le 20 juillet 2019 à 14:00, proposé par Test offerer (Adresse : 123 rue test, 93000 Test city).
                </p>
                <table>
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
    stock.bookings = [booking_1, booking_2]

    # When
    recap_email = make_booking_recap_email(stock, booking_2)

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
            <p>Cher partenaire Pass Culture,</p>
            <p>Test (test@email.com) vient de faire une nouvelle réservation.</p>
            <p>
            Voici le récapitulatif des réservations à ce jour (total 1) pour Test Book, proposé par Test offerer (Adresse : 123 rue test, 93000 Test city).
            </p>
            <table>
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
    recap_email = make_booking_recap_email(stock, booking)

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
def test_maybe_send_offerer_validation_email_does_not_send_email_if_all_validated(app):
    # Given
    offerer = create_offerer(siren='732075312', address='122 AVENUE DE FRANCE', city='Paris', postal_code='75013',
                             name='Accenture', validation_token=None)

    user = create_user(public_name='Test', departement_code=75, email='user@accenture.com', can_book_free_offers=False,
                       validation_token=None)

    user_offerer = create_user_offerer(user, offerer, validation_token=None)

    # When
    maybe_send_offerer_validation_email(offerer, user_offerer)

    # Then
    assert not app.mailjet_client.send.create.called


@mocked_mail
@clean_database
@pytest.mark.standalone
def test_maybe_send_offerer_validation_email_raises_exception_if_status_code_400(app):
    # Given
    validation_token = secrets.token_urlsafe(20)
    offerer = create_offerer(siren='732075312', address='122 AVENUE DE FRANCE', city='Paris', postal_code='75013',
                             name='Accenture', validation_token=validation_token)

    user = create_user(public_name='Test', departement_code=75, email='user@accenture.com', can_book_free_offers=False,
                       validation_token=validation_token)

    user_offerer = create_user_offerer(user, offerer, validation_token)

    app.mailjet_client.send.create.return_value = Mock(status_code=400)

    # When
    with pytest.raises(MailServiceException):
        maybe_send_offerer_validation_email(offerer, user_offerer)


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


@mocked_mail
@clean_database
@pytest.mark.standalone
def test_send_booking_recap_emails_does_not_send_email_to_offer_booking_email_if_feature_is_disabled(app):
    # given
    user = create_user()
    booking = create_booking(user)
    offerer = create_offerer()
    venue = create_venue(offerer)
    offer = create_thing_offer(venue, booking_email='offer.booking.email@test.com')
    stock = create_stock_with_thing_offer(offerer, venue, offer)
    app.mailjet_client.send.create.return_value = Mock(status_code=200)

    with patch('utils.mailing.feature_send_mail_to_users_enabled') as send_mail_to_users:
        send_mail_to_users.return_value = False
        # when
        send_booking_recap_emails(stock, booking)

    # then
    app.mailjet_client.send.create.assert_called_once()
    args = app.mailjet_client.send.create.call_args
    assert args[1]['data']['To'] == 'passculture-dev@beta.gouv.fr'


@pytest.mark.standalone
@mocked_mail
@clean_database
def test_send_booking_recap_emails_sends_email_to_offer_booking_email_if_feature_is_enabled(app):
    # given
    user = create_user()
    booking = create_booking(user)
    offerer = create_offerer()
    venue = create_venue(offerer)
    offer = create_thing_offer(venue, booking_email='offer.booking.email@test.com')
    stock = create_stock_with_thing_offer(offerer, venue, offer)
    app.mailjet_client.send.create.return_value = Mock(status_code=200)

    with patch('utils.mailing.feature_send_mail_to_users_enabled') as send_mail_to_users:
        send_mail_to_users.return_value = True
        # when
        send_booking_recap_emails(stock, booking)

    # then
    app.mailjet_client.send.create.assert_called_once()
    args = app.mailjet_client.send.create.call_args
    assert 'offer.booking.email@test.com' in args[1]['data']['To']
    assert 'passculture@beta.gouv.fr' in args[1]['data']['To']


@mocked_mail
@clean_database
@pytest.mark.standalone
def test_send_final_booking_recap_email_does_not_send_email_to_offer_booking_email_if_feature_is_disabled(app):
    # given
    offerer = create_offerer()
    venue = create_venue(offerer)
    stock = create_stock_with_event_offer(offerer, venue, booking_email='offer.booking.email@test.com')
    app.mailjet_client.send.create.return_value = Mock(status_code=200)

    with patch('utils.mailing.feature_send_mail_to_users_enabled') as send_mail_to_users:
        send_mail_to_users.return_value = False
        # when
        send_final_booking_recap_email(stock)

    # then
    app.mailjet_client.send.create.assert_called_once()
    args = app.mailjet_client.send.create.call_args
    assert args[1]['data']['To'] == 'passculture-dev@beta.gouv.fr'


@mocked_mail
@clean_database
@pytest.mark.standalone
def test_send_final_booking_recap_email_sends_email_to_offer_booking_email_if_feature_is_enabled(app):
    # given
    offerer = create_offerer()
    venue = create_venue(offerer)
    stock = create_stock_with_event_offer(offerer, venue, booking_email = 'offer.booking.email@test.com')
    app.mailjet_client.send.create.return_value = Mock(status_code=200)

    with patch('utils.mailing.feature_send_mail_to_users_enabled') as send_mail_to_users:
        send_mail_to_users.return_value = True
        # when
        send_final_booking_recap_email(stock)

    # then
    app.mailjet_client.send.create.assert_called_once()
    args = app.mailjet_client.send.create.call_args
    assert 'offer.booking.email@test.com' in args[1]['data']['To']
    assert 'passculture@beta.gouv.fr' in args[1]['data']['To']
