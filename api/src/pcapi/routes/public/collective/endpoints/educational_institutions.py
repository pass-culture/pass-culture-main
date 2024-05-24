from pcapi.core.educational.api.institution import search_educational_institution
from pcapi.routes.public import spectree_schemas
from pcapi.routes.public.collective.blueprint import collective_offers_blueprint
from pcapi.routes.public.collective.serialization import institutions as institutions_serialization
from pcapi.routes.public.documentation_constants import http_responses
from pcapi.routes.public.documentation_constants import tags
from pcapi.serialization.decorator import spectree_serialize
from pcapi.serialization.spec_tree import ExtendResponse as SpectreeResponse
from pcapi.validation.routes.users_authentifications import api_key_required


@collective_offers_blueprint.route("/collective/educational-institutions/", methods=["GET"])
@spectree_serialize(
    api=spectree_schemas.public_api_schema,
    tags=[tags.COLLECTIVE_EDUCATIONAL_DATA_TAG],
    resp=SpectreeResponse(
        **(
            {
                "HTTP_200": (
                    institutions_serialization.CollectiveOffersListEducationalInstitutionResponseModel,
                    "La liste des établissement scolaires éligibles.",
                ),
            }
            | http_responses.HTTP_40X_SHARED_BY_API_ENDPOINTS
            | http_responses.HTTP_400_BAD_REQUEST
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
