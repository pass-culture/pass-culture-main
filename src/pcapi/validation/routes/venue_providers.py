import json

from pcapi.models import ApiErrors
from pcapi.models import Provider


def check_new_venue_provider_information(payload: json):
    errors = ApiErrors()
    errors.status_code = 400

    if "venueId" not in payload:
        errors.add_error("venueId", "Ce champ est obligatoire")
    if "providerId" not in payload:
        errors.add_error("providerId", "Ce champ est obligatoire")

    errors.maybe_raise()


def check_existing_provider(provider: Provider):
    if not provider:
        errors = ApiErrors()
        errors.status_code = 400
        errors.add_error("provider", "Cette source n'est pas disponible")
        raise errors
