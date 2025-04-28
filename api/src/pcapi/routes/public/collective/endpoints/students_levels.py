from pcapi.core.educational import models as educational_models
from pcapi.repository.session_management import atomic
from pcapi.routes.public import blueprints
from pcapi.routes.public import spectree_schemas
from pcapi.routes.public.collective.serialization import students_levels as students_levels_serialization
from pcapi.routes.public.documentation_constants import http_responses
from pcapi.routes.public.documentation_constants import tags
from pcapi.serialization.decorator import spectree_serialize
from pcapi.serialization.spec_tree import ExtendResponse as SpectreeResponse
from pcapi.validation.routes.users_authentifications import provider_api_key_required


@blueprints.public_api.route("/v2/collective/student-levels", methods=["GET"])
@atomic()
@provider_api_key_required
@spectree_serialize(
    api=spectree_schemas.public_api_schema,
    tags=[tags.COLLECTIVE_OFFER_ATTRIBUTES],
    resp=SpectreeResponse(
        **(
            {
                "HTTP_200": (
                    students_levels_serialization.CollectiveOffersListStudentLevelsResponseModel,
                    http_responses.HTTP_200_MESSAGE,
                )
            }
            | http_responses.HTTP_40X_SHARED_BY_API_ENDPOINTS
        )
    ),
)
def list_students_levels() -> students_levels_serialization.CollectiveOffersListStudentLevelsResponseModel:
    """
    Get Student Levels

    List student levels eligible for collective offers (for instance: `"Collège - 6e"`).
    """
    return students_levels_serialization.CollectiveOffersListStudentLevelsResponseModel(
        __root__=[
            students_levels_serialization.CollectiveOffersStudentLevelResponseModel(
                id=student_level.name, name=student_level.value
            )
            for student_level in educational_models.StudentLevels
        ]
    )
