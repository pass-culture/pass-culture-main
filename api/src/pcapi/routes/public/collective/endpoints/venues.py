from pcapi.core.offerers import api as offerers_api
from pcapi.core.providers import repository as providers_repository
from pcapi.repository import atomic
from pcapi.routes.public import blueprints
from pcapi.routes.public import spectree_schemas
from pcapi.routes.public.collective.serialization import venues as serialization
from pcapi.routes.public.documentation_constants import http_responses
from pcapi.routes.public.documentation_constants import tags
from pcapi.routes.public.serialization import venues as venues_serialization
from pcapi.serialization.decorator import spectree_serialize
from pcapi.serialization.spec_tree import ExtendResponse as SpectreeResponse
from pcapi.validation.routes.users_authentifications import current_api_key
from pcapi.validation.routes.users_authentifications import provider_api_key_required


@blueprints.deprecated_collective_public_api.route("/v2/collective/venues", methods=["GET"])
@atomic()
@provider_api_key_required
@spectree_serialize(
    api=spectree_schemas.deprecated_collective_public_api_schema,
    tags=[tags.DEPRECATED_COLLECTIVE_VENUES],
    deprecated=True,
    resp=SpectreeResponse(
        **(
            {
                "HTTP_200": (
                    serialization.CollectiveOffersListVenuesResponseModel,
                    http_responses.HTTP_200_MESSAGE,
                )
            }
            | http_responses.HTTP_40X_SHARED_BY_API_ENDPOINTS
        )
    ),
)
def list_venues() -> serialization.CollectiveOffersListVenuesResponseModel:
    """
    Get all venues

    This route is deprecated and should not be used anymore.
    """
    venues = providers_repository.get_providers_venues(current_api_key.providerId)

    return serialization.CollectiveOffersListVenuesResponseModel(
        __root__=[venues_serialization.VenueResponse.build_model(venue) for venue in venues]
    )


@blueprints.deprecated_collective_public_api.route("/v2/collective/offerer_venues", methods=["GET"])
@atomic()
@provider_api_key_required
@spectree_serialize(
    api=spectree_schemas.deprecated_collective_public_api_schema,
    tags=[tags.DEPRECATED_COLLECTIVE_VENUES],
    deprecated=True,
    resp=SpectreeResponse(
        **(
            {
                "HTTP_200": (
                    venues_serialization.GetOfferersVenuesResponse,
                    http_responses.HTTP_200_MESSAGE,
                )
            }
            | http_responses.HTTP_40X_SHARED_BY_API_ENDPOINTS
        )
    ),
)
def deprecated_get_offerer_venues(
    query: venues_serialization.GetOfferersVenuesQuery,
) -> venues_serialization.GetOfferersVenuesResponse:
    """
    [DEPRECATED]

    You should be using [**/public/offer/v1/offerer_venues endpoint**](/rest-api#tag/Venues/operation/GetOffererVenues).
    """
    rows = offerers_api.get_providers_offerer_and_venues(current_api_key.provider, query.siren)
    return venues_serialization.GetOfferersVenuesResponse.serialize_offerers_venues(rows)
