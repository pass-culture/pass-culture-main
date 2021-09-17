from pcapi.core.offerers.repository import find_virtual_venue_by_offerer_id
from pcapi.models import ApiErrors
from pcapi.models import Venue
from pcapi.repository import offerer_queries


def validate(venue: Venue, api_errors: ApiErrors) -> ApiErrors:
    if venue.siret is not None and not len(venue.siret) == 14:
        api_errors.add_error("siret", f"Ce code SIRET est invalide : {venue.siret}")

    if venue.postalCode is not None and len(venue.postalCode) != 5:
        api_errors.add_error("postalCode", "Ce code postal est invalide")

    if venue.managingOffererId is not None:
        if venue.managingOfferer is None:
            managing_offerer = offerer_queries.find_by_id(venue.managingOffererId)
        else:
            managing_offerer = venue.managingOfferer
        if managing_offerer.siren is None:
            api_errors.add_error(
                "siren", "Ce lieu ne peut enregistrer de SIRET car la structure associée n’a pas de SIREN renseigné"
            )
        if (
            venue.siret is not None
            and managing_offerer is not None
            and managing_offerer.siren is not None
            and not venue.siret.startswith(managing_offerer.siren)
        ):
            api_errors.add_error("siret", "Le code SIRET doit correspondre à un établissement de votre structure")

    if venue.isVirtual:
        offerer_id = venue.managingOffererId

        if offerer_id is None:
            offerer_id = venue.managingOfferer.id

        already_existing_virtual_venue = find_virtual_venue_by_offerer_id(offerer_id)
        if already_existing_virtual_venue is not None and already_existing_virtual_venue.id != venue.id:
            api_errors.add_error("isVirtual", "Un lieu pour les offres numériques existe déjà pour cette structure")

    return api_errors
