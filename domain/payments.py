from models.payment import Payment, PaymentType


def create_initial_payment_for_booking(booking, author, comment=None):
    offerer = booking.stock.resolvedOffer.venue.managingOfferer

    payment = Payment()
    payment.booking = booking
    payment.author = author
    payment.offerer = offerer
    payment.iban = offerer.iban
    payment.type = PaymentType.INITIAL

    return payment
