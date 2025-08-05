import logging

from pcapi.connectors import api_adresse
from pcapi.core.geography import models as geography_models
from pcapi.core.geography import repository as geography_repository
from pcapi.core.offerers import api as offerers_api
from pcapi.models import api_errors
from pcapi.models import db
from pcapi.routes.public import blueprints
from pcapi.routes.public import spectree_schemas
from pcapi.routes.public.documentation_constants import http_responses
from pcapi.routes.public.documentation_constants import tags
from pcapi.serialization.decorator import spectree_serialize
from pcapi.serialization.spec_tree import ExtendResponse as SpectreeResponse
from pcapi.utils.transaction_manager import atomic
from pcapi.validation.routes.users_authentifications import provider_api_key_required

from .serializers.addresses import AddressModel
from .serializers.addresses import AddressResponse
from .serializers.addresses import SearchAddressResponse


logger = logging.getLogger(__name__)


@blueprints.public_api.route("/public/offers/v1/addresses/<int:address_id>", methods=["GET"])
@atomic()
@provider_api_key_required
@spectree_serialize(
    api=spectree_schemas.public_api_schema,
    tags=[tags.ADDRESSES],
    response_model=AddressResponse,
    resp=SpectreeResponse(
        **(
            {"HTTP_200": (AddressResponse, http_responses.HTTP_200_MESSAGE)}
            # errors
            | http_responses.HTTP_40X_SHARED_BY_API_ENDPOINTS
            | http_responses.HTTP_400_BAD_REQUEST
            | http_responses.HTTP_404_ADDRESS_NOT_FOUND
        )
    ),
)
def get_address(
    address_id: int,
) -> AddressResponse:
    """
    Get Address

    Return an address by id
    """
    address = db.session.get(geography_models.Address, address_id)
    if not address:
        raise api_errors.ResourceNotFoundError({"address": "We could not find any address for the given `id`"})

    return AddressResponse.from_orm(address)


@blueprints.public_api.route("/public/offers/v1/addresses/search", methods=["GET"])
@atomic()
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
        )
    ),
)
def search_addresses(query: AddressModel) -> SearchAddressResponse:
    """
    Search Addresses

    This endpoint returns addresses that match the provided literal address.
    To enhance the precision of the search, you can provide optional latitude and longitude coordinates.


    If no address matches the given parameters, you may use the **Create Address** endpoint to add a new address.

    **Important Note:** If the municipality (identified by the `city` and `postalCode` parameters) is not found on the [**Base Nationale d'Adresses (BAN) API**](https://adresse.data.gouv.fr/),
    this endpoints will return a **400 Bad Request** error.
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
            # we use the postal sent by the client because in the case of a big city like Paris or Lyon
            # `api_adresse.get_municipality_centroid` returns a default postal code (the postal code of the
            # 1st neighborhood) which might lead to incoherent addresses
            postal_code=query.postalCode,
            latitude=query.latitude,
            longitude=query.longitude,
        )

    return SearchAddressResponse(addresses=[AddressResponse.from_orm(address) for address in addresses])


@blueprints.public_api.route("/public/offers/v1/addresses", methods=["POST"])
@atomic()
@provider_api_key_required
@spectree_serialize(
    api=spectree_schemas.public_api_schema,
    tags=[tags.ADDRESSES],
    response_model=AddressResponse,
    resp=SpectreeResponse(
        **(
            {"HTTP_200": (AddressResponse, http_responses.HTTP_200_MESSAGE)}
            # errors
            | http_responses.HTTP_40X_SHARED_BY_API_ENDPOINTS
            | http_responses.HTTP_400_BAD_REQUEST
        )
    ),
)
def create_address(body: AddressModel) -> AddressResponse:
    """
    Create Address

    This endpoint allows you to add an address to the Pass Culture database.

    Before the address is saved, it will be normalized using the [**Base Nationale d'Adresses (BAN) API**](https://adresse.data.gouv.fr/).

    **Important Notes:**

    - If the address is not found in the BAN API, you must provide valid `latitude` and `longitude` coordinates.
    Otherwise, the endpoint will return a **400 Bad Request** error.

    - If the municipality (identified by the `city` and `postalCode` parameters) is not found in the BAN API,
    the endpoint will return a **400 Bad Request** error.
    """
    ban_address = _get_ban_address_or_none(street=body.street, postal_code=body.postalCode, city=body.city)

    if ban_address:
        location_data = offerers_api.LocationData(
            street=ban_address.street,
            city=ban_address.city,
            postal_code=ban_address.postcode,
            insee_code=ban_address.citycode,
            latitude=ban_address.latitude,
            longitude=ban_address.longitude,
            ban_id=ban_address.id,
        )
    else:
        municipality_address = _get_municipality_or_raise_400(city=body.city, postal_code=body.postalCode)
        if body.latitude is None or body.longitude is None:
            raise api_errors.ApiErrors(
                {
                    "__root__": [
                        "The address you provided could not be found in the BAN API. Please provide valid `latitude` and `longitude` coordinates for this address to proceed."
                    ]
                }
            )
        location_data = offerers_api.LocationData(
            # Data coming from the BAN API
            city=municipality_address.city,
            insee_code=municipality_address.citycode,
            ban_id=None,
            # Data coming from the request body
            street=body.street,
            # we use the postal sent by the client because in the case of a big city like Paris or Lyon
            # `api_adresse.get_municipality_centroid` returns a default postal code (the postal code of the
            # 1st neighborhood) which might lead to incoherent addresses
            postal_code=body.postalCode,
            latitude=body.latitude,
            longitude=body.longitude,
        )

    address = offerers_api.get_or_create_address(
        location_data=location_data,
        is_manual_edition=ban_address is None,
    )

    return AddressResponse.from_orm(address)


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
    except (api_adresse.NoResultException, api_adresse.InvalidFormatException):
        ban_address = None
    except api_adresse.AdresseApiServerErrorException:
        raise api_errors.ApiErrors({"global": ["BAN API is unavailable"]}, status_code=500)

    return ban_address


def _get_municipality_or_raise_400(city: str, postal_code: str) -> api_adresse.AddressInfo:
    try:
        municipality_address = api_adresse.get_municipality_centroid(city=city, postcode=postal_code)
    except api_adresse.NoResultException:
        raise api_errors.ApiErrors(
            {"__root__": [f"No municipality found for `city={city}` and `postalCode={postal_code}`"]}
        )
    except api_adresse.InvalidFormatException:
        raise api_errors.ApiErrors({"__root__": [f"Invalid format for `city={city}` and `postalCode={postal_code}`"]})
    except api_adresse.AdresseApiServerErrorException:
        raise api_errors.ApiErrors({"global": ["BAN API is unavailable"]}, status_code=500)

    return municipality_address
