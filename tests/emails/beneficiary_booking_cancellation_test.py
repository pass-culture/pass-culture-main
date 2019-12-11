from datetime import datetime
from unittest.mock import patch

from freezegun import freeze_time

from emails.beneficiary_booking_cancellation import \
    make_beneficiary_booking_cancellation_email_data
from tests.test_utils import create_booking, create_offer_with_event_product, \
    create_offer_with_thing_product, \
    create_recommendation, create_stock_from_offer, \
    create_user, create_offerer, create_venue


class MakeBeneficiaryBookingCancellationEmailDataTest:
    @patch('emails.beneficiary_booking_cancellation.SUPPORT_EMAIL_ADDRESS', 'support@example.com')
    @patch('emails.beneficiary_booking_cancellation.format_environment_for_email', return_value='')
    def test_should_return_thing_data_when_booking_is_a_thing(self, mock_format_environment_for_email):
        # Given
        beneficiary = create_user(first_name='Fabien', email='fabien@example.com')
        thing_offer = create_offer_with_thing_product(venue=None, thing_name='Test thing name', idx=123456)
        recommendation = create_recommendation(offer=thing_offer, user=beneficiary)
        recommendation.mediationId = 36
        stock = create_stock_from_offer(offer=thing_offer, price=10.2)
        booking = create_booking(beneficiary, stock=stock, recommendation=recommendation, is_cancelled=1)

        # When
        email_data = make_beneficiary_booking_cancellation_email_data(booking)

        # Then
        assert email_data == {
            'FromEmail': 'support@example.com',
            'Mj-TemplateID': 1091464,
            'Mj-TemplateLanguage': True,
            'To': 'fabien@example.com',
            'Vars': {
                'env': '',
                'event_date': '',
                'event_hour': '',
                'is_event': 0,
                'is_free_offer': '0',
                'mediation_id': 36,
                'offer_id': 'AHREA',
                'offer_name': 'Test thing name',
                'offer_price': '10.2',
                'user_first_name': 'Fabien',
            },
        }

    @freeze_time('2019-11-26 18:29:20.891028')
    @patch('emails.beneficiary_booking_cancellation.SUPPORT_EMAIL_ADDRESS', 'support@example.com')
    @patch('emails.beneficiary_booking_cancellation.format_environment_for_email', return_value='-testing')
    def test_should_return_event_data_when_booking_is_an_event(self, mock_format_environment_for_email):
        # Given
        venue = create_venue(create_offerer())
        beneficiary = create_user(first_name='Fabien', email='fabien@example.com')
        event_offer = create_offer_with_event_product(venue, event_name='Test event name', idx=123456)
        recommendation = create_recommendation(offer=event_offer, user=beneficiary)
        recommendation.mediationId = 36
        stock = create_stock_from_offer(offer=event_offer, price=10.2, beginning_datetime=datetime.utcnow())
        booking = create_booking(beneficiary, stock=stock, recommendation=recommendation, is_cancelled=1)

        # When
        email_data = make_beneficiary_booking_cancellation_email_data(booking)

        # Then
        assert email_data == {
            'FromEmail': 'support@example.com',
            'Mj-TemplateID': 1091464,
            'Mj-TemplateLanguage': True,
            'To': 'fabien@example.com',
            'Vars': {
                'env': '-testing',
                'event_date': '26 novembre',
                'event_hour': '19h29',
                'is_event': 1,
                'is_free_offer': '0',
                'mediation_id': 36,
                'offer_id': 'AHREA',
                'offer_name': 'Test event name',
                'offer_price': '10.2',
                'user_first_name': 'Fabien',
            },
        }

    def test_should_return_its_free_offer_when_offer_price_equals_to_zero(self):
        # Given
        beneficiary = create_user()
        thing_offer = create_offer_with_thing_product(venue=None)
        recommendation = create_recommendation()
        recommendation.mediationId = 36
        stock = create_stock_from_offer(offer=thing_offer, price=0)
        booking = create_booking(beneficiary, stock=stock, recommendation=recommendation, is_cancelled=1)

        # When
        email_data = make_beneficiary_booking_cancellation_email_data(booking)

        # Then
        assert email_data['Vars']['is_free_offer'] == '1'

    def test_should_return_empty_mediation_id_when_no_mediation(self):
        # Given
        beneficiary = create_user()
        thing_offer = create_offer_with_thing_product(venue=None)
        recommendation = create_recommendation()
        stock = create_stock_from_offer(offer=thing_offer)
        booking = create_booking(beneficiary, stock=stock, recommendation=recommendation, is_cancelled=1)

        # When
        email_data = make_beneficiary_booking_cancellation_email_data(booking)

        # Then
        assert email_data['Vars']['mediation_id'] == 'vide'

    def test_should_return_the_price_multiplied_by_quantity_when_it_is_a_duo_offer(self):
        # Given
        beneficiary = create_user()
        thing_offer = create_offer_with_thing_product(venue=None)
        recommendation = create_recommendation()
        stock = create_stock_from_offer(offer=thing_offer, price=10)
        booking = create_booking(beneficiary, stock=stock, recommendation=recommendation, is_cancelled=1, quantity=2)

        # When
        email_data = make_beneficiary_booking_cancellation_email_data(booking)

        # Then
        assert email_data['Vars']['offer_price'] == '20'
