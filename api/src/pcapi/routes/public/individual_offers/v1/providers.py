from pcapi.core.providers import api as providers_api
from pcapi.core.providers import exceptions as providers_exceptions
from pcapi.core.providers import repository as providers_repository
from pcapi.models import api_errors
from pcapi.routes.public import blueprints
from pcapi.routes.public import spectree_schemas
from pcapi.routes.public.documentation_constants import http_responses
from pcapi.routes.public.documentation_constants import tags
from pcapi.routes.public.serialization import providers as providers_serialization
from pcapi.routes.public.serialization import venues as venues_serialization
from pcapi.serialization.decorator import spectree_serialize
from pcapi.serialization.spec_tree import ExtendResponse as SpectreeResponse
from pcapi.validation.routes.users_authentifications import api_key_required
from pcapi.validation.routes.users_authentifications import current_api_key


@blueprints.public_api.route("/public/providers/v1/provider", methods=["GET"])
@api_key_required
@spectree_serialize(
    api=spectree_schemas.public_api_schema,
    tags=[tags.PROVIDERS],
    response_model=providers_serialization.ProviderResponse,
    resp=SpectreeResponse(
        **(
            {"HTTP_200": (providers_serialization.ProviderResponse, "Your provider has been returned")}
            # errors
            | http_responses.HTTP_40X_SHARED_BY_API_ENDPOINTS
        )
    ),
)
def get_provider() -> providers_serialization.ProviderResponse:
    """
    Get my provider

    Return your provider information.
    """
    return providers_serialization.ProviderResponse.build_model(current_api_key.provider)


@blueprints.public_api.route("/public/providers/v1/provider", methods=["PATCH"])
@api_key_required
@spectree_serialize(
    api=spectree_schemas.public_api_schema,
    tags=[tags.PROVIDERS],
    response_model=providers_serialization.ProviderResponse,
    resp=SpectreeResponse(
        **(
            {"HTTP_200": (providers_serialization.ProviderResponse, "Your provider has been returned")}
            # errors
            | http_responses.HTTP_40X_SHARED_BY_API_ENDPOINTS
            | http_responses.HTTP_400_BAD_REQUEST
        )
    ),
)
def update_provider(body: providers_serialization.ProviderUpdate) -> providers_serialization.ProviderResponse:
    """
    Update my provider

    Endpoint to set the urls used by our notification system to notify/request your solution.
    """
    provider = current_api_key.provider
    update_body = body.dict(exclude_unset=True)

    try:
        provider = providers_api.update_provider_external_urls(
            provider,
            notification_external_url=update_body.get("notification_url", providers_api.UNCHANGED),
            booking_external_url=update_body.get("booking_url", providers_api.UNCHANGED),
            cancel_external_url=update_body.get("cancel_url", providers_api.UNCHANGED),
        )
    except providers_exceptions.TicketingUrlsCannotBeUnset as e:
        raise api_errors.ApiErrors(
            {
                "ticketing_urls": {
                    "description": "You cannot unset your `booking_url` and `cancel_url` because you have event(s) with stocks linked to your ticketing system",
                    "blocking_events_ids": e.blocking_events_ids,
                }
            }
        )
    except providers_exceptions.TicketingUrlsMustBeBothSet:
        raise api_errors.ApiErrors(
            {"ticketing_urls": "Your `booking_url` and `cancel_url` must be either both set or both unset"}
        )

    return providers_serialization.ProviderResponse.build_model(provider)


@blueprints.public_api.route("/public/providers/v1/venues/<int:venue_id>", methods=["PATCH"])
@spectree_serialize(
    on_success_status=204,
    api=spectree_schemas.public_api_schema,
    tags=[tags.PROVIDERS],
    response_model=venues_serialization.VenueResponse,
    resp=SpectreeResponse(
        **(
            http_responses.HTTP_204_VENUE_PROVIDER_EXTERNAL_URLS_UPDATE_SUCCESS
            # errors
            | http_responses.HTTP_40X_SHARED_BY_API_ENDPOINTS
            | http_responses.HTTP_400_BAD_REQUEST
            | http_responses.HTTP_404_VENUE_NOT_FOUND
        )
    ),
)
@api_key_required
def update_venue_external_urls(
    venue_id: int,
    body: providers_serialization.VenueProviderExternalUrlsUpdate,
) -> None:
    """
    Update external urls for specific venues

    Endpoint to set the urls used by our notification system to notify/request your solution.
    """

    venue_provider = providers_repository.get_venue_provider_by_venue_and_provider_ids(
        venue_id=venue_id, provider_id=current_api_key.provider.id
    )

    if not venue_provider:
        raise api_errors.ResourceNotFoundError({"global": "This venue cannot be found"})

    update_body = body.dict(exclude_unset=True)

    try:
        providers_api.update_venue_provider_external_urls(
            venue_provider,
            notification_external_url=update_body.get("notification_url", providers_api.UNCHANGED),
            booking_external_url=update_body.get("booking_url", providers_api.UNCHANGED),
            cancel_external_url=update_body.get("cancel_url", providers_api.UNCHANGED),
        )
    except providers_exceptions.TicketingUrlsCannotBeUnset as e:
        raise api_errors.ApiErrors(
            {
                "ticketing_urls": {
                    "description": "You cannot unset your `booking_url` and `cancel_url` because you have event(s) with stocks linked to your ticketing system",
                    "blocking_events_ids": e.blocking_events_ids,
                }
            }
        )
    except providers_exceptions.TicketingUrlsMustBeBothSet:
        raise api_errors.ApiErrors(
            {"ticketing_urls": "Your `booking_url` and `cancel_url` must be either both set or both unset"}
        )
