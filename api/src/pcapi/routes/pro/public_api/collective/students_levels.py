from pcapi.core.educational import models as educational_models
from pcapi.routes.pro import blueprint
from pcapi.routes.serialization import public_api_collective_offers_serialize
from pcapi.serialization.decorator import spectree_serialize
from pcapi.validation.routes.users_authentifications import api_key_required


@blueprint.pro_public_api_v2.route("/collective-offers/student-levels", methods=["GET"])
@api_key_required
@spectree_serialize(
    on_success_status=200,
    on_error_statuses=[401],
    response_model=public_api_collective_offers_serialize.CollectiveOffersListStudentLevelsResponseModel,
    api=blueprint.pro_public_schema_v2,
)
def list_students_levels() -> public_api_collective_offers_serialize.CollectiveOffersListStudentLevelsResponseModel:
    # in French, to be used by Swagger for the API documentation
    """Récupération de la liste des publics cibles pour lesquelles des offres collectives peuvent être proposées."""
    return public_api_collective_offers_serialize.CollectiveOffersListStudentLevelsResponseModel(
        __root__=[
            public_api_collective_offers_serialize.CollectiveOffersStudentLevelResponseModel(
                id=student_level.name, name=student_level.value
            )
            for student_level in educational_models.StudentLevels
        ]
    )
