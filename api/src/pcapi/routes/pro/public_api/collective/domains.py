from typing import cast

from pcapi.core.educational import repository as educational_repository
from pcapi.routes.pro import blueprint
from pcapi.routes.serialization import BaseModel
from pcapi.routes.serialization import public_api_collective_offers_serialize
from pcapi.serialization.decorator import spectree_serialize
from pcapi.serialization.spec_tree import ExtendResponse as SpectreeResponse
from pcapi.validation.routes.users_authentifications import api_key_required


@blueprint.pro_public_api_v2.route("/collective/educational-domains", methods=["GET"])
@api_key_required
@spectree_serialize(
    api=blueprint.pro_public_schema_v2,
    tags=["API offres collectives"],
    resp=SpectreeResponse(
        **(
            {
                "HTTP_200": (
                    public_api_collective_offers_serialize.CollectiveOffersListDomainsResponseModel,
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
def list_educational_domains() -> public_api_collective_offers_serialize.CollectiveOffersListDomainsResponseModel:
    # in French, to be used by Swagger for the API documentation
    """Récupération de la liste des domaines d'éducation pouvant être associés aux offres collectives."""
    educational_domains = educational_repository.get_all_educational_domains_ordered_by_name()

    return public_api_collective_offers_serialize.CollectiveOffersListDomainsResponseModel(
        __root__=[
            public_api_collective_offers_serialize.CollectiveOffersDomainResponseModel.from_orm(educational_domain)
            for educational_domain in educational_domains
        ]
    )
