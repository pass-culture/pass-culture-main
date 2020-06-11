from domain.beneficiary.beneficiary_repository import BeneficiaryRepository
from domain.booking.booking_repository import BookingRepository
from domain.services.notification.notification_service import NotificationService
from models import RightsType
from validation.routes.bookings import check_booking_is_cancellable_by_user
from validation.routes.users_authorizations import check_user_can_cancel_booking_by_id


class CancelABooking:
    def __init__(self,
                 booking_repository: BookingRepository,
                 beneficiary_repository: BeneficiaryRepository,
                 notification_service: NotificationService):
        self.notification_service = notification_service
        self.beneficiary_repository = beneficiary_repository
        self.booking_repository = booking_repository

    def execute(self, booking_id: int, beneficary_id: int, current_user):
        booking_offerer = self.booking_repository.find_booking_with_offerer(booking_id=booking_id)
        beneficiary = self.beneficiary_repository.find_beneficiary_by_user_id(user_id=beneficary_id)

        is_offerer_cancellation = current_user.hasRights(RightsType.editor, booking_offerer)
        is_user_cancellation = booking_offerer.user == current_user
        check_user_can_cancel_booking_by_id(is_user_cancellation, is_offerer_cancellation)

        if is_user_cancellation:
            check_booking_is_cancellable_by_user(booking_offerer, is_user_cancellation)

        if booking_offerer.isCancelled:
            return booking_offerer

        booking_offerer.isCancelled = True

        self.booking_repository.save(booking_offerer)
        self.notification_service.send_booking_cancellation_emails_to_user_and_offerer(booking_offerer,
                                                                                       is_offerer_cancellation,
                                                                                       is_user_cancellation)
        return booking_offerer
