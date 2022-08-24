from pcapi.core.educational import api as educational_api
from pcapi.routes.pro import blueprint
from pcapi.routes.serialization import public_api_collective_offers_serialize
from pcapi.serialization.decorator import spectree_serialize
from pcapi.validation.routes.users_authentifications import api_key_required


@blueprint.pro_public_api_v2.route("/collective/educational-institutions/", methods=["GET"])
@api_key_required
@spectree_serialize(
    on_success_status=200,
    on_error_statuses=[401],
    response_model=public_api_collective_offers_serialize.CollectiveOffersListEducationalInstitutionResponseModel,
    api=blueprint.pro_public_schema_v2,
)
def list_educational_institutions(
    query: public_api_collective_offers_serialize.GetListEducationalInstitutionsQueryModel,
) -> public_api_collective_offers_serialize.CollectiveOffersListEducationalInstitutionResponseModel:
    # in French, to be used by Swagger for the API documentation
    """Récupération de la liste établissements scolaires."""

    institutions = educational_api.search_educational_institution(
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
