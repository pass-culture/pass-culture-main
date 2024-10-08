import logging

from pcapi.core.geography import models as geography_models
from pcapi.models import api_errors
from pcapi.routes.public import blueprints
from pcapi.routes.public import spectree_schemas
from pcapi.routes.public.documentation_constants import http_responses
from pcapi.routes.public.documentation_constants import tags
from pcapi.serialization.decorator import spectree_serialize
from pcapi.serialization.spec_tree import ExtendResponse as SpectreeResponse
from pcapi.validation.routes.users_authentifications import provider_api_key_required

from .serializers.addresses import GetAddressResponse


logger = logging.getLogger(__name__)


@blueprints.public_api.route("/public/offers/v1/addresses/<int:address_id>", methods=["GET"])
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
    address_id: int,
) -> GetAddressResponse:
    """
    Get Address

    Return an address by id
    """
    address = geography_models.Address.query.get(address_id)
    if not address:
        raise api_errors.ResourceNotFoundError({"address": "We could not find any address for the given `id`"})

    return GetAddressResponse.from_orm(address)
