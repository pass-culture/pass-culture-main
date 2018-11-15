from models.pc_object import PcObject
from utils.logger import logger
from utils.test_utils import create_stock_from_event_occurrence

def create_handmade_event_stocks(event_occurrences_by_name):
    logger.info("create_handmade_event_stocks")

    event_stocks_by_name = {}

    event_stocks_by_name['Rencontre avec Franck Lepage / LE GRAND REX PARIS / 0 / 20h / 10 / 10'] = create_stock_from_event_occurrence(
        available=10,
        event_occurrence=event_occurrences_by_name['Rencontre avec Franck Lepage / LE GRAND REX PARIS / 0 / 20h'],
        price=10
    )

    event_stocks_by_name['Rencontre avec Franck Lepage / LE GRAND REX PARIS / 0 / 20h / 15 / 15'] = create_stock_from_event_occurrence(
        available=15,
        event_occurrence=event_occurrences_by_name['Rencontre avec Franck Lepage / LE GRAND REX PARIS / 0 / 20h'],
        price=15
    )

    event_stocks_by_name['Rencontre avec Franck Lepage / LE GRAND REX PARIS / 1 / 20h / 100 / 10'] = create_stock_from_event_occurrence(
        available=100,
        event_occurrence=event_occurrences_by_name['Rencontre avec Franck Lepage / LE GRAND REX PARIS / 1 / 20h'],
        price=10
    )

    event_stocks_by_name['Rencontre avec Franck Lepage / LE GRAND REX PARIS / 1 / 20h / 90 / 15'] = create_stock_from_event_occurrence(
        available=90,
        event_occurrence=event_occurrences_by_name['Rencontre avec Franck Lepage / LE GRAND REX PARIS / 1 / 20h'],
        price=15
    )

    event_stocks_by_name['Concert de Gael Faye / THEATRE DE L ODEON / 0 / 20h / 50 / 50'] = create_stock_from_event_occurrence(
        available=50,
        event_occurrence=event_occurrences_by_name['Concert de Gael Faye / THEATRE DE L ODEON / 0 / 20h'],
        price=50
    )

    event_stocks_by_name['PNL chante Marx / THEATRE DE L ODEON / 0 / 20h / 50 / 50'] = create_stock_from_event_occurrence(
        available=50,
        event_occurrence=event_occurrences_by_name['PNL chante Marx / THEATRE DE L ODEON / 0 / 20h'],
        price=50
    )

    event_stocks_by_name['Le temps des cerises en mode mixolydien / KWATA / 0 / 20h / 50 / 50'] = create_stock_from_event_occurrence(
        available=50,
        event_occurrence=event_occurrences_by_name['Le temps des cerises en mode mixolydien / KWATA / 0 / 20h'],
        price=50
    )

    PcObject.check_and_save(*event_stocks_by_name.values())

    return event_stocks_by_name
