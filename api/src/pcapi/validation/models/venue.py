from pcapi.core.offerers import models as offerers_models
from pcapi.core.offerers.models import Venue
from pcapi.models import db
from pcapi.models.api_errors import ApiErrors


def validate(venue: Venue, api_errors: ApiErrors) -> ApiErrors:
    if venue.siret and len(venue.siret) != 14:
        api_errors.add_error("siret", f"Ce code {venue.identifier_name} est invalide : {venue.siret}")

    if venue.postalCode and len(venue.postalCode) != 5:
        api_errors.add_error("postalCode", "Ce code postal est invalide")

    if venue.managingOffererId:
        if not venue.managingOfferer:
            managing_offerer = db.session.query(offerers_models.Offerer).filter_by(id=venue.managingOffererId).one()
        else:
            managing_offerer = venue.managingOfferer
        if venue.siret and managing_offerer and not venue.siret.startswith(managing_offerer.siren):
            api_errors.add_error(
                "siret", f"Le code {venue.identifier_name} doit correspondre à un établissement de votre structure"
            )

    return api_errors
