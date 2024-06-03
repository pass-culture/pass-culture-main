from flask_login import login_required

from pcapi.core.offerers.models import Venue
import pcapi.core.providers.repository as providers_repository
from pcapi.routes.serialization.providers_serialize import ListProviderResponse
from pcapi.routes.serialization.providers_serialize import ProviderResponse
from pcapi.serialization.decorator import spectree_serialize

from . import blueprint


@blueprint.pro_private_api.route("/venueProviders/<int:venue_id>", methods=["GET"])
@login_required
@spectree_serialize(
    response_model=ListProviderResponse,  # type: ignore[arg-type]
    on_success_status=200,
    on_error_statuses=[401, 404],
    api=blueprint.pro_private_schema,
)
def get_providers_by_venue(venue_id: int) -> ListProviderResponse:
    venue = Venue.query.get_or_404(venue_id)
    providers = providers_repository.get_available_providers(venue)
    return ListProviderResponse(__root__=[ProviderResponse.from_orm(provider) for provider in providers])
