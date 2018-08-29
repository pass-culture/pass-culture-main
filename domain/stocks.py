from models import ApiErrors
from repository import offerer_queries
from utils.human_ids import dehumanize


def find_offerer_for_new_stock(stock_dict):
    if 'offerId' in stock_dict:
        stock_id = dehumanize(stock_dict['offerId'])
        offerer = offerer_queries.get_by_offer_id(stock_id)
        _check_offer_offerer_exists(offerer)
    if 'eventOccurrenceId' in stock_dict:
        event_occurrence_id = dehumanize(stock_dict['eventOccurrenceId'])
        offerer = offerer_queries.get_by_event_occurrence_id(event_occurrence_id)
        _check_event_occurrence_offerer_exists(offerer)
    return offerer


def check_offer_id_xor_event_occurrence_id_in_request(stock_dict):
    if 'offerId' not in stock_dict and 'eventOccurrenceId' not in stock_dict:
        api_errors = ApiErrors()
        api_errors.addError('offerId', 'cette entrée est obligatoire en absence de eventOccurrenceId')
        api_errors.addError('eventOccurrenceId', 'cette entrée est obligatoire en absence de offerId')
        raise api_errors


def _check_offer_offerer_exists(offerer):
    if offerer is None:
        api_errors = ApiErrors()
        api_errors.addError('offerId', 'l\'offreur associé à cette offre est inconnu')
        raise api_errors


def _check_event_occurrence_offerer_exists(offerer):
    if offerer is None:
        api_errors = ApiErrors()
        api_errors.addError('eventOccurrenceId', 'l\'offreur associé à cet évènement est inconnu')
        raise api_errors
