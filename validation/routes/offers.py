from models import RightsType, Offer
from models.api_errors import ResourceNotFoundError, ApiErrors
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
        errors = ResourceNotFoundError()
        errors.add_error(
            'global',
            "Ce lieu n'a pas été trouvé"
        )
        raise errors


def check_valid_edition(payload: dict):
    forbidden_keys = {'idAtProviders', 'dateModifiedAtLastProvider', 'thumbCount',
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


def check_offer_name_length_is_valid(offer_name: str):
    max_offer_name_length = 90
    if len(offer_name) > max_offer_name_length:
        api_error = ApiErrors()
        api_error.add_error('name', 'Le titre de l’offre doit faire au maximum 90 caractères.')
        raise api_error


def check_offer_id_is_present_in_request(offer_id: str):
    if offer_id is None:
        errors = ApiErrors()
        errors.status_code = 400
        errors.add_error('global', 'Le paramètre offerId est obligatoire')
        errors.maybe_raise()
        raise errors


def check_offer_is_editable(offer: Offer):
    if not offer.isEditable:
        error = ApiErrors()
        error.status_code = 400
        error.add_error('global', "Les offres importées ne sont pas modifiables")
        raise error
