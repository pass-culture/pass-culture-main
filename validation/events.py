from models import ApiErrors


def check_has_venue_id(venue_id):
    if venue_id is None:
        api_errors = ApiErrors()
        api_errors.addError('venueId', 'Vous devez préciser un identifiant de lieu')
        raise api_errors