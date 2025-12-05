from pcapi.core.offerers.repository import find_venue_by_id
from pcapi.core.offers.models import Offer
from pcapi.models.api_errors import ApiErrors
from pcapi.models.offer_mixin import OfferStatus


def validate(offer: Offer, api_errors: ApiErrors) -> ApiErrors:
    venue = offer.venue if offer.venue else find_venue_by_id(offer.venueId)
    assert venue is not None  # helps mypy below

    if offer.status == OfferStatus.DRAFT:
        return api_errors

    if offer.hasUrl:
        if offer.subcategory.is_offline_only:
            api_errors.add_error(
                "url", f"Une offre de sous-catégorie {offer.subcategory.pro_label} ne peut pas être numérique"
            )
    else:
        if offer.subcategory.is_online_only:
            api_errors.add_error("url", f'Une offre de catégorie {offer.subcategory.id} doit contenir un champ "url"')

    return api_errors
