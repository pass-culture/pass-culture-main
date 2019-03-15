from models import ApiErrors


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


def check_request_has_offer_id(request_data: dict):
    if 'offerId' not in request_data:
        raise ApiErrors({'offerId': ['Ce paramètre est obligatoire']})