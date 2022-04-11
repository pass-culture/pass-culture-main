import logging
from typing import Optional

from pcapi.connectors.beneficiaries import exceptions as beneficiaries_exceptions
from pcapi.core.fraud import api as fraud_api
from pcapi.core.fraud.ubble import api as ubble_fraud_api
from pcapi.core.subscription import api as subscription_api
from pcapi.core.subscription import profile_options
from pcapi.core.subscription.ubble import api as ubble_subscription_api
from pcapi.core.users import models as users_models
from pcapi.models import api_errors
from pcapi.routes.native.security import authenticated_user_required
from pcapi.serialization.decorator import spectree_serialize

from . import blueprint
from .serialization import subscription as serializers


logger = logging.getLogger(__name__)


@blueprint.native_v1.route("/subscription/next_step", methods=["GET"])
@spectree_serialize(
    response_model=serializers.NextSubscriptionStepResponse,
    on_success_status=200,
    api=blueprint.api,
)  # type: ignore
@authenticated_user_required
def next_subscription_step(
    user: users_models.User,
) -> Optional[serializers.NextSubscriptionStepResponse]:
    next_step = subscription_api.get_next_subscription_step(user)
    logger.info("next_subscription_step: %s", next_step.value if next_step else None, extra={"user_id": user.id})
    return serializers.NextSubscriptionStepResponse(
        next_subscription_step=next_step,
        allowed_identity_check_methods=subscription_api.get_allowed_identity_check_methods(user),
        maintenance_page_type=subscription_api.get_maintenance_page_type(user),
        has_identity_check_pending=fraud_api.has_user_pending_identity_check(user),
    )


@blueprint.native_v1.route("/subscription/profile", methods=["POST"])
@spectree_serialize(on_success_status=204, api=blueprint.api)
@authenticated_user_required
def complete_profile(user: users_models.User, body: serializers.ProfileUpdateRequest) -> None:
    subscription_api.complete_profile(
        user,
        first_name=body.first_name,
        last_name=body.last_name,
        address=body.address,
        city=body.city,
        postal_code=body.postal_code,
        activity=users_models.ActivityEnum[body.activity_id.value].value,
        school_type=users_models.SchoolTypeEnum[body.school_type_id.value] if body.school_type_id is not None else None,
    )


@blueprint.native_v1.route("/subscription/profile_options", methods=["GET"])
@spectree_serialize(
    response_model=serializers.ProfileOptionsResponse,
    on_success_status=200,
    api=blueprint.api,
)  # type: ignore
def get_profile_options() -> serializers.ProfileOptionsResponse:
    return serializers.ProfileOptionsResponse(
        school_types=[
            serializers.SchoolTypeResponseModel.from_orm(school_type)
            for school_type in profile_options.ALL_SCHOOL_TYPES
        ],
        activities=[
            serializers.ActivityResponseModel.from_orm(activity) for activity in profile_options.ALL_ACTIVITIES
        ],
    )


@blueprint.native_v1.route("/subscription/honor_statement", methods=["POST"])
@spectree_serialize(on_success_status=204, api=blueprint.api)
@authenticated_user_required
def create_honor_statement_fraud_check(user: users_models.User) -> None:
    fraud_api.create_honor_statement_fraud_check(user, "statement from /subscription/honor_statement endpoint")

    subscription_api.activate_beneficiary_if_no_missing_step(user)


@blueprint.native_v1.route("/ubble_identification", methods=["POST"])
@spectree_serialize(api=blueprint.api, response_model=serializers.IdentificationSessionResponse)
@authenticated_user_required
def start_identification_session(
    user: users_models.User, body: serializers.IdentificationSessionRequest
) -> serializers.IdentificationSessionResponse:

    if user.eligibility is None:
        raise api_errors.ApiErrors(
            {"code": "IDCHECK_NOT_ELIGIBLE", "message": "Non éligible à un crédit"},
            status_code=400,
        )

    if not ubble_fraud_api.is_user_allowed_to_perform_ubble_check(user, user.eligibility):
        raise api_errors.ApiErrors(
            {"code": "IDCHECK_ALREADY_PROCESSED", "message": "Une identification a déjà été traitée"},
            status_code=400,
        )

    fraud_check = ubble_fraud_api.get_restartable_identity_checks(user)
    if fraud_check:
        return serializers.IdentificationSessionResponse(identificationUrl=fraud_check.source_data().identification_url)  # type: ignore [union-attr]

    try:
        identification_url = ubble_subscription_api.start_ubble_workflow(user, body.redirectUrl)
        return serializers.IdentificationSessionResponse(identificationUrl=identification_url)

    except beneficiaries_exceptions.IdentificationServiceUnavailable:
        raise api_errors.ApiErrors(
            {"code": "IDCHECK_SERVICE_UNAVAILABLE", "message": "Le service d'identification n'est pas joignable"},
            status_code=503,
        )

    except beneficiaries_exceptions.IdentificationServiceError:
        raise api_errors.ApiErrors(
            {
                "code": "IDCHECK_SERVICE_ERROR",
                "message": "Une erreur s'est produite à l'appel du service d'identification",
            },
            status_code=500,
        )
