import typing

from pcapi.core.auth.utils import get_current_user
from pcapi.core.fraud import api as fraud_api
from pcapi.core.fraud import models as fraud_models
from pcapi.core.permissions import models as perm_models
from pcapi.core.permissions import utils as perm_utils
from pcapi.core.subscription import api as subscription_api
from pcapi.core.subscription.phone_validation import api as phone_validation_api
from pcapi.core.subscription.phone_validation import exceptions as phone_validation_exceptions
from pcapi.core.users import api as users_api
from pcapi.core.users import exceptions as users_exceptions
from pcapi.core.users import external as users_external
from pcapi.core.users import models as users_models
from pcapi.core.users import repository as users_repository
from pcapi.core.users.email.update import request_email_update_from_admin
from pcapi.core.users.utils import sanitize_email
from pcapi.models.api_errors import ApiErrors
from pcapi.serialization.decorator import spectree_serialize

from . import blueprint
from . import serialization
from . import utils


# Same methods as called from legacy backoffice with Flask-Admin
SUBSCRIPTION_ITEM_METHODS = [
    subscription_api.get_email_validation_subscription_item,
    subscription_api.get_phone_validation_subscription_item,
    subscription_api.get_profile_completion_subscription_item,
    subscription_api.get_identity_check_subscription_item,
    subscription_api.get_honor_statement_subscription_item,
]


@blueprint.backoffice_blueprint.route("public_accounts/search", methods=["GET"])
@spectree_serialize(
    response_model=serialization.ListPublicAccountsResponseModel,
    on_success_status=200,
    api=blueprint.api,
)
@perm_utils.permission_required(perm_models.Permissions.SEARCH_PUBLIC_ACCOUNT)
def search_public_account(
    query: serialization.PublicAccountSearchQuery,
) -> serialization.ListPublicAccountsResponseModel:
    terms = query.q.split()
    sorts = query.sort.split(",") if query.sort else ["id"]

    paginated = users_api.search_public_account(terms, order_by=sorts).paginate(
        page=query.page,
        per_page=query.perPage,
    )

    response = typing.cast(
        serialization.ListPublicAccountsResponseModel,
        utils.build_paginated_response(
            response_model=serialization.ListPublicAccountsResponseModel,
            pages=paginated.pages,
            total=paginated.total,
            page=paginated.page,
            sort=query.sort,
            data=[serialization.PublicAccount.from_orm(account) for account in paginated.items],
        ),
    )
    return response


@blueprint.backoffice_blueprint.route("public_accounts/<int:user_id>", methods=["GET"])
@spectree_serialize(
    response_model=serialization.PublicAccount,
    on_success_status=200,
    api=blueprint.api,
)
@perm_utils.permission_required(perm_models.Permissions.READ_PUBLIC_ACCOUNT)
def get_public_account(user_id: int) -> serialization.PublicAccount:
    user = utils.get_user_or_error(user_id)

    return serialization.PublicAccount.from_orm(user)


@blueprint.backoffice_blueprint.route("public_accounts/<int:user_id>", methods=["PUT"])
@spectree_serialize(
    response_model=serialization.PublicAccount,
    on_success_status=200,
    api=blueprint.api,
)
@perm_utils.permission_required(perm_models.Permissions.MANAGE_PUBLIC_ACCOUNT)
def update_public_account(user_id: int, body: serialization.PublicAccountUpdateRequest) -> serialization.PublicAccount:
    user = users_repository.get_user_by_id(user_id)
    if not user:
        raise ApiErrors(errors={"user_id": "L'utilisateur n'existe pas"})

    if body.phoneNumber:
        # Waiting for clarification about phone number changes allowed or not
        raise ApiErrors(errors={"phoneNumber": "La modification du numéro de téléphone n'est pas autorisée"})

    users_api.update_user_information(
        user,
        first_name=body.firstName,
        last_name=body.lastName,
        birth_date=body.dateOfBirth,
        id_piece_number=body.idPieceNumber,
        address=body.address,
        postal_code=body.postalCode,
        city=body.city,
        commit=True,
    )

    if body.email and body.email != sanitize_email(user.email):  # type: ignore [arg-type]
        try:
            request_email_update_from_admin(user, body.email)
        except users_exceptions.EmailExistsError:
            raise ApiErrors(errors={"email": "L'email est déjà associé à un autre utilisateur"})

    users_external.update_external_user(user)

    return serialization.PublicAccount.from_orm(user)


@blueprint.backoffice_blueprint.route("public_accounts/<int:user_id>/credit", methods=["GET"])
@spectree_serialize(
    response_model=serialization.GetBeneficiaryCreditResponseModel,
    on_success_status=200,
    api=blueprint.api,
)
@perm_utils.permission_required(perm_models.Permissions.READ_PUBLIC_ACCOUNT)
def get_beneficiary_credit(user_id: int) -> serialization.GetBeneficiaryCreditResponseModel:
    user = utils.get_user_or_error(user_id)

    domains_credit = users_api.get_domains_credit(user) if user.is_beneficiary else None

    return serialization.GetBeneficiaryCreditResponseModel(
        initialCredit=float(domains_credit.all.initial) if domains_credit else 0.0,
        remainingCredit=float(domains_credit.all.remaining) if domains_credit else 0.0,
        remainingDigitalCredit=float(domains_credit.digital.remaining)
        if domains_credit and domains_credit.digital
        else 0.0,
        dateCreated=getattr(user.deposit, "dateCreated", None),
    )


@blueprint.backoffice_blueprint.route("public_accounts/<int:user_id>/history", methods=["GET"])
@spectree_serialize(
    response_model=serialization.GetUserSubscriptionHistoryResponseModel,
    on_success_status=200,
    api=blueprint.api,
)
@perm_utils.permission_required(perm_models.Permissions.READ_PUBLIC_ACCOUNT)
def get_user_subscription_history(user_id: int) -> serialization.GetUserSubscriptionHistoryResponseModel:
    user = utils.get_user_or_error(user_id)

    subscriptions = {}

    for eligibility in list(users_models.EligibilityType):
        subscriptions[eligibility.name] = serialization.EligibilitySubscriptionHistoryModel(
            subscriptionItems=[
                serialization.SubscriptionItemModel.from_orm(method(user, eligibility))
                for method in SUBSCRIPTION_ITEM_METHODS
            ],
            idCheckHistory=[
                serialization.IdCheckItemModel.from_orm(fraud_check)
                for fraud_check in user.beneficiaryFraudChecks
                if fraud_check.eligibilityType == eligibility
            ],
        )

    return serialization.GetUserSubscriptionHistoryResponseModel(subscriptions=subscriptions)


@blueprint.backoffice_blueprint.route("public_accounts/<int:user_id>/review", methods=["POST"])
@spectree_serialize(
    response_model=serialization.BeneficiaryReviewResponseModel,
    on_success_status=200,
    api=blueprint.api,
)
@perm_utils.permission_required(perm_models.Permissions.REVIEW_PUBLIC_ACCOUNT)
def review_public_account(
    user_id: int, body: serialization.BeneficiaryReviewRequestModel
) -> serialization.BeneficiaryReviewResponseModel:
    user = utils.get_user_or_error(user_id, error_code=412)

    eligibility = None if body.eligibility is None else users_models.EligibilityType[body.eligibility]

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

    return serialization.BeneficiaryReviewResponseModel(
        userId=review.user.id,
        authorId=review.author.id,
        review=getattr(review.review, "value", None),
        reason=review.reason,
    )


@blueprint.backoffice_blueprint.route("public_accounts/<int:user_id>/resend-validation-email", methods=["POST"])
@spectree_serialize(on_success_status=204, api=blueprint.api)
@perm_utils.permission_required(perm_models.Permissions.MANAGE_PUBLIC_ACCOUNT)
def resend_validation_email(user_id: int) -> None:
    user = utils.get_user_or_error(user_id)

    if user.has_admin_role or user.has_pro_role:
        raise ApiErrors(errors={"user_id": "Cette action n'est pas supportée pour les utilisateurs admin ou pro"})

    if user.isEmailValidated:
        raise ApiErrors(errors={"user_id": "L'adresse email est déjà validée"})

    users_api.request_email_confirmation(user)


@blueprint.backoffice_blueprint.route("public_accounts/<int:user_id>/send-phone-validation-code", methods=["POST"])
@spectree_serialize(on_success_status=204, api=blueprint.api)
@perm_utils.permission_required(perm_models.Permissions.MANAGE_PUBLIC_ACCOUNT)
def send_phone_validation_code(user_id: int) -> None:
    user = utils.get_user_or_error(user_id)

    try:
        phone_validation_api.send_phone_validation_code(user, user.phoneNumber, ignore_limit=True)

    except phone_validation_exceptions.UserPhoneNumberAlreadyValidated:
        raise ApiErrors({"user_id": "Le numéro de téléphone est déjà validé"})

    except phone_validation_exceptions.InvalidPhoneNumber:
        raise ApiErrors({"user_id": "Le numéro de téléphone est invalide"})

    except phone_validation_exceptions.UserAlreadyBeneficiary:
        raise ApiErrors({"user_id": "L'utilisateur est déjà bénéficiaire"})

    except phone_validation_exceptions.UnvalidatedEmail:
        raise ApiErrors({"user_id": "L'email de l'utilisateur n'est pas encore validé"})

    except phone_validation_exceptions.PhoneAlreadyExists:
        raise ApiErrors({"user_id": "Un compte est déjà associé à ce numéro"})

    except phone_validation_exceptions.PhoneVerificationException:
        raise ApiErrors({"user_id": "L'envoi du code a échoué"})


@blueprint.backoffice_blueprint.route("public_accounts/<int:user_id>/skip-phone-validation", methods=["POST"])
@spectree_serialize(on_success_status=204, api=blueprint.api)
@perm_utils.permission_required(perm_models.Permissions.MANAGE_PUBLIC_ACCOUNT)
def skip_phone_validation(user_id: int) -> None:
    user = utils.get_user_or_error(user_id)
    try:
        users_api.skip_phone_validation_step(user)
    except phone_validation_exceptions.UserPhoneNumberAlreadyValidated:
        raise ApiErrors({"user_id": "Le numéro de téléphone est déjà validé"})


@blueprint.backoffice_blueprint.route("public_accounts/<int:user_id>/logs", methods=["GET"])
@spectree_serialize(
    response_model=serialization.PublicHistoryResponseModel,
    on_success_status=200,
    api=blueprint.api,
)
@perm_utils.permission_required(perm_models.Permissions.READ_PUBLIC_ACCOUNT)
def get_public_history(user_id: int) -> serialization.PublicHistoryResponseModel:
    user = utils.get_user_or_error(user_id)

    history = users_api.public_account_history(user)

    return serialization.PublicHistoryResponseModel(
        history=[serialization.PublicHistoryItem(**item) for item in history]
    )
