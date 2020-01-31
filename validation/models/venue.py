from models import ApiErrors
from models.db import Model
from repository import offerer_queries
from repository import venue_queries


def validate_venue(model: Model, api_errors: ApiErrors) -> ApiErrors:
    if model.siret is not None and not len(model.siret) == 14:
        api_errors.add_error('siret', f'Ce code SIRET est invalide : {model.siret}')

    if model.postalCode is not None and len(model.postalCode) != 5:
        api_errors.add_error('postalCode', 'Ce code postal est invalide')

    if model.managingOffererId is not None:
        if model.managingOfferer is None:
            managing_offerer = offerer_queries.find_by_id(model.managingOffererId)
        else:
            managing_offerer = model.managingOfferer

        if managing_offerer.siren is None:
            api_errors.add_error('siren', 'Ce lieu ne peut enregistrer de SIRET car la structure associée n’a pas de SIREN renseigné')

        if model.siret is not None \
                and managing_offerer is not None \
                and not model.siret.startswith(managing_offerer.siren):
            api_errors.add_error('siret', 'Le code SIRET doit correspondre à un établissement de votre structure')

    if model.isVirtual:
        offerer_id = model.managingOffererId

        if offerer_id is None:
            offerer_id = model.managingOfferer.id

        already_existing_virtual_venue = venue_queries.find_by_offrer_id_and_is_virtual(offerer_id)

        if already_existing_virtual_venue is not None \
                and already_existing_virtual_venue.id != model.id:
            api_errors.add_error('isVirtual', 'Un lieu pour les offres numériques existe déjà pour cette structure')

    return api_errors
