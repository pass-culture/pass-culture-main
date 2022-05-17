from flask_login import login_required

from pcapi.core.offerers.models import Venue
from pcapi.core.providers.repository import get_enabled_providers_for_pro
from pcapi.core.providers.repository import get_providers_enabled_for_pro_excluding_specific_providers
from pcapi.core.providers.repository import get_providers_to_exclude
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
    provider_to_excludes = get_providers_to_exclude(venue)
    if len(provider_to_excludes) > 0:
        providers = get_providers_enabled_for_pro_excluding_specific_providers(provider_to_excludes)
    else:
        providers = get_enabled_providers_for_pro()

    return ListProviderResponse(__root__=[ProviderResponse.from_orm(provider) for provider in providers])
