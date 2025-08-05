from flask_login import login_required

import pcapi.core.providers.repository as providers_repository
from pcapi.core.offerers.models import Venue
from pcapi.models.utils import get_or_404
from pcapi.routes.serialization.providers_serialize import ListProviderResponse
from pcapi.routes.serialization.providers_serialize import ProviderResponse
from pcapi.serialization.decorator import spectree_serialize
from pcapi.utils.transaction_manager import atomic

from . import blueprint


@blueprint.pro_private_api.route("/venueProviders/<int:venue_id>", methods=["GET"])
@atomic()
@login_required
@spectree_serialize(
    response_model=ListProviderResponse,  # type: ignore[arg-type]
    on_success_status=200,
    on_error_statuses=[401, 404],
    api=blueprint.pro_private_schema,
)
def get_providers_by_venue(venue_id: int) -> ListProviderResponse:
    venue = get_or_404(Venue, venue_id)
    providers = providers_repository.get_available_providers(venue)
    return ListProviderResponse(__root__=[ProviderResponse.from_orm(provider) for provider in providers])
