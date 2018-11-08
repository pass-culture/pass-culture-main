from models.pc_object import PcObject
from utils.logger import logger
from utils.test_utils import create_stock_from_event_occurrence

def create_grid_event_stocks(event_occurrences_by_name):
    logger.info('create_grid_event_stocks')

    event_stocks_by_name = {}
    for event_occurrence_mock in event_occurrences_by_name.values():


        stock_mock = {
            "available": 10,
            "eventOccurrenceId": event_occurrence_mock['id'],
            "id": humanize(incremented_id),
            "price": 10
        }

    PcObject.check_and_save(*event_stocks_by_name)

    return event_stocks_by_name
