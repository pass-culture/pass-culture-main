from flask_login import login_required

from pcapi.core.providers import api
from pcapi.core.providers import repository
from pcapi.flask_app import private_api
from pcapi.routes.serialization.venue_provider_serialize import ListVenueProviderQuery
from pcapi.routes.serialization.venue_provider_serialize import ListVenueProviderResponse
from pcapi.routes.serialization.venue_provider_serialize import PostVenueProviderBody
from pcapi.routes.serialization.venue_provider_serialize import VenueProviderResponse
from pcapi.serialization.decorator import spectree_serialize


@private_api.route("/venueProviders", methods=["GET"])
@login_required
@spectree_serialize(on_success_status=200, response_model=ListVenueProviderResponse)
def list_venue_providers(query: ListVenueProviderQuery) -> ListVenueProviderResponse:
    venue_provider_list = repository.get_venue_provider_list(query.venue_id)
    return ListVenueProviderResponse(
        venue_providers=[VenueProviderResponse.from_orm(venue_provider) for venue_provider in venue_provider_list]
    )


@private_api.route("/venueProviders", methods=["POST"])
@login_required
@spectree_serialize(on_success_status=201, response_model=VenueProviderResponse)
def create_venue_provider(body: PostVenueProviderBody) -> VenueProviderResponse:
    body.venueIdAtOfferProvider = None

    new_venue_provider = api.create_venue_provider(body)

    return VenueProviderResponse.from_orm(new_venue_provider)
