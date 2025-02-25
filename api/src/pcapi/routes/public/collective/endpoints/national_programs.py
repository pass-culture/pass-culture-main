import typing

from pcapi.core.educational import models as educational_models
from pcapi.routes.public import blueprints
from pcapi.routes.public import spectree_schemas
from pcapi.routes.public.documentation_constants import http_responses
from pcapi.routes.public.documentation_constants import tags
from pcapi.routes.serialization import national_programs as serialization
from pcapi.serialization.decorator import spectree_serialize
from pcapi.serialization.spec_tree import ExtendResponse as SpectreeResponse
from pcapi.validation.routes.users_authentifications import provider_api_key_required


@blueprints.public_api.route("/v2/collective/national-programs/", methods=["GET"])
@provider_api_key_required
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
def get_national_programs() -> serialization.ListNationalProgramsResponseModel:
    """
    Get National Programs

    List national programs (for instance: `Collège au cinéma`, `Jeunes en librairie`...)
    """
    programs: typing.Iterable[educational_models.NationalProgram] = educational_models.NationalProgram.query.filter(
        educational_models.NationalProgram.isActive.is_(True)
    )

    return serialization.ListNationalProgramsResponseModel(
        __root__=[serialization.NationalProgramModel(id=program.id, name=program.name) for program in programs]
    )
