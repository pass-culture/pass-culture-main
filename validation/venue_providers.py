import json

from models import ApiErrors
from repository.provider_queries import find_provider_by_id
from utils.human_ids import dehumanize


def _validate_existing_provider(provider_id: int):
    provider = find_provider_by_id(provider_id)
    is_provider_available_for_pro_usage = provider and provider.isActive and provider.enabledForPro
    if not is_provider_available_for_pro_usage:
        errors = ApiErrors()
        errors.status_code = 400
        errors.add_error('provider', "Cette source n'est pas disponible")
        raise errors


def validate_new_venue_provider_information(payload: json):
    errors = ApiErrors()
    errors.status_code = 400

    if 'venueIdAtOfferProvider' not in payload:
        errors.add_error('venueIdAtOfferProvider', 'Ce champ est obligatoire')
    if 'venueId' not in payload:
        errors.add_error('venueId', 'Ce champ est obligatoire')
    if 'providerId' not in payload:
        errors.add_error('providerId', 'Ce champ est obligatoire')

    errors.maybe_raise()

    provider_id = dehumanize(payload.get('providerId'))

    _validate_existing_provider(provider_id)
