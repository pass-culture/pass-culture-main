from flask_login import current_user

from pcapi.core.discoveries import discovery_service
from pcapi.routes.native.security import authenticated_and_active_user_required
from pcapi.serialization.decorator import spectree_serialize
from pcapi.utils.transaction_manager import atomic

from .. import blueprint
from .serialization import discoveries as serializers


@blueprint.native_route("/discoveries", methods=["POST"])
@atomic()
@authenticated_and_active_user_required
@spectree_serialize(response_model=serializers.DiscoveryResponseSchema, on_error_statuses=[400, 404], api=blueprint.api)
def create_discovery(body: serializers.CreateDiscoverySchema) -> serializers.DiscoveryResponseSchema:
    discovery = discovery_service.create_discovery(current_user.id, body)
    return serializers.DiscoveryResponseSchema.build(discovery)


@blueprint.native_route("/users/me/discoveries", methods=["GET"])
@atomic()
@authenticated_and_active_user_required
@spectree_serialize(response_model=serializers.DiscoveriesResponseSchema, api=blueprint.api)
def get_user_discoveries(query: serializers.DiscoveriesQuerySchema) -> serializers.DiscoveriesResponseSchema:
    discoveries = discovery_service.get_user_discoveries(current_user.id, query.page, query.limit)
    return serializers.DiscoveriesResponseSchema(
        page=query.page,
        limit=query.limit,
        discoveries=[serializers.DiscoveryResponseSchema.build(discovery) for discovery in discoveries],
    )
