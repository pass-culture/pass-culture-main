from flask_login import login_required

from pcapi.core.offerers.models import Venue
from pcapi.core.providers.repository import get_enabled_providers_for_pro
from pcapi.core.providers.repository import get_providers_enabled_for_pro_excluding_specific_provider
from pcapi.core.providers.repository import is_venue_known_by_allocine
from pcapi.local_providers import AllocineStocks
from pcapi.routes.serialization.providers_serialize import ListProviderResponse
from pcapi.routes.serialization.providers_serialize import ProviderResponse
from pcapi.serialization.decorator import spectree_serialize
from pcapi.utils.rest import load_or_404

from . import blueprint


@blueprint.pro_private_api.route("/providers/<venue_id>", methods=["GET"])
@login_required
@spectree_serialize(
    response_model=ListProviderResponse,  # type: ignore [arg-type]
    on_success_status=200,
    on_error_statuses=[401, 404],
    api=blueprint.pro_private_schema,
)
def get_providers_by_venue(venue_id: str) -> ListProviderResponse:
    venue = load_or_404(Venue, venue_id)
    known_venue = is_venue_known_by_allocine(venue)

    if known_venue:
        providers = get_enabled_providers_for_pro()
    else:
        allocine_local_class = AllocineStocks.__name__
        providers = get_providers_enabled_for_pro_excluding_specific_provider(allocine_local_class)
    return ListProviderResponse(__root__=[ProviderResponse.from_orm(provider) for provider in providers])
