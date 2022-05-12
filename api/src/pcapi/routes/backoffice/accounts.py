from pcapi.core.permissions import models as perm_models
from pcapi.core.permissions import utils as perm_utils
from pcapi.core.users import api as users_api
from pcapi.core.users import repository as users_repository
from pcapi.models.api_errors import ApiErrors
from pcapi.serialization.decorator import spectree_serialize

from . import blueprint
from .serialization import GetBeneficiaryCreditResponseModel
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
    accounts = users_api.search_public_account(terms)

    return ListPublicAccountsResponseModel(accounts=[PublicAccount.from_orm(account) for account in accounts])


@blueprint.backoffice_blueprint.route("public_accounts/user/<int:user_id>/credit", methods=["GET"])
@perm_utils.permission_required(perm_models.Permissions.READ_PUBLIC_ACCOUNT)
@spectree_serialize(
    response_model=GetBeneficiaryCreditResponseModel,
    on_success_status=200,
    api=blueprint.api,
)
def get_beneficiary_credit(user_id: int) -> GetBeneficiaryCreditResponseModel:
    user = users_repository.get_user_by_id(user_id)
    if not user:
        raise ApiErrors(errors={"user_id": "User does not exist"})

    domains_credit = users_api.get_domains_credit(user) if user.is_beneficiary else None

    return GetBeneficiaryCreditResponseModel(
        initialCredit=float(domains_credit.all.initial) if domains_credit else 0.0,
        remainingCredit=float(domains_credit.all.remaining) if domains_credit else 0.0,
        remainingDigitalCredit=float(domains_credit.digital.remaining)
        if domains_credit and domains_credit.digital
        else 0.0,
    )
