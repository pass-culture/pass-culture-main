from datetime import datetime, timedelta, timezone
from unittest.mock import patch

from emails.beneficiary_warning_after_pro_booking_cancellation import \
    retrieve_data_to_warn_beneficiary_after_pro_booking_cancellation
from tests.conftest import clean_database
from tests.test_utils import create_booking, create_stock_from_event_occurrence, create_event_occurrence, \
    create_offer_with_event_product, create_venue, create_offerer, create_user, create_offer_with_thing_product, \
    create_stock_from_offer
from utils.mailing import DEV_EMAIL_ADDRESS, SUPPORT_EMAIL_ADDRESS


class RetrieveDataToWarnBeneficiaryAfterProBookingCancellationTest:
    @clean_database
    def test_retrieve_data_to_warn_beneficiary_after_pro_booking_cancellation_when_booking_is_sent_from_support_when_feature_send_mail_to_users_is_enabled(self, app):
        # Given
        beginning_datetime = datetime(2019, 7, 20, 12, 0, 0, tzinfo=timezone.utc)
        end_datetime = beginning_datetime + timedelta(hours=1)
        booking_limit_datetime = beginning_datetime - timedelta(hours=1)

        user = create_user(public_name='John Doe')
        offerer = create_offerer(name='Test offerer')
        venue = create_venue(offerer)
        offer = create_offer_with_event_product(venue, event_name='Mains, sorts et papiers')
        event_occurrence = create_event_occurrence(offer, beginning_datetime=beginning_datetime,
                                                   end_datetime=end_datetime)
        stock = create_stock_from_event_occurrence(event_occurrence, price=20, available=10,
                                                   booking_limit_date=booking_limit_datetime)
        booking = create_booking(user, stock)

        # When
        with patch('emails.beneficiary_warning_after_pro_booking_cancellation.feature_send_mail_to_users_enabled', return_value=True):
            email = retrieve_data_to_warn_beneficiary_after_pro_booking_cancellation(booking)

        # Then
        assert email['FromEmail'] == SUPPORT_EMAIL_ADDRESS

    @clean_database
    def test_retrieve_data_to_warn_beneficiary_after_pro_booking_cancellation_when_booking_is_sent_from_dev_when_feature_send_mail_to_users_is_not_enabled(self, app):
        # Given
        beginning_datetime = datetime(2019, 7, 20, 12, 0, 0, tzinfo=timezone.utc)
        end_datetime = beginning_datetime + timedelta(hours=1)
        booking_limit_datetime = beginning_datetime - timedelta(hours=1)

        user = create_user(public_name='John Doe')
        offerer = create_offerer(name='Test offerer')
        venue = create_venue(offerer)
        offer = create_offer_with_event_product(venue, event_name='Mains, sorts et papiers')
        event_occurrence = create_event_occurrence(offer, beginning_datetime=beginning_datetime,
                                                   end_datetime=end_datetime)
        stock = create_stock_from_event_occurrence(event_occurrence, price=20, available=10,
                                                   booking_limit_date=booking_limit_datetime)
        booking = create_booking(user, stock)

        # When
        with patch('emails.beneficiary_warning_after_pro_booking_cancellation.feature_send_mail_to_users_enabled', return_value=False):
            email = retrieve_data_to_warn_beneficiary_after_pro_booking_cancellation(booking)

        # Then
        assert email['FromEmail'] == DEV_EMAIL_ADDRESS



    @clean_database
    def test_retrieve_data_to_warn_beneficiary_after_pro_booking_cancellation_when_booking_is_sent_to_user_when_feature_send_mail_to_users_is_enabled(self, app):
        # Given
        beginning_datetime = datetime(2019, 7, 20, 12, 0, 0, tzinfo=timezone.utc)
        end_datetime = beginning_datetime + timedelta(hours=1)
        booking_limit_datetime = beginning_datetime - timedelta(hours=1)

        user = create_user(public_name='John Doe')
        offerer = create_offerer(name='Test offerer')
        venue = create_venue(offerer)
        offer = create_offer_with_event_product(venue, event_name='Mains, sorts et papiers')
        event_occurrence = create_event_occurrence(offer, beginning_datetime=beginning_datetime,
                                                   end_datetime=end_datetime)
        stock = create_stock_from_event_occurrence(event_occurrence, price=20, available=10,
                                                   booking_limit_date=booking_limit_datetime)
        booking = create_booking(user, stock)

        # When
        with patch('emails.beneficiary_warning_after_pro_booking_cancellation.feature_send_mail_to_users_enabled', return_value=True):
            email = retrieve_data_to_warn_beneficiary_after_pro_booking_cancellation(booking)

        # Then
        assert email['To'] == user.email

    @clean_database
    def test_retrieve_data_to_warn_beneficiary_after_pro_booking_cancellation_when_booking_is_sent_to_dev_when_feature_send_mail_to_users_is_not_enabled(self, app):
        # Given
        beginning_datetime = datetime(2019, 7, 20, 12, 0, 0, tzinfo=timezone.utc)
        end_datetime = beginning_datetime + timedelta(hours=1)
        booking_limit_datetime = beginning_datetime - timedelta(hours=1)

        user = create_user(public_name='John Doe')
        offerer = create_offerer(name='Test offerer')
        venue = create_venue(offerer)
        offer = create_offer_with_event_product(venue, event_name='Mains, sorts et papiers')
        event_occurrence = create_event_occurrence(offer, beginning_datetime=beginning_datetime,
                                                   end_datetime=end_datetime)
        stock = create_stock_from_event_occurrence(event_occurrence, price=20, available=10,
                                                   booking_limit_date=booking_limit_datetime)
        booking = create_booking(user, stock)

        # When
        with patch('emails.beneficiary_warning_after_pro_booking_cancellation.feature_send_mail_to_users_enabled', return_value=False):
            email = retrieve_data_to_warn_beneficiary_after_pro_booking_cancellation(booking)

        # Then
        assert email['To'] == DEV_EMAIL_ADDRESS


    @clean_database
    def test_retrieve_data_to_warn_beneficiary_after_pro_booking_cancellation_when_booking_is_on_an_event(self, app):
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
        email = retrieve_data_to_warn_beneficiary_after_pro_booking_cancellation(booking)
        print(email)

        # Then
        assert email['Vars']['prix_offre'] == '20'
        assert email['Vars']['offer_price'] == '1'
        assert email['Vars']['heure_event'] == '14h'
        assert email['Vars']['date_event'] == '20 Juillet 2019'
        assert email['Vars']['nom_lieu'] == venue.name
        assert email['Vars']['event'] == '1'
        assert email['Vars']['prenom_user'] == user.firstName
        assert email['Vars']['nom_offre'] == offer.name

    @clean_database
    def test_retrieve_data_to_warn_beneficiary_after_pro_booking_cancellation_when_booking_is_on_a_thing(self, app):
        # Given
        user = create_user()
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue, thing_name='Test Book')
        stock = create_stock_from_offer(offer, price=15)
        booking = create_booking(user, stock)

        # When
        email = retrieve_data_to_warn_beneficiary_after_pro_booking_cancellation(booking)

        # Then
        assert email['Vars']['prix_offre'] == '15'
        assert email['Vars']['offer_price'] == '1'
        assert email['Vars']['heure_event'] == ''
        assert email['Vars']['date_event'] == ''
        assert email['Vars']['nom_lieu'] == venue.name
        assert email['Vars']['event'] == '0'
        assert email['Vars']['prenom_user'] == user.firstName
        assert email['Vars']['nom_offre'] == offer.name


    @clean_database
    def test_retrieve_data_to_warn_beneficiary_after_pro_booking_cancellation_when_booking_is_on_a_free_offer(self, app):
        # Given
        user = create_user()
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock = create_stock_from_offer(offer, price=0)
        booking = create_booking(user, stock)

        # When
        email = retrieve_data_to_warn_beneficiary_after_pro_booking_cancellation(booking)

        # Then
        assert email['Vars']['offer_price'] == '0'
        assert email['Vars']['prix_offre'] == '0'


    @clean_database
    def test_retrieve_data_to_warn_beneficiary_after_pro_booking_cancellation_when_venue_has_a_public_name(self,
                                                                                                              app):
        # Given
        user = create_user()
        offerer = create_offerer()
        venue = create_venue(offerer, publicName="Mon nouveau nom")
        offer = create_offer_with_thing_product(venue,)
        stock = create_stock_from_offer(offer)
        booking = create_booking(user, stock)

        # When
        email = retrieve_data_to_warn_beneficiary_after_pro_booking_cancellation(booking)

        # Then

        assert email['Vars']['nom_lieu'] == venue.publicName
