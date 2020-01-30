from typing import Dict, List

from models import ApiErrors, Offer


def check_stocks_are_editable_for_offer(offer: Offer):
    if offer.isFromProvider:
        api_errors = ApiErrors()
        api_errors.add_error('global', 'Les offres importées ne sont pas modifiables')
        raise api_errors


def check_stocks_are_editable_in_patch_stock(offer: Offer):
    local_class = offer.lastProvider.localClass if offer.lastProvider else ''
    is_not_editable = offer.isFromProvider is True and 'TiteLive' in local_class
    if is_not_editable:
        api_errors = ApiErrors()
        api_errors.add_error('global', 'Les offres importées ne sont pas modifiables')
        raise api_errors


def check_offer_offerer_exists(offerer):
    if offerer is None:
        api_errors = ApiErrors()
        api_errors.add_error('offerId', 'l\'offreur associé à cette offre est inconnu')
        raise api_errors


def check_event_occurrence_offerer_exists(offerer):
    if offerer is None:
        api_errors = ApiErrors()
        api_errors.add_error('eventOccurrenceId', 'l\'offreur associé à cet évènement est inconnu')
        raise api_errors


def check_request_has_offer_id(request_data: dict):
    if 'offerId' not in request_data:
        raise ApiErrors({'offerId': ['Ce paramètre est obligatoire']})


def check_dates_are_allowed_on_new_stock(request_data: dict, offer: Offer):
    if offer.isThing:
        _forbid_dates_on_stock_for_thing_offer(request_data)
    else:
        if request_data.get('endDatetime', None) is None:
            raise ApiErrors({'endDatetime': ['Ce paramètre est obligatoire']})

        if request_data.get('beginningDatetime', None) is None:
            raise ApiErrors({'beginningDatetime': ['Ce paramètre est obligatoire']})

        if request_data.get('bookingLimitDatetime', None) is None:
            raise ApiErrors({'bookingLimitDatetime': ['Ce paramètre est obligatoire']})


def check_dates_are_allowed_on_existing_stock(request_data: dict, offer: Offer):
    if offer.isThing:
        _forbid_dates_on_stock_for_thing_offer(request_data)
    else:
        if 'endDatetime' in request_data and request_data['endDatetime'] is None:
            raise ApiErrors({'endDatetime': ['Ce paramètre est obligatoire']})

        if 'beginningDatetime' in request_data and request_data['beginningDatetime'] is None:
            raise ApiErrors({'beginningDatetime': ['Ce paramètre est obligatoire']})

        if 'bookingLimitDatetime' in request_data and request_data['bookingLimitDatetime'] is None:
            raise ApiErrors({'bookingLimitDatetime': ['Ce paramètre est obligatoire']})


def _forbid_dates_on_stock_for_thing_offer(request_data):
    if 'beginningDatetime' in request_data or 'endDatetime' in request_data:
        raise ApiErrors(
            {'global': [
                'Impossible de mettre des dates de début et fin si l\'offre ne porte pas sur un évenement'
            ]})


def check_only_editable_fields_will_be_updated(stock_updated_fields: List, stock_editable_fields: List):
    if not set(stock_updated_fields).issubset(stock_editable_fields):
        api_errors = ApiErrors()
        api_errors.status_code = 400
        api_errors.add_error('global', 'Pour les offres importées, certains champs ne sont pas modifiables')
        raise api_errors


def get_updated_fields_after_patch(old_stock: Dict, new_stock: Dict) -> List:
    common_keys = set(old_stock).intersection(set(new_stock))
    filtered_old_dict = {key: old_stock[key] for key in common_keys}
    filtered_new_dict = {key: new_stock[key] for key in common_keys}
    updated_fields = [key for key in common_keys if filtered_new_dict[key] != filtered_old_dict[key]]
    return updated_fields
