from datetime import timedelta

from models.pc_object import PcObject
from utils.date import today, strftime
from utils.logger import logger
from tests.test_utils import create_event_occurrence

def create_handmade_event_occurrences(offers_by_name):
    logger.info('create_handmade_event_occurrences')

    event_occurrences_by_name = {}

    event_occurrences_by_name['Rencontre avec Franck Lepage / THEATRE LE GRAND REX PARIS / 0 / 20h'] = create_event_occurrence(
        beginning_datetime=strftime(today),
        end_datetime=strftime(today + timedelta(hours=1)),
        offer=offers_by_name['Rencontre avec Franck Lepage / THEATRE LE GRAND REX PARIS']
    )

    event_occurrences_by_name['Rencontre avec Franck Lepage / THEATRE LE GRAND REX PARIS / 1 / 20h'] = create_event_occurrence(
        beginning_datetime=strftime(today + timedelta(days=1)),
        end_datetime=strftime(today + timedelta(days=1, hours=1)),
        offer=offers_by_name['Rencontre avec Franck Lepage / THEATRE LE GRAND REX PARIS']
    )

    event_occurrences_by_name['Concert de Gael Faye / THEATRE DE L ODEON / 0 / 20h'] = create_event_occurrence(
        beginning_datetime=strftime(today),
        end_datetime=strftime(today + timedelta(hours=2)),
        offer=offers_by_name['Concert de Gael Faye / THEATRE DE L ODEON']
    )

    event_occurrences_by_name['PNL chante Marx / THEATRE DE L ODEON / 0 / 20h'] = create_event_occurrence(
        beginning_datetime=strftime(today),
        end_datetime=strftime(today + timedelta(hours=3)),
        offer=offers_by_name['PNL chante Marx / THEATRE DE L ODEON']
    )

    event_occurrences_by_name['Le temps des cerises en mode mixolydien / ASSOCIATION KWATA / 0 / 20h'] = create_event_occurrence(
        beginning_datetime=strftime(today + timedelta(days=1)),
        end_datetime=strftime(today + timedelta(days=1, hours=3)),
        offer=offers_by_name['Le temps des cerises en mode mixolydien / ASSOCIATION KWATA']
    )

    PcObject.check_and_save(*event_occurrences_by_name.values())

    logger.info('created {} event_occurrences'.format(len(event_occurrences_by_name)))

    return event_occurrences_by_name
