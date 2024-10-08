import logging

from pcapi.connectors import api_adresse
from pcapi.core.geography import models as geography_models
from pcapi.core.geography import repository as geography_repository
from pcapi.models import api_errors
from pcapi.routes.public import blueprints
from pcapi.routes.public import spectree_schemas
from pcapi.routes.public.documentation_constants import http_responses
from pcapi.routes.public.documentation_constants import tags
from pcapi.serialization.decorator import spectree_serialize
from pcapi.serialization.spec_tree import ExtendResponse as SpectreeResponse
from pcapi.validation.routes.users_authentifications import provider_api_key_required

from .serializers.addresses import GetAddressResponse
from .serializers.addresses import SearchAddressQuery
from .serializers.addresses import SearchAddressResponse


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


@blueprints.public_api.route("/public/offers/v1/addresses/search", methods=["GET"])
@provider_api_key_required
@spectree_serialize(
    api=spectree_schemas.public_api_schema,
    tags=[tags.ADDRESSES],
    response_model=SearchAddressResponse,
    resp=SpectreeResponse(
        **(
            {"HTTP_200": (SearchAddressResponse, http_responses.HTTP_200_MESSAGE)}
            # errors
            | http_responses.HTTP_40X_SHARED_BY_API_ENDPOINTS
            | http_responses.HTTP_400_BAD_REQUEST
            | http_responses.HTTP_404_MUNICIPALITY_NOT_FOUND
        )
    ),
)
def search_addresses(
    query: SearchAddressQuery,
) -> SearchAddressResponse:
    """
    Search Addresses

    This endpoint returns addresses that match the provided literal address.
    To enhance the precision of the search, you can provide optional latitude and longitude coordinates.

    If the municipality does not exist on the Base Nationale d'Adresses (BAN) API, this endpoints will return
    a **400 Resource not found** error.

    If no address matches the given parameters, you may use the **Create Address** endpoint to add a new address.
    """
    ban_address = _get_ban_address_or_none(street=query.street, postal_code=query.postalCode, city=query.city)

    if ban_address:
        addresses = geography_repository.search_addresses(
            # `query.street` is there to make mypy happy,
            # `ban_address.street` should alway be defined
            # as we call `api_adresse.get_address` with `strict=True`
            street=ban_address.street or query.street,
            city=ban_address.city,
            postal_code=ban_address.postcode,
            latitude=query.latitude,
            longitude=query.longitude,
        )
    else:
        municipality_address = _get_municipality_or_raise_400(city=query.city, postal_code=query.postalCode)
        addresses = geography_repository.search_addresses(
            street=query.street,
            city=municipality_address.city,  # we use normalized data for `city`
            postal_code=municipality_address.postcode,  # we use normalized data for `postal_code`
            latitude=query.latitude,
            longitude=query.longitude,
        )

    return SearchAddressResponse(addresses=[GetAddressResponse.from_orm(address) for address in addresses])


def _get_ban_address_or_none(street: str, city: str, postal_code: str) -> api_adresse.AddressInfo | None:
    """
    Call BAN API in strict mode. If no result found, return `None`.
    """
    try:
        ban_address = api_adresse.get_address(
            address=street,
            postcode=postal_code,
            city=city,
            strict=True,
        )
    except api_adresse.NoResultException:
        ban_address = None

    return ban_address


def _get_municipality_or_raise_400(city: str, postal_code: str) -> api_adresse.AddressInfo:
    try:
        municipality_address = api_adresse.get_municipality_centroid(city=city, postcode=postal_code)
    except api_adresse.NoResultException:
        raise api_errors.ApiErrors(
            {"__root__": [f"No municipality found for `city={city}` and `postalCode={postal_code}`"]}
        )

    return municipality_address
