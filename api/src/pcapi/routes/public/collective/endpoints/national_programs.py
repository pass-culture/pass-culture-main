from pcapi.core.educational import repository
from pcapi.routes.public import blueprints
from pcapi.routes.public import spectree_schemas
from pcapi.routes.public.documentation_constants import http_responses
from pcapi.routes.public.documentation_constants import tags
from pcapi.routes.public.services.authentication import api_key_required
from pcapi.routes.serialization import educational_serialize
from pcapi.serialization.decorator import spectree_serialize
from pcapi.serialization.spec_tree import ExtendResponse as SpectreeResponse
from pcapi.utils.transaction_manager import atomic


@blueprints.public_api.route("/v2/collective/national-programs/", methods=["GET"])
@atomic()
@api_key_required
@spectree_serialize(
    api=spectree_schemas.public_api_schema,
    tags=[tags.COLLECTIVE_OFFER_ATTRIBUTES],
    resp=SpectreeResponse(
        **(
            {"HTTP_200": (educational_serialize.ListNationalProgramsResponseModel, http_responses.HTTP_200_MESSAGE)}
            | http_responses.HTTP_40X_SHARED_BY_API_ENDPOINTS
        ),
    ),
)
def get_national_programs() -> educational_serialize.ListNationalProgramsResponseModel:
    """
    Get National Programs

    List national programs (for instance: `Collège au cinéma`, `Jeunes en librairie`...)
    """
    programs = repository.get_active_national_programs()

    return educational_serialize.ListNationalProgramsResponseModel(
        [educational_serialize.NationalProgramModelV2.model_validate(program) for program in programs]
    )
