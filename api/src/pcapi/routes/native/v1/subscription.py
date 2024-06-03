import logging
import typing

from pydantic.v1 import ValidationError

from pcapi.core.external.attributes import api as external_attributes_api
from pcapi.core.fraud import api as fraud_api
from pcapi.core.fraud import models as fraud_models
from pcapi.core.fraud.ubble import api as ubble_fraud_api
from pcapi.core.subscription import api as subscription_api
from pcapi.core.subscription import models as subscription_models
from pcapi.core.subscription import profile_options
from pcapi.core.subscription.ubble import api as ubble_subscription_api
from pcapi.core.users import models as users_models
from pcapi.models import api_errors
from pcapi.routes.native.security import authenticated_and_active_user_required
from pcapi.serialization.decorator import spectree_serialize
from pcapi.utils import requests as requests_utils

from .. import blueprint
from .serialization import subscription as serializers


logger = logging.getLogger(__name__)


@blueprint.native_route("/subscription/next_step", methods=["GET"])
@spectree_serialize(
    response_model=serializers.NextSubscriptionStepResponse,
    on_success_status=200,
    api=blueprint.api,
    deprecated=True,
)
@authenticated_and_active_user_required
def next_subscription_step(
    user: users_models.User,
) -> serializers.NextSubscriptionStepResponse | None:
    user_subscription_state = subscription_api.get_user_subscription_state(user)
    logger.info(
        "next_subscription_step: %s",
        user_subscription_state.next_step.value if user_subscription_state.next_step else None,
        extra={"user_id": user.id},
    )
    return serializers.NextSubscriptionStepResponse(
        next_subscription_step=user_subscription_state.next_step,
        # FIXME: (thconte, 03/04/2023) deprecated. Remove this field when:
        # [ ] it is not used anymore in the frontend
        # [ ] a forced updated happened
        allowed_identity_check_methods=subscription_api.get_allowed_identity_check_methods(user),
        maintenance_page_type=subscription_api.get_maintenance_page_type(user),
        has_identity_check_pending=fraud_api.has_user_pending_identity_check(user),
        subscription_message=user_subscription_state.subscription_message,  # type: ignore[arg-type]
    )


@blueprint.native_route("/subscription/stepper", methods=["GET"])
@spectree_serialize(
    response_model=serializers.SubscriptionStepperResponse,
    on_success_status=200,
    api=blueprint.api,
    deprecated=True,
)
@authenticated_and_active_user_required
def get_subscription_stepper_deprecated(user: users_models.User) -> serializers.SubscriptionStepperResponse:
    user_subscription_state = subscription_api.get_user_subscription_state(user)
    stepper_header = subscription_api.get_stepper_title_and_subtitle(user, user_subscription_state)
    subscription_steps_to_display = subscription_api.get_subscription_steps_to_display(user, user_subscription_state)

    return serializers.SubscriptionStepperResponse(
        subscription_steps_to_display=[
            serializers.SubscriptionStepDetailsResponse(
                title=step.title,
                subtitle=step.subtitle,
                completion_state=step.completion_state,
                name=step.name,
            )
            for step in subscription_steps_to_display
        ],
        allowed_identity_check_methods=subscription_api.get_allowed_identity_check_methods(user),
        maintenance_page_type=subscription_api.get_maintenance_page_type(user),
        title=stepper_header.title,
        subtitle=stepper_header.subtitle,
        error_message=(
            user_subscription_state.subscription_message.message_summary
            if user_subscription_state.subscription_message
            else None
        ),
    )


@blueprint.native_route("/subscription/stepper", version="v2", methods=["GET"])
@spectree_serialize(
    response_model=serializers.SubscriptionStepperResponseV2,
    on_success_status=200,
    api=blueprint.api,
)
@authenticated_and_active_user_required
def get_subscription_stepper(user: users_models.User) -> serializers.SubscriptionStepperResponseV2:
    user_subscription_state = subscription_api.get_user_subscription_state(user)
    stepper_header = subscription_api.get_stepper_title_and_subtitle(user, user_subscription_state)
    subscription_steps_to_display = subscription_api.get_subscription_steps_to_display(user, user_subscription_state)

    return serializers.SubscriptionStepperResponseV2(
        subscription_steps_to_display=[
            serializers.SubscriptionStepDetailsResponse(
                title=step.title,
                subtitle=step.subtitle,
                completion_state=step.completion_state,
                name=step.name,
            )
            for step in subscription_steps_to_display
        ],
        allowed_identity_check_methods=subscription_api.get_allowed_identity_check_methods(user),
        has_identity_check_pending=fraud_api.has_user_pending_identity_check(user),
        maintenance_page_type=subscription_api.get_maintenance_page_type(user),
        next_subscription_step=user_subscription_state.next_step,
        title=stepper_header.title,
        subtitle=stepper_header.subtitle,
        subscription_message=user_subscription_state.subscription_message,  # type: ignore[arg-type]
    )


@blueprint.native_route("/subscription/profile", methods=["GET"])
@spectree_serialize(on_success_status=200, on_error_statuses=[404], api=blueprint.api)
@authenticated_and_active_user_required
def get_profile(user: users_models.User) -> serializers.ProfileResponse | None:
    if (profile_data := subscription_api.get_profile_data(user)) is not None:
        try:
            return serializers.ProfileResponse(profile=serializers.ProfileContent(**profile_data.dict()))
        except ValidationError as e:
            logger.error("Invalid profile data for user %s: %s", user.id, e)
            return serializers.ProfileResponse()  # type: ignore[call-arg]

    raise api_errors.ResourceNotFoundError()


@blueprint.native_route("/subscription/profile", methods=["POST"])
@spectree_serialize(on_success_status=204, api=blueprint.api)
@authenticated_and_active_user_required
def complete_profile(user: users_models.User, body: serializers.ProfileUpdateRequest) -> None:
    subscription_api.complete_profile(
        user,
        first_name=body.first_name,
        last_name=body.last_name,
        address=body.address,
        city=body.city,
        postal_code=body.postal_code,
        activity=users_models.ActivityEnum[body.activity_id.value],
        school_type=users_models.SchoolTypeEnum[body.school_type_id.value] if body.school_type_id is not None else None,
    )
    is_activated = subscription_api.activate_beneficiary_if_no_missing_step(user)

    if not is_activated:
        external_attributes_api.update_external_user(user)


@blueprint.native_route("/subscription/activity_types", methods=["GET"])
@spectree_serialize(
    response_model=serializers.ActivityTypesResponse,
    on_success_status=200,
    api=blueprint.api,
)
@authenticated_and_active_user_required
def get_activity_types(user: users_models.User) -> serializers.ActivityTypesResponse:
    activities = [serializers.ActivityResponseModel.from_orm(activity) for activity in profile_options.ALL_ACTIVITIES]
    middle_school = serializers.ActivityResponseModel.from_orm(profile_options.MIDDLE_SCHOOL_STUDENT)
    if user.eligibility == users_models.EligibilityType.AGE18 and middle_school in activities:
        activities.remove(middle_school)

    return serializers.ActivityTypesResponse(activities=activities)


@blueprint.native_route("/subscription/honor_statement", methods=["POST"])
@spectree_serialize(on_success_status=204, api=blueprint.api)
@authenticated_and_active_user_required
def create_honor_statement_fraud_check(user: users_models.User) -> None:
    fraud_api.create_honor_statement_fraud_check(user, "statement from /subscription/honor_statement endpoint")

    is_activated = subscription_api.activate_beneficiary_if_no_missing_step(user)

    if not is_activated:
        external_attributes_api.update_external_user(user)


@blueprint.native_route("/ubble_identification", methods=["POST"])
@spectree_serialize(api=blueprint.api, response_model=serializers.IdentificationSessionResponse)
@authenticated_and_active_user_required
def start_identification_session(
    user: users_models.User, body: serializers.IdentificationSessionRequest
) -> serializers.IdentificationSessionResponse:
    if user.eligibility is None:
        raise api_errors.ApiErrors(
            {"code": "IDCHECK_NOT_ELIGIBLE", "message": "Non éligible à un crédit"},
            status_code=400,
        )

    if (
        not subscription_api.get_user_subscription_state(user).next_step
        == subscription_models.SubscriptionStep.IDENTITY_CHECK
    ):
        raise api_errors.ApiErrors(
            {"code": "IDCHECK_ALREADY_PROCESSED", "message": "Une identification a déjà été traitée"},
            status_code=400,
        )

    fraud_check = ubble_fraud_api.get_restartable_identity_checks(user)
    if fraud_check:
        source_data = typing.cast(fraud_models.UbbleContent, fraud_check.source_data())
        if not source_data.identification_url:
            raise api_errors.ApiErrors(
                {"code": "IDENTIFICATION_URL_NOT_FOUND", "message": "L'url d'identification n'a pas été trouvée"},
                status_code=400,
            )
        return serializers.IdentificationSessionResponse(identificationUrl=source_data.identification_url)

    declared_names = subscription_api.get_declared_names(user)

    if not declared_names:
        logger.error("Ubble: no names found to start identification session", extra={"user_id": user.id})
        raise api_errors.ApiErrors({"code": "NO_FIRST_NAME_AND_LAST_NAME"})

    try:
        identification_url = ubble_subscription_api.start_ubble_workflow(
            user, declared_names[0], declared_names[1], body.redirectUrl
        )
        return serializers.IdentificationSessionResponse(identificationUrl=identification_url)  # type: ignore[arg-type]

    except requests_utils.ExternalAPIException as exception:
        if exception.is_retryable:
            code = "IDCHECK_SERVICE_UNAVAILABLE"
            message = "Le service d'identification n'est pas joignable"
            return_status = 503
        else:
            code = "IDCHECK_SERVICE_ERROR"
            message = "Une erreur s'est produite à l'appel du service d'identification"
            return_status = 500
        raise api_errors.ApiErrors({"code": code, "message": message}, status_code=return_status)
