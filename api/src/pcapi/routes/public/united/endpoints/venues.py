from pcapi.core.providers import repository as providers_repository
from pcapi.routes.public.collective.serialization import venues as serialization
import pcapi.routes.public.serialization.venues as venues_serialization
from pcapi.routes.public.united import utils
from pcapi.validation.routes.users_authentifications import current_api_key


VENUES_TAG = "Venues"


@utils.public_api_route("/venues", method="GET", tags=[VENUES_TAG])
def list_venues() -> serialization.CollectiveOffersListVenuesResponseModel:
    """Venues list

    Fetch all of the authenticated user's venues: all that are linked to
    the API token.

    All venues are listed with their coordinates.
    """
    venues = providers_repository.get_providers_venues(current_api_key.providerId)

    return serialization.CollectiveOffersListVenuesResponseModel(
        __root__=[venues_serialization.VenueResponse.build_model(venue) for venue in venues]
    )
