import logging

from pcapi import settings
from pcapi.connectors.dms import api as dms_connector_api
from pcapi.core import logging as core_logging
from pcapi.core.fraud import api as fraud_api
from pcapi.core.fraud.ubble import api as ubble_fraud_api
from pcapi.core.subscription import api as subscription_api
from pcapi.core.subscription import exceptions as subscription_exceptions
from pcapi.core.subscription import messages as subscription_messages
from pcapi.core.subscription.dms import api as dms_subscription_api
from pcapi.core.subscription.ubble import api as ubble_subscription_api
from pcapi.core.users.repository import find_user_by_email
from pcapi.models.api_errors import ApiErrors
from pcapi.models.beneficiary_import import BeneficiaryImportSources
from pcapi.models.beneficiary_import_status import ImportStatus
from pcapi.repository import repository
from pcapi.routes.apis import public_api
from pcapi.serialization.decorator import spectree_serialize
from pcapi.validation.routes import dms as dms_validation
from pcapi.validation.routes import ubble as ubble_validation


logger = logging.getLogger(__name__)


DMS_APPLICATION_MAP = {
    dms_connector_api.GraphQLApplicationStates.draft: ImportStatus.DRAFT,
    dms_connector_api.GraphQLApplicationStates.on_going: ImportStatus.ONGOING,
    # dms_connector_api.GraphQLApplicationStates.accepted: ImportStatus what to do with it ?
    # for now it will be done in the import_dms_users script
    # later we might want to run the user validation and then archive the application
    dms_connector_api.GraphQLApplicationStates.refused: ImportStatus.REJECTED,
    dms_connector_api.GraphQLApplicationStates.without_continuation: ImportStatus.WITHOUT_CONTINUATION,
}


@public_api.route("/webhooks/dms/application_status", methods=["POST"])
@dms_validation.require_dms_token
@spectree_serialize(on_success_status=204, json_format=False)
def dms_webhook_update_application_status(form: dms_validation.DMSWebhookRequest) -> None:
    client = dms_connector_api.DMSGraphQLClient()
    raw_data = client.get_single_application_details(form.dossier_id)

    user_email = raw_data["dossier"]["usager"]["email"]
    application_id = raw_data["dossier"]["number"]
    dossier_id = raw_data["dossier"]["id"]

    log_extra_data = {
        "application_id": application_id,
        "dossier_id": form.dossier_id,
        "procedure_id": form.procedure_id,
        "user_email": user_email,
    }

    user = find_user_by_email(user_email)
    if not user:
        if form.state == dms_connector_api.GraphQLApplicationStates.draft:
            client.send_user_message(
                dossier_id,
                settings.DMS_INSTRUCTOR_ID,
                subscription_messages.DMS_ERROR_MESSAGE_USER_NOT_FOUND,
            )

        logger.info(
            "User not found for application %s procedure %s email %s",
            application_id,
            form.procedure_id,
            user_email,
            extra=log_extra_data,
        )
        return
    try:
        application = dms_connector_api.parse_beneficiary_information_graphql(raw_data["dossier"], form.procedure_id)
        core_logging.log_for_supervision(
            logger=logger,
            log_level=logging.INFO,
            log_message="Successfully parsed DMS application",
            extra=log_extra_data,
        )
    except subscription_exceptions.DMSParsingError as parsing_error:
        subscription_messages.on_dms_application_parsing_errors_but_updatables_values(
            user, list(parsing_error.errors.keys())
        )
        if form.state == dms_connector_api.GraphQLApplicationStates.draft:
            dms_subscription_api.notify_parsing_exception(parsing_error.errors, dossier_id, client)

        logger.info(
            "Cannot parse DMS application %s in webhook. Errors will be handled in the import_dms_users cron",
            form.dossier_id,
            extra=log_extra_data,
        )
        return

    eligibility_type = fraud_api.decide_eligibility(user, application)
    if eligibility_type is None:
        logger.info(
            "Birthdate of DMS application %d shows that user is not eligible",
            form.dossier_id,
            extra=log_extra_data,
        )
        subscription_messages.on_dms_application_parsing_errors_but_updatables_values(user, ["birth_date"])
        if form.state == dms_connector_api.GraphQLApplicationStates.draft:
            client.send_user_message(
                dossier_id,
                settings.DMS_INSTRUCTOR_ID,
                subscription_messages.DMS_ERROR_MESSSAGE_BIRTH_DATE,
            )
        return

    import_status = DMS_APPLICATION_MAP.get(form.state)
    if import_status:
        subscription_api.attach_beneficiary_import_details(
            user,
            form.dossier_id,
            form.procedure_id,
            BeneficiaryImportSources.demarches_simplifiees,
            eligibility_type=eligibility_type,
            details="Webhook status update",
            status=import_status,
        )

    dms_subscription_api.handle_dms_state(user, application, form.procedure_id, form.dossier_id, form.state)

    if not user.hasCompletedIdCheck:
        user.hasCompletedIdCheck = True
        repository.save(user)


@public_api.route("/webhooks/ubble/application_status", methods=["POST"])
@ubble_validation.require_ubble_signature
@spectree_serialize(
    headers=ubble_validation.WebhookRequestHeaders,
    on_success_status=200,
    response_model=ubble_validation.WebhookDummyReponse,
)
def ubble_webhook_update_application_status(
    body: ubble_validation.WebhookRequest,
) -> ubble_validation.WebhookDummyReponse:
    logger.info("Ubble webhook called", extra={"identification_id": body.identification_id, "status": str(body.status)})

    fraud_check = ubble_fraud_api.get_ubble_fraud_check(body.identification_id)
    if not fraud_check:
        raise ValueError(f"no Ubble fraud check found with identification_id {body.identification_id}")

    try:
        ubble_subscription_api.update_ubble_workflow(fraud_check, body.status)
    except Exception as err:
        logger.warning(
            "Could not update Ubble workflow %s for user #%s",
            body.identification_id,
            fraud_check.userId,
            extra={"exception": err},
        )
        raise ApiErrors({"msg": "an error occured during workflow update"}, status_code=500)
    else:
        return ubble_validation.WebhookDummyReponse()
