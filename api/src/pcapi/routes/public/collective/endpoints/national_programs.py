import pcapi.core.educational.models as educational_models
from pcapi.routes.public import spectree_schemas
from pcapi.routes.public.collective.blueprint import collective_offers_blueprint
from pcapi.routes.public.documentation_constants import http_responses
from pcapi.routes.public.documentation_constants import tags
from pcapi.routes.serialization import national_programs as serialization
from pcapi.serialization.decorator import spectree_serialize
from pcapi.serialization.spec_tree import ExtendResponse as SpectreeResponse
from pcapi.validation.routes.users_authentifications import api_key_required


@collective_offers_blueprint.route("/collective/national-programs/", methods=["GET"])
@spectree_serialize(
    api=spectree_schemas.public_api_schema,
    tags=[tags.COLLECTIVE_OFFER_ATTRIBUTES],
    resp=SpectreeResponse(
        **(
            {"HTTP_200": (serialization.ListNationalProgramsResponseModel, http_responses.HTTP_200_MESSAGE)}
            | http_responses.HTTP_40X_SHARED_BY_API_ENDPOINTS
        ),
    ),
)
@api_key_required
def get_national_programs() -> serialization.ListNationalProgramsResponseModel:
    """
    Get all known national programs
    """
    query = educational_models.NationalProgram.query
    return serialization.ListNationalProgramsResponseModel(
        __root__=[serialization.NationalProgramModel(id=program.id, name=program.name) for program in query]
    )
