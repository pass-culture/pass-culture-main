from models import Booking
from models.payment import Payment


def create_payment_for_booking(booking: Booking) -> Payment:
    payment = Payment()
    payment.booking = booking
    return payment
