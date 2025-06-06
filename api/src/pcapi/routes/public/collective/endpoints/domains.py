from pcapi.core.educational import repository as educational_repository
from pcapi.repository.session_management import atomic
from pcapi.routes.public import blueprints
from pcapi.routes.public import spectree_schemas
from pcapi.routes.public.collective.serialization import domains as domains_serialization
from pcapi.routes.public.documentation_constants import http_responses
from pcapi.routes.public.documentation_constants import tags
from pcapi.serialization.decorator import spectree_serialize
from pcapi.serialization.spec_tree import ExtendResponse as SpectreeResponse
from pcapi.utils.cache import cached_view
from pcapi.validation.routes.users_authentifications import provider_api_key_required


@blueprints.public_api.route("/v2/collective/educational-domains", methods=["GET"])
@atomic()
@provider_api_key_required
@spectree_serialize(
    api=spectree_schemas.public_api_schema,
    tags=[tags.COLLECTIVE_OFFER_ATTRIBUTES],
    resp=SpectreeResponse(
        **(
            {
                "HTTP_200": (
                    domains_serialization.CollectiveOffersListDomainsResponseModel,
                    http_responses.HTTP_200_MESSAGE,
                ),
            }
            | http_responses.HTTP_40X_SHARED_BY_API_ENDPOINTS
        )
    ),
)
@cached_view(prefix="pro_public_api_v2")
def list_educational_domains() -> domains_serialization.CollectiveOffersListDomainsResponseModel:
    """
    Get Educational Domains

    Return the educational domains that can be linked to a collective offer.
    """
    educational_domains = educational_repository.get_all_educational_domains_ordered_by_name()

    return domains_serialization.CollectiveOffersListDomainsResponseModel(
        __root__=[
            domains_serialization.CollectiveOffersDomainResponseModel.build(educational_domain)
            for educational_domain in educational_domains
        ]
    )
