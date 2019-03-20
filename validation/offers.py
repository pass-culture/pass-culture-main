from flask import Request

from models import RightsType
from models.api_errors import ResourceNotFound, ApiErrors
from utils.rest import ensure_current_user_has_rights


def check_user_has_rights_for_query(offerer_id, venue, venue_id):
    if venue_id:
        ensure_current_user_has_rights(RightsType.editor,
                                       venue.managingOffererId)
    elif offerer_id:
        ensure_current_user_has_rights(RightsType.editor,
                                       offerer_id)


def check_venue_exists_when_requested(venue, venue_id):
    if venue_id and venue is None:
        errors = ResourceNotFound()
        errors.addError(
            'global',
            "Ce lieu n'a pas été trouvé"
        )
        raise errors


def check_valid_edition(response: Request, thing_or_event_dict: dict):
    forbidden_keys = {'idAtProviders', 'dateModifiedAtLastProvider', 'thumbCount', 'firstThumbDominantColor',
                      'owningOffererId', 'id', 'lastProviderId', 'isNational', 'dateCreated'}
    all_keys = response.keys()
    if thing_or_event_dict:
        all_keys = set(all_keys).union(set(thing_or_event_dict.keys()))
    keys_in_error = forbidden_keys.intersection(all_keys)
    if thing_or_event_dict and keys_in_error:
        errors = ApiErrors()
        for key in keys_in_error:
            errors.addError(key, 'Vous ne pouvez pas modifier cette information')
        raise errors
