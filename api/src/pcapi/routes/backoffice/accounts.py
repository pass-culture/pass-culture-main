from pcapi.core.permissions import models as perm_models
from pcapi.core.permissions import utils as perm_utils
from pcapi.core.subscription import api as subscription_api
from pcapi.core.users import api as users_api
from pcapi.core.users import models as users_models
from pcapi.core.users import repository as users_repository
from pcapi.models.api_errors import ApiErrors
from pcapi.serialization.decorator import spectree_serialize

from . import blueprint
from .serialization import EligibilitySubscriptionHistoryModel
from .serialization import GetBeneficiaryCreditResponseModel
from .serialization import GetUserSubscriptionHistoryResponseModel
from .serialization import IdCheckItemModel
from .serialization import ListPublicAccountsResponseModel
from .serialization import PublicAccount
from .serialization import PublicAccountSearchQuery
from .serialization import SubscriptionItemModel


# Same methods as called from legacy backoffice with Flask-Admin
SUBSCRIPTION_ITEM_METHODS = [
    subscription_api.get_email_validation_subscription_item,
    subscription_api.get_phone_validation_subscription_item,
    subscription_api.get_profile_completion_subscription_item,
    subscription_api.get_identity_check_subscription_item,
    subscription_api.get_honor_statement_subscription_item,
]


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


@blueprint.backoffice_blueprint.route("public_accounts/user/<int:user_id>", methods=["GET"])
@perm_utils.permission_required(perm_models.Permissions.READ_PUBLIC_ACCOUNT)
@spectree_serialize(
    response_model=PublicAccount,
    on_success_status=200,
    api=blueprint.api,
)
def get_public_account(user_id: int) -> PublicAccount:
    user = users_repository.get_user_by_id(user_id)

    return PublicAccount.from_orm(user)


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


@blueprint.backoffice_blueprint.route("public_accounts/user/<int:user_id>/history", methods=["GET"])
@perm_utils.permission_required(perm_models.Permissions.READ_PUBLIC_ACCOUNT)
@spectree_serialize(
    response_model=GetUserSubscriptionHistoryResponseModel,
    on_success_status=200,
    api=blueprint.api,
)
def get_user_subscription_history(user_id: int) -> GetUserSubscriptionHistoryResponseModel:
    user = users_repository.get_user_by_id(user_id)
    if not user:
        raise ApiErrors(errors={"user_id": "User does not exist"})

    subscriptions = {}

    for eligibility in list(users_models.EligibilityType):
        subscriptions[eligibility.name] = EligibilitySubscriptionHistoryModel(
            subscriptionItems=[
                SubscriptionItemModel.from_orm(method(user, eligibility)) for method in SUBSCRIPTION_ITEM_METHODS
            ],
            idCheckHistory=[
                IdCheckItemModel.from_orm(fraud_check)
                for fraud_check in user.beneficiaryFraudChecks
                if fraud_check.eligibilityType == eligibility
            ],
        )

    return GetUserSubscriptionHistoryResponseModel(subscriptions=subscriptions)
