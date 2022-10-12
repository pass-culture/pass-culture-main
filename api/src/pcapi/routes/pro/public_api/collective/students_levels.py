from functools import lru_cache
from typing import cast

from pcapi import settings
from pcapi.core.educational import models as educational_models
from pcapi.routes.pro import blueprint
from pcapi.routes.serialization import BaseModel
from pcapi.routes.serialization import public_api_collective_offers_serialize
from pcapi.serialization.decorator import spectree_serialize
from pcapi.serialization.spec_tree import ExtendResponse as SpectreeResponse
from pcapi.validation.routes.users_authentifications import api_key_required


@blueprint.pro_public_api_v2.route("/collective/student-levels", methods=["GET"])
@lru_cache(maxsize=1 if not (settings.IS_RUNNING_TESTS or settings.IS_DEV) else 0)
@spectree_serialize(
    api=blueprint.pro_public_schema_v2,
    tags=["API offres collectives BETA"],
    resp=SpectreeResponse(
        **(
            {
                "HTTP_200": (
                    public_api_collective_offers_serialize.CollectiveOffersListStudentLevelsResponseModel,
                    "La liste des domaines d'éducation.",
                ),
                "HTTP_401": (
                    cast(BaseModel, public_api_collective_offers_serialize.AuthErrorResponseModel),
                    "Authentification nécessaire",
                ),
            }
        )
    ),
)
@api_key_required
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
