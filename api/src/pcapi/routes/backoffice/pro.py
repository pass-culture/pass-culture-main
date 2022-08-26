import typing

from pcapi.core.permissions import models as perm_models
from pcapi.core.permissions import utils as perm_utils
from pcapi.core.users import api as users_api
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
    query: serialization.SearchQuery,
) -> serialization.SearchProResponseModel:
    terms = query.q.split()
    sorts = query.sort.split(",") if query.sort else None

    paginated = users_api.search_pro_account(terms, order_by=sorts).paginate(
        page=query.page,
        per_page=query.perPage,
    )

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
                    resourceType="proUser", id=account.id, payload=serialization.ProUserPayload.from_orm(account)
                )
                for account in paginated.items
            ],
        ),
    )
    return response
