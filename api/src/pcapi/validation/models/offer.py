from pcapi.core.offerers.repository import find_venue_by_id
from pcapi.core.offers.models import Offer
from pcapi.models.api_errors import ApiErrors


def validate(offer: Offer, api_errors: ApiErrors) -> ApiErrors:
    venue = offer.venue if offer.venue else find_venue_by_id(offer.venueId)  # type: ignore [arg-type]

    if offer.isDigital:
        if not venue.isVirtual:  # type: ignore [union-attr]
            api_errors.add_error(
                "venue", 'Une offre numérique doit obligatoirement être associée au lieu "Offre numérique"'
            )

        if offer.is_offline_only:
            api_errors.add_error(
                "url", f"Une offre de sous-catégorie {offer.subcategory.pro_label} ne peut pas être numérique"
            )
    else:
        if venue.isVirtual:
            api_errors.add_error("venue", 'Une offre physique ne peut être associée au lieu "Offre numérique"')

    return api_errors
