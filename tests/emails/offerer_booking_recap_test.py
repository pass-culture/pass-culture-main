from datetime import datetime, timezone
from unittest.mock import patch

from domain.booking.booking import Booking
from domain.stock.stock import Stock
from emails.offerer_booking_recap import retrieve_data_for_offerer_booking_recap_email
from models import ThingType
from repository import repository
from tests.conftest import clean_database
from tests.domain_creators.generic_creators import create_domain_beneficiary
from model_creators.generic_creators import create_booking, create_user, create_offerer, create_venue, \
    create_deposit, create_stock
from model_creators.specific_creators import create_stock_from_offer, create_product_with_thing_type, \
    create_offer_with_thing_product, create_offer_with_event_product


class MakeOffererBookingRecapEmailWithMailjetTemplateTest:
    @patch('emails.offerer_booking_recap.SUPPORT_EMAIL_ADDRESS', 'support@example.com')
    @patch('utils.mailing.DEV_EMAIL_ADDRESS', 'dev@example.com')
    @clean_database
    def test_should_write_email_with_right_data_when_offer_is_an_event(self, app):
        # Given
        user_sql_entity = create_user(idx=1, email='test@example.com', first_name='John', last_name='Doe')
        offerer = create_offerer(idx=1)
        venue = create_venue(offerer, name='Test offerer', idx=1, postal_code='75000')
        event_offer = create_offer_with_event_product(venue, idx=1)
        beginning_datetime = datetime(2019, 11, 6, 14, 59, 5, tzinfo=timezone.utc)
        stock_sql_entity = create_stock(beginning_datetime=beginning_datetime, idx=1, offer=event_offer, price=0)
        booking_sql_entity = create_booking(idx=1, user=user_sql_entity, stock=stock_sql_entity, venue=venue,
                                            token='ABC123')
        repository.save(booking_sql_entity)

        user = create_domain_beneficiary(identifier=1, email='test@example.com', first_name='John', last_name='Doe')
        stock = Stock(
            identifier=1,
            quantity=None,
            offer=event_offer,
            price=0,
            beginning_datetime=beginning_datetime,
        )
        booking = Booking(identifier=1, beneficiary=user, stock=stock, amount=0, quantity=1, token='ABC123')

        recipient = ['initial_recipient@example.com']
        stock.bookings = [booking]

        # When
        email = retrieve_data_for_offerer_booking_recap_email(booking, recipient)

        # Then
        assert email == {
            'FromEmail': 'support@example.com',
            'MJ-TemplateID': 1095029,
            'MJ-TemplateLanguage': True,
            'To': 'dev@example.com',
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

    @patch('emails.offerer_booking_recap.SUPPORT_EMAIL_ADDRESS', 'support@example.com')
    @patch('utils.mailing.DEV_EMAIL_ADDRESS', 'dev@example.com')
    @clean_database
    def test_should_write_email_with_right_data_when_offer_is_a_book(self, app):
        # Given
        user = create_user(idx=1, email='test@example.com', first_name='John', last_name='Doe')
        offerer = create_offerer(idx=1)
        extra_data = {'isbn': '123456789'}
        venue = create_venue(offerer, name='Test offerer', is_virtual=True, siret=None, idx=1)

        thing_product = create_product_with_thing_type(thing_name='Le récit de voyage', extra_data=extra_data)
        event_offer = create_offer_with_thing_product(venue=venue, product=thing_product, idx=1)
        stock = create_stock(idx=1, offer=event_offer, price=0)
        booking = create_booking(idx=1, user=user, stock=stock, venue=venue, token='ABC123')
        repository.save(booking)

        user = create_domain_beneficiary(identifier=1, email='test@example.com', first_name='John', last_name='Doe')
        stock = Stock(
            identifier=1,
            quantity=None,
            offer=event_offer,
            price=0,
        )
        booking = Booking(identifier=1, beneficiary=user, stock=stock, amount=0, quantity=1, token='ABC123')
        stock.bookings = [booking]

        # When
        email = retrieve_data_for_offerer_booking_recap_email(booking, [])

        # Then
        assert email == {
            'FromEmail': 'support@example.com',
            'MJ-TemplateID': 1095029,
            'MJ-TemplateLanguage': True,
            'To': 'dev@example.com',
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
                    'quantity': 1,
                    'offer_type': 'book',
                    'departement': 'numérique',
                    'users': [{'firstName': 'John',
                               'lastName': 'Doe',
                               'email': 'test@example.com',
                               'contremarque': 'ABC123'}]
                }
        }

    @patch('emails.offerer_booking_recap.SUPPORT_EMAIL_ADDRESS', 'support@example.com')
    @patch('utils.mailing.DEV_EMAIL_ADDRESS', 'dev@example.com')
    @clean_database
    def test_should_not_truncate_price(self, app):
        # Given
        user_sql_entity = create_user(idx=1, email='test@example.com', first_name='John', last_name='Doe')
        offerer = create_offerer(idx=1)
        deposit = create_deposit(user_sql_entity, amount=50, source='public')
        venue = create_venue(offerer, name='Test offerer', idx=1, postal_code='75000')
        event_offer = create_offer_with_event_product(venue, is_duo=True, idx=1)
        beginning_datetime = datetime(2019, 11, 6, 14, 00, 0, tzinfo=timezone.utc)
        stock_sql_entity = create_stock(beginning_datetime=beginning_datetime, idx=1, offer=event_offer, price=5.86)
        booking_sql_entity = create_booking(idx=1, user=user_sql_entity, stock=stock_sql_entity, venue=venue,
                                            token='ABC123')
        repository.save(deposit, booking_sql_entity)

        user = create_domain_beneficiary(identifier=1, email='test@example.com', first_name='John', last_name='Doe',
                                         wallet_balance=50)
        stock = Stock(
            identifier=1,
            quantity=None,
            offer=event_offer,
            price=5.86,
            beginning_datetime=beginning_datetime
        )
        booking = Booking(identifier=1, beneficiary=user, stock=stock, amount=0, quantity=1, token='ABC123')
        stock.bookings = [booking]

        # When
        email = retrieve_data_for_offerer_booking_recap_email(booking, [])

        # Then
        assert email == {
            'FromEmail': 'support@example.com',
            'MJ-TemplateID': 1095029,
            'MJ-TemplateLanguage': True,
            'To': 'dev@example.com',
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

    @patch('emails.offerer_booking_recap.SUPPORT_EMAIL_ADDRESS', 'support@example.com')
    @patch('utils.mailing.DEV_EMAIL_ADDRESS', 'dev@example.com')
    @clean_database
    def test_returns_empty_ISBN_when_no_extra_data(self, app):
        # Given
        user_sql_entity = create_user(idx=1, email='test@example.com', first_name='John', last_name='Doe')
        offerer = create_offerer(idx=1)
        venue = create_venue(offerer, name='Test offerer', is_virtual=True, siret=None, idx=1)
        thing_offer = create_offer_with_thing_product(venue, thing_type=ThingType.LIVRE_EDITION, idx=1)
        thing_offer.extraData = None
        beginning_datetime = datetime(2019, 11, 6, 14, 00, 0, tzinfo=timezone.utc)
        stock_sql_entity = create_stock(beginning_datetime=beginning_datetime, idx=1, offer=thing_offer, price=0)
        booking_sql_entity = create_booking(idx=1, user=user_sql_entity, stock=stock_sql_entity, venue=venue,
                                            token='ABC123')
        repository.save(booking_sql_entity)

        user = create_domain_beneficiary(identifier=1, email='test@example.com', first_name='John', last_name='Doe')
        stock = Stock(
            identifier=1,
            quantity=None,
            offer=thing_offer,
            price=0,
            beginning_datetime=beginning_datetime
        )
        booking = Booking(identifier=1, beneficiary=user, stock=stock, amount=0, quantity=1, token='ABC123')
        stock.bookings = [booking]

        # When
        email_data_template = retrieve_data_for_offerer_booking_recap_email(booking, [])

        # Then
        assert email_data_template == {
            'FromEmail': 'support@example.com',
            'MJ-TemplateID': 1095029,
            'MJ-TemplateLanguage': True,
            'To': 'dev@example.com',
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

    @patch('emails.offerer_booking_recap.SUPPORT_EMAIL_ADDRESS', 'support@example.com')
    @patch('utils.mailing.DEV_EMAIL_ADDRESS', 'dev@example.com')
    @clean_database
    def test_returns_empty_ISBN_when_extra_data_has_no_key_isbn(self, app):
        # Given
        user_sql_entity = create_user(idx=1, email="test@example.com", first_name='John', last_name='Doe')
        offerer = create_offerer(idx=1)
        venue = create_venue(offerer, name='Test offerer', is_virtual=True, siret=None, idx=1)
        thing_offer = create_offer_with_thing_product(venue, thing_type=ThingType.LIVRE_EDITION, idx=1)
        beginning_datetime = datetime(2019, 11, 6, 14, 00, 0, tzinfo=timezone.utc)
        stock_sql_entity = create_stock(beginning_datetime=beginning_datetime, idx=1, offer=thing_offer, price=0)
        booking_sql_entity = create_booking(idx=1, user=user_sql_entity, stock=stock_sql_entity, venue=venue,
                                            token='ABC123')

        repository.save(booking_sql_entity)

        user = create_domain_beneficiary(identifier=1, email='test@example.com', first_name='John', last_name='Doe')
        stock = Stock(
            identifier=1,
            quantity=None,
            offer=thing_offer,
            price=0,
            beginning_datetime=beginning_datetime
        )
        booking = Booking(identifier=1, beneficiary=user, stock=stock, amount=0, quantity=1, token='ABC123')
        stock.bookings = [booking]

        # When
        thing_offer.extraData = {}
        email_data_template = retrieve_data_for_offerer_booking_recap_email(booking, [])

        # Then
        assert email_data_template == {
            'FromEmail': 'support@example.com',
            'MJ-TemplateID': 1095029,
            'MJ-TemplateLanguage': True,
            'To': 'dev@example.com',
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

    @patch('emails.offerer_booking_recap.SUPPORT_EMAIL_ADDRESS', 'support@example.com')
    @patch('repository.feature_queries.IS_PROD', True)
    @clean_database
    def test_returns_recipients_email_when_production_environment(self, app):
        # Given
        user_sql_entity = create_user(email='test@example.com', first_name='John', last_name='Doe')
        offerer = create_offerer(idx=1)
        venue = create_venue(offerer, name='Test offerer', idx=1, postal_code='75000')
        thing_offer = create_offer_with_thing_product(venue, thing_type=ThingType.LIVRE_EDITION, idx=1)
        beginning_datetime = datetime(2019, 11, 6, 14, 00, 0, tzinfo=timezone.utc)
        stock_sql_entity = create_stock_from_offer(thing_offer, beginning_datetime=beginning_datetime, price=0)
        booking_sql_entity = create_booking(user=user_sql_entity, stock=stock_sql_entity, venue=venue, token='ABC123')

        repository.save(booking_sql_entity)

        user = create_domain_beneficiary(identifier=1, email='test@example.com', first_name='John', last_name='Doe')
        stock = Stock(
            identifier=1,
            quantity=None,
            offer=thing_offer,
            price=0,
            beginning_datetime=beginning_datetime
        )
        booking = Booking(identifier=1, beneficiary=user, stock=stock, amount=0, quantity=1, token='ABC123')
        stock.bookings = [booking]

        recipients = ['dev@example.com', 'administration@example.com']

        # When
        email_data_template = retrieve_data_for_offerer_booking_recap_email(booking, recipients)

        # Then
        assert email_data_template.get('To') == ', '.join(recipients)

    @patch('emails.offerer_booking_recap.SUPPORT_EMAIL_ADDRESS', 'support@example.com')
    @patch('utils.mailing.DEV_EMAIL_ADDRESS', 'dev@example.com')
    @clean_database
    def test_returns_dev_email_adress_when_feature_send_mail_to_users_disabled(self, app):
        # Given
        user_sql_entity = create_user(idx=1, email='test@example.com', first_name='John', last_name='Doe')
        offerer = create_offerer(idx=1)
        venue = create_venue(offerer, name='Test offerer', idx=1, postal_code='75000')
        thing_offer = create_offer_with_thing_product(venue, thing_type=ThingType.LIVRE_EDITION, idx=1)
        beginning_datetime = datetime(2019, 11, 6, 14, 00, 0, tzinfo=timezone.utc)
        stock_sql_entity = create_stock(beginning_datetime=beginning_datetime, idx=1, offer=thing_offer, price=0)
        booking_sql_entity = create_booking(idx=1, user=user_sql_entity, stock=stock_sql_entity, venue=venue,
                                            token='ABC123')

        repository.save(booking_sql_entity)

        user = create_domain_beneficiary(identifier=1, email='test@example.com', first_name='John', last_name='Doe')
        stock = Stock(
            identifier=1,
            quantity=None,
            offer=thing_offer,
            price=0,
            beginning_datetime=beginning_datetime
        )
        booking = Booking(identifier=1, beneficiary=user, stock=stock, amount=0, quantity=1, token='ABC123')
        stock.bookings = [booking]

        recipients = ['dev@example.com', 'administration@example.com']

        # When
        email_data_template = retrieve_data_for_offerer_booking_recap_email(booking, recipients)

        # Then
        assert email_data_template.get('To') != ', '.join(recipients)
        assert email_data_template.get('To') == 'dev@example.com'

    @patch('emails.offerer_booking_recap.SUPPORT_EMAIL_ADDRESS', 'support@example.com')
    @patch('utils.mailing.DEV_EMAIL_ADDRESS', 'dev@example.com')
    @clean_database
    def test_returns_email_with_correct_data_when_two_users_book_the_same_offer(self, app):
        # Given
        user_sql_entity_1 = create_user(idx=1, email='test@example.com', first_name='Jean', last_name='Dupont')
        user_sql_entity_2 = create_user(idx=2, email='mail@example.com', first_name='Jaja', last_name='Dudu')
        offerer = create_offerer(idx=1)
        venue = create_venue(offerer, idx=1, postal_code='75000')
        thing_offer = create_offer_with_thing_product(venue, thing_type=ThingType.LIVRE_EDITION, idx=1)
        beginning_datetime = datetime(2019, 11, 6, 14, 00, 0, tzinfo=timezone.utc)
        stock_sql_entity = create_stock(beginning_datetime=beginning_datetime, idx=1, offer=thing_offer, price=0)
        booking_sql_entity_1 = create_booking(idx=1, user=user_sql_entity_1, stock=stock_sql_entity, venue=venue,
                                              token='ACVSDC')
        booking_sql_entity_2 = create_booking(idx=2, user=user_sql_entity_2, stock=stock_sql_entity, venue=venue,
                                              token='TEST95')

        repository.save(booking_sql_entity_1, booking_sql_entity_2)

        user1 = create_domain_beneficiary(identifier=1, email='test@example.com', first_name='Jean', last_name='Dupont')
        user2 = create_domain_beneficiary(identifier=2, email='mail@example.com', first_name='Jaja', last_name='Dudu')
        stock = Stock(
            identifier=1,
            quantity=None,
            offer=thing_offer,
            price=0,
            beginning_datetime=beginning_datetime
        )
        booking1 = Booking(identifier=1, beneficiary=user1, stock=stock, amount=0, quantity=1, token='ACVSDC')
        booking2 = Booking(identifier=2, beneficiary=user2, stock=stock, amount=0, quantity=1, token='TEST95')
        stock.bookings = [booking1, booking2]

        # When
        email_data_template = retrieve_data_for_offerer_booking_recap_email(booking1, [])

        # Then
        email_data_template_users = email_data_template.get('Vars').get('users')
        user_jean_dupont = {'firstName': 'Jean',
                            'lastName': 'Dupont',
                            'email': 'test@example.com',
                            'contremarque': 'ACVSDC'}
        user_jaja_dudu = {'firstName': 'Jaja',
                          'lastName': 'Dudu',
                          'email': 'mail@example.com',
                          'contremarque': 'TEST95'}
        assert user_jean_dupont in email_data_template_users
        assert user_jaja_dudu in email_data_template_users

    @patch('emails.offerer_booking_recap.SUPPORT_EMAIL_ADDRESS', 'support@example.com')
    @patch('utils.mailing.DEV_EMAIL_ADDRESS', 'dev@example.com')
    @clean_database
    def test_returns_email_with_link_to_the_corresponding_offer(self, app):
        # Given
        user_sql_entity = create_user(idx=1, email='test@example.com', first_name='Jean', last_name='Dupont')
        offerer = create_offerer(idx=1)
        venue = create_venue(offerer, name='Test offerer', idx=1, postal_code='75000')
        thing_offer = create_offer_with_thing_product(venue, thing_type=ThingType.LIVRE_EDITION, idx=3)
        beginning_datetime = datetime(2019, 11, 6, 14, 00, 0, tzinfo=timezone.utc)
        stock_sql_entity = create_stock(beginning_datetime=beginning_datetime, idx=1, offer=thing_offer, price=0)
        booking_sql_entity = create_booking(idx=1, user=user_sql_entity, stock=stock_sql_entity, venue=venue,
                                            token='ACVSDC')
        repository.save(booking_sql_entity)

        user = create_domain_beneficiary(identifier=1, email='test@example.com', first_name='Jean', last_name='Dupont')
        stock = Stock(
            identifier=1,
            quantity=None,
            offer=thing_offer,
            price=0,
            beginning_datetime=beginning_datetime
        )
        booking = Booking(identifier=1, beneficiary=user, stock=stock, amount=0, quantity=1, token='ACVSDC')
        stock.bookings = [booking]

        # When
        email_data_template = retrieve_data_for_offerer_booking_recap_email(booking, [])

        # Then
        assert email_data_template \
                   .get('Vars') \
                   .get('lien_offre_pcpro') == 'http://localhost:3001/offres/AM?lieu=AE&structure=AE'
