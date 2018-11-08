from models.pc_object import PcObject
from utils.logger import logger
from utils.test_utils import create_booking

def create_scratch_bookings(recommendations_by_name, stocks_by_name, users_by_name):
    logger.info('create_scratch_bookings')

    bookings_by_name = {}

    bookings_by_name['Rencontre avec Franck Lepage / LE GRAND REX PARIS / 20 / jeune 93 / '] = create_booking(
        amount=1,
        recommendation=recommendations_by_name['Rencontre avec Franck Lepage / LE GRAND REX PARIS / jeune 93'],
        stock=stocks_by_name['Rencontre avec Franck Lepage / LE GRAND REX PARIS / 20'],
        token="2ALYY5",
        user=users_by_name['jeune_93']
    ),


    bookings_by_name['ravage / THEATRE DE L ODEON / 20 / jeune 93'] = create_booking(
        amount=1,
        recommendation=recommendations_by_name['ravage / THEATRE DE L ODEON / 20'],
        stock=stocks_by_name['rencontre_avec_franck_lepage_le_grand_rex_paris_20'],
        token="2AEVY3",
        user=users_by_name['jeune_93']
    )

    return bookings_by_name
