from decimal import Decimal, InvalidOperation

from models import ApiErrors, Venue

MAX_LONGITUDE = 180
MAX_LATITUDE = 90


def check_existing_venue(venue: Venue):
    if not venue:
        errors = ApiErrors()
        errors.status_code = 404
        errors.add_error('venue', "Ce lieu n'existe pas")
        raise errors


def validate_coordinates(raw_latitude, raw_longitude):
    api_errors = ApiErrors()

    if raw_latitude:
        _validate_latitude(api_errors, raw_latitude)

    if raw_longitude:
        _validate_longitude(api_errors, raw_longitude)

    if api_errors.errors:
        raise api_errors


def check_valid_edition(request, venue):
    managing_offerer_id = request.json.get('managingOffererId')
    siret = request.json.get('siret')
    if managing_offerer_id:
        errors = ApiErrors()
        errors.add_error('managingOffererId', 'Vous ne pouvez pas changer la structure d\'un lieu')
        raise errors
    if siret and venue.siret and siret != venue.siret:
        errors = ApiErrors()
        errors.add_error('siret', 'Vous ne pouvez pas modifier le siret d\'un lieu')
        raise errors


def _validate_longitude(api_errors, raw_longitude):
    try:
        longitude = Decimal(raw_longitude)
    except InvalidOperation:
        api_errors.add_error('longitude', 'Format incorrect')
    else:
        if longitude > MAX_LONGITUDE or longitude < -MAX_LONGITUDE:
            api_errors.add_error('longitude', 'La longitude doit être comprise entre -180.0 et +180.0')


def _validate_latitude(api_errors, raw_latitude):
    try:
        latitude = Decimal(raw_latitude)
    except InvalidOperation:
        api_errors.add_error('latitude', 'Format incorrect')
    else:
        if latitude > MAX_LATITUDE or latitude < -MAX_LATITUDE:
            api_errors.add_error('latitude', 'La latitude doit être comprise entre -90.0 et +90.0')
