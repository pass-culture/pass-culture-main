from models import Booking, Stock, User
from models.pc_object import PcObject
from utils.human_ids import dehumanize
from utils.logger import logger


def create_or_find_booking(booking_mock):
    stock = Stock.query.get(dehumanize(booking_mock['stockId']))
    user = User.query.get(dehumanize(booking_mock['userId']))

    logger.info("look booking " + str(stock) + " " + user.email + " " + booking_mock.get('id'))

    if 'id' in booking_mock:
        booking = Booking.query.get(dehumanize(booking_mock['id']))
    else:
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
        if 'id' in booking_mock:
            booking.id = dehumanize(booking_mock['id'])
        PcObject.check_and_save(booking)
        logger.info("created booking " + str(booking))
    else:
        logger.info('--already here-- booking' + str(booking))

    return booking
