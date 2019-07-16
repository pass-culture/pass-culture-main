from flask import Request

from models import RightsType
from models.api_errors import ResourceNotFound, ApiErrors
from models.offer_type import ProductType
from utils.rest import ensure_current_user_has_rights


def check_user_has_rights_for_query(offerer_id, venue, venue_id):
    if venue_id:
        ensure_current_user_has_rights(RightsType.editor,
                                       venue.managingOffererId)
    elif offerer_id:
        ensure_current_user_has_rights(RightsType.editor,
                                       offerer_id)


def check_has_venue_id(venue_id):
    if venue_id is None:
        api_errors = ApiErrors()
        api_errors.add_error('venueId', 'Vous devez préciser un identifiant de lieu')
        raise api_errors


def check_venue_exists_when_requested(venue, venue_id):
    if venue_id and venue is None:
        errors = ResourceNotFound()
        errors.add_error(
            'global',
            "Ce lieu n'a pas été trouvé"
        )
        raise errors


def check_valid_edition(payload: dict):
    forbidden_keys = {'idAtProviders', 'dateModifiedAtLastProvider', 'thumbCount', 'firstThumbDominantColor',
                      'owningOffererId', 'id', 'lastProviderId', 'dateCreated'}
    all_keys = payload.keys()
    keys_in_error = forbidden_keys.intersection(all_keys)
    if keys_in_error:
        errors = ApiErrors()
        for key in keys_in_error:
            errors.add_error(key, 'Vous ne pouvez pas modifier cette information')
        raise errors


def check_offer_type_is_valid(offer_type_name):
    if not ProductType.is_thing(offer_type_name) and not ProductType.is_event(offer_type_name):
        api_error = ApiErrors()
        api_error.add_error('type',
                           'Le type de cette offre est inconnu')
        raise api_error


def check_offer_id_and_mediation_id_are_present_in_request(offer_id: str, mediation_id: str):
    if offer_id is None \
            or mediation_id is None:
        errors = ApiErrors()
        errors.status_code = 400
        errors.addError('global', "Les paramères offerId et mediationId sont obligatoires")
        errors.maybeRaise()
        raise errors
