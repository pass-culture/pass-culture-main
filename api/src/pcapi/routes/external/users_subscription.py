import logging

from pcapi import settings
from pcapi.connectors import api_demarches_simplifiees
from pcapi.core.fraud import api as fraud_api
from pcapi.core.subscription import api as subscription_api
from pcapi.core.subscription import messages as subscription_messages
from pcapi.models.beneficiary_import import BeneficiaryImportSources
from pcapi.models.beneficiary_import_status import ImportStatus
from pcapi.repository import repository
from pcapi.repository.user_queries import find_user_by_email
from pcapi.routes.apis import public_api
from pcapi.scripts.beneficiary import remote_import
from pcapi.serialization.decorator import spectree_serialize
from pcapi.validation.routes import dms as dms_validation
from pcapi.validation.routes import ubble as ubble_validation


logger = logging.getLogger(__name__)

DMS_APPLICATION_MAP = {
    api_demarches_simplifiees.GraphQLApplicationStates.draft: ImportStatus.DRAFT,
    api_demarches_simplifiees.GraphQLApplicationStates.on_going: ImportStatus.ONGOING,
    # api_demarches_simplifiees.GraphQLApplicationStates.accepted: ImportStatus what to do with it ?
    # for now it will be done in the remote_import script
    # later we might want to run the user validation and then archive the application
    api_demarches_simplifiees.GraphQLApplicationStates.refused: ImportStatus.REJECTED,
    api_demarches_simplifiees.GraphQLApplicationStates.without_continuation: ImportStatus.WITHOUT_CONTINUATION,
}


@public_api.route("/webhooks/dms/application_status", methods=["POST"])
@dms_validation.require_dms_token
@spectree_serialize(on_success_status=204, json_format=False)
def dms_webhook_update_application_status(form: dms_validation.DMSWebhookRequest) -> None:
    client = api_demarches_simplifiees.DMSGraphQLClient()
    raw_data = client.get_single_application_details(form.dossier_id)
    # todo(bcalvez) Use new IdcheckBackend to correctly convert this data
    user = find_user_by_email(raw_data["dossier"]["usager"]["email"])
    if not user:
        if raw_data["dossier"]["state"] == api_demarches_simplifiees.GraphQLApplicationStates.draft.value:
            client.send_user_message(
                raw_data["dossier"]["id"],
                settings.DMS_INSTRUCTOR_EMAIL,
                subscription_messages.DMS_ERROR_MESSAGE_USER_NOT_FOUND,
            )
        logger.info(
            "User not found for application %d procedure %d email %s",
            raw_data["dossier"]["number"],
            form.procedure_id,
            raw_data["dossier"]["usager"]["email"],
            extra={
                "application_id": raw_data["dossier"]["number"],
                "dossier_id": form.dossier_id,
                "procedure_id": form.procedure_id,
                "user_email": raw_data["dossier"]["usager"]["email"],
            },
        )
        return
    try:
        application = remote_import.parse_beneficiary_information_graphql(raw_data["dossier"], form.procedure_id)
    except remote_import.DMSParsingError as parsing_error:
        if raw_data["dossier"]["state"] == api_demarches_simplifiees.GraphQLApplicationStates.draft.value:
            remote_import.notify_parsing_exception(parsing_error.errors, raw_data["dossier"]["id"], client)

        logger.info(
            "Cannot parse DMS application %d in webhook. Errors will be handled in the remote_import cron",
            form.dossier_id,
            extra={
                "application_id": raw_data["dossier"]["number"],
                "dossier_id": form.dossier_id,
                "procedure_id": form.procedure_id,
                "user_email": raw_data["dossier"]["usager"]["email"],
            },
        )
        return

    import_status = DMS_APPLICATION_MAP.get(form.state)
    if import_status:
        subscription_api.attach_beneficiary_import_details(
            user,
            form.dossier_id,
            form.procedure_id,
            BeneficiaryImportSources.demarches_simplifiees,
            eligibility_type=fraud_api.get_eligibility_type(application),
            details="Webhook status update",
            status=import_status,
        )

    if form.state == api_demarches_simplifiees.GraphQLApplicationStates.draft:
        subscription_messages.on_dms_application_received(user)
    if form.state == api_demarches_simplifiees.GraphQLApplicationStates.refused:
        subscription_messages.on_dms_application_refused(user)
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
    fraud_check = fraud_api.get_ubble_fraud_check(body.identification_id)
    if not fraud_check:
        raise ValueError(f"no Ubble fraud check found with identification_id {body.identification_id}")

    subscription_api.update_ubble_workflow(fraud_check, body.status)

    return ubble_validation.WebhookDummyReponse()
