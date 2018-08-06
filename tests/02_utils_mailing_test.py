import secrets
from unittest.mock import Mock, patch

import pytest
from bs4 import BeautifulSoup

from models import Offerer, UserOfferer, User
from utils.config import IS_DEV, IS_STAGING, ENV
from utils.mailing import make_user_booking_recap_email, send_booking_confirmation_email_to_user, \
    make_booking_recap_email, make_final_recap_email_for_stock_with_event, write_object_validation_email, \
    maybe_send_offerer_validation_email

from utils.test_utils import create_stock_with_event_offer, create_stock_with_thing_offer, \
    create_user_for_booking_email_test, create_booking_for_booking_email_test, MOCKED_SIREN_ENTREPRISES_API_RETURN, \
    get_mocked_response_status_200, get_mocked_response_status_400

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

SUBJECT_OFFERER_BOOKING_CONFIRMATION_EMAIL =\
    '[Reservations] Nouvelle reservation pour Mains, sorts et papiers le 20 juillet 2019 à 14:00'
HTML_OFFERER_BOOKING_CONFIRMATION_EMAIL = \
    '<html><body>' + \
    '<p>Cher partenaire Pass Culture,</p>' + \
    '<p>Test (test@email.com) vient de faire une nouvelle réservation.</p>' + \
    '<p>Voici le récapitulatif des réservations à ce jour (total 1)' + \
    ' pour Mains, sorts et papiers le 20 juillet 2019 à 14:00,' + \
    ' proposé par Test offerer (Adresse : 123 rue test, 93000 Test city).</p>' + \
    '<table><tr><th>Nom ou pseudo</th><th>Email</th><th>Code réservation</th></tr>' +\
    '<tr><td>Test</td><td>test@email.com</td><td>56789</td></tr></table>' +\
    '</body></html>'


def test_01_make_user_booking_event_recap_email_should_have_standard_subject(app):
    # Given
    stock = create_stock_with_event_offer()
    user = create_user_for_booking_email_test()
    booking = create_booking_for_booking_email_test(user, stock)

    # When
    recap_email = make_user_booking_recap_email(booking, is_cancellation=False)
    # Then
    assert recap_email['Subject'] == SUBJECT_USER_EVENT_BOOKING_CONFIRMATION_EMAIL


def test_02_make_user_booking_event_recap_email_should_have_standard_body(app):
    # Given
    stock = create_stock_with_event_offer()
    user = create_user_for_booking_email_test()
    booking = create_booking_for_booking_email_test(user, stock)
    expected_email_soup = BeautifulSoup(HTML_USER_BOOKING_EVENT_CONFIRMATION_EMAIL, 'html.parser')

    # When
    recap_email = make_user_booking_recap_email(booking, is_cancellation=False)
    recap_email_soup = BeautifulSoup(recap_email['Html-part'], 'html.parser')

    # Then
    assert recap_email_soup.prettify() == expected_email_soup.prettify()


def test_03_make_user_booking_event_recap_email_should_have_standard_subject_cancellation(app):
    # Given
    stock = create_stock_with_event_offer()
    user = create_user_for_booking_email_test()
    booking = create_booking_for_booking_email_test(user, stock)

    # When
    recap_email = make_user_booking_recap_email(booking, is_cancellation=True)
    # Then
    assert recap_email['Subject'] == SUBJECT_USER_BOOKING_EVENT_CANCELLATION_EMAIL


def test_04_make_user_booking_event_recap_email_should_have_standard_body_cancellation(app):
    # Given
    stock = create_stock_with_event_offer()
    user = create_user_for_booking_email_test()
    booking = create_booking_for_booking_email_test(user, stock)
    expected_email_soup = BeautifulSoup(HTML_USER_BOOKING_EVENT_CANCELLATION_EMAIL, 'html.parser')


    # When
    recap_email = make_user_booking_recap_email(booking, is_cancellation=True)
    recap_email_soup = BeautifulSoup(recap_email['Html-part'], 'html.parser')

    # Then
    print(user.publicName)
    assert recap_email_soup.prettify() == expected_email_soup.prettify()


def test_05_send_booking_confirmation_email_to_user_should_call_mailjet_send_create(app):
    # Given
    stock = create_stock_with_event_offer()
    user = create_user_for_booking_email_test()
    booking = create_booking_for_booking_email_test(user, stock)
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


def test_06_maker_user_booking_thing_recap_email_should_have_standard_body(app):
    stock = create_stock_with_thing_offer()
    stock.offer.thing.idAtProviders = '12345'
    user = create_user_for_booking_email_test()
    booking = create_booking_for_booking_email_test(user, stock)
    expected_email_soup = BeautifulSoup(HTML_USER_BOOKING_THING_CONFIRMATION_EMAIL, 'html.parser')

    # When
    recap_email = make_user_booking_recap_email(booking, is_cancellation=False)
    recap_email_soup = BeautifulSoup(recap_email['Html-part'], 'html.parser')

    # Then
    assert recap_email_soup.prettify() == expected_email_soup.prettify()


def test_07_maker_user_booking_thing_recap_email_should_have_standard_subject(app):
    stock = create_stock_with_thing_offer()
    stock.offer.thing.idAtProviders = '12345'
    user = create_user_for_booking_email_test()
    booking = create_booking_for_booking_email_test(user, stock)

    # When
    recap_email = make_user_booking_recap_email(booking, is_cancellation=False)
    # Then
    assert recap_email['Subject'] == SUBJECT_USER_THING_BOOKING_CONFIRMATION_EMAIL


def test_8_make_user_booking_thing_recap_email_should_have_standard_subject_cancellation(app):
    # Given
    stock = create_stock_with_thing_offer()
    stock.offer.thing.idAtProviders = '12345'
    user = create_user_for_booking_email_test()
    booking = create_booking_for_booking_email_test(user, stock)

    # When
    recap_email = make_user_booking_recap_email(booking, is_cancellation=True)
    # Then
    assert recap_email['Subject'] == SUBJECT_USER_BOOKING_THING_CANCELLATION_EMAIL


def test_9_make_user_booking_thing_recap_email_should_have_standard_body_cancellation(app):
    # Given
    stock = create_stock_with_thing_offer()
    stock.offer.thing.idAtProviders = '12345'
    user = create_user_for_booking_email_test()
    booking = create_booking_for_booking_email_test(user, stock)
    expected_email_soup = BeautifulSoup(HTML_USER_BOOKING_THING_CANCELLATION_EMAIL, 'html.parser')

    # When
    recap_email = make_user_booking_recap_email(booking, is_cancellation=True)
    recap_email_soup = BeautifulSoup(recap_email['Html-part'], 'html.parser')

    # Then
    assert recap_email_soup.prettify() == expected_email_soup.prettify()


def test_10_booking_recap_email_html_should_have_place_and_structure(app):
    # Given
    stock = create_stock_with_event_offer()
    user = create_user_for_booking_email_test()
    booking = create_booking_for_booking_email_test(user, stock)
    expected_email_soup = BeautifulSoup(HTML_OFFERER_BOOKING_CONFIRMATION_EMAIL, 'html.parser')

    # When
    recap_email = make_booking_recap_email(stock, booking)
    recap_email_soup = BeautifulSoup(recap_email['Html-part'], 'html.parser')

    print(recap_email_soup.prettify())
    # Then
    assert recap_email_soup.prettify() == expected_email_soup.prettify()


def test_11_booking_recap_email_subject_should_have_defined_structure(app):
    # Given
    stock = create_stock_with_event_offer()
    user = create_user_for_booking_email_test()
    booking = create_booking_for_booking_email_test(user, stock)

    # When
    recap_email = make_booking_recap_email(stock, booking)

    # Then
    assert recap_email['Subject'] == SUBJECT_OFFERER_BOOKING_CONFIRMATION_EMAIL


def test_12_offerer_recap_email_subject_past_offer_without_booking(app):
    # Given
    expected_subject = '[Reservations] Récapitulatif pour Mains, sorts et papiers le 20 juillet 2017 à 14:00'
    stock = create_stock_with_event_offer(beginning_datetime_future=False)

    #When
    recap_email = make_final_recap_email_for_stock_with_event(stock)

    assert recap_email['Subject'] == expected_subject


def test_13_offerer_recap_email_past_offer_without_booking(app):
    #Given
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
    stock = create_stock_with_event_offer(beginning_datetime_future=False)

    #When
    recap_email = make_final_recap_email_for_stock_with_event(stock)
    recap_email_soup = BeautifulSoup(recap_email['Html-part'], 'html.parser')

    #Then
    assert expected_html_soup.prettify() == recap_email_soup.prettify()


def test_14_offerer_recap_email_past_offer_with_booking(app):
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
    offer = create_stock_with_event_offer(beginning_datetime_future=False)
    user = create_user_for_booking_email_test()
    booking = create_booking_for_booking_email_test(user, offer)
    offer.bookings = [booking]

    # When
    recap_email = make_final_recap_email_for_stock_with_event(offer)
    recap_email_soup = BeautifulSoup(recap_email['Html-part'], 'html.parser')

    # Then
    assert recap_email_soup.prettify() == expected_html_soup.prettify()


def test_15_offerer_recap_email_future_offer_when_new_booking_with_old_booking(app):
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
                        <td>56789</td>
                    </tr>
                </table>
            </body>
        </html>'''
    expected_html_soup = BeautifulSoup(expected_html, 'html.parser')
    stock = create_stock_with_event_offer(beginning_datetime_future=True)
    user_1 = create_user_for_booking_email_test()
    user_2 = create_user_for_booking_email_test()
    user_2.publicName = 'Test 2'
    user_2.email = 'other_test@email.com'
    booking_1 = create_booking_for_booking_email_test(user_1, stock)
    booking_2 = create_booking_for_booking_email_test(user_2, stock)
    stock.bookings = [booking_1, booking_2]

    # When
    recap_email = make_booking_recap_email(stock, booking_2)
    recap_email_soup = BeautifulSoup(recap_email['Html-part'], 'html.parser')

    # Then
    print(recap_email_soup.prettify() )
    assert recap_email_soup.prettify() == expected_html_soup.prettify()


def test_17_offerer_booking_recap_email_book(app):
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
    expected_html_soup = BeautifulSoup(expected_html, 'html.parser')
    stock = create_stock_with_thing_offer()
    user = create_user_for_booking_email_test()
    booking = create_booking_for_booking_email_test(user, stock)

    # When
    recap_email = make_booking_recap_email(stock, booking)
    recap_email_soup = BeautifulSoup(recap_email['Html-part'], 'html.parser')

    # Then
    print(recap_email_soup.prettify())
    assert recap_email_soup.prettify() == expected_html_soup.prettify()


@patch('requests.get', return_value=get_mocked_response_status_200())
def test_18_validation_email(mock, app):
    # Given
    validation_token = secrets.token_urlsafe(20)
    offerer_data= {'validationToken': validation_token,
                   'siren': '732075312',
                   'address': '122 AVENUE DE FRANCE',
                   'city': 'Paris',
                   'postalCode': '75013',
                   'name' : 'Accenture',
                   }
    offerer = Offerer(from_dict=offerer_data)

    user_data = {
        'canBookFreeOffers': False,
        'departementCode': '75000',
        'email': 'user@accenture.com',
        'validationToken': validation_token
    }
    user = User(from_dict=user_data)
    user.setPassword('totallysafepsswd')

    user_offerer = UserOfferer()
    user_offerer.user = user
    user_offerer.offerer = offerer
    user_offerer.validationToken = validation_token

    # When
    email = write_object_validation_email(offerer, user_offerer)
    email_html_soup = BeautifulSoup(email['Html-part'], features="html.parser")
    all_paragraphs = email_html_soup.find_all('p')
    all_h3_user_offerer = email_html_soup.find_all('h3', "user_offerer")
    all_pre_user_offerer = email_html_soup.find_all('pre', "user_offerer")
    all_h4_user_offerer = email_html_soup.find_all('h4', "user_offerer")
    all_a = email_html_soup.find_all('a')
    all_h3_offerer = email_html_soup.find_all('h3', "offerer")
    all_pre_offerer = email_html_soup.find_all('pre', "offerer")
    all_h4_offerer = email_html_soup.find_all('h4', "offerer")


    # Then
    assert str(all_paragraphs[0]) == '<p>Inscription ou rattachement PRO à valider</p>'
    assert str(all_h3_offerer[0]) == '<h3 class="offerer">Nouvelle Structure : </h3>'
    assert str(all_h3_user_offerer[0]) == '<h3 class="user_offerer">Nouveau Rattachement : </h3>'
    assert str(all_h4_user_offerer[0]) == '<h4 class="user_offerer">Utilisateur: </h4>'
    assert 'UserOfferers' in str(all_pre_user_offerer[0])
    assert "'address': '122 AVENUE DE FRANCE'" in str(all_pre_offerer[0])
    assert "'city': 'Paris'" in str(all_pre_offerer[0])
    assert "'name': 'Accenture'" in str(all_pre_offerer[0])
    assert "'postalCode': '75013'" in str(all_pre_offerer[0])
    assert "'siren': '732075312'" in str(all_pre_offerer[0])
    assert "'validationToken': '{}'".format(validation_token) in str(all_pre_offerer[0])
    assert str(all_h4_offerer[0]) == '<h4 class="offerer">Infos API entreprise : </h4>'
    assert "'numero_tva_intra': 'FR60732075312'" in str(all_pre_offerer[1])
    assert '<a href="localhost/validate?modelNames=Offerer,UserOfferer&amp;token={}">cliquez ici</a>'.format(
        validation_token) in str(all_a[0])
    assert "'other_etablissements_sirets': ['73207531200213', '73207531200197', '73207531200171']".replace(
        ' ', '').replace('\n', '') in str(all_pre_offerer[1]).replace(' ', '').replace('\n', '')
    assert 'siege_social' in str(all_pre_offerer[1])


@patch('requests.get', return_value=get_mocked_response_status_400())
def test_19_validation_email_raises_value_error_when_api_does_not_respond(mock, app):
    # Given
    validation_token = secrets.token_urlsafe(20)
    offerer_data = {'validationToken': validation_token,
                    'siren': '732075312',
                    'address': '122 AVENUE DE FRANCE',
                    'offerer.city': 'Paris',
                    'offerer.postalCode': '75013',
                    'offerer.name': 'Accenture'}
    offerer = Offerer(from_dict=offerer_data)

    user_data = {
        'canBookFreeOffers': False,
        'departementCode': '75000',
        'email': 'user@accenture.com',
        'validationToken': validation_token
    }
    user = User(from_dict=user_data)
    user.setPassword('totallysafepsswd')

    user_offerer = UserOfferer()
    user_offerer.user = user
    user_offerer.offerer = offerer
    user_offerer.validationToken = validation_token

    #When
    with pytest.raises(ValueError) as error:
        write_object_validation_email(offerer, user_offerer)
        #Then
        assert 'Error getting API entreprise DATA for SIREN' in str(error.value)


def test_20_validation_email_raises_value_error_when_object_to_validate_not_offerer_or_userOfferer(app):
    # Given
    validation_token = secrets.token_urlsafe(20)
    user_data = {
        'canBookFreeOffers': False,
        'departementCode': '75000',
        'email': 'user@accenture.com',
        'validationToken': validation_token
    }
    user = User(from_dict=user_data)
    user.setPassword('totallysafepsswd')

    with pytest.raises(ValueError) as error:
        write_object_validation_email(user)
        assert 'Unexpected object type in maybe_send_pro_validation_email :' in str(error.value)


def test_21_maybe_send_offerer_validation_email_does_not_send_email_if_all_validated(app):
    # Given
    offerer_data= {
                   'siren': '732075312',
                   'address': '122 AVENUE DE FRANCE',
                   'city': 'Paris',
                   'postalCode': '75013',
                   'name' : 'Accenture',
                   }
    offerer = Offerer(from_dict=offerer_data)

    user_data = {
        'canBookFreeOffers': False,
        'departementCode': '75000',
        'email': 'user@accenture.com',
    }
    user = User(from_dict=user_data)
    user.setPassword('totallysafepsswd')

    user_offerer = UserOfferer()
    user_offerer.user = user
    user_offerer.offerer = offerer

    #When
    maybe_send_offerer_validation_email(offerer, user_offerer)

    #Then
    assert not app.mailjet_client.send.create.called


def test_22_maybe_send_offerer_validation_email_raises_exception_if_status_code_400(app):
    # Given
    validation_token = secrets.token_urlsafe(20)
    offerer_data = {'validationToken': validation_token,
                    'siren': '732075312',
                    'address': '122 AVENUE DE FRANCE',
                    'offerer.city': 'Paris',
                    'offerer.postalCode': '75013',
                    'offerer.name': 'Accenture'}
    offerer = Offerer(from_dict=offerer_data)

    user_data = {
        'canBookFreeOffers': False,
        'departementCode': '75000',
        'email': 'user@accenture.com',
        'validationToken': validation_token
    }
    user = User(from_dict=user_data)
    user.setPassword('totallysafepsswd')

    user_offerer = UserOfferer()
    user_offerer.user = user
    user_offerer.offerer = offerer
    user_offerer.validationToken = validation_token

    app.mailjet_client.send.create.return_value = Mock(status_code=400)

    #When
    with pytest.raises(Exception):
        maybe_send_offerer_validation_email(offerer, user_offerer)

@patch('requests.get', return_value=get_mocked_response_status_200())
def test_23_validation_email_should_not_return_clearTextPassword(mock, app):
    # Given
    validation_token = secrets.token_urlsafe(20)
    offerer_data= {'validationToken': validation_token,
                   'siren': '732075312',
                   'address': '122 AVENUE DE FRANCE',
                   'city': 'Paris',
                   'postalCode': '75013',
                   'name' : 'Accenture',
                   }
    offerer = Offerer(from_dict=offerer_data)

    user_data = {
        'canBookFreeOffers': False,
        'departementCode': '75000',
        'email': 'user@accenture.com',
        'validationToken': validation_token
    }
    user = User(from_dict=user_data)
    user.setPassword('totallysafepsswd')

    user_offerer = UserOfferer()
    user_offerer.user = user
    user_offerer.offerer = offerer
    user_offerer.validationToken = validation_token

    # When
    email = write_object_validation_email(offerer, user_offerer)
    email_html_soup = BeautifulSoup(email['Html-part'], features="html.parser")

    # Then
    assert 'clearTextPassword' not in str(email_html_soup)
    assert 'totallysafepsswd' not in str(email_html_soup)


# def test_16_offerer_recap_email_future_offer_when_cancellation_with_one_booking(app):
#     # Given
#     expected_html = '''
#         <html>
#             <body>
#                 <p>Cher partenaire Pass Culture,</p
#                 <p>Test (test@email.com) vient d'annuler sa réservation</p>
#                 <p>Voici le récapitulatif final des réservations (total 2) pour Mains, sorts et papiers le 1 août 2018 à 10:58, proposé par Test offerer (Adresse : 123 rue test, 93000 Test city).
#                 </p>
#                 <p>Aucune réservation</p>
#             </body>
#         </html>'''
#     expected_html_soup = BeautifulSoup(expected_html, 'html.parser')
#     stock = create_stock_with_event_offer(beginning_datetime_future=True)
#     user = create_user_for_booking_email_test()
#     booking = create_booking_for_booking_email_test(user, stock, is_cancellation=True)
#
#     # When
#     recap_email = make_booking_recap_email(stock, booking, is_cancellation=True)
#     recap_email_soup = BeautifulSoup(recap_email['Html-part'], 'html.parser')
#
#     # Then
#     assert recap_email_soup.prettify() == expected_html_soup.prettify()