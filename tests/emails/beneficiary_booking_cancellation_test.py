from datetime import datetime, timedelta

from bs4 import BeautifulSoup

from tests.conftest import mocked_mail, clean_database
from tests.test_utils import create_offerer, create_venue, create_stock_with_event_offer, create_user, create_booking, \
    create_offer_with_thing_product, create_stock_with_thing_offer
from tests.utils.mailing_test import _remove_whitespaces
from emails.beneficiary_booking_cancellation import make_user_booking_cancellation_recap_email

@mocked_mail
@clean_database
def test_should_return_thing_data_when_booking_is_a_thing(app):
    # Given
    offerer = create_offerer()
    venue = create_venue(offerer, 'Test Venue', 'reservations@test.fr', '123 rue test', '93000', 'Test city', '93')
    thing_offer = create_offer_with_thing_product(venue=None, thing_name='Test name thing')
    stock = create_stock_with_thing_offer(offerer=None, venue=venue, offer=thing_offer)
    stock.offer.product.idAtProviders = '12345'
    user = create_user('Test', departement_code='93', email='test@example.com', can_book_free_offers=True)
    booking = create_booking(user, stock, venue, None)

    # When
    recap_email = make_user_booking_cancellation_recap_email(booking)

    # Then
    html_email = _remove_whitespaces(recap_email['Html-part'])
    recap_email_soup = BeautifulSoup(html_email, 'html.parser')
    assert 'Votre commande pour Test Book (Ref: 12345),' in recap_email_soup.find("div",
                                                                                  {"id": 'mail-content'}).text
    assert data == {
        'FromEmail': 'support@example.com',
        'Mj-TemplateID': 1091464,
        'Mj-TemplateLanguage': True,
        'To': 'fabien@example.net',
        'Vars': {
            'prenom_user': 'Fabien',
            'env': '',
            'event': 0,
            'nom_offre': 'Test name thing',
            'date_annulation': '',
            'heure_annulation': '',
            'date_event': '',
            'heure_event': '',
            'offer_price': '',
            'prix_offre': '',
            'offer_id': '',
            'mediation_id': '',
        },
    }


# @mocked_mail
# @clean_database
# def test_make_user_booking_event_recap_email_should_have_standard_cancellation_body_and_subject(app):
#     # Given
#     beginning_datetime = datetime(2019, 7, 20, 12, 0, 0)
#     end_datetime = beginning_datetime + timedelta(hours=1)
#     booking_limit_datetime = beginning_datetime - timedelta(hours=1)
#     offerer = create_offerer()
#     venue = create_venue(offerer, 'Test offerer', 'reservations@test.fr', '123 rue test', '93000', 'Test city',
#                          '93')
#     stock = create_stock_with_event_offer(offerer=None, venue=venue, beginning_datetime=beginning_datetime,
#                                           end_datetime=end_datetime, booking_limit_datetime=booking_limit_datetime)
#     user = create_user('Test', departement_code='93', email='test@example.com', can_book_free_offers=True)
#     booking = create_booking(user, stock, venue, None)

#     # When
#     recap_email = make_user_booking_cancellation_recap_email(booking)

#     # Then
#     email_html = _remove_whitespaces(recap_email['Html-part'])
#     recap_email_soup = BeautifulSoup(email_html, 'html.parser')
#     mail_content = recap_email_soup.find('div', {"id": 'mail-content'}).text
#     assert 'Votre réservation pour Mains, sorts et papiers,' in mail_content
#     assert 'proposé par Test offerer' in mail_content
#     assert 'le 20 juillet 2019 à 14:00,' in mail_content
#     assert 'a bien été annulée.' in mail_content
#     assert recap_email['Subject'] == 'Annulation de votre réservation pour Mains, sorts et papiers le 20 juillet 2019 à 14:00'

