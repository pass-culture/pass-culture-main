from pcapi.core.offerers import models as offerers_models
from pcapi.core.offerers.repository import find_virtual_venue_by_offerer_id
from pcapi.models import ApiErrors
from pcapi.models import Venue


def validate(venue: Venue, api_errors: ApiErrors) -> ApiErrors:
    if venue.siret and len(venue.siret) != 14:
        api_errors.add_error("siret", f"Ce code SIRET est invalide : {venue.siret}")

    if venue.postalCode and len(venue.postalCode) != 5:
        api_errors.add_error("postalCode", "Ce code postal est invalide")

    if venue.managingOffererId:
        if not venue.managingOfferer:
            managing_offerer = offerers_models.Offerer.query.get(venue.managingOffererId)
        else:
            managing_offerer = venue.managingOfferer
        if not managing_offerer.siren:
            api_errors.add_error(
                "siren", "Ce lieu ne peut enregistrer de SIRET car la structure associée n’a pas de SIREN renseigné"
            )
        if (
            venue.siret
            and managing_offerer
            and managing_offerer.siren
            and not venue.siret.startswith(managing_offerer.siren)
        ):
            api_errors.add_error("siret", "Le code SIRET doit correspondre à un établissement de votre structure")

    if venue.isVirtual:
        offerer_id = venue.managingOffererId
        if not offerer_id:
            offerer_id = venue.managingOfferer.id
        already_existing_virtual_venue = find_virtual_venue_by_offerer_id(offerer_id)
        if already_existing_virtual_venue and already_existing_virtual_venue.id != venue.id:
            api_errors.add_error("isVirtual", "Un lieu pour les offres numériques existe déjà pour cette structure")

    return api_errors
