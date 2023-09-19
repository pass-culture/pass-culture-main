from pcapi.core.offerers import api as offerers_api
import pcapi.routes.public.serialization.venues as venues_serialization
from pcapi.routes.public.united import utils
from pcapi.validation.routes.users_authentifications import current_api_key


OFFERERS_TAG = "Offerers"


@utils.public_api_route("/offerer/venues", method="GET", tags=[OFFERERS_TAG])
def get_offerer_venues(
    query: venues_serialization.GetOfferersVenuesQuery,
) -> venues_serialization.GetOfferersVenuesResponse:
    """Offerers' venues

    Fetch authenticated user's venues, grouped by offerer.
    """
    rows = offerers_api.get_providers_offerer_and_venues(current_api_key.provider, query.siren)
    return venues_serialization.GetOfferersVenuesResponse.serialize_offerers_venues(rows)
