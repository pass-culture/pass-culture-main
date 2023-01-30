from typing import cast

from pcapi.core.educational import repository as educational_repository
from pcapi.routes.public import blueprints
from pcapi.routes.public.collective.serialization import domains as domains_serialization
from pcapi.routes.public.collective.serialization import offers as offers_serialization
from pcapi.routes.serialization import BaseModel
from pcapi.serialization.decorator import spectree_serialize
from pcapi.serialization.spec_tree import ExtendResponse as SpectreeResponse
from pcapi.utils.cache import cached_view
from pcapi.validation.routes.users_authentifications import api_key_required


@blueprints.v2_prefixed_public_api.route("/collective/educational-domains", methods=["GET"])
@spectree_serialize(
    api=blueprints.v2_prefixed_public_api_schema,
    tags=["API offres collectives BETA"],
    resp=SpectreeResponse(
        **(
            {
                "HTTP_200": (
                    domains_serialization.CollectiveOffersListDomainsResponseModel,
                    "La liste des domaines d'éducation.",
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
@cached_view(prefix="pro_public_api_v2")
def list_educational_domains() -> domains_serialization.CollectiveOffersListDomainsResponseModel:
    # in French, to be used by Swagger for the API documentation
    """Récupération de la liste des domaines d'éducation pouvant être associés aux offres collectives."""
    educational_domains = educational_repository.get_all_educational_domains_ordered_by_name()

    return domains_serialization.CollectiveOffersListDomainsResponseModel(
        __root__=[
            domains_serialization.CollectiveOffersDomainResponseModel.from_orm(educational_domain)
            for educational_domain in educational_domains
        ]
    )
