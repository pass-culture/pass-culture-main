from datetime import datetime
from unittest.mock import patch

from emails.offerer_bookings_recap_after_deleting_stock import \
    retrieve_offerer_bookings_recap_email_data_after_offerer_cancellation
from tests.model_creators.generic_creators import create_user, create_offerer, create_venue, create_booking
from tests.model_creators.specific_creators import create_offer_with_event_product, create_event_occurrence, \
    create_stock_from_event_occurrence, create_product_with_thing_type, create_offer_with_thing_product, \
    create_stock_from_offer


class RetrieveOffererBookingsRecapEmailDataAfterOffererCancellationTest:
    @patch('emails.offerer_bookings_recap_after_deleting_stock.DEV_EMAIL_ADDRESS', 'dev@example.com')
    @patch('emails.offerer_bookings_recap_after_deleting_stock.feature_send_mail_to_users_enabled', return_value=False)
    def test_should_send_mail_to_pass_culture_dev_when_feature_send_mail_to_users_is_disabled(self,
                                                                                              feature_send_mail_to_users_enabled):
        # Given
        user = create_user()
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_event_product(venue)
        event_occurrence = create_event_occurrence(offer)
        stock = create_stock_from_event_occurrence(event_occurrence)
        booking = create_booking(user=user, stock=stock)
        bookings = [booking]
        recipients = 'administration@example.com, fake_email@example.com'

        # When
        mailjet_data = retrieve_offerer_bookings_recap_email_data_after_offerer_cancellation(bookings, recipients)

        # Then
        assert mailjet_data['To'] == 'dev@example.com'

    @patch('emails.offerer_bookings_recap_after_deleting_stock.feature_send_mail_to_users_enabled', return_value=True)
    def test_should_send_mail_to_offerer_and_pass_culture_administration_when_feature_send_mail_to_users_is_enabled(
            self,
            feature_send_mail_to_users_enabled):
        # Given
        user = create_user()
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_event_product(venue)
        event_occurrence = create_event_occurrence(offer)
        stock = create_stock_from_event_occurrence(event_occurrence)
        booking = create_booking(user=user, stock=stock)
        bookings = [booking]
        recipients = 'administration@example.com, offerer@example.com'

        # When
        mailjet_data = retrieve_offerer_bookings_recap_email_data_after_offerer_cancellation(bookings, recipients)

        # Then
        assert mailjet_data['To'] == 'administration@example.com, offerer@example.com'

    @patch('emails.offerer_bookings_recap_after_deleting_stock.SUPPORT_EMAIL_ADDRESS', 'support@example.com')
    @patch('emails.offerer_bookings_recap_after_deleting_stock.format_environment_for_email', return_value='')
    @patch('emails.offerer_bookings_recap_after_deleting_stock.build_pc_pro_offer_link',
           return_value='http://pc_pro.com/offer_link')
    @patch('emails.offerer_bookings_recap_after_deleting_stock.feature_send_mail_to_users_enabled', return_value=True)
    def test_should_return_mailjet_data_with_correct_information_when_offer_is_an_event(self,
                                                                                        format_environment_for_email,
                                                                                        build_pc_pro_offer_link,
                                                                                        feature_send_mail_to_users_enabled):
        # Given
        user = create_user(public_name='John Doe', first_name='John', last_name='Doe', email='john@example.com')
        offerer = create_offerer()
        venue = create_venue(offerer, name='Venue name')
        offer = create_offer_with_event_product(venue, event_name='My Event')
        stock = create_stock_from_offer(offer, price=12.52, beginning_datetime=datetime(2019, 10, 9, 10, 20, 00))
        booking = create_booking(user, stock=stock, venue=venue, quantity=2, token='12345')
        bookings = [booking]
        recipients = 'administration@example.com, offerer@example.com'

        # When
        mailjet_data = retrieve_offerer_bookings_recap_email_data_after_offerer_cancellation(bookings, recipients)

        # Then
        assert mailjet_data == {
            'FromEmail': 'support@example.com',
            'MJ-TemplateID': 1116333,
            'MJ-TemplateLanguage': True,
            'To': 'administration@example.com, offerer@example.com',
            'Vars': {
                'offer_name': 'My Event',
                'lien_offre_pcpro': 'http://pc_pro.com/offer_link',
                'venue_name': 'Venue name',
                'price': '12.52',
                'is_event': 1,
                'event_date': '09-Oct-2019',
                'event_hour': '12h20',
                'quantity': 2,
                'reservations_number': 1,
                'env': '',
                'users': [{'countermark': '12345',
                           'email': 'john@example.com',
                           'firstName': 'John',
                           'lastName': 'Doe'}],
            }
        }

    @patch('emails.offerer_bookings_recap_after_deleting_stock.SUPPORT_EMAIL_ADDRESS', 'support@example.com')
    @patch('emails.offerer_bookings_recap_after_deleting_stock.DEV_EMAIL_ADDRESS', 'dev@example.com')
    @patch('emails.offerer_bookings_recap_after_deleting_stock.format_environment_for_email', return_value='-testing')
    @patch('emails.offerer_bookings_recap_after_deleting_stock.build_pc_pro_offer_link',
           return_value='http://pc_pro.com/offer_link')
    @patch('emails.offerer_bookings_recap_after_deleting_stock.feature_send_mail_to_users_enabled', return_value=False)
    def test_should_return_mailjet_data_when_multiple_bookings_and_offer_is_a_thing(self, format_environment_for_email,
                                                                                    build_pc_pro_offer_link,
                                                                                    feature_send_mail_to_users_enabled):
        # Given
        user = create_user(public_name='John Doe', first_name='John', last_name='Doe', email='john@example.com')
        offerer = create_offerer()
        venue = create_venue(offerer, name='La petite librairie', public_name='La grande librairie')
        thing_product = create_product_with_thing_type(thing_name='Le récit de voyage')
        offer = create_offer_with_thing_product(venue=venue, product=thing_product)
        stock = create_stock_from_offer(offer, price=0)
        booking = create_booking(user=user, stock=stock, token='12346', quantity=6)

        user2 = create_user(public_name='James Bond', first_name='James', last_name='Bond', email='bond@example.com')
        booking2 = create_booking(user=user2, stock=stock, token='12345')
        recipients = 'administration@example.com, fake_email@example.com'
        bookings = [booking, booking2]

        # When
        mailjet_data = retrieve_offerer_bookings_recap_email_data_after_offerer_cancellation(bookings, recipients)

        # Then
        assert mailjet_data == {
            'FromEmail': 'support@example.com',
            'MJ-TemplateID': 1116333,
            'MJ-TemplateLanguage': True,
            'To': 'dev@example.com',
            'Vars': {
                'offer_name': 'Le récit de voyage',
                'lien_offre_pcpro': 'http://pc_pro.com/offer_link',
                'venue_name': 'La grande librairie',
                'price': 'Gratuit',
                'is_event': 0,
                'event_date': '',
                'event_hour': '',
                'quantity': 7,
                'reservations_number': 2,
                'env': '-testing',
                'users': [{'countermark': '12346',
                           'email': 'john@example.com',
                           'firstName': 'John',
                           'lastName': 'Doe'},
                          {'countermark': '12345',
                           'email': 'bond@example.com',
                           'firstName': 'James',
                           'lastName': 'Bond'}]
            }
        }
