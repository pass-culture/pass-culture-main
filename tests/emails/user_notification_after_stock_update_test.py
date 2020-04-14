from datetime import datetime
from unittest.mock import patch

from emails.user_notification_after_stock_update import retrieve_data_to_warn_user_after_stock_update_affecting_booking
from tests.model_creators.generic_creators import create_user, create_offerer, create_venue, create_booking
from tests.model_creators.specific_creators import create_offer_with_event_product, create_event_occurrence, \
    create_stock_from_event_occurrence


class RetrieveDataToWarnUserAfterStockUpdateAffectingBookingTest:
    @patch('emails.user_notification_after_stock_update.feature_send_mail_to_users_enabled')
    def test_should_send_email_to_user_when_feature_send_mail_to_users_is_enabled(self,
                                                                                  feature_send_mail_to_users_enabled):
        # Given
        user = create_user()
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_event_product(venue)
        event_occurrence = create_event_occurrence(offer)
        stock = create_stock_from_event_occurrence(event_occurrence)
        booking = create_booking(user=user, stock=stock)
        feature_send_mail_to_users_enabled.return_value = True

        # When
        booking_info_for_mailjet = retrieve_data_to_warn_user_after_stock_update_affecting_booking(booking)

        # Then
        assert booking_info_for_mailjet['To'] == user.email

    @patch('emails.user_notification_after_stock_update.DEV_EMAIL_ADDRESS', 'dev@example.com')
    @patch('emails.user_notification_after_stock_update.feature_send_mail_to_users_enabled')
    def test_should_send_email_to_specific_email_address_when_feature_send_mail_to_users_is_disabled(self,
                                                                                                     feature_send_mail_to_users_enabled):
        # Given
        user = create_user()
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_event_product(venue)
        event_occurrence = create_event_occurrence(offer)
        stock = create_stock_from_event_occurrence(event_occurrence)
        booking = create_booking(user=user, stock=stock)
        feature_send_mail_to_users_enabled.return_value = False

        # When
        booking_info_for_mailjet = retrieve_data_to_warn_user_after_stock_update_affecting_booking(booking)

        # Then
        assert booking_info_for_mailjet['To'] == 'dev@example.com'

    @patch('emails.user_notification_after_stock_update.DEV_EMAIL_ADDRESS', 'dev@example.com')
    @patch('emails.user_notification_after_stock_update.SUPPORT_EMAIL_ADDRESS', 'support@example.com')
    def test_should_send_email_when_booking_date_have_been_changed(self, app):
        # Given
        beginning_datetime = datetime(2019, 7, 20, 12, 0, 0)

        user = create_user()
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_event_product(venue)
        event_occurrence = create_event_occurrence(offer, beginning_datetime=beginning_datetime)
        stock = create_stock_from_event_occurrence(event_occurrence, price=20)
        booking = create_booking(user=user, stock=stock)

        # When
        booking_info_for_mailjet = retrieve_data_to_warn_user_after_stock_update_affecting_booking(booking)

        # Then
        assert booking_info_for_mailjet == {
            'FromEmail': 'support@example.com',
            'MJ-TemplateID': 1332139,
            'MJ-TemplateLanguage': True,
            'To': 'dev@example.com',
            'Vars': {
                'offer_name': booking.stock.offer.name,
                'user_first_name': user.firstName,
                'venue_name': booking.stock.offer.venue.name,
                'event_date': 'samedi 20 juillet 2019',
                'event_hour': '14h',
            }
        }
