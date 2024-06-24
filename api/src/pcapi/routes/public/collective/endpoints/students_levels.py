from pcapi.core.educational import models as educational_models
from pcapi.routes.public import spectree_schemas
from pcapi.routes.public.collective.blueprint import collective_offers_blueprint
from pcapi.routes.public.collective.serialization import students_levels as students_levels_serialization
from pcapi.routes.public.documentation_constants import http_responses
from pcapi.routes.public.documentation_constants import tags
from pcapi.serialization.decorator import spectree_serialize
from pcapi.serialization.spec_tree import ExtendResponse as SpectreeResponse
from pcapi.validation.routes.users_authentifications import api_key_required


@collective_offers_blueprint.route("/collective/student-levels", methods=["GET"])
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
@api_key_required
def list_students_levels() -> students_levels_serialization.CollectiveOffersListStudentLevelsResponseModel:
    """
    Get student levels eligible for collective offers
    """
    return students_levels_serialization.CollectiveOffersListStudentLevelsResponseModel(
        __root__=[
            students_levels_serialization.CollectiveOffersStudentLevelResponseModel(
                id=student_level.name, name=student_level.value
            )
            for student_level in educational_models.StudentLevels
        ]
    )
