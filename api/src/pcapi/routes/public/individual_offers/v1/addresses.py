import logging

from pcapi.connectors import api_adresse
from pcapi.core.geography import repository as geography_repository
from pcapi.core.offerers import api as offerers_api
from pcapi.core.offerers import schemas as offerers_schemas
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
from .serializers.addresses import PostAddressBody


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


@blueprints.public_api.route("/public/offers/v1/addresses", methods=["POST"])
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
        )
    ),
)
def post_address(
    body: PostAddressBody,
) -> GetAddressResponse:
    """
    Create Address

    This endpoint adds a new address to the Pass Culture database, allowing you to associate it with your offers for localization.

    Before inserting the address, this endpoints does two things :

    - **Address Existence Check:** The system verifies if an address with the same coordinates (`latitude`, longitude) already exists in the database. If it does, the request will return a 400 Bad Request error.

    - **BAN API Lookup:** The endpoint checks the address against the Base Adresse Nationale (BAN) API. If the address exists there, the `banId` will be added to the stored address.
    """
    existing_address = geography_repository.get_address_by_lat_long(
        latitude=float(body.latitude),
        longitude=float(body.longitude),
    )

    if existing_address:
        raise api_errors.ApiErrors({"global": "address already exists"})

    is_manual_edition = False
    try:
        api_adresse.get_address(body.street, body.postalCode, body.city, strict=True)
    except api_adresse.NoResultException:
        is_manual_edition = True  # Address was not found on BAN API

    data = body.dict()
    address = offerers_api.create_offerer_address_from_address_api(
        offerers_schemas.AddressBodyModel(isManualEdition=is_manual_edition, **data)
    )

    return GetAddressResponse.from_orm(address)
