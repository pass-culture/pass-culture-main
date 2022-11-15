from typing import cast

from pcapi.core.educational.api.institution import search_educational_institution
from pcapi.routes.pro import blueprint
from pcapi.routes.serialization import BaseModel
from pcapi.routes.serialization import public_api_collective_offers_serialize
from pcapi.serialization.decorator import spectree_serialize
from pcapi.serialization.spec_tree import ExtendResponse as SpectreeResponse
from pcapi.validation.routes.users_authentifications import api_key_required


@blueprint.pro_public_api_v2.route("/collective/educational-institutions/", methods=["GET"])
@spectree_serialize(
    api=blueprint.pro_public_schema_v2,
    tags=["API offres collectives BETA"],
    resp=SpectreeResponse(
        **(
            {
                "HTTP_200": (
                    public_api_collective_offers_serialize.CollectiveOffersListEducationalInstitutionResponseModel,
                    "La liste des établissement scolaires éligibles.",
                ),
                "HTTP_400": (
                    cast(BaseModel, public_api_collective_offers_serialize.ErrorResponseModel),
                    "Requête malformée",
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
def list_educational_institutions(
    query: public_api_collective_offers_serialize.GetListEducationalInstitutionsQueryModel,
) -> public_api_collective_offers_serialize.CollectiveOffersListEducationalInstitutionResponseModel:
    # in French, to be used by Swagger for the API documentation
    """Récupération de la liste établissements scolaires."""

    institutions = search_educational_institution(
        name=query.name,
        city=query.city,
        postal_code=query.postal_code,
        educational_institution_id=query.id,
        institution_type=query.institution_type,
        limit=query.limit,
    )
    return public_api_collective_offers_serialize.CollectiveOffersListEducationalInstitutionResponseModel(
        __root__=[
            public_api_collective_offers_serialize.CollectiveOffersEducationalInstitutionResponseModel.from_orm(
                institution
            )
            for institution in institutions
        ]
    )
