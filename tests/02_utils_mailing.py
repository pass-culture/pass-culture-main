from unittest.mock import Mock

from utils.config import IS_DEV, IS_STAGING, ENV
from utils.mailing import make_user_booking_recap_email, send_booking_confirmation_email_to_user, \
    make_booking_recap_email

from utils.test_utils import create_stock_with_event_occasion, create_stock_with_thing_occasion, \
    create_user_for_booking_email_test, create_booking_for_booking_email_test

SUBJECT_USER_EVENT_BOOKING_CONFIRMATION_EMAIL = \
    'Confirmation de votre réservation pour Mains, sorts et papiers le 20 juillet 2019 à 14:00'


HTML_USER_BOOKING_EVENT_CONFIRMATION_EMAIL = '<html><body>' + \
           '<p>Cher Test,</p>' + \
           '<p>Nous vous confirmons votre réservation pour Mains, sorts et papiers le 20 juillet 2019 à 14:00,' + \
           ' proposé par Test offerer (Adresse : 123 rue test, 93000 Test city).</p>' + \
           '<p>Votre code de réservation est le 56789.</p>' + \
           '<p>Cordialement,</p>' + \
           '<p>L\'équipe pass culture</p>' + \
           '</body></html>'

SUBJECT_USER_THING_BOOKING_CONFIRMATION_EMAIL = \
    'Confirmation de votre commande pour Test Book'

HTML_USER_BOOKING_THING_CONFIRMATION_EMAIL = '<html><body>' + \
           '<p>Cher Test,</p>' + \
           '<p>Nous vous confirmons votre commande pour Test Book (Ref: 12345),' + \
           ' proposé par Test offerer.</p>' + \
           '<p>Votre code de réservation est le 56789.</p>' + \
           '<p>Cordialement,</p>' + \
           '<p>L\'équipe pass culture</p>' + \
           '</body></html>'

SUBJECT_USER_BOOKING_THING_CANCELLATION_EMAIL = \
    'Annulation de votre commande pour Test Book'

HTML_USER_BOOKING_THING_CANCELLATION_EMAIL = '<html><body>' + \
           '<p>Cher Test,</p>' + \
           '<p>Votre commande pour Test Book (Ref: 12345), ' + \
           'proposé par Test offerer ' + \
           'a bien été annulée.</p>' + \
           '<p>Cordialement,</p>' + \
           '<p>L\'équipe pass culture</p>' + \
           '</body></html>'

SUBJECT_USER_BOOKING_EVENT_CANCELLATION_EMAIL = \
    'Annulation de votre réservation pour Mains, sorts et papiers le 20 juillet 2019 à 14:00'

HTML_USER_BOOKING_EVENT_CANCELLATION_EMAIL = '<html><body>' + \
           '<p>Cher Test,</p>' + \
           '<p>Votre réservation pour Mains, sorts et papiers, ' + \
           'proposé par Test offerer ' + \
           'le 20 juillet 2019 à 14:00, ' + \
           'a bien été annulée.</p>' + \
           '<p>Cordialement,</p>' + \
           '<p>L\'équipe pass culture</p>' + \
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


def test_01_make_user_booking_event_recap_email_should_have_standard_subject():
    # Given
    stock = create_stock_with_event_occasion()
    user = create_user_for_booking_email_test()
    booking = create_booking_for_booking_email_test(user, stock)

    # When
    recap_email = make_user_booking_recap_email(booking, is_cancellation=False)
    # Then
    assert recap_email['Subject'] == SUBJECT_USER_EVENT_BOOKING_CONFIRMATION_EMAIL


def test_02_make_user_booking_event_recap_email_should_have_standard_body():
    # Given
    stock = create_stock_with_event_occasion()
    user = create_user_for_booking_email_test()
    booking = create_booking_for_booking_email_test(user, stock)

    # When
    recap_email = make_user_booking_recap_email(booking, is_cancellation=False)
    # Then
    assert recap_email['Html-part'] == HTML_USER_BOOKING_EVENT_CONFIRMATION_EMAIL


def test_03_make_user_booking_event_recap_email_should_have_standard_subject_cancellation():
    # Given
    stock = create_stock_with_event_occasion()
    user = create_user_for_booking_email_test()
    booking = create_booking_for_booking_email_test(user, stock)

    # When
    recap_email = make_user_booking_recap_email(booking, is_cancellation=True)
    # Then
    assert recap_email['Subject'] == SUBJECT_USER_BOOKING_EVENT_CANCELLATION_EMAIL


def test_04_make_user_booking_event_recap_email_should_have_standard_body_cancellation():
    # Given
    stock = create_stock_with_event_occasion()
    user = create_user_for_booking_email_test()
    booking = create_booking_for_booking_email_test(user, stock)

    # When
    recap_email = make_user_booking_recap_email(booking, is_cancellation=True)
    # Then
    assert recap_email['Html-part'] == HTML_USER_BOOKING_EVENT_CANCELLATION_EMAIL


def test_05_send_booking_confirmation_email_to_user_should_call_mailjet_send_create(app):
    # Given
    stock = create_stock_with_event_occasion()
    user = create_user_for_booking_email_test()
    booking = create_booking_for_booking_email_test(user, stock)
    mail_html = HTML_USER_BOOKING_EVENT_CONFIRMATION_EMAIL

    if IS_DEV or IS_STAGING:
        beginning_email = '<p>This is a test (ENV={}). In production, email would have been sent to : '.format(ENV) \
                + 'test@email.com</p>'
        recipients = 'passculture-dev@beta.gouv.fr'
        mail_html = beginning_email + mail_html
    else:
        recipients = 'test@email.com'

    expected_email = {
      "FromName": 'Pass Culture',
      'FromEmail': 'passculture@beta.gouv.fr',
      'To': recipients,
      'Subject': SUBJECT_USER_EVENT_BOOKING_CONFIRMATION_EMAIL,
      'Html-part': mail_html
    }

    app.mailjet_client.send.create.return_value = Mock(status_code=200)

    # When
    send_booking_confirmation_email_to_user(booking)

    # Then
    app.mailjet_client.send.create.assert_called_once_with(data=expected_email)


def test_06_booking_recap_email_html_should_have_place_and_structure():
    # Given
    stock = create_stock_with_event_occasion()

    user = create_user_for_booking_email_test()

    booking = create_booking_for_booking_email_test(user, stock)

    # When
    recap_email = make_booking_recap_email(stock, booking)

    # Then
    assert recap_email['Html-part'] == HTML_OFFERER_BOOKING_CONFIRMATION_EMAIL


def test_07_booking_recap_email_subject_should_have_defined_structure():
    # Given
    stock = create_stock_with_event_occasion()
    user = create_user_for_booking_email_test()
    booking = create_booking_for_booking_email_test(user, stock)

    # When
    recap_email = make_booking_recap_email(stock, booking)

    # Then
    assert recap_email['Subject'] == SUBJECT_OFFERER_BOOKING_CONFIRMATION_EMAIL


def test_08_maker_user_booking_thing_recap_email_should_have_standard_body():
    stock = create_stock_with_thing_occasion()
    stock.occasion.thing.idAtProviders = '12345'
    user = create_user_for_booking_email_test()
    booking = create_booking_for_booking_email_test(user, stock)

    # When
    recap_email = make_user_booking_recap_email(booking, is_cancellation=False)
    # Then
    assert recap_email['Html-part'] == HTML_USER_BOOKING_THING_CONFIRMATION_EMAIL


def test_09_maker_user_booking_thing_recap_email_should_have_standard_subject():
    stock = create_stock_with_thing_occasion()
    stock.occasion.thing.idAtProviders = '12345'
    user = create_user_for_booking_email_test()
    booking = create_booking_for_booking_email_test(user, stock)

    # When
    recap_email = make_user_booking_recap_email(booking, is_cancellation=False)
    # Then
    assert recap_email['Subject'] == SUBJECT_USER_THING_BOOKING_CONFIRMATION_EMAIL


def test_10_make_user_booking_thing_recap_email_should_have_standard_subject_cancellation():
    # Given
    stock = create_stock_with_thing_occasion()
    stock.occasion.thing.idAtProviders = '12345'
    user = create_user_for_booking_email_test()
    booking = create_booking_for_booking_email_test(user, stock)

    # When
    recap_email = make_user_booking_recap_email(booking, is_cancellation=True)
    # Then
    assert recap_email['Subject'] == SUBJECT_USER_BOOKING_THING_CANCELLATION_EMAIL


def test_11_make_user_booking_thing_recap_email_should_have_standard_body_cancellation():
    # Given
    stock = create_stock_with_thing_occasion()
    stock.occasion.thing.idAtProviders = '12345'
    user = create_user_for_booking_email_test()
    booking = create_booking_for_booking_email_test(user, stock)

    # When
    recap_email = make_user_booking_recap_email(booking, is_cancellation=True)
    # Then
    assert recap_email['Html-part'] == HTML_USER_BOOKING_THING_CANCELLATION_EMAIL