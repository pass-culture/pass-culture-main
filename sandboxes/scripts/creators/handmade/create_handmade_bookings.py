from models.pc_object import PcObject
from utils.logger import logger
from utils.test_utils import create_booking

def create_handmade_bookings(recommendations_by_name, stocks_by_name, users_by_name):
    logger.info('create_handmade_bookings')

    bookings_by_name = {}

    stock = stocks_by_name['Rencontre avec Franck Lepage / LE GRAND REX PARIS / 0 / 20h / 10 / 10']
    bookings_by_name['Rencontre avec Franck Lepage / LE GRAND REX PARIS / 20h / 10 / 10 / jeune 93'] = create_booking(
        users_by_name['jeune 93'],
        recommendation=recommendations_by_name['Rencontre avec Franck Lepage / LE GRAND REX PARIS / jeune 93'],
        stock=stock,
        token="2ALYY5"
    )

    stock = stocks_by_name['Ravage / THEATRE DE L ODEON / 50 / 50']
    bookings_by_name['Ravage / THEATRE DE L ODEON / 50 / 50 / jeune 93'] = create_booking(
        users_by_name['jeune 93'],
        recommendation=recommendations_by_name['Ravage / THEATRE DE L ODEON / jeune 93'],
        stock=stock,
        token="2AEVY3"
    )

    PcObject.check_and_save(*bookings_by_name.values())

    logger.info('created {} bookings'.format(len(bookings_by_name)))

    return bookings_by_name
