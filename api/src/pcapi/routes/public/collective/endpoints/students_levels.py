from pcapi.core.educational import models as educational_models
from pcapi.routes.public import documentation_constants
from pcapi.routes.public import spectree_schemas
from pcapi.routes.public.collective.blueprint import collective_offers_blueprint
from pcapi.routes.public.collective.serialization import offers as offers_serialization
from pcapi.routes.public.collective.serialization import students_levels as students_levels_serialization
from pcapi.serialization.decorator import spectree_serialize
from pcapi.serialization.spec_tree import ExtendResponse as SpectreeResponse
from pcapi.validation.routes.users_authentifications import api_key_required


@collective_offers_blueprint.route("/collective/student-levels", methods=["GET"])
@spectree_serialize(
    api=spectree_schemas.public_api_schema,
    tags=[documentation_constants.COLLECTIVE_EDUCATIONAL_DATA],
    resp=SpectreeResponse(
        HTTP_200=(
            students_levels_serialization.CollectiveOffersListStudentLevelsResponseModel,
            "La liste des domaines d'éducation.",
        ),
        HTTP_401=(
            offers_serialization.AuthErrorResponseModel,
            "Authentification nécessaire",
        ),
    ),
)
@api_key_required
def list_students_levels() -> students_levels_serialization.CollectiveOffersListStudentLevelsResponseModel:
    # in French, to be used by Swagger for the API documentation
    """Récupération de la liste des publics cibles pour lesquelles des offres collectives peuvent être proposées."""
    return students_levels_serialization.CollectiveOffersListStudentLevelsResponseModel(
        __root__=[
            students_levels_serialization.CollectiveOffersStudentLevelResponseModel(
                id=student_level.name, name=student_level.value
            )
            for student_level in educational_models.StudentLevels
        ]
    )
