from typing import cast

from pcapi.core.educational.api.institution import search_educational_institution
from pcapi.routes.public import blueprints
from pcapi.routes.public.collective.serialization import institutions as institutions_serialization
from pcapi.routes.public.collective.serialization import offers as offers_serialization
from pcapi.routes.serialization import BaseModel
from pcapi.serialization.decorator import spectree_serialize
from pcapi.serialization.spec_tree import ExtendResponse as SpectreeResponse
from pcapi.validation.routes.users_authentifications import api_key_required


@blueprints.v2_prefixed_public_api.route("/collective/educational-institutions/", methods=["GET"])
@spectree_serialize(
    api=blueprints.v2_prefixed_public_api_schema,
    tags=["API offres collectives"],
    resp=SpectreeResponse(
        **(
            {
                "HTTP_200": (
                    institutions_serialization.CollectiveOffersListEducationalInstitutionResponseModel,
                    "La liste des établissement scolaires éligibles.",
                ),
                "HTTP_400": (
                    cast(BaseModel, offers_serialization.ErrorResponseModel),
                    "Requête malformée",
                ),
                "HTTP_401": (
                    cast(BaseModel, offers_serialization.AuthErrorResponseModel),
                    "Authentification nécessaire",
                ),
            }
        )
    ),
)
@api_key_required
def list_educational_institutions(
    query: institutions_serialization.GetListEducationalInstitutionsQueryModel,
) -> institutions_serialization.CollectiveOffersListEducationalInstitutionResponseModel:
    # in French, to be used by Swagger for the API documentation
    """Récupération de la liste établissements scolaires."""

    institutions = search_educational_institution(
        name=query.name,
        city=query.city,
        postal_code=query.postal_code,
        educational_institution_id=query.id,
        institution_type=query.institution_type,
        uai=query.uai,
        limit=query.limit,
    )
    return institutions_serialization.CollectiveOffersListEducationalInstitutionResponseModel(
        __root__=[
            institutions_serialization.CollectiveOffersEducationalInstitutionResponseModel.from_orm(institution)
            for institution in institutions
        ]
    )
