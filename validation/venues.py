from decimal import Decimal, InvalidOperation

from models import ApiErrors
import re

MAX_LONGITUDE = 180
MAX_LATITUDE = 90


def validate_coordinates(raw_latitude, raw_longitude):
    api_errors = ApiErrors()

    if raw_latitude:
        _validate_latitude(api_errors, raw_latitude)

    if raw_longitude:
        _validate_longitude(api_errors, raw_longitude)

    if api_errors.errors:
        raise api_errors


def check_valid_edition(request):
    managing_offerer_id = request.json.get('managingOffererId')
    siret = request.json.get('siret')
    if managing_offerer_id:
        errors = ApiErrors()
        errors.addError('managingOffererId', 'Vous ne pouvez pas changer la structure d\'un lieu')
        raise errors
    if siret:
        errors = ApiErrors()
        errors.addError('siret', 'Vous ne pouvez pas modifier le siret d\'un lieu')
        raise errors


def _validate_longitude(api_errors, raw_longitude):
    try:
        longitude = Decimal(raw_longitude)
    except InvalidOperation:
        api_errors.addError('longitude', 'Format incorrect')
    else:
        if longitude > MAX_LONGITUDE or longitude < -MAX_LONGITUDE:
            api_errors.addError('longitude', 'La longitude doit être comprise entre -180.0 et +180.0')


def _validate_latitude(api_errors, raw_latitude):
    try:
        latitude = Decimal(raw_latitude)
    except InvalidOperation:
        api_errors.addError('latitude', 'Format incorrect')
    else:
        if latitude > MAX_LATITUDE or latitude < -MAX_LATITUDE:
            api_errors.addError('latitude', 'La latitude doit être comprise entre -90.0 et +90.0')


def check_get_venues_params(param: {}) -> []:
    if param.get('dpt', []):
        _check_dpt_list(param['dpt'])

    if param.get('has_validated_offerer', None):
        _check_has_validated_offerer_param(param['has_validated_offerer'])

    if param.get('zip_codes', []):
        _check_zip_codes_list(param['zip_codes'])

    if param.get('from_date', None):
        _check_date_format(param['from_date'])

    if param.get('to_date', None):
        _check_date_format(param['to_date'])

    if param.get('has_siret', None):
        _check_has_siret_param(param['has_siret'])

    if param.get('venue_type', None):
        _check_venue_type_param(param['venue_type'])

    if param.get('has_offer', None):
        _check_has_offer_param(param['has_offer'])

    if param.get('is_validated', None):
        _check_is_validated_param(param['is_validated'])

    return True


def _check_date_format(date: str) -> bool:
    if re.search('^\d{4}-\d{2}-\d{2}$', date):
       return True
    api_errors = ApiErrors()
    api_errors.addError('date_format', 'to_date ou from_date doit être de type aaaa-mm-jj')
    raise api_errors


def _check_dpt_list(dpt_list:  []) -> bool:
    for dpt in dpt_list:
       if not re.search('^\d{2}$|^2{1}(a|b|A|B)$|^\d{3}$', dpt):
            api_errors = ApiErrors()
            api_errors.addError('dpt', 
                'dpt doit être de type xx ou xxx (2 ou 3 chiffres), ou 2A, ou 2B)')
            raise api_errors
    return True


def _check_zip_codes_list(zip_codes_list:  []) -> bool:

    for zip_code in zip_codes_list:
        if not re.search('^\d{5}$|^2{1}(a|b|A|B)\d{3}$', zip_code):
            api_errors = ApiErrors()
            api_errors.addError('zip_codes',
                'zip_codes de type xxxxx (5 chiffres, ex: 78140 ou 2a000)')
            raise api_errors
    return True


def _check_has_validated_offerer_param(has_validated_offerer: str) -> bool:
    valid_param = ['YES', 'NO']
    for elem in valid_param:
        if has_validated_offerer == elem:
            return True
    api_errors = ApiErrors()
    api_errors.addError('has_validated_offerer', 
        'has_validated_offerer accepte YES ou NO')
    raise api_errors


def _check_venue_type_param(venue_type: str) -> bool:
    valid_param = ['NOT_VIRTUAL', 'VIRTUAL']
    for elem in valid_param:
        if venue_type == elem:
            return True
    api_errors = ApiErrors()
    api_errors.addError('venue_type', 'venue_type accepte NOT_VIRTUAL ou VIRTUAL')
    raise api_errors


def _check_has_offer_param(has_offer: str) -> bool:
    valid_param = ['ALL', 'VALID', 'WITHOUT', 'EXPIRED']
    for elem in valid_param:
        if has_offer == elem:
            return True
    api_errors = ApiErrors()
    api_errors.addError('has_offer', 'has_offer accepte ALL ou VALID ou WITHOUT ou EXPIRED')
    raise api_errors


def _check_has_siret_param(has_siret: str) -> bool:
    valid_param = ['YES', 'NO']
    for elem in valid_param:
        if has_siret == elem:
            return True
    api_errors = ApiErrors()
    api_errors.addError('has_siret', 'has_siret accepte YES ou NO')   
    raise api_errors


def _check_is_validated_param(is_validated: str) -> bool:
    valid_param = ['YES', 'NO']
    for elem in valid_param:
        if is_validated == elem:
            return True
    api_errors = ApiErrors()
    api_errors.addError('is_validated', 'is_validated accepte YES ou NO')   
    raise api_errors
