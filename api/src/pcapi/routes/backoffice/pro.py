import typing

from pcapi.core.offerers import api as offerers_api
from pcapi.core.permissions import models as perm_models
from pcapi.core.permissions import utils as perm_utils
from pcapi.core.users import api as users_api
from pcapi.models.api_errors import ApiErrors
from pcapi.serialization.decorator import spectree_serialize

from . import blueprint
from . import serialization
from . import utils


@blueprint.backoffice_blueprint.route("pro/search", methods=["GET"])
@spectree_serialize(
    response_model=serialization.SearchProResponseModel,
    on_success_status=200,
    api=blueprint.api,
)
@perm_utils.permission_required(perm_models.Permissions.SEARCH_PRO_ACCOUNT)
def search_pro(
    query: serialization.ProSearchQuery,
) -> serialization.SearchProResponseModel:
    terms = query.q.split()
    sorts = query.sort.split(",") if query.sort else None

    # First version of pro search: no aggregration, a single type is requested.
    match query.type:
        case "proUser":
            paginated = users_api.search_pro_account(terms, order_by=sorts).paginate(
                page=query.page,
                per_page=query.perPage,
            )
            response_payload_type: typing.Type = serialization.ProUserPayload
        case "offerer":
            paginated = offerers_api.search_offerer(terms, order_by=sorts).paginate(
                page=query.page,
                per_page=query.perPage,
            )
            response_payload_type = serialization.OffererPayload
        case "venue":
            raise ApiErrors(errors={"type": ["La recherche par lieu n'est pas encore implémentée."]})
        case _:
            raise ApiErrors(errors={"type": ["Le type de ressource est invalide."]})

    response = typing.cast(
        serialization.SearchProResponseModel,
        utils.build_paginated_response(
            response_model=serialization.SearchProResponseModel,
            pages=paginated.pages,
            total=paginated.total,
            page=paginated.page,
            sort=query.sort,
            data=[
                serialization.ProResult(
                    resourceType=query.type, id=account.id, payload=response_payload_type.from_orm(account)
                )
                for account in paginated.items
            ],
        ),
    )
    return response
