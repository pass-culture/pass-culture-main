from pcapi.core.auth.utils import get_current_user
from pcapi.core.fraud import api as fraud_api
from pcapi.core.fraud import models as fraud_models
from pcapi.core.permissions import models as perm_models
from pcapi.core.permissions import utils as perm_utils
from pcapi.core.subscription import api as subscription_api
from pcapi.core.users import api as users_api
from pcapi.core.users import models as users_models
from pcapi.core.users import repository as users_repository
from pcapi.models.api_errors import ApiErrors
from pcapi.serialization.decorator import spectree_serialize

from . import blueprint
from . import serialization as s11n


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
    response_model=s11n.ListPublicAccountsResponseModel,
    on_success_status=200,
    api=blueprint.api,
)
def search_public_account(query: s11n.PublicAccountSearchQuery) -> s11n.ListPublicAccountsResponseModel:
    terms = query.q.split()
    accounts = users_api.search_public_account(terms)

    return s11n.ListPublicAccountsResponseModel(accounts=[s11n.PublicAccount.from_orm(account) for account in accounts])


@blueprint.backoffice_blueprint.route("public_accounts/user/<int:user_id>", methods=["GET"])
@perm_utils.permission_required(perm_models.Permissions.READ_PUBLIC_ACCOUNT)
@spectree_serialize(
    response_model=s11n.PublicAccount,
    on_success_status=200,
    api=blueprint.api,
)
def get_public_account(user_id: int) -> s11n.PublicAccount:
    user = users_repository.get_user_by_id(user_id)

    return s11n.PublicAccount.from_orm(user)


@blueprint.backoffice_blueprint.route("public_accounts/user/<int:user_id>/credit", methods=["GET"])
@perm_utils.permission_required(perm_models.Permissions.READ_PUBLIC_ACCOUNT)
@spectree_serialize(
    response_model=s11n.GetBeneficiaryCreditResponseModel,
    on_success_status=200,
    api=blueprint.api,
)
def get_beneficiary_credit(user_id: int) -> s11n.GetBeneficiaryCreditResponseModel:
    user = users_repository.get_user_by_id(user_id)
    if not user:
        raise ApiErrors(errors={"user_id": "L'utilisateur n'existe pas"})

    domains_credit = users_api.get_domains_credit(user) if user.is_beneficiary else None

    return s11n.GetBeneficiaryCreditResponseModel(
        initialCredit=float(domains_credit.all.initial) if domains_credit else 0.0,
        remainingCredit=float(domains_credit.all.remaining) if domains_credit else 0.0,
        remainingDigitalCredit=float(domains_credit.digital.remaining)
        if domains_credit and domains_credit.digital
        else 0.0,
    )


@blueprint.backoffice_blueprint.route("public_accounts/user/<int:user_id>/history", methods=["GET"])
@perm_utils.permission_required(perm_models.Permissions.READ_PUBLIC_ACCOUNT)
@spectree_serialize(
    response_model=s11n.GetUserSubscriptionHistoryResponseModel,
    on_success_status=200,
    api=blueprint.api,
)
def get_user_subscription_history(user_id: int) -> s11n.GetUserSubscriptionHistoryResponseModel:
    user = users_repository.get_user_by_id(user_id)
    if not user:
        raise ApiErrors(errors={"user_id": "L'utilisateur n'existe pas"})

    subscriptions = {}

    for eligibility in list(users_models.EligibilityType):
        subscriptions[eligibility.name] = s11n.EligibilitySubscriptionHistoryModel(
            subscriptionItems=[
                s11n.SubscriptionItemModel.from_orm(method(user, eligibility)) for method in SUBSCRIPTION_ITEM_METHODS
            ],
            idCheckHistory=[
                s11n.IdCheckItemModel.from_orm(fraud_check)
                for fraud_check in user.beneficiaryFraudChecks
                if fraud_check.eligibilityType == eligibility
            ],
        )

    return s11n.GetUserSubscriptionHistoryResponseModel(subscriptions=subscriptions)


@blueprint.backoffice_blueprint.route("public_accounts/user/<int:user_id>/review", methods=["POST"])
@perm_utils.permission_required(perm_models.Permissions.REVIEW_PUBLIC_ACCOUNT)
@spectree_serialize(
    response_model=s11n.BeneficiaryReviewResponseModel,
    on_success_status=200,
    api=blueprint.api,
)
def review_public_account(
    user_id: int, body: s11n.BeneficiaryReviewRequestModel
) -> s11n.BeneficiaryReviewResponseModel:
    user = users_repository.get_user_by_id(user_id)
    if not user:
        raise ApiErrors(errors={"user_id": "User does not exist"}, status_code=412)

    eligibility = None if body.eligibility is None else users_models.EligibilityType(body.eligibility)

    try:
        review = fraud_api.validate_beneficiary(
            user=user,
            reviewer=get_current_user(),
            reason=body.reason,
            review=fraud_models.FraudReviewStatus(body.review),
            eligibility=eligibility,
        )

    except (fraud_api.FraudCheckError, fraud_api.EligibilityError) as err:
        raise ApiErrors({"global": str(err)}, status_code=412) from err

    return s11n.BeneficiaryReviewResponseModel(
        userId=review.user.id,
        authorId=review.author.id,
        review=getattr(review.review, "value", None),
        reason=review.reason,
    )


@blueprint.backoffice_blueprint.route("public_accounts/user/<int:user_id>/resend-validation-email", methods=["POST"])
@perm_utils.permission_required(perm_models.Permissions.MANAGE_PUBLIC_ACCOUNT)
@spectree_serialize(on_success_status=204, api=blueprint.api)
def resend_validation_email(user_id: int) -> None:
    user = users_repository.get_user_by_id(user_id)
    if not user:
        raise ApiErrors(errors={"user_id": "L'utilisateur n'existe pas"})

    if user.has_admin_role or user.has_pro_role:
        raise ApiErrors(errors={"user_id": "Cette action n'est pas supportée pour les utilisateurs admin ou pro"})

    if user.isEmailValidated:
        raise ApiErrors(errors={"user_id": "L'adresse email est déjà validée"})

    users_api.request_email_confirmation(user)
