from models import ApiErrors, Offer


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


def check_stock_has_dates_for_event_offer(request_data: dict, offer: Offer):
    if offer.thing:
        if 'beginningDatetime' in request_data or 'endDatetime' in request_data:
            raise ApiErrors(
                {'global': [
                    'Impossible de mettre des dates de début et fin si l\'offre ne porte pas sur un évenement'
                ]})

    else:
        if 'endDatetime' not in request_data:
            raise ApiErrors({'endDatetime': ['Ce paramètre est obligatoire']})

        if 'beginningDatetime' not in request_data:
            raise ApiErrors({'beginningDatetime': ['Ce paramètre est obligatoire']})
