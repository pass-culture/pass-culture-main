from pcapi.core.permissions import models as perm_models
from pcapi.core.permissions import utils as perm_utils
from pcapi.core.users import api as user_api
from pcapi.serialization.decorator import spectree_serialize

from . import blueprint
from .serialization import ListPublicAccountsResponseModel
from .serialization import PublicAccount
from .serialization import PublicAccountSearchQuery


@blueprint.backoffice_blueprint.route("public_accounts/search", methods=["GET"])
@perm_utils.permission_required(perm_models.Permissions.SEARCH_PUBLIC_ACCOUNT)
@spectree_serialize(
    response_model=ListPublicAccountsResponseModel,
    on_success_status=200,
    api=blueprint.api,
)
def search_public_account(query: PublicAccountSearchQuery) -> ListPublicAccountsResponseModel:
    terms = query.q.split()
    accounts = user_api.search_public_account(terms)

    return ListPublicAccountsResponseModel(accounts=[PublicAccount.from_orm(account) for account in accounts])
