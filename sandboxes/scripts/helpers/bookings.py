from models import Booking
from models.pc_object import PcObject
from utils.logger import logger


def create_or_find_booking(booking_mock, stock=None, user=None, store=None):
    if stock is None:
        stock = store['stocks_by_key'][booking_mock['stockKey']]
    if user is None:
        user = store['users_by_key'][booking_mock['userKey']]

    booking = Booking.query.filter_by(
        stockId=stock.id,
        userId=user.id,
        token=booking_mock['token']
    ).first()

    if booking is None:
        booking = Booking(from_dict=booking_mock)
        booking.stock = stock
        booking.user = user
        booking.amount = stock.price
        PcObject.check_and_save(booking)
        logger.info("created booking " + str(booking))
    else:
        logger.info('--already here-- booking' + str(booking))

    return booking


def create_or_find_bookings(*booking_mocks, store=None):
    if store is None:
        store = {}

    bookings_count = str(len(booking_mocks))
    logger.info("BOOKING MOCKS " + bookings_count)

    store['bookings_by_key'] = {}

    for (booking_index, booking_mock) in enumerate(booking_mocks):
        logger.info("look booking " + booking_mock['stockKey'] + " " + str(booking_index) + "/" + bookings_count)
        booking = create_or_find_booking(booking_mock, store=store)
        store['bookings_by_key'][booking_mock['key']] = booking
