from pcapi.core.educational import repository as educational_repository
from pcapi.routes.apis import api
from pcapi.routes.apis import public_api
from pcapi.routes.serialization import educational_domains as educational_domains_serialization
from pcapi.serialization.decorator import spectree_serialize


@public_api.route("/collective/educational-domains", methods=["GET"])
@spectree_serialize(
    on_success_status=200,
    response_model=educational_domains_serialization.EducationalDomainsResponseModel,
    api=api,
)
def list_educational_domains() -> educational_domains_serialization.EducationalDomainsResponseModel:
    educational_domains = educational_repository.get_all_educational_domains_ordered_by_name()
    return educational_domains_serialization.EducationalDomainsResponseModel(
        __root__=[
            educational_domains_serialization.EducationalDomainResponseModel.from_orm(educational_domain)
            for educational_domain in educational_domains
        ]
    )
