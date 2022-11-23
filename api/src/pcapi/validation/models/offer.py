from pcapi.core.offerers.repository import find_venue_by_id
from pcapi.core.offers.models import Offer
from pcapi.models.api_errors import ApiErrors


def validate(offer: Offer, api_errors: ApiErrors) -> ApiErrors:
    venue = offer.venue if offer.venue else find_venue_by_id(offer.venueId)

    if offer.isDigital:
        if not venue.isVirtual:  # type: ignore [union-attr]
            api_errors.add_error(
                "venue", 'Une offre numérique doit obligatoirement être associée au lieu "Offre numérique"'
            )

        if offer.subcategory.is_offline_only:
            api_errors.add_error(
                "url", f"Une offre de sous-catégorie {offer.subcategory.pro_label} ne peut pas être numérique"
            )
    else:
        if venue.isVirtual:
            api_errors.add_error("venue", 'Une offre physique ne peut être associée au lieu "Offre numérique"')

        if offer.subcategory.is_online_only:
            api_errors.add_error(
                "subcategory", f'Une offre de catégorie {offer.subcategory.id} doit contenir un champ "url"'
            )

    return api_errors
