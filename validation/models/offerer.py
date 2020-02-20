from models import ApiErrors, Offerer


def validate(offerer: Offerer, api_errors: ApiErrors) -> ApiErrors:
    if offerer.siren is not None and (not len(offerer.siren) == 9):
        api_errors.add_error('siren', 'Ce code SIREN est invalide')

    return api_errors
