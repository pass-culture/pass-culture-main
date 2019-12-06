from datetime import datetime, timedelta, timezone
from unittest.mock import patch

from emails.beneficiary_warning_after_pro_booking_cancellation import \
    retrieve_data_to_warn_beneficiary_after_pro_booking_cancellation
from tests.test_utils import create_booking, create_stock_from_event_occurrence, create_event_occurrence, \
    create_offer_with_event_product, create_venue, create_offerer, create_user, create_offer_with_thing_product, \
    create_stock_from_offer


class RetrieveDataToWarnBeneficiaryAfterProBookingCancellationTest:
    @patch('emails.beneficiary_warning_after_pro_booking_cancellation.feature_send_mail_to_users_enabled', return_value=True)
    def test_should_send_mail_to_user_when_feature_send_mail_to_users_is_enabled(self, feature_send_mail_to_users_enabled):
        # Given
        user = create_user()
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_event_product(venue)
        event_occurrence = create_event_occurrence(offer)
        stock = create_stock_from_event_occurrence(event_occurrence)
        booking = create_booking(user, stock)

        # When
        mailjet_data = retrieve_data_to_warn_beneficiary_after_pro_booking_cancellation(booking)

        # Then
        assert mailjet_data['To'] == user.email

    @patch('emails.beneficiary_warning_after_pro_booking_cancellation.DEV_EMAIL_ADDRESS', 'dev@example.com')
    @patch('emails.beneficiary_warning_after_pro_booking_cancellation.feature_send_mail_to_users_enabled', return_value=False)
    def test_should_send_mail_to_dev_when_feature_send_mail_to_users_is_disabled(self, feature_send_mail_to_users_enabled):
        # Given
        user = create_user()
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_event_product(venue)
        event_occurrence = create_event_occurrence(offer)
        stock = create_stock_from_event_occurrence(event_occurrence)
        booking = create_booking(user, stock)

        # When
        mailjet_data = retrieve_data_to_warn_beneficiary_after_pro_booking_cancellation(booking)

        # Then
        assert mailjet_data['To'] == 'dev@example.com'

    @patch('emails.beneficiary_warning_after_pro_booking_cancellation.SUPPORT_EMAIL_ADDRESS', 'support@example.com')
    @patch('emails.beneficiary_warning_after_pro_booking_cancellation.DEV_EMAIL_ADDRESS', 'dev@example.com')
    def test_should_return_event_data_when_booking_is_on_an_event(self):
        # Given
        beginning_datetime = datetime(2019, 7, 20, 12, 0, 0, tzinfo=timezone.utc)

        user = create_user()
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_event_product(venue)
        event_occurrence = create_event_occurrence(offer, beginning_datetime=beginning_datetime)
        stock = create_stock_from_event_occurrence(event_occurrence, price=20)
        booking = create_booking(user, stock)

        # When
        mailjet_data = retrieve_data_to_warn_beneficiary_after_pro_booking_cancellation(booking)

        # Then
        assert mailjet_data == {
            'FromEmail': 'support@example.com',
            'MJ-TemplateID': 1116690,
            'MJ-TemplateLanguage': True,
            'To': 'dev@example.com',
            'Vars': {
                'event_hour': '14h',
                'event_date': 'samedi 20 juillet 2019',
                'is_event': 1,
                'is_free_offer': '1',
                'offer_name': booking.stock.offer.name,
                'offer_price': '20',
                'user_first_name': user.firstName,
                'venue_name': booking.stock.offer.venue.name
            }
        }

    @patch('emails.beneficiary_warning_after_pro_booking_cancellation.SUPPORT_EMAIL_ADDRESS', 'support@example.com')
    @patch('emails.beneficiary_warning_after_pro_booking_cancellation.DEV_EMAIL_ADDRESS', 'dev@example.com')
    def test_should_return_thing_data_when_booking_is_on_a_thing(self):
        # Given
        user = create_user()
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock = create_stock_from_offer(offer, price=15)
        booking = create_booking(user, stock)

        # When
        mailjet_data = retrieve_data_to_warn_beneficiary_after_pro_booking_cancellation(booking)

        # Then
        assert mailjet_data == {
            'FromEmail': 'support@example.com',
            'MJ-TemplateID': 1116690,
            'MJ-TemplateLanguage': True,
            'To': 'dev@example.com',
            'Vars': {
                'event_hour': '',
                'event_date': '',
                'is_event': 0,
                'is_free_offer': '1',
                'offer_name': booking.stock.offer.name,
                'offer_price': '15',
                'user_first_name': user.firstName,
                'venue_name': booking.stock.offer.venue.name
            }
        }

    def test_should_not_display_the_price_when_booking_is_on_a_free_offer(self):
        # Given
        user = create_user()
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock = create_stock_from_offer(offer, price=0)
        booking = create_booking(user, stock)

        # When
        mailjet_data = retrieve_data_to_warn_beneficiary_after_pro_booking_cancellation(booking)

        # Then
        assert mailjet_data['Vars']['is_free_offer'] == '0'
        assert mailjet_data['Vars']['offer_price'] == '0'

    def test_should_use_venue_public_name_when_venue_has_one(self):
        # Given
        user = create_user()
        offerer = create_offerer()
        venue = create_venue(offerer, publicName="Mon nouveau nom")
        offer = create_offer_with_thing_product(venue,)
        stock = create_stock_from_offer(offer)
        booking = create_booking(user, stock)

        # When
        mailjet_data = retrieve_data_to_warn_beneficiary_after_pro_booking_cancellation(booking)

        # Then
        assert mailjet_data['Vars']['venue_name'] == "Mon nouveau nom"
