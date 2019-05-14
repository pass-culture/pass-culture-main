from models.pc_object import PcObject
from models.payment_status import TransactionStatus
from sandboxes.scripts.utils.select import remove_every
from tests.test_utils import create_payment
from utils.logger import logger

from pprint import pprint

BOOKINGS_WITH_PAYMENTS_REMOVE_RATIO = 5

def create_industrial_payments(
    bookings_by_name
):
    logger.info('create_industrial_payments')

    payments_by_name = {}

    booking_items = bookings_by_name.items()

    booking_items_with_booking = remove_every(
        booking_items,
        BOOKINGS_WITH_PAYMENTS_REMOVE_RATIO
    )

    transaction_statuses = [t for t in TransactionStatus]


    for (booking_index, (booking_name, booking)) in enumerate(booking_items_with_booking):
        payment_name = booking_name
        venue = booking.stock.offer.venue
        offerer = venue.managingOfferer
        transaction_status_index = booking_index%len(transaction_statuses)
        transaction_status = transaction_statuses[transaction_status_index]

        payment = create_payment(
            booking,
            offerer,
            booking.amount,
            bic=venue.bic or offerer.bic,
            iban=venue.iban or offerer.iban,
            payment_message_name="Mars 2055: 1er virement {}".format(booking_index),
            status=transaction_status
        )

        payments_by_name[payment_name] = payment

    PcObject.check_and_save(*payments_by_name.values())

    logger.info('created {} payments'.format(len(payments_by_name)))

    return payments_by_name
