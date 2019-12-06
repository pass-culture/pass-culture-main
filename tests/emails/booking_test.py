from datetime import datetime, timedelta

from bs4 import BeautifulSoup

from tests.conftest import mocked_mail, clean_database
from tests.test_utils import create_offerer, create_venue, create_stock_with_event_offer, create_user, create_booking, \
    create_offer_with_thing_product, create_stock_with_thing_offer
from tests.utils.mailing_test import _remove_whitespaces
from utils.mailing import make_user_booking_confirmation_recap_email


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
    recap_email = make_user_booking_confirmation_recap_email(booking)

    # Then
    email_html = _remove_whitespaces(recap_email['Html-part'])
    recap_email_soup = BeautifulSoup(email_html, 'html.parser')
    mail_content = recap_email_soup.find("div", {"id": 'mail-content'}).text
    mail_greeting = recap_email_soup.find("p", {"id": 'mail-greeting'}).text
    mail_salutation = recap_email_soup.find("p", {"id": 'mail-salutation'}).text
    assert recap_email['Subject'] == 'Confirmation de votre réservation pour Mains, sorts et papiers le 20 juillet 2019 à 14:00'
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
    recap_email = make_user_booking_confirmation_recap_email(booking)

    # Then
    email_html = _remove_whitespaces(recap_email['Html-part'])
    recap_email_soup = BeautifulSoup(email_html, 'html.parser')
    mail_content = recap_email_soup.find("div", {"id": 'mail-content'}).text
    assert 'Nous vous confirmons votre commande pour Test Book (Ref: 12345),' in mail_content
    assert 'proposé par Test offerer.' in mail_content
    assert recap_email['Subject'] == 'Confirmation de votre commande pour Test Book'
