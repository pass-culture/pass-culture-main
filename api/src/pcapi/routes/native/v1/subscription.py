import logging
import typing
from functools import partial

from flask_login import current_user
from pydantic.v1 import ValidationError

from pcapi.connectors.beneficiaries import ubble as ubble_connector
from pcapi.core.external.attributes import api as external_attributes_api
from pcapi.core.subscription import api as subscription_api
from pcapi.core.subscription import exceptions
from pcapi.core.subscription import fraud_check_api as fraud_api
from pcapi.core.subscription import profile_options
from pcapi.core.subscription import schemas as subscription_schemas
from pcapi.core.subscription.bonus import fraud_check_api as bonus_fraud_api
from pcapi.core.subscription.bonus import tasks as bonus_tasks
from pcapi.core.subscription.ubble import api as ubble_subscription_api
from pcapi.core.subscription.ubble import fraud_check_api as ubble_fraud_api
from pcapi.core.subscription.ubble import schemas as ubble_schemas
from pcapi.core.users import api as users_api
from pcapi.core.users import models as users_models
from pcapi.models import api_errors
from pcapi.routes.native.security import authenticated_and_active_user_required
from pcapi.serialization.decorator import spectree_serialize
from pcapi.utils.transaction_manager import atomic
from pcapi.utils.transaction_manager import on_commit

from .. import blueprint
from .serialization import subscription as serializers


logger = logging.getLogger(__name__)


@blueprint.native_route("/subscription/stepper", version="v2", methods=["GET"])
@spectree_serialize(
    response_model=serializers.SubscriptionStepperResponseV2,
    on_success_status=200,
    api=blueprint.api,
)
@authenticated_and_active_user_required
def get_subscription_stepper() -> serializers.SubscriptionStepperResponseV2:
    user_subscription_state = subscription_api.get_user_subscription_state(current_user)
    subscription_message = user_subscription_state.subscription_message
    stepper_header = subscription_api.get_stepper_title_and_subtitle(current_user, user_subscription_state)
    subscription_steps_to_display = subscription_api.get_subscription_steps_to_display(
        current_user, user_subscription_state
    )

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
        allowed_identity_check_methods=subscription_api.get_allowed_identity_check_methods(current_user),
        has_identity_check_pending=fraud_api.has_user_pending_identity_check(current_user),
        maintenance_page_type=subscription_api.get_maintenance_page_type(current_user),
        next_subscription_step=user_subscription_state.next_step,
        title=stepper_header.title,
        subtitle=stepper_header.subtitle,
        subscription_message=serializers.SubscriptionMessageV2.from_orm(subscription_message)
        if subscription_message
        else None,
    )


@blueprint.native_route("/subscription/profile", methods=["GET"])
@spectree_serialize(on_success_status=200, on_error_statuses=[404], api=blueprint.api)
@authenticated_and_active_user_required
def get_profile() -> serializers.ProfileResponse | None:
    if (profile_data := subscription_api.get_profile_data(current_user)) is not None:
        try:
            return serializers.ProfileResponse(profile=serializers.ProfileContent(**profile_data.dict()))
        except ValidationError as e:
            logger.error("Invalid profile data for user %s: %s", current_user.id, e)
            return serializers.ProfileResponse()

    raise api_errors.ResourceNotFoundError()


@blueprint.native_route("/subscription/profile", methods=["POST"])
@spectree_serialize(on_success_status=204, api=blueprint.api)
@authenticated_and_active_user_required
@atomic()
def complete_profile(body: serializers.ProfileUpdateRequest) -> None:
    try:
        subscription_api.complete_profile(
            current_user,
            first_name=body.first_name,
            last_name=body.last_name,
            address=body.address,
            city=body.city,
            postal_code=body.postal_code,
            activity=users_models.ActivityEnum[body.activity_id.value],
            school_type=(
                users_models.SchoolTypeEnum[body.school_type_id.value] if body.school_type_id is not None else None
            ),
        )
    except exceptions.IneligiblePostalCodeException:
        raise api_errors.ApiErrors({"code": "INELIGIBLE_POSTAL_CODE"})

    is_activated = subscription_api.activate_beneficiary_if_no_missing_step(current_user)
    if not is_activated:
        external_attributes_api.update_external_user(current_user)


@blueprint.native_route("/subscription/activity_types", methods=["GET"])
@spectree_serialize(
    response_model=serializers.ActivityTypesResponse,
    on_success_status=200,
    api=blueprint.api,
)
@authenticated_and_active_user_required
def get_activity_types() -> serializers.ActivityTypesResponse:
    activities = [serializers.ActivityResponseModel.from_orm(activity) for activity in profile_options.ALL_ACTIVITIES]
    middle_school = serializers.ActivityResponseModel.from_orm(profile_options.MIDDLE_SCHOOL_STUDENT)
    if current_user.is_18_or_above_eligible and middle_school in activities:
        activities.remove(middle_school)

    return serializers.ActivityTypesResponse(activities=activities)


@blueprint.native_route("/subscription/honor_statement", methods=["POST"])
@spectree_serialize(on_success_status=204, api=blueprint.api)
@authenticated_and_active_user_required
@atomic()
def create_honor_statement_fraud_check() -> None:
    fraud_api.create_honor_statement_fraud_check(current_user, "statement from /subscription/honor_statement endpoint")

    is_activated = subscription_api.activate_beneficiary_if_no_missing_step(current_user)

    if not is_activated:
        external_attributes_api.update_external_user(current_user)


@blueprint.native_route("/ubble_identification", methods=["POST"])
@spectree_serialize(api=blueprint.api, response_model=serializers.IdentificationSessionResponse)
@authenticated_and_active_user_required
@atomic()
def start_identification_session(
    body: serializers.IdentificationSessionRequest,
) -> serializers.IdentificationSessionResponse:
    if current_user.eligibility is None:
        raise api_errors.ApiErrors(
            {"code": "IDCHECK_NOT_ELIGIBLE", "message": "Non éligible à un crédit"},
            status_code=400,
        )

    if (
        not subscription_api.get_user_subscription_state(current_user).next_step
        == subscription_schemas.SubscriptionStep.IDENTITY_CHECK
    ):
        raise api_errors.ApiErrors(
            {"code": "IDCHECK_ALREADY_PROCESSED", "message": "Une identification a déjà été traitée"},
            status_code=400,
        )

    fraud_check = ubble_fraud_api.get_restartable_identity_checks(current_user)
    if fraud_check:
        source_data = typing.cast(ubble_schemas.UbbleContent, fraud_check.source_data())
        if source_data.identification_url:
            return serializers.IdentificationSessionResponse(identificationUrl=source_data.identification_url)

    declared_names = subscription_api.get_declared_names(current_user)

    if not declared_names:
        logger.error("Ubble: no names found to start identification session", extra={"user_id": current_user.id})
        raise api_errors.ApiErrors({"code": "NO_FIRST_NAME_AND_LAST_NAME"})

    try:
        identification_url = ubble_subscription_api.start_ubble_workflow(
            current_user, declared_names[0], declared_names[1], body.redirectUrl
        )
        return serializers.IdentificationSessionResponse(identificationUrl=identification_url)  # type: ignore[arg-type]

    except ubble_connector.UbbleHttpError as exception:
        if isinstance(exception, ubble_connector.UbbleServerError):
            code = "IDCHECK_SERVICE_UNAVAILABLE"
            message = "Le service d'identification n'est pas joignable"
            return_status = 503
        else:
            code = "IDCHECK_SERVICE_ERROR"
            message = "Une erreur s'est produite à l'appel du service d'identification"
            return_status = 500
        raise api_errors.ApiErrors({"code": code, "message": message}, status_code=return_status)


@blueprint.native_route("/subscription/bonus/quotient_familial", methods=["POST"])
@spectree_serialize(on_success_status=204, api=blueprint.api)
@authenticated_and_active_user_required
@atomic()
def create_quotient_familial_bonus_credit_fraud_check(body: serializers.BonusCreditRequest) -> None:
    if not users_api.get_user_is_eligible_for_bonification(current_user):
        raise api_errors.ApiErrors(
            {"code": "BONUS_NOT_ELIGIBLE", "message": "Non éligible à la bonification"},
            status_code=400,
        )
    fraud_check = bonus_fraud_api.create_bonus_credit_fraud_check(
        current_user,
        last_name=body.last_name,
        common_name=body.common_name,
        first_names=body.first_names,
        birth_date=body.birth_date,
        gender=body.gender,
        birth_country_cog_code=body.birth_country_cog_code,
        birth_city_cog_code=body.birth_city_cog_code,
        origin="enrolled from /subscription/bonus/quotient_familial endpoint",
    )
    payload = bonus_tasks.GetQuotientFamilialTaskPayload(fraud_check_id=fraud_check.id).model_dump()
    on_commit(partial(bonus_tasks.apply_for_quotient_familial_bonus_task.delay, payload))
