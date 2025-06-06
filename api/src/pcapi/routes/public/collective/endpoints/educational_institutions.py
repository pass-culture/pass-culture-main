from pcapi.core.educational.api.institution import search_educational_institution
from pcapi.repository.session_management import atomic
from pcapi.routes.public import blueprints
from pcapi.routes.public import spectree_schemas
from pcapi.routes.public.collective.serialization import institutions as institutions_serialization
from pcapi.routes.public.documentation_constants import http_responses
from pcapi.routes.public.documentation_constants import tags
from pcapi.serialization.decorator import spectree_serialize
from pcapi.serialization.spec_tree import ExtendResponse as SpectreeResponse
from pcapi.validation.routes.users_authentifications import provider_api_key_required


@blueprints.public_api.route("/v2/collective/educational-institutions/", methods=["GET"])
@atomic()
@provider_api_key_required
@spectree_serialize(
    api=spectree_schemas.public_api_schema,
    tags=[tags.COLLECTIVE_OFFER_ATTRIBUTES],
    resp=SpectreeResponse(
        **(
            {
                "HTTP_200": (
                    institutions_serialization.CollectiveOffersListEducationalInstitutionResponseModel,
                    http_responses.HTTP_200_MESSAGE,
                ),
            }
            | http_responses.HTTP_40X_SHARED_BY_API_ENDPOINTS
            | http_responses.HTTP_400_BAD_REQUEST
        )
    ),
)
def list_educational_institutions(
    query: institutions_serialization.GetListEducationalInstitutionsQueryModel,
) -> institutions_serialization.CollectiveOffersListEducationalInstitutionResponseModel:
    """
    Get Educational Institutions
    """

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
