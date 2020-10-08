from unittest.mock import MagicMock, patch

from infrastructure.repository.booking.booking_sql_repository import BookingSQLRepository
from infrastructure.services.notification.mailjet_notification_service import MailjetNotificationService
from tests.domain_creators.generic_creators import create_domain_beneficiary, create_domain_booking, create_domain_stock
from model_creators.generic_creators import create_offerer, create_venue
from model_creators.specific_creators import create_offer_with_thing_product
from use_cases.cancel_a_booking import CancelABooking


class CancelABookingTest:
    def setup_method(self):
        self.booking_repository = BookingSQLRepository()
        self.booking_repository.find_booking_by_id_and_beneficiary_id = MagicMock()
        self.booking_repository.save = MagicMock()
        self.notification_service = MailjetNotificationService()
        self.notification_service.send_booking_cancellation_emails_to_user_and_offerer = MagicMock()
        self.cancel_a_booking = CancelABooking(booking_repository=self.booking_repository,
                                               notification_service=self.notification_service)

    @patch('use_cases.cancel_a_booking.send_raw_email')
    def test_user_can_cancel_a_booking(self, mock_send_raw_email, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        beneficiary = create_domain_beneficiary(identifier=5)
        stock = create_domain_stock(identifier=1, quantity=1, price=1, offer=offer)
        booking = create_domain_booking(beneficiary=beneficiary, identifier=2, stock=stock)
        mock_cancelled_booking = create_domain_booking(beneficiary=beneficiary, identifier=2, stock=stock,
                                                       is_cancelled=True)
        self.booking_repository.find_booking_by_id_and_beneficiary_id.return_value = booking
        self.booking_repository.save.return_value = mock_cancelled_booking

        # When
        result = self.cancel_a_booking.execute(booking_id=booking.identifier,
                                               beneficiary_id=beneficiary.identifier)

        # Then
        self.booking_repository.save.assert_called_once_with(booking)
        self.notification_service.send_booking_cancellation_emails_to_user_and_offerer.assert_called_once_with(
            booking=mock_cancelled_booking,
            is_offerer_cancellation=False,
            is_user_cancellation=True,
            send_email=mock_send_raw_email
        )
        assert result.isCancelled is True
