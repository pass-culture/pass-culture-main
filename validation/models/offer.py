from models import ApiErrors
from models.db import Model
from repository import venue_queries


def validate(offer: Model, api_errors: ApiErrors) -> ApiErrors:
    venue = offer.venue if offer.venue else venue_queries.find_by_id(offer.venueId)

    if offer.isDigital:
        if not venue.isVirtual:
            api_errors.add_error('venue', 'Une offre numérique doit obligatoirement être associée au lieu "Offre numérique"')

        if offer.type_can_only_be_offline():
            api_errors.add_error('url', f'Une offre de type {offer.get_label_from_type_string()} ne peut pas être numérique')
    else:
        if venue.isVirtual:
            api_errors.add_error('venue', 'Une offre physique ne peut être associée au lieu "Offre numérique"')

    return api_errors
