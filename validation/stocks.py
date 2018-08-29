from models import ApiErrors


def check_offer_id_xor_event_occurrence_id_in_request(stock_dict):
    if 'offerId' not in stock_dict and 'eventOccurrenceId' not in stock_dict:
        api_errors = ApiErrors()
        api_errors.addError('offerId', 'cette entrée est obligatoire en absence de eventOccurrenceId')
        api_errors.addError('eventOccurrenceId', 'cette entrée est obligatoire en absence de offerId')
        raise api_errors


def check_offer_offerer_exists(offerer):
    if offerer is None:
        api_errors = ApiErrors()
        api_errors.addError('offerId', 'l\'offreur associé à cette offre est inconnu')
        raise api_errors


def check_event_occurrence_offerer_exists(offerer):
    if offerer is None:
        api_errors = ApiErrors()
        api_errors.addError('eventOccurrenceId', 'l\'offreur associé à cet évènement est inconnu')
        raise api_errors