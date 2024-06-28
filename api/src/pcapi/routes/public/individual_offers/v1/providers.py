from pcapi.routes.public import blueprints
from pcapi.routes.public import spectree_schemas
from pcapi.routes.public.documentation_constants import http_responses
from pcapi.routes.public.documentation_constants import tags
from pcapi.routes.public.serialization import providers as providers_serialization
from pcapi.serialization.decorator import spectree_serialize
from pcapi.serialization.spec_tree import ExtendResponse as SpectreeResponse
from pcapi.validation.routes.users_authentifications import api_key_required
from pcapi.validation.routes.users_authentifications import current_api_key


@blueprints.public_api.route("/public/providers/v1/provider", methods=["GET"])
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
@api_key_required
def get_provider() -> providers_serialization.ProviderResponse:
    """
    Get my provider

    Return your provider information.
    """
    return providers_serialization.ProviderResponse.build_model(current_api_key.provider)
