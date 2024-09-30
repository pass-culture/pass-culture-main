import logging

from pcapi.core.geography import repository as geography_repository
from pcapi.models import api_errors
from pcapi.routes.public import blueprints
from pcapi.routes.public import spectree_schemas
from pcapi.routes.public.documentation_constants import http_responses
from pcapi.routes.public.documentation_constants import tags
from pcapi.serialization.decorator import spectree_serialize
from pcapi.serialization.spec_tree import ExtendResponse as SpectreeResponse
from pcapi.validation.routes.users_authentifications import provider_api_key_required

from .serializers.addresses import GetAddressQuery
from .serializers.addresses import GetAddressResponse


logger = logging.getLogger(__name__)


@blueprints.public_api.route("/public/offers/v1/addresses", methods=["GET"])
@provider_api_key_required
@spectree_serialize(
    api=spectree_schemas.public_api_schema,
    tags=[tags.ADDRESSES],
    response_model=GetAddressResponse,
    resp=SpectreeResponse(
        **(
            {"HTTP_200": (GetAddressResponse, http_responses.HTTP_200_MESSAGE)}
            # errors
            | http_responses.HTTP_40X_SHARED_BY_API_ENDPOINTS
            | http_responses.HTTP_400_BAD_REQUEST
            | http_responses.HTTP_404_ADDRESS_NOT_FOUND
        )
    ),
)
def get_address(
    query: GetAddressQuery,
) -> GetAddressResponse:
    """
    Get Address

    Return an address matching either a pair of coordinates (`latitude/longitude`) or a Base nationale d'adresse ID (`banId`).
    Only one method can be used per request; you cannot provide both `latitude/longitude` and `banId` at the same time.

    If no address matches the provided parameters, you may create a new address using the **Create Address** endpoint.
    """
    if query.banId:
        address = geography_repository.get_address_by_ban_id(query.banId)
        if not address:
            raise api_errors.ResourceNotFoundError({"address": "We could not find any address for the given `banId`"})
    else:
        address = geography_repository.get_address_by_lat_long(
            latitude=float(query.latitude),  # type: ignore[arg-type]
            longitude=float(query.longitude),  # type: ignore[arg-type]
        )
        if not address:
            raise api_errors.ResourceNotFoundError(
                {"address": "We could not find any address for the given `latitude/longitude`"}
            )

    return GetAddressResponse.from_orm(address)
