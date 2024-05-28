import pcapi.core.educational.models as educational_models
from pcapi.routes.public import documentation_constants
from pcapi.routes.public import spectree_schemas
from pcapi.routes.public.collective.blueprint import collective_offers_blueprint
from pcapi.routes.public.collective.serialization import offers as offers_serialization
from pcapi.routes.serialization import national_programs as serialization
from pcapi.serialization.decorator import spectree_serialize
from pcapi.serialization.spec_tree import ExtendResponse as SpectreeResponse
from pcapi.validation.routes.users_authentifications import api_key_required


BASE_CODE_DESCRIPTIONS = {
    "HTTP_401": (offers_serialization.AuthErrorResponseModel, "Authentification nécessaire"),
    "HTTP_403": (
        offers_serialization.ErrorResponseModel,
        "Vous n'avez pas les droits nécessaires pour voir ces informations",
    ),
}


@collective_offers_blueprint.route("/collective/national-programs/", methods=["GET"])
@spectree_serialize(
    api=spectree_schemas.public_api_schema,
    tags=[documentation_constants.COLLECTIVE_EDUCATIONAL_DATA],
    resp=SpectreeResponse(
        **(BASE_CODE_DESCRIPTIONS),
        HTTP_200=(
            serialization.ListNationalProgramsResponseModel,
            "Il n'y a pas de dispositifs nationaux",
        ),
    ),
)
@api_key_required
def get_national_programs() -> serialization.ListNationalProgramsResponseModel:
    # in French, to be used by Swagger for the API documentation
    """Liste de tous les dispositifs nationaux connus"""
    query = educational_models.NationalProgram.query
    return serialization.ListNationalProgramsResponseModel(
        __root__=[serialization.NationalProgramModel(id=program.id, name=program.name) for program in query]
    )
