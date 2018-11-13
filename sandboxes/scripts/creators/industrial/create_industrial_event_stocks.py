from models.pc_object import PcObject
from utils.logger import logger
from utils.test_utils import create_stock_from_event_occurrence

def create_industrial_event_stocks(event_occurrences_by_name):
    logger.info('create_industrial_event_stocks')

    event_stocks_by_name = {}

    for (event_occurrence_name, event_occurrence) in event_occurrences_by_name.items():
        available = 10
        price = 10
        name = event_occurrence_name + "/" + str(available) + "/" + str(price)
        event_stocks_by_name[name] = create_stock_from_event_occurrence(
            event_occurrence,
            available=available,
            price=price
        )

    PcObject.check_and_save(*event_stocks_by_name.values())

    return event_stocks_by_name
