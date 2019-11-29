from datetime import datetime, timezone, timedelta
from unittest.mock import patch

from bs4 import BeautifulSoup

from emails.beneficiary_offer_cancellation import make_offerer_booking_recap_email_after_user_cancellation_data, \
    _is_offer_active_for_recap
from models import PcObject
from tests.conftest import clean_database
from tests.test_utils import create_user, create_offerer, create_venue, create_offer_with_event_product, \
    create_event_occurrence, create_stock_from_event_occurrence, create_booking, create_offer_with_thing_product, \
    create_stock_from_offer, create_product_with_thing_type, create_mocked_bookings
from tests.utils.mailing_test import _remove_whitespaces
from utils.mailing import make_offerer_driven_cancellation_email_for_user, \
    make_offerer_driven_cancellation_email_for_offerer, make_batch_cancellation_email


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


class MakeOffererBookingRecapEmailAfterUserCancellationWithMailjetTemplateTest:
    @patch('emails.beneficiary_offer_cancellation.SUPPORT_EMAIL_ADDRESS', 'support@example.com')
    @patch('emails.beneficiary_offer_cancellation.DEV_EMAIL_ADDRESS', 'dev@example.com')
    @patch('emails.beneficiary_offer_cancellation.build_pc_pro_offer_link', return_value='http://pc_pro.com/offer_link')
    @patch('emails.beneficiary_offer_cancellation._is_offer_active_for_recap', return_value=True)
    def test_should_return_mailjet_data_with_no_ongoing_booking(self, mock_is_offer_active,
                                                                mock_build_pc_pro_offer_link):
        # Given
        user = create_user(public_name='Jean Dupont', email='jean.dupont@example.com')
        offerer = create_offerer(postal_code=75)
        venue = create_venue(offerer, name='Venue name')
        offer = create_offer_with_event_product(venue, event_name='My Event')
        stock = create_stock_from_offer(offer, price=12, beginning_datetime=datetime(2019, 10, 9, 10, 20, 00))
        booking = create_booking(user, stock, venue, quantity=2, is_cancelled=True)
        recipients = 'support@example.com'

        # When
        mailjet_data = make_offerer_booking_recap_email_after_user_cancellation_data(booking, recipients)

        # Then
        assert mailjet_data == {
            'FromEmail': 'support@example.com',
            'MJ-TemplateID': 780015,
            'MJ-TemplateLanguage': True,
            'To': 'dev@example.com',
            'Vars': {
                'departement': 75,
                'nom_offre': 'My Event',
                'lien_offre_pcpro': 'http://pc_pro.com/offer_link',
                'nom_lieu': 'Venue name',
                'prix': 12,
                'is_event': 1,
                'date': '09-Oct-2019',
                'heure': '12h20',
                'quantite': 2,
                'user_name': 'Jean Dupont',
                'user_email': 'jean.dupont@example.com',
                'is_active': 1,
                'nombre_resa': 0,
                'env': '-development',
                'users': [],
            },
        }

    @patch('emails.beneficiary_offer_cancellation.SUPPORT_EMAIL_ADDRESS', 'support@example.com')
    @patch('emails.beneficiary_offer_cancellation.DEV_EMAIL_ADDRESS', 'dev@example.com')
    @patch('emails.beneficiary_offer_cancellation.build_pc_pro_offer_link', return_value='http://pc_pro.com/offer_link')
    @patch('emails.beneficiary_offer_cancellation._is_offer_active_for_recap', return_value=True)
    def test_should_return_mailjet_data_with_ongoing_bookings(self, mock_is_offer_active, mock_build_pc_pro_offer_link):
        # Given
        user1 = create_user(public_name='Jean Dupont', email='jean.dupont@example.com')
        user2 = create_user(public_name='Jean Val', email='jean.val@example.com')
        offerer = create_offerer(postal_code=75)
        venue = create_venue(offerer, name='Venue name')
        offer = create_offer_with_event_product(venue, event_name='My Event')
        stock = create_stock_from_offer(offer, price=12, beginning_datetime=datetime(2019, 10, 9, 10, 20, 00))
        booking1 = create_booking(user1, stock, venue, quantity=2, is_cancelled=True)
        create_booking(user2, stock, venue, quantity=1, is_cancelled=False, token='29JM9Q')
        recipients = 'support@example.com'

        # When
        mailjet_data = make_offerer_booking_recap_email_after_user_cancellation_data(booking1, recipients)

        # Then
        assert mailjet_data == {
            'FromEmail': 'support@example.com',
            'MJ-TemplateID': 780015,
            'MJ-TemplateLanguage': True,
            'To': 'dev@example.com',
            'Vars': {
                'departement': 75,
                'nom_offre': 'My Event',
                'lien_offre_pcpro': 'http://pc_pro.com/offer_link',
                'nom_lieu': 'Venue name',
                'prix': 12,
                'is_event': 1,
                'date': '09-Oct-2019',
                'heure': '12h20',
                'quantite': 2,
                'user_name': 'Jean Dupont',
                'user_email': 'jean.dupont@example.com',
                'is_active': 1,
                'nombre_resa': 1,
                'env': '-development',
                'users': [
                    {
                        'contremarque': '29JM9Q',
                        'email': 'jean.val@example.com',
                        'firstName': 'John',
                        'lastName': 'Doe'
                    }
                ]
            }
        }

    @patch('emails.beneficiary_offer_cancellation.SUPPORT_EMAIL_ADDRESS', 'support@example.com')
    @patch('emails.beneficiary_offer_cancellation.DEV_EMAIL_ADDRESS', 'dev@example.com')
    @patch('emails.beneficiary_offer_cancellation.build_pc_pro_offer_link', return_value='http://pc_pro.com/offer_link')
    @patch('emails.beneficiary_offer_cancellation._is_offer_active_for_recap', return_value=False)
    def test_should_return_mailjet_data_on_thing_offer(self, mock_is_offer_active, mock_build_pc_pro_offer_link):
        # Given
        user1 = create_user(public_name='Jean Dupont', email='jean.dupont@example.com')
        user2 = create_user(public_name='Jean Val', email='jean.val@example.com')
        offerer = create_offerer(postal_code=75)
        venue = create_venue(offerer, name='Venue name')
        offer = create_offer_with_thing_product(venue, thing_name='My Thing')
        stock = create_stock_from_offer(offer, price=12)
        booking1 = create_booking(user1, stock, venue, quantity=2, is_cancelled=True)
        create_booking(user2, stock, venue, quantity=1, is_cancelled=False, token='29JM9Q')
        recipients = 'support@example.com'

        # When
        mailjet_data = make_offerer_booking_recap_email_after_user_cancellation_data(booking1, recipients)

        # Then
        assert mailjet_data == {
            'FromEmail': 'support@example.com',
            'MJ-TemplateID': 780015,
            'MJ-TemplateLanguage': True,
            'To': 'dev@example.com',
            'Vars': {
                'departement': 75,
                'nom_offre': 'My Thing',
                'lien_offre_pcpro': 'http://pc_pro.com/offer_link',
                'nom_lieu': 'Venue name',
                'prix': 12,
                'is_event': 0,
                'date': '',
                'heure': '',
                'quantite': 2,
                'user_name': 'Jean Dupont',
                'user_email': 'jean.dupont@example.com',
                'is_active': 0,
                'nombre_resa': 1,
                'env': '-development',
                'users': [
                    {
                        'contremarque': '29JM9Q',
                        'email': 'jean.val@example.com',
                        'firstName': 'John',
                        'lastName': 'Doe'
                    }
                ]
            }
        }


class IsOfferActiveForRecapTest:
    @clean_database
    def test_should_return_true_when_offer_is_active_and_stock_still_bookable(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue, is_active=True)
        stock = create_stock_from_offer(offer, available=2, booking_limit_datetime=datetime.now() + timedelta(days=6))
        PcObject.save(stock)

        # When
        is_active = _is_offer_active_for_recap(stock)

        # Then
        assert is_active

    @clean_database
    def test_should_return_false_when_offer_is_not_active(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue, is_active=False)
        stock = create_stock_from_offer(offer, available=2, booking_limit_datetime=datetime.now() + timedelta(days=6))
        PcObject.save(stock)

        # When
        is_active = _is_offer_active_for_recap(stock)

        # Then
        assert not is_active

    @clean_database
    def test_should_return_false_when_stock_has_no_remaining_quantity(self, app):
        # Given
        user = create_user()
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue, is_active=True)
        stock = create_stock_from_offer(offer, price=0,
                                        available=2,
                                        booking_limit_datetime=datetime.now() + timedelta(days=6))
        booking = create_booking(user, stock, quantity=2)
        PcObject.save(booking)

        # When
        is_active = _is_offer_active_for_recap(stock)

        # Then
        assert not is_active

    @clean_database
    def test_should_return_false_when_stock_booking_limit_is_past(self, app):
        # Given
        user = create_user()
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue, is_active=True)
        stock = create_stock_from_offer(offer, price=0,
                                        available=2,
                                        booking_limit_datetime=datetime.now() - timedelta(days=6))
        booking = create_booking(user, stock, quantity=2)
        PcObject.save(booking)

        # When
        is_active = _is_offer_active_for_recap(stock)

        # Then
        assert not is_active
