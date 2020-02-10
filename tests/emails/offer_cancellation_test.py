from datetime import datetime, timezone, timedelta
from unittest.mock import patch

from bs4 import BeautifulSoup

from emails.beneficiary_offer_cancellation import retrieve_offerer_booking_recap_email_data_after_user_cancellation, \
    _is_offer_active_for_recap
from repository import repository
from tests.conftest import clean_database
from tests.model_creators.generic_creators import create_booking, create_user, create_offerer, create_venue
from tests.model_creators.specific_creators import create_stock_from_event_occurrence, create_stock_from_offer, \
    create_product_with_thing_type, create_offer_with_thing_product, create_offer_with_event_product, \
    create_event_occurrence
from utils.mailing import make_offerer_driven_cancellation_email_for_offerer


class MakeOffererDrivenCancellationEmailForOffererTest:
    @clean_database
    def test_make_offerer_driven_cancellation_email_for_offerer_event_when_no_other_booking(self, app):
        # Given
        beginning_datetime = datetime(2019, 7, 20, 12, 0, 0, tzinfo=timezone.utc)
        end_datetime = beginning_datetime + timedelta(hours=1)
        booking_limit_datetime = beginning_datetime - timedelta(hours=1)

        user = create_user(email='john@doe.fr', public_name='John Doe')
        offerer = create_offerer(name='Test offerer')
        venue = create_venue(offerer, name='Le petit théâtre', address='1 rue de la Libération', city='Montreuil',
                             postal_code='93100')
        offer = create_offer_with_event_product(venue, event_name='Le théâtre des ombres')
        event_occurrence = create_event_occurrence(offer, beginning_datetime=beginning_datetime,
                                                   end_datetime=end_datetime)
        stock = create_stock_from_event_occurrence(event_occurrence, price=20, available=10,
                                                   booking_limit_date=booking_limit_datetime)
        booking = create_booking(user=user, stock=stock)

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
    def test_make_offerer_driven_cancellation_email_for_offerer_event_when_other_booking(self, app):
        # Given
        user1 = create_user(email='john@doe.fr', first_name='John', last_name='Doe', public_name='John Doe')
        user2 = create_user(email='jane@smith.fr', first_name='Jane', last_name='Smith', public_name='Jane S.')
        offerer = create_offerer(name='Test offerer')
        venue = create_venue(offerer, name='Le petit théâtre', address='1 rue de la Libération', city='Montreuil',
                             postal_code='93100')
        offer = create_offer_with_event_product(venue, event_name='Le théâtre des ombres')
        event_occurrence = create_event_occurrence(offer,
                                                   beginning_datetime=datetime(2019, 7, 20, 12, 0, 0,
                                                                               tzinfo=timezone.utc))
        stock = create_stock_from_event_occurrence(event_occurrence, price=20, available=10)
        booking1 = create_booking(user=user1, stock=stock, token='98765')
        booking2 = create_booking(user=user2, stock=stock, token='12345')

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
    def test_make_offerer_driven_cancellation_email_for_offerer_thing_and_already_existing_booking(self, app):
        # Given
        user = create_user(email='john@doe.fr', first_name='John', last_name='Doe', public_name='John Doe')
        offerer = create_offerer(name='Test offerer')
        venue = create_venue(offerer, name='La petite librairie', address='1 rue de la Libération', city='Montreuil',
                             postal_code='93100')
        thing_product = create_product_with_thing_type(thing_name='Le récit de voyage')
        offer = create_offer_with_thing_product(venue=venue, product=thing_product)
        stock = create_stock_from_offer(offer, price=0, available=10)
        booking = create_booking(user=user, stock=stock, token='12346')

        user2 = create_user(email='bond@james.bond.uk', first_name='James', last_name='Bond',
                            public_name='James Bond')
        booking2 = create_booking(user=user2, stock=stock, token='12345')
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


class MakeOffererBookingRecapEmailAfterUserCancellationWithMailjetTemplateTest:
    @patch('emails.beneficiary_offer_cancellation.SUPPORT_EMAIL_ADDRESS', 'support@example.com')
    @patch('emails.beneficiary_offer_cancellation.DEV_EMAIL_ADDRESS', 'dev@example.com')
    @patch('emails.beneficiary_offer_cancellation.build_pc_pro_offer_link', return_value='http://pc_pro.com/offer_link')
    @patch('emails.beneficiary_offer_cancellation._is_offer_active_for_recap', return_value=True)
    def test_should_return_mailjet_data_with_no_ongoing_booking(self, mock_is_offer_active,
                                                                mock_build_pc_pro_offer_link):
        # Given
        user = create_user(email='jean.dupont@example.com', public_name='Jean Dupont')
        offerer = create_offerer()
        venue = create_venue(offerer, name='Venue name', departement_code='75')
        offer = create_offer_with_event_product(venue, event_name='My Event')
        stock = create_stock_from_offer(offer, price=12.52, beginning_datetime=datetime(2019, 10, 9, 10, 20, 00))
        booking = create_booking(user=user, stock=stock, venue=venue, is_cancelled=True, quantity=2)
        recipients = 'support@example.com'

        # When
        mailjet_data = retrieve_offerer_booking_recap_email_data_after_user_cancellation(booking, recipients)

        # Then
        assert mailjet_data == {
            'FromEmail': 'support@example.com',
            'MJ-TemplateID': 780015,
            'MJ-TemplateLanguage': True,
            'To': 'dev@example.com',
            'Vars': {
                'departement': '75',
                'nom_offre': 'My Event',
                'lien_offre_pcpro': 'http://pc_pro.com/offer_link',
                'nom_lieu': 'Venue name',
                'prix': '12.52',
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
        user1 = create_user(email='jean.dupont@example.com', public_name='Jean Dupont')
        user2 = create_user(email='jean.val@example.com', public_name='Jean Val', first_name='John', last_name='Doe')
        offerer = create_offerer()
        venue = create_venue(offerer, name='Venue name', departement_code='75')
        offer = create_offer_with_event_product(venue, event_name='My Event')
        stock = create_stock_from_offer(offer, price=0, beginning_datetime=datetime(2019, 10, 9, 10, 20, 00))
        booking1 = create_booking(user=user1, stock=stock, venue=venue, is_cancelled=True, quantity=2)
        create_booking(user=user2, stock=stock, venue=venue, is_cancelled=False, quantity=1, token='29JM9Q')
        recipients = 'support@example.com'

        # When
        mailjet_data = retrieve_offerer_booking_recap_email_data_after_user_cancellation(booking1, recipients)

        # Then
        assert mailjet_data == {
            'FromEmail': 'support@example.com',
            'MJ-TemplateID': 780015,
            'MJ-TemplateLanguage': True,
            'To': 'dev@example.com',
            'Vars': {
                'departement': '75',
                'nom_offre': 'My Event',
                'lien_offre_pcpro': 'http://pc_pro.com/offer_link',
                'nom_lieu': 'Venue name',
                'prix': 'Gratuit',
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
        user1 = create_user(email='jean.dupont@example.com', public_name='Jean Dupont')
        user2 = create_user(email='jean.val@example.com', public_name='Jean Val', first_name='John', last_name='Doe')
        offerer = create_offerer()
        venue = create_venue(offerer, name='Venue name', departement_code='75')
        offer = create_offer_with_thing_product(venue, thing_name='My Thing')
        stock = create_stock_from_offer(offer, price=12)
        booking1 = create_booking(user=user1, stock=stock, venue=venue, is_cancelled=True, quantity=2)
        create_booking(user=user2, stock=stock, venue=venue, is_cancelled=False, quantity=1, token='29JM9Q')
        recipients = 'support@example.com'

        # When
        mailjet_data = retrieve_offerer_booking_recap_email_data_after_user_cancellation(booking1, recipients)

        # Then
        assert mailjet_data == {
            'FromEmail': 'support@example.com',
            'MJ-TemplateID': 780015,
            'MJ-TemplateLanguage': True,
            'To': 'dev@example.com',
            'Vars': {
                'departement': '75',
                'nom_offre': 'My Thing',
                'lien_offre_pcpro': 'http://pc_pro.com/offer_link',
                'nom_lieu': 'Venue name',
                'prix': '12',
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

    @patch('emails.beneficiary_offer_cancellation.SUPPORT_EMAIL_ADDRESS', 'support@example.com')
    @patch('emails.beneficiary_offer_cancellation.DEV_EMAIL_ADDRESS', 'dev@example.com')
    @patch('emails.beneficiary_offer_cancellation.build_pc_pro_offer_link', return_value='http://pc_pro.com/offer_link')
    @patch('emails.beneficiary_offer_cancellation._is_offer_active_for_recap', return_value=False)
    def test_should_return_numerique_when_venue_is_virtual(self, mock_is_offer_active, mock_build_pc_pro_offer_link):
        # Given
        user1 = create_user(email='jean.dupont@example.com', public_name='Jean Dupont')
        user2 = create_user(email='jean.val@example.com', public_name='Jean Val', first_name='John', last_name='Doe')
        offerer = create_offerer()
        venue = create_venue(offerer, name='Venue name', is_virtual=True)
        offer = create_offer_with_thing_product(venue, thing_name='My Thing')
        stock = create_stock_from_offer(offer, price=12)
        booking1 = create_booking(user=user1, stock=stock, venue=venue, is_cancelled=True, quantity=2)
        create_booking(user=user2, stock=stock, venue=venue, is_cancelled=False, quantity=1, token='29JM9Q')
        recipients = 'support@example.com'

        # When
        mailjet_data = retrieve_offerer_booking_recap_email_data_after_user_cancellation(booking1, recipients)

        # Then
        assert mailjet_data == {
            'FromEmail': 'support@example.com',
            'MJ-TemplateID': 780015,
            'MJ-TemplateLanguage': True,
            'To': 'dev@example.com',
            'Vars': {
                'departement': 'numérique',
                'nom_offre': 'My Thing',
                'lien_offre_pcpro': 'http://pc_pro.com/offer_link',
                'nom_lieu': 'Venue name',
                'prix': '12',
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
        repository.save(stock)

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
        repository.save(stock)

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
        booking = create_booking(user=user, stock=stock, quantity=2)
        repository.save(booking)

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
        booking = create_booking(user=user, stock=stock, quantity=2)
        repository.save(booking)

        # When
        is_active = _is_offer_active_for_recap(stock)

        # Then
        assert not is_active

    @clean_database
    def test_should_return_true_when_stock_is_unlimited(self, app):
        # Given
        user = create_user()
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue, is_active=True)
        stock = create_stock_from_offer(offer, price=0,
                                        available=None)
        booking = create_booking(user=user, stock=stock, quantity=2)
        repository.save(booking)

        # When
        is_active = _is_offer_active_for_recap(stock)

        # Then
        assert is_active

    @clean_database
    def test_should_return_false_when_stock_is_unlimited_but_booking_date_is_past(self, app):
        # Given
        user = create_user()
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue, is_active=True)
        stock = create_stock_from_offer(offer, price=0,
                                        available=None,
                                        booking_limit_datetime=datetime.now() - timedelta(days=6))
        booking = create_booking(user=user, stock=stock, quantity=2)
        repository.save(booking)

        # When
        is_active = _is_offer_active_for_recap(stock)

        # Then
        assert not is_active
