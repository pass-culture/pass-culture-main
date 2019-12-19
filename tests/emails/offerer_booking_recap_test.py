from datetime import datetime, timezone, timedelta
from unittest.mock import patch

from bs4 import BeautifulSoup
from freezegun import freeze_time

from models import PcObject, ThingType, EventType, Offerer
from tests.conftest import clean_database, mocked_mail
from tests.model_creators.generic_creators import create_booking, create_user, create_offerer, create_venue, create_deposit
from tests.model_creators.specific_creators import create_stock_with_event_offer, create_stock_from_event_occurrence, \
    create_stock_from_offer, create_stock_with_thing_offer, create_product_with_thing_type, \
    create_offer_with_thing_product, create_offer_with_event_product, create_event_occurrence
from tests.utils.mailing_test import _remove_whitespaces
from utils.mailing import ADMINISTRATION_EMAIL_ADDRESS, \
    make_offerer_booking_recap_email_after_user_action
from emails.offerer_booking_recap import retrieve_data_for_offerer_booking_recap_email


class MakeOffererBookingRecapEmailWithMailjetTemplateTest:
    @clean_database
    def test_should_write_email_with_right_data_when_offer_is_an_event(self, app):
        # Given
        user = create_user(email='test@example.com', first_name='John', last_name='Doe')
        offerer = create_offerer(idx=1)
        venue = create_venue(offerer, name='Test offerer', siret='89765389057043', idx=1,
                             departement_code='75', postal_code='75000')
        event_offer = create_offer_with_event_product(venue, idx=1)
        beginning_datetime = datetime(2019, 11, 6, 14, 59, 5, tzinfo=timezone.utc)
        stock = create_stock_from_offer(event_offer, beginning_datetime=beginning_datetime, price=0, available=10)
        booking = create_booking(user=user, stock=stock, venue=venue, token='ABC123')
        recipient = ['dev@passculture.app']
        stock.bookings = [booking]

        PcObject.save(stock)

        # When
        email = retrieve_data_for_offerer_booking_recap_email(booking, recipient)

        # Then
        assert email == {
            'FromEmail': 'support@passculture.app',
            'MJ-TemplateID': 1095029,
            'MJ-TemplateLanguage': True,
            'To': 'dev@passculture.app',
            'Vars':
                {
                    'nom_offre': 'Test event',
                    'nom_lieu': 'Test offerer',
                    'prix': 'Gratuit',
                    'date': '06-Nov-2019',
                    'heure': '15h59',
                    'quantity': 1,
                    'user_firstName': 'John',
                    'user_lastName': 'Doe',
                    'user_email': 'test@example.com',
                    'is_event': 1,
                    'nombre_resa': 1,
                    'contremarque': 'ABC123',
                    'env': '-development',
                    'ISBN': '',
                    'lien_offre_pcpro': 'http://localhost:3001/offres/AE?lieu=AE&structure=AE',
                    'offer_type': 'EventType.SPECTACLE_VIVANT',
                    'departement': '75',
                    'users': [{'firstName': 'John',
                               'lastName': 'Doe',
                               'email': 'test@example.com',
                               'contremarque': 'ABC123'}]
                }
        }

    @clean_database
    def test_should_write_email_with_right_data_when_offer_is_a_book(self, app):
        # Given
        user = create_user(email='test@example.com', first_name='John', last_name='Doe')
        offerer = create_offerer(idx=1)
        extra_data = {'isbn': '123456789'}
        venue = create_venue(offerer, name='Test offerer', is_virtual=True, siret=None, idx=1)

        thing_product = create_product_with_thing_type(thing_name='Le récit de voyage', extra_data=extra_data)
        event_offer = create_offer_with_thing_product(venue, thing_product, idx=1)
        stock = create_stock_from_offer(event_offer, price=0)
        booking = create_booking(user=user, stock=stock, venue=venue, quantity=3, token='ABC123')
        recipient = ['dev@passculture.app']
        stock.bookings = [booking]

        PcObject.save(stock)

        # When
        email = retrieve_data_for_offerer_booking_recap_email(booking, recipient)

        # Then
        assert email == {
            'FromEmail': 'support@passculture.app',
            'MJ-TemplateID': 1095029,
            'MJ-TemplateLanguage': True,
            'To': 'dev@passculture.app',
            'Vars':
                {
                    'nom_offre': 'Le récit de voyage',
                    'nom_lieu': 'Test offerer',
                    'prix': 'Gratuit',
                    'ISBN': '123456789',
                    'nombre_resa': 1,
                    'contremarque': 'ABC123',
                    'env': '-development',
                    'lien_offre_pcpro': 'http://localhost:3001/offres/AE?lieu=AE&structure=AE',

                    'user_firstName': 'John',
                    'user_lastName': 'Doe',
                    'user_email': 'test@example.com',
                    'is_event': 0,
                    'date': '',
                    'heure': '',
                    'quantity': 3,
                    'offer_type': 'book',
                    'departement': 'numérique',
                    'users': [{'firstName': 'John',
                               'lastName': 'Doe',
                               'email': 'test@example.com',
                               'contremarque': 'ABC123'}]
                }
        }

    @clean_database
    def test_should_not_truncate_price(self, app):
        # Given
        user = create_user(email='test@example.com', first_name='John', last_name='Doe')
        offerer = create_offerer(idx=1)
        deposit = create_deposit(user, amount=50, source='public')
        venue = create_venue(offerer, name='Test offerer', siret='89765389057043', idx=1,
                             departement_code='75', postal_code='75000')
        event_offer = create_offer_with_event_product(venue, is_duo=True, idx=1)
        beginning_datetime = datetime(2019, 11, 6, 14, 00, 0, tzinfo=timezone.utc)
        stock = create_stock_from_offer(event_offer, beginning_datetime=beginning_datetime, price=5.86, available=10)
        booking = create_booking(user=user, stock=stock, venue=venue, token='ABC123')
        stock.bookings = [booking]
        recipient = ['dev@passculture.app']

        PcObject.save(deposit, stock)

        # When
        email = retrieve_data_for_offerer_booking_recap_email(booking, recipient)

        # Then
        assert email == {
            'FromEmail': 'support@passculture.app',
            'MJ-TemplateID': 1095029,
            'MJ-TemplateLanguage': True,
            'To': 'dev@passculture.app',
            'Vars':
                {
                    'nom_offre': 'Test event',
                    'nom_lieu': 'Test offerer',
                    'prix': '5.86',
                    'date': '06-Nov-2019',
                    'heure': '15h',
                    'quantity': 1,
                    'user_firstName': 'John',
                    'user_lastName': 'Doe',
                    'user_email': 'test@example.com',
                    'is_event': 1,
                    'ISBN': '',
                    'offer_type': 'EventType.SPECTACLE_VIVANT',
                    'departement': '75',
                    'nombre_resa': 1,
                    'contremarque': 'ABC123',
                    'env': '-development',
                    'lien_offre_pcpro': 'http://localhost:3001/offres/AE?lieu=AE&structure=AE',
                    'users': [{'firstName': 'John',
                               'lastName': 'Doe',
                               'email': 'test@example.com',
                               'contremarque': 'ABC123'}]
                }
        }

    @clean_database
    def test_returns_empty_ISBN_when_no_extra_data(self, app):
        # Given
        user = create_user(email='test@example.com', first_name='John', last_name='Doe')
        offerer = create_offerer(idx=1)
        venue = create_venue(offerer, name='Test offerer', is_virtual=True, siret=None, idx=1)
        thing_offer = create_offer_with_thing_product(venue, thing_type=ThingType.LIVRE_EDITION, idx=1)
        beginning_datetime = datetime(2019, 11, 6, 14, 00, 0, tzinfo=timezone.utc)
        stock = create_stock_from_offer(thing_offer, beginning_datetime=beginning_datetime, price=0, available=10)
        booking = create_booking(user=user, stock=stock, venue=venue, token='ABC123')
        recipient = ['dev@passculture.app']
        stock.bookings = [booking]

        PcObject.save(stock)

        # When
        thing_offer.extraData = None
        email_data_template = retrieve_data_for_offerer_booking_recap_email(booking, recipient)

        # Then
        assert email_data_template == {
            'FromEmail': 'support@passculture.app',
            'MJ-TemplateID': 1095029,
            'MJ-TemplateLanguage': True,
            'To': 'dev@passculture.app',
            'Vars':
                {
                    'nom_offre': 'Test Book',
                    'nom_lieu': 'Test offerer',
                    'prix': 'Gratuit',
                    'date': '',
                    'heure': '',
                    'quantity': 1,
                    'user_firstName': 'John',
                    'user_lastName': 'Doe',
                    'user_email': 'test@example.com',
                    'is_event': 0,
                    'ISBN': '',
                    'offer_type': 'book',
                    'departement': 'numérique',
                    'nombre_resa': 1,
                    'contremarque': 'ABC123',
                    'env': '-development',
                    'lien_offre_pcpro': 'http://localhost:3001/offres/AE?lieu=AE&structure=AE',
                    'users': [{'firstName': 'John',
                               'lastName': 'Doe',
                               'email': 'test@example.com',
                               'contremarque': 'ABC123'}]
                }
        }

    @clean_database
    def test_returns_empty_ISBN_when_extra_data_has_no_key_isbn(self, app):
        # Given
        user = create_user(email="test@example.com", first_name='John', last_name='Doe')
        offerer = create_offerer(idx=1)
        venue = create_venue(offerer, name='Test offerer', is_virtual=True, siret=None, idx=1)
        thing_offer = create_offer_with_thing_product(venue, thing_type=ThingType.LIVRE_EDITION, idx=1)
        beginning_datetime = datetime(2019, 11, 6, 14, 00, 0, tzinfo=timezone.utc)
        stock = create_stock_from_offer(thing_offer, beginning_datetime=beginning_datetime, price=0, available=10)
        booking = create_booking(user=user, stock=stock, venue=venue, token='ABC123')
        stock.bookings = [booking]
        recipient = ['dev@passculture.app']

        PcObject.save(stock)

        # When
        thing_offer.extraData = {}
        email_data_template = retrieve_data_for_offerer_booking_recap_email(booking, recipient)

        # Then
        assert email_data_template == {
            'FromEmail': 'support@passculture.app',
            'MJ-TemplateID': 1095029,
            'MJ-TemplateLanguage': True,
            'To': 'dev@passculture.app',
            'Vars':
                {
                    'nom_offre': 'Test Book',
                    'nom_lieu': 'Test offerer',
                    'prix': 'Gratuit',
                    'date': '',
                    'heure': '',
                    'quantity': 1,
                    'user_firstName': 'John',
                    'user_lastName': 'Doe',
                    'user_email': 'test@example.com',
                    'is_event': 0,
                    'ISBN': '',
                    'departement': 'numérique',
                    'offer_type': 'book',
                    'lien_offre_pcpro': 'http://localhost:3001/offres/AE?lieu=AE&structure=AE',
                    'nombre_resa': 1,
                    'env': '-development',
                    'contremarque': 'ABC123',
                    'users': [{'firstName': 'John',
                               'lastName': 'Doe',
                               'email': 'test@example.com',
                               'contremarque': 'ABC123'}]
                }
        }

    @patch('utils.mailing.feature_send_mail_to_users_enabled', return_value=True)
    @clean_database
    def test_returns_multiple_offer_email_when_production_environment(self, app):
        # Given
        user = create_user(email='test@example.com', first_name='John', last_name='Doe')
        offerer = create_offerer(idx=1)
        venue = create_venue(offerer, name='Test offerer', siret='89765389057043', idx=1,
                             departement_code='75', postal_code='75000')
        thing_offer = create_offer_with_thing_product(venue, thing_type=ThingType.LIVRE_EDITION,
                                                      booking_email='dev@passculture.app', idx=1)
        beginning_datetime = datetime(2019, 11, 6, 14, 00, 0, tzinfo=timezone.utc)
        stock = create_stock_from_offer(thing_offer, beginning_datetime=beginning_datetime, price=0, available=10)
        booking = create_booking(user=user, stock=stock, venue=venue, token='ABC123')
        stock.bookings = [booking]
        recipient = ['dev@passculture.app', ADMINISTRATION_EMAIL_ADDRESS]

        PcObject.save(stock)

        # When
        thing_offer.extraData = None

        email_data_template = retrieve_data_for_offerer_booking_recap_email(booking, recipient)

        # Then
        assert email_data_template == {
            'FromEmail': 'support@passculture.app',
            'MJ-TemplateID': 1095029,
            'MJ-TemplateLanguage': True,
            'To': f'dev@passculture.app, {ADMINISTRATION_EMAIL_ADDRESS}',
            'Vars':
                {
                    'nom_offre': 'Test Book',
                    'nom_lieu': 'Test offerer',
                    'prix': 'Gratuit',
                    'date': '',
                    'heure': '',
                    'quantity': 1,
                    'user_firstName': 'John',
                    'user_lastName': 'Doe',
                    'user_email': 'test@example.com',
                    'is_event': 0,
                    'ISBN': '',
                    'offer_type': 'book',
                    'departement': '75',
                    'nombre_resa': 1,
                    'contremarque': 'ABC123',
                    'env': '-development',
                    'lien_offre_pcpro': 'http://localhost:3001/offres/AE?lieu=AE&structure=AE',
                    'users': [{'firstName': 'John',
                               'lastName': 'Doe',
                               'email': 'test@example.com',
                               'contremarque': 'ABC123'}]
                }
        }

    @patch('utils.mailing.IS_PROD', False)
    @patch('utils.mailing.feature_send_mail_to_users_enabled', return_value=True)
    @clean_database
    def test_returns_email_with_correct_data_when_two_users_book_the_same_offer(self, app):
        # Given
        user_1 = create_user(can_book_free_offers=True, departement_code='93', email='test@example.com',
                             first_name='Jean', last_name='Dupont', public_name='Test')
        user_2 = create_user(can_book_free_offers=True, departement_code='93', email='mail@example.com',
                             first_name='Jaja', last_name='Dudu', public_name='Test')
        offerer = create_offerer(idx=1)
        venue = create_venue(offerer, name='Test offerer', siret='89765389057043', idx=1,
                             departement_code='75', postal_code='75000')
        thing_offer = create_offer_with_thing_product(venue, thing_type=ThingType.LIVRE_EDITION,
                                                      booking_email='dev@passculture.app', idx=1)
        beginning_datetime = datetime(2019, 11, 6, 14, 00, 0, tzinfo=timezone.utc)
        stock = create_stock_from_offer(thing_offer, beginning_datetime=beginning_datetime, price=0, available=10)
        booking_1 = create_booking(user=user_1, stock=stock, venue=venue, token='ACVSDC')
        booking_2 = create_booking(user=user_2, stock=stock, venue=venue, token='TEST95')
        stock.bookings = [booking_1, booking_2]
        recipient = ['dev@passculture.app', ADMINISTRATION_EMAIL_ADDRESS]

        PcObject.save(stock)

        # When
        thing_offer.extraData = None

        email_data_template = retrieve_data_for_offerer_booking_recap_email(booking_1, recipient)

        # Then
        assert email_data_template == {
            'FromEmail': 'support@passculture.app',
            'MJ-TemplateID': 1095029,
            'MJ-TemplateLanguage': True,
            'To': f'dev@passculture.app, {ADMINISTRATION_EMAIL_ADDRESS}',
            'Vars':
                {
                    'nom_offre': 'Test Book',
                    'nom_lieu': 'Test offerer',
                    'prix': 'Gratuit',
                    'date': '',
                    'heure': '',
                    'quantity': 1,
                    'user_firstName': 'Jean',
                    'user_lastName': 'Dupont',
                    'user_email': 'test@example.com',
                    'is_event': 0,
                    'ISBN': '',
                    'offer_type': 'book',
                    'lien_offre_pcpro': 'http://localhost:3001/offres/AE?lieu=AE&structure=AE',
                    'departement': '75',
                    'nombre_resa': 2,
                    'env': '-development',
                    'contremarque': 'ACVSDC',
                    'users': [{'firstName': 'Jean',
                               'lastName': 'Dupont',
                               'email': 'test@example.com',
                               'contremarque': 'ACVSDC'},
                              {'firstName': 'Jaja',
                               'lastName': 'Dudu',
                               'email': 'mail@example.com',
                               'contremarque': 'TEST95'}
                              ]
                }
        }

    @patch('utils.mailing.IS_PROD', True)
    @clean_database
    def test_returns_email_with_link_to_the_corresponding_offer(self, app):
        # Given
        user = create_user(can_book_free_offers=True, departement_code='93', email='test@example.com',
                           first_name='Jean', last_name='Dupont', public_name='Test')

        offerer = create_offerer(idx=1)
        venue = create_venue(offerer, name='Test offerer', siret='89765389057043', idx=1,
                             departement_code='75', postal_code='75000')
        thing_offer = create_offer_with_thing_product(venue, thing_type=ThingType.LIVRE_EDITION,
                                                      booking_email='dev@passculture.app', idx=3)
        beginning_datetime = datetime(2019, 11, 6, 14, 00, 0, tzinfo=timezone.utc)
        stock = create_stock_from_offer(thing_offer, beginning_datetime=beginning_datetime, price=0, available=10)
        booking = create_booking(user=user, stock=stock, venue=venue, token='ACVSDC')
        stock.bookings = [booking]
        recipient = ['dev@passculture.app', ADMINISTRATION_EMAIL_ADDRESS]

        PcObject.save(stock)

        # When
        thing_offer.extraData = None

        email_data_template = retrieve_data_for_offerer_booking_recap_email(booking, recipient)

        # Then
        assert email_data_template == {
            'FromEmail': 'support@passculture.app',
            'MJ-TemplateID': 1095029,
            'MJ-TemplateLanguage': True,
            'To': f'dev@passculture.app',
            'Vars':
                {
                    'nom_offre': 'Test Book',
                    'nom_lieu': 'Test offerer',
                    'prix': 'Gratuit',
                    'date': '',
                    'heure': '',
                    'quantity': 1,
                    'user_firstName': 'Jean',
                    'user_lastName': 'Dupont',
                    'user_email': 'test@example.com',
                    'is_event': 0,
                    'ISBN': '',
                    'offer_type': 'book',
                    'lien_offre_pcpro': 'http://localhost:3001/offres/AM?lieu=AE&structure=AE',
                    'departement': '75',
                    'nombre_resa': 1,
                    'env': '',
                    'contremarque': 'ACVSDC',
                    'users': [{'firstName': 'Jean',
                               'lastName': 'Dupont',
                               'email': 'test@example.com',
                               'contremarque': 'ACVSDC'}]
                }
        }


class MakeOffererBookingRecapEmailAfterUserActionTest:
    @mocked_mail
    @clean_database
    def test_booking_recap_email_html_should_contain_all_bookings_information(app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer, name='Test offerer', address='123 rue test', postal_code='93000', city='Test city', departement_code='93')
        beginning_datetime = datetime(2019, 7, 20, 12, 0, 0)
        end_datetime = beginning_datetime + timedelta(hours=1)
        booking_limit_datetime = beginning_datetime - timedelta(hours=1)

        stock = create_stock_with_event_offer(offerer=None, venue=venue, event_type=EventType.SPECTACLE_VIVANT,
                                              offer_id=1,
                                              beginning_datetime=beginning_datetime, end_datetime=end_datetime,
                                              booking_limit_datetime=booking_limit_datetime)
        user = create_user(can_book_free_offers=True, departement_code='93', email='test@example.com',
                           first_name='First', last_name='Last', public_name='Test')
        booking = create_booking(user=user, stock=stock, venue=venue)
        booking.token = '56789'

        # When
        with patch('utils.mailing.booking_queries.find_ongoing_bookings_by_stock', return_value=[booking]):
            recap_email = make_offerer_booking_recap_email_after_user_action(booking)

        # Then
        email_html = _remove_whitespaces(recap_email['Html-part'])
        recap_email_soup = BeautifulSoup(email_html, 'html.parser')
        mail_greeting = recap_email_soup.find('p', {'id': 'mail-greeting'}).text
        action = recap_email_soup.find('p', {'id': 'action'}).text
        recap_table = recap_email_soup.find('table', {'id': 'recap-table'}).text
        recap = recap_email_soup.find('p', {'id': 'recap'}).text
        assert 'Cher partenaire pass Culture,' in mail_greeting
        assert 'First Last (test@example.com) vient de faire une nouvelle réservation.' in action
        assert 'Voici le récapitulatif des réservations à ce jour :' in recap
        assert '(total 1) pour Mains, sorts et papiers (Spectacle vivant) http://localhost:3001/offres/AE' in recap
        assert 'le 20 juillet 2019 à 14:00,' in recap
        assert 'proposé par Test offerer (Adresse : 123 rue test, 93000 Test city).' in recap
        assert 'Prénom' in recap_table
        assert 'Nom' in recap_table
        assert 'Email' in recap_table
        assert 'Code réservation' in recap_table
        assert 'First' in recap_table
        assert 'Last' in recap_table
        assert 'test@example.com' in recap_table
        assert '56789' in recap_table
        assert recap_email[
                   'Subject'] == '[Réservations 93] Nouvelle réservation pour Mains, sorts et papiers - 20 juillet 2019 à 14:00'

    @mocked_mail
    @clean_database
    def test_booking_recap_email_html_should_have_unsubscribe_option(app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer, name='Test offerer', address='123 rue test', postal_code='93000', city='Test city', departement_code='93')
        stock = create_stock_with_event_offer(offerer=None, venue=venue)
        user = create_user(can_book_free_offers=True, departement_code='93', email='test@example.com',
                           public_name='Test')
        booking = create_booking(user=user, stock=stock, venue=venue)
        booking.token = '56789'

        # When
        with patch('utils.mailing.booking_queries.find_ongoing_bookings_by_stock', return_value=[booking]):
            recap_email = make_offerer_booking_recap_email_after_user_action(booking)

        # Then
        email_html = _remove_whitespaces(recap_email['Html-part'])
        recap_email_soup = BeautifulSoup(email_html, 'html.parser')
        unsubscribe_option = recap_email_soup.find('p', {'id': 'unsubscribe-option'}).text
        change_email = recap_email_soup.find('a', {'id': 'change-email'})['href']
        remove_email = recap_email_soup.find('a', {'id': 'remove-email'})['href']
        assert 'Vous recevez ce message parce que votre adresse e-mail est renseignée comme adresse de contact sur votre offre.' in unsubscribe_option
        assert 'Si vous souhaitez modifier l’adresse de contact cliquez ici : être notifié des réservations à une autre adresse e-mail.' in unsubscribe_option
        assert 'Si vous ne souhaitez plus recevoir de notifications de réservations par e-mail, cliquez ici : ne plus recevoir les notifications de réservations.' in unsubscribe_option
        assert 'mailto:support@passculture.app?subject=Changer%20l%27adresse%20e-mail%20de%20notification%20des%20r%C3%A9servations' == \
               change_email
        assert 'mailto:support@passculture.app?subject=Ne%20plus%20recevoir%20les%20notifications%20de%20r%C3%A9servations' == \
               remove_email

    @mocked_mail
    @clean_database
    def test_booking_recap_email_html_should_not_retrieve_cancelled_or_used_bookings(app):
        # Given
        offerer = Offerer()
        venue = create_venue(offerer, name='Test offerer', address='123 rue test', postal_code='93000', city='Test city', departement_code='93')
        stock = create_stock_with_event_offer(offerer=Offerer(), venue=venue)

        user1 = create_user(can_book_free_offers=True, departement_code='93', email='test@example.com',
                            first_name='First1', last_name='Last1', public_name='Test1')
        booking1 = create_booking(user=user1, stock=stock)

        user2 = create_user(can_book_free_offers=True, departement_code='93', email='test@example.com',
                            first_name='First2', last_name='Last2', public_name='Test2')
        booking2 = create_booking(user=user2, stock=stock)

        ongoing_bookings = [booking1, booking2]

        # When
        with patch('utils.mailing.booking_queries.find_ongoing_bookings_by_stock', return_value=ongoing_bookings):
            recap_email = make_offerer_booking_recap_email_after_user_action(booking1)

        # Then
        email_html = BeautifulSoup(recap_email['Html-part'], 'html.parser')
        html_recap_table = str(email_html.find("table", {"id": "recap-table"}))
        assert '<td>First1</td>' in html_recap_table
        assert '<td>First2</td>' in html_recap_table
        assert '<td>Cancelled</td>' not in html_recap_table
        assert '<td>Used</td>' not in html_recap_table

    @mocked_mail
    @clean_database
    def test_offerer_recap_email_future_offer_when_new_booking_with_old_booking(app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer, name='Test offerer', address='123 rue test', postal_code='93000', city='Test city', departement_code='93')
        stock = create_stock_with_event_offer(offerer=None, venue=venue)
        user_1 = create_user(can_book_free_offers=True, departement_code='93', email='test@example.com',
                             first_name='John', last_name='Doe', public_name='Test')
        user_2 = create_user(can_book_free_offers=True, departement_code='93', email='test@example.com',
                             first_name='Jane', last_name='Doe', public_name='Test 2')
        user_2.email = 'other_test@example.com'
        booking_1 = create_booking(user=user_1, stock=stock, venue=venue)
        booking_1.token = '56789'
        booking_2 = create_booking(user=user_2, stock=stock, venue=venue)
        booking_2.token = '67890'

        # When
        with patch('utils.mailing.booking_queries.find_ongoing_bookings_by_stock', return_value=[booking_1, booking_2]):
            recap_email = make_offerer_booking_recap_email_after_user_action(booking_2)

        # Then
        email_html = _remove_whitespaces(recap_email['Html-part'])
        recap_email_soup = BeautifulSoup(email_html, 'html.parser')
        action_html = recap_email_soup.find('p', {'id': 'action'}).text
        recap_table_html = recap_email_soup.find('table', {'id': 'recap-table'}).text
        recap_html = recap_email_soup.find('p', {'id': 'recap'}).text
        assert 'Jane Doe (other_test@example.com) vient de faire une nouvelle réservation.' in action_html
        assert '(total 2) pour Mains, sorts et papiers' in recap_html
        assert 'John' in recap_table_html
        assert 'Jane' in recap_table_html
        assert 'test@example.com' in recap_table_html
        assert 'other_test@example.com' in recap_table_html
        assert '56789' in recap_table_html
        assert '67890' in recap_table_html

    @mocked_mail
    @clean_database
    def test_offerer_booking_recap_email_for_a_thing_offer_has_action_and_recap_html(app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer, name='Test offerer', address='123 rue test', postal_code='93000', city='Test city', departement_code='93')
        thing_offer = create_offer_with_thing_product(venue=None, thing_type=ThingType.AUDIOVISUEL)
        stock = create_stock_with_thing_offer(offerer=None, venue=venue, offer=thing_offer)
        stock.offer.id = 1
        user1 = create_user(can_book_free_offers=True, departement_code='93', email='test1@email.com',
                            first_name='Joe', last_name='Dalton', public_name='Test')
        user2 = create_user(can_book_free_offers=True, departement_code='93', email='test2@email.com',
                            first_name='Averell', last_name='Dalton', public_name='Test')
        booking1 = create_booking(user=user1, stock=stock, venue=venue, token='56789')
        booking2 = create_booking(user=user2, stock=stock, venue=venue, token='12345')

        # When
        with patch('utils.mailing.booking_queries.find_ongoing_bookings_by_stock', return_value=[booking1, booking2]):
            recap_email = make_offerer_booking_recap_email_after_user_action(booking1)

        # Then

        email_html = _remove_whitespaces(recap_email['Html-part'])
        recap_email_soup = BeautifulSoup(email_html, 'html.parser')
        recap_html = recap_email_soup.find("p", {"id": 'recap'}).text
        action_html = recap_email_soup.find("p", {"id": 'action'}).text
        assert 'Joe Dalton (test1@email.com) vient de faire une nouvelle réservation' in action_html
        assert 'Voici le récapitulatif des réservations à ce jour :' in recap_html
        assert '(total 2) pour Test Book' in recap_html
        assert '(Audiovisuel - films sur supports physiques et VOD)' in recap_html
        assert 'http://localhost:3001/offres/AE' in recap_html
        assert 'proposé par Test offerer (Adresse : 123 rue test, 93000 Test city).' in recap_html

    @mocked_mail
    @clean_database
    def test_offerer_booking_recap_email_thing_offer_has_recap_table(app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer, name='Test offerer', address='123 rue test', postal_code='93000', city='Test city', departement_code='93')
        thing_offer = create_offer_with_thing_product(venue=None, thing_type=ThingType.AUDIOVISUEL)
        stock = create_stock_with_thing_offer(offerer=None, venue=venue, offer=thing_offer)
        stock.offer.id = 1
        user1 = create_user(can_book_free_offers=True, departement_code='93', email='test1@email.com',
                            first_name='Joe', last_name='Dalton', public_name='Test')
        user2 = create_user(can_book_free_offers=True, departement_code='93', email='test2@email.com',
                            first_name='Averell', last_name='Dalton', public_name='Test')
        booking1 = create_booking(user=user1, stock=stock, venue=venue, token='56789')
        booking2 = create_booking(user=user2, stock=stock, venue=venue, token='12345')

        # When
        with patch('utils.mailing.booking_queries.find_ongoing_bookings_by_stock', return_value=[booking1, booking2]):
            recap_email = make_offerer_booking_recap_email_after_user_action(booking1)

        # Then

        email_html = _remove_whitespaces(recap_email['Html-part'])
        recap_email_soup = BeautifulSoup(email_html, 'html.parser')
        recap_table_html = recap_email_soup.find("table", {"id": 'recap-table'}).text
        assert 'Joe' in recap_table_html
        assert 'Averell' in recap_table_html
        assert 'test1@email.com' in recap_table_html
        assert 'test2@email.com' in recap_table_html

    @mocked_mail
    @clean_database
    def test_offerer_booking_recap_email_thing_offer_does_not_have_validation_tokens(app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer, name='Test offerer', address='123 rue test', postal_code='93000', city='Test city', departement_code='93')
        thing_offer = create_offer_with_thing_product(venue=None, thing_type=ThingType.AUDIOVISUEL)
        stock = create_stock_with_thing_offer(offerer=None, venue=venue, offer=thing_offer)
        stock.offer.id = 1
        user1 = create_user(can_book_free_offers=True, departement_code='93', email='test1@email.com',
                            first_name='Joe', last_name='Dalton', public_name='Test')
        user2 = create_user(can_book_free_offers=True, departement_code='93', email='test2@email.com',
                            first_name='Averell', last_name='Dalton', public_name='Test')
        booking1 = create_booking(user=user1, stock=stock, venue=venue, token='56789')
        booking2 = create_booking(user=user2, stock=stock, venue=venue, token='12345')

        # When
        with patch('utils.mailing.booking_queries.find_ongoing_bookings_by_stock', return_value=[booking1, booking2]):
            recap_email = make_offerer_booking_recap_email_after_user_action(booking1)

        # Then

        email_html = _remove_whitespaces(recap_email['Html-part'])
        recap_email_soup = BeautifulSoup(email_html, 'html.parser')
        recap_table_html = recap_email_soup.find("table", {"id": 'recap-table'}).text
        assert '12345' not in recap_table_html
        assert '56789' not in recap_table_html

    @freeze_time('2018-10-15 09:21:34')
    @clean_database
    def test_make_offerer_booking_recap_email_after_user_cancellation_for_physical_venue(app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer, name='Test offerer', address='123 rue test', postal_code='93000', city='Test city', departement_code='93')
        event_offer = create_offer_with_event_product(venue, event_name='Test Event')
        now = datetime.utcnow() + timedelta()
        event_occurrence = create_event_occurrence(event_offer, beginning_datetime=now)
        stock = create_stock_from_event_occurrence(event_occurrence, price=0)
        user_1 = create_user(departement_code='93', email='test1@email.com', first_name='John', last_name='Doe',
                             public_name='Test1')
        user_2 = create_user(departement_code='93', email='test2@email.com', first_name='Jane', last_name='Doe',
                             public_name='Test2')
        booking_1 = create_booking(user=user_1, stock=stock, venue=venue)
        booking_2 = create_booking(user=user_2, stock=stock, venue=venue)
        booking_2.isCancelled = True
        PcObject.save(booking_1, booking_2)

        # When
        with patch('utils.mailing.booking_queries.find_ongoing_bookings_by_stock', return_value=[booking_1]):
            recap_email = make_offerer_booking_recap_email_after_user_action(booking_2, is_cancellation=True)

        # Then
        email_html = _remove_whitespaces(recap_email['Html-part'])
        parsed_email = BeautifulSoup(email_html, 'html.parser')
        assert "<strong>Jane Doe</strong> (test2@email.com) vient d'annuler sa réservation." in str(
            parsed_email.find("p", {"id": "action"}))
        assert "Voici le récapitulatif des réservations à ce jour :" in str(parsed_email.find("p", {"id": "recap"}))
        assert "(total 1) pour Test Event" in str(parsed_email.find("p", {"id": "recap"}))
        assert "le 15 octobre 2018 à 11:21," in str(parsed_email.find("p", {"id": "recap"}))
        assert "proposé par Test offerer (Adresse : 123 rue test, 93000 Test city)." in str(
            parsed_email.find("p", {"id": "recap"}))
        assert "<td>John</td>" in str(parsed_email.find("table", {"id": "recap-table"}))
        assert "<td>Jane</td>" not in str(parsed_email.find("table", {"id": "recap-table"}))
        assert "<td>test1@email.com</td>" in str(parsed_email.find("table", {"id": "recap-table"}))
        assert "<td>{token}</td>".format(token=booking_1.token) in str(
            parsed_email.find("table", {"id": "recap-table"}))

    @freeze_time('2018-10-15 09:21:34')
    @clean_database
    def test_offerer_booking_recap_email_after_user_cancellation_should_have_unsubscribe_option(app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer, name='Test offerer', address='123 rue test', postal_code='93000', city='Test city', departement_code='93')
        event_offer = create_offer_with_event_product(venue, event_name='Test Event')
        now = datetime.utcnow() + timedelta()
        event_occurrence = create_event_occurrence(event_offer, beginning_datetime=now)
        stock = create_stock_from_event_occurrence(event_occurrence, price=0)
        user_1 = create_user(departement_code='93', email='test1@email.com', public_name='Test1')
        user_2 = create_user(departement_code='93', email='test2@email.com', public_name='Test2')
        booking_1 = create_booking(user=user_1, stock=stock, venue=venue)
        booking_2 = create_booking(user=user_2, stock=stock, venue=venue)
        booking_2.isCancelled = True
        PcObject.save(booking_1, booking_2)

        # When
        with patch('utils.mailing.booking_queries.find_ongoing_bookings_by_stock', return_value=[booking_1]):
            recap_email = make_offerer_booking_recap_email_after_user_action(booking_2, is_cancellation=True)

        # Then
        email_html = _remove_whitespaces(recap_email['Html-part'])
        parsed_email = BeautifulSoup(email_html, 'html.parser')

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

    @clean_database
    def test_booking_cancellation_email_of_thing_for_offerer_does_not_show_address_when_virtual_venue(app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer, name='Test offerer', is_virtual=True, siret=None,
                             postal_code=None,
                             departement_code=None, address=None)
        thing_offer = create_offer_with_thing_product(venue, thing_name='Test')
        stock = create_stock_from_offer(thing_offer, price=0)
        user_1 = create_user(departement_code='93', email='test1@email.com', public_name='Test1')
        user_2 = create_user(departement_code='93', email='test2@email.com', public_name='Test2')
        booking_1 = create_booking(user=user_1, stock=stock, venue=venue)
        booking_2 = create_booking(user=user_2, stock=stock, venue=venue)
        booking_2.isCancelled = True
        PcObject.save(booking_1, booking_2)

        # When
        with patch('utils.mailing.booking_queries.find_ongoing_bookings_by_stock', return_value=[booking_1]):
            recap_email = make_offerer_booking_recap_email_after_user_action(booking_2, is_cancellation=True)

            # Then
            email_html = BeautifulSoup(recap_email['Html-part'], 'html.parser')
        email_racap_html = email_html.find('p', {'id': 'recap'}).text
        assert 'Offre numérique proposée par Test offerer' in email_racap_html
        assert '(Adresse:' not in email_racap_html

    @clean_database
    def test_offerer_email_after_booking_cancellation_by_user_for_event_does_not_contain_address_when_venue_is_virtual(app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer, name='Test offerer', is_virtual=True, siret=None,
                             postal_code=None,
                             departement_code=None, address=None)
        event_offer = create_offer_with_event_product(venue, event_name='Test')
        event_occurrence = create_event_occurrence(event_offer, beginning_datetime=datetime.utcnow())
        stock = create_stock_from_event_occurrence(event_occurrence, price=0)
        user_1 = create_user(departement_code='93', email='test1@email.com', public_name='Test1')
        user_2 = create_user(departement_code='93', email='test2@email.com', public_name='Test2')
        booking_1 = create_booking(user=user_1, stock=stock, venue=venue)
        booking_2 = create_booking(user=user_2, stock=stock, venue=venue)
        booking_2.isCancelled = True
        PcObject.save(booking_1, booking_2)

        # When
        with patch('utils.mailing.booking_queries.find_ongoing_bookings_by_stock', return_value=[booking_1]):
            recap_email = make_offerer_booking_recap_email_after_user_action(booking_2, is_cancellation=True)

            # Then
            email_html = BeautifulSoup(recap_email['Html-part'], 'html.parser')
        assert 'Offre numérique proposée par Test offerer.' in str(email_html.find('p', {'id': 'recap'}))
        assert 'annuler sa réservation' in str(email_html.find('p', {'id': 'action'}))
        assert '(Adresse:' not in str(email_html.find('p', {'id': 'action'}))

    @clean_database
    def test_booking_cancellation_email_of_thing_for_offerer_contains_cancellation_subject_without_date(app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer, name='Test offerer')
        thing_offer = create_offer_with_thing_product(venue, thing_name='Test')
        stock = create_stock_from_offer(thing_offer, price=0)
        user_1 = create_user(departement_code='93', email='test1@email.com', public_name='Test1')
        user_2 = create_user(departement_code='93', email='test2@email.com', public_name='Test2')
        booking_1 = create_booking(user=user_1, stock=stock, venue=venue)
        booking_2 = create_booking(user=user_2, stock=stock, venue=venue)
        booking_2.isCancelled = True
        PcObject.save(booking_1, booking_2)

        # When
        with patch('utils.mailing.booking_queries.find_ongoing_bookings_by_stock', return_value=[booking_1]):
            recap_email = make_offerer_booking_recap_email_after_user_action(booking_2, is_cancellation=True)

        # Then
        assert recap_email['Subject'] == '[Réservations] Annulation de réservation pour Test'

    @freeze_time('2018-10-15 09:21:34')
    @clean_database
    def test_booking_cancellation_email_of_event_for_offerer_has_cancellation_subject_with_date(app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer, name='Test offerer')
        event_offer = create_offer_with_event_product(venue, event_name='Test')
        event_occurrence = create_event_occurrence(event_offer, beginning_datetime=datetime.utcnow())
        stock = create_stock_from_event_occurrence(event_occurrence, price=0)
        user_1 = create_user(departement_code='93', email='test1@email.com', public_name='Test1')
        user_2 = create_user(departement_code='93', email='test2@email.com', public_name='Test2')
        booking_1 = create_booking(user=user_1, stock=stock, venue=venue)
        booking_2 = create_booking(user=user_2, stock=stock, venue=venue)
        booking_2.isCancelled = True
        PcObject.save(booking_1, booking_2)

        # When
        with patch('utils.mailing.booking_queries.find_ongoing_bookings_by_stock', return_value=[booking_1]):
            recap_email = make_offerer_booking_recap_email_after_user_action(booking_2, is_cancellation=True)

        # Then
        assert recap_email['Subject'] == '[Réservations] Annulation de réservation pour Test - 15 octobre 2018 à 11:21'

    @clean_database
    def test_booking_cancellation_email_for_offerer_has_recap_information_but_no_token(app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer, name='Test offerer', is_virtual=True, siret=None)
        thing_offer = create_offer_with_thing_product(venue)
        stock = create_stock_from_offer(thing_offer, price=0)
        user_1 = create_user(departement_code='93', email='test1@email.com', first_name='Jane', last_name='Doe',
                             public_name='Test1')
        user_2 = create_user(departement_code='93', email='test2@email.com', first_name='Lucy', last_name='Smith',
                             public_name='Test2')
        booking_1 = create_booking(user=user_1, stock=stock, venue=venue, token='12345')
        booking_2 = create_booking(user=user_2, stock=stock, venue=venue, token='56789')
        booking_2.isCancelled = True
        PcObject.save(booking_1, booking_2)

        # When
        with patch('utils.mailing.booking_queries.find_ongoing_bookings_by_stock', return_value=[booking_1]):
            recap_email = make_offerer_booking_recap_email_after_user_action(booking_2, is_cancellation=True)

        # Then
        email_html = BeautifulSoup(recap_email['Html-part'], 'html.parser')
        recap_table_html = email_html.find('table', {'id': 'recap-table'}).text
        assert 'Jane' in recap_table_html
        assert 'Lucy' not in recap_table_html
        assert 'test1@email.com' in recap_table_html
        assert 'test2@email.com' not in recap_table_html
        assert '12345' not in recap_table_html
        assert '56789' not in recap_table_html
