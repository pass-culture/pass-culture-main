from flask_login import login_required

from pcapi.core.offerers.models import Venue
from pcapi.core.providers.repository import get_enabled_providers_for_pro
from pcapi.core.providers.repository import get_providers_enabled_for_pro_excluding_specific_provider
from pcapi.core.providers.repository import has_allocine_pivot_for_venue
from pcapi.local_providers import AllocineStocks
from pcapi.routes.apis import private_api
from pcapi.routes.serialization import as_dict
from pcapi.routes.serialization import providers_serialize as serializers
from pcapi.serialization.decorator import spectree_serialize
from pcapi.utils.rest import load_or_404


@private_api.route("/providers/<venue_id>", methods=["GET"])
@login_required
@spectree_serialize(response_model=serializers.ListProviderResponse, on_error_statuses=[404])
def get_providers_by_venue(venue_id: str) -> serializers.ListProviderResponse:
    venue = load_or_404(Venue, venue_id)
    has_allocine_pivot = has_allocine_pivot_for_venue(venue)
    if has_allocine_pivot:
        providers = get_enabled_providers_for_pro()
    else:
        allocine_local_class = AllocineStocks.__name__
        providers = get_providers_enabled_for_pro_excluding_specific_provider(allocine_local_class)
    result = []
    for provider in providers:
        provider_dict = as_dict(provider)
        del provider_dict["apiUrl"]
        del provider_dict["authToken"]
        del provider_dict["pricesInCents"]
        result.append(provider_dict)
    return serializers.ListProviderResponse(__root__=result)
