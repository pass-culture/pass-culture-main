from pcapi.core.educational import models
from pcapi.routes.public import blueprints
from pcapi.routes.public import spectree_schemas
from pcapi.routes.public.collective.serialization import additional_fee_types
from pcapi.routes.public.documentation_constants import http_responses
from pcapi.routes.public.documentation_constants import tags
from pcapi.routes.public.services.authentication import api_key_required
from pcapi.serialization.decorator import spectree_serialize
from pcapi.serialization.spec_tree import ExtendResponse as SpectreeResponse
from pcapi.utils.transaction_manager import atomic


@blueprints.public_api.route("/v2/collective/additional-fee-types", methods=["GET"])
@atomic()
@api_key_required
@spectree_serialize(
    api=spectree_schemas.public_api_schema,
    tags=[tags.COLLECTIVE_OFFER_ATTRIBUTES],
    resp=SpectreeResponse(
        **(
            {"HTTP_200": (additional_fee_types.GetAdditionalFeeTypes, http_responses.HTTP_200_MESSAGE)}
            | http_responses.HTTP_40X_SHARED_BY_API_ENDPOINTS
        )
    ),
)
def get_additional_fee_types() -> additional_fee_types.GetAdditionalFeeTypes:
    """
    Get Collective Additional Fee Types

    Return the list of available types for a collective offer additional fee.

    See the `additionalFees` field in the collective routes.
    """
    return additional_fee_types.GetAdditionalFeeTypes(
        [
            additional_fee_types.GetAdditionalFeeType(name=fee_type.name)
            for fee_type in models.CollectiveAdditionalFeeType
        ]
    )
