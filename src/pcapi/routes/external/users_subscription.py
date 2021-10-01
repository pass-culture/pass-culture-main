import logging

from pcapi.connectors import api_demarches_simplifiees
from pcapi.core.subscription import api as subscription_api
from pcapi.models import BeneficiaryImportSources
from pcapi.models import ImportStatus
from pcapi.repository import repository
from pcapi.repository.user_queries import find_user_by_email
from pcapi.routes.apis import public_api
from pcapi.scripts.beneficiary import remote_import
from pcapi.serialization.decorator import spectree_serialize
from pcapi.validation.routes import dms as dms_validation


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
    application = remote_import.parse_beneficiary_information_graphql(raw_data["dossier"], form.procedure_id)

    user = find_user_by_email(application.email)
    if not user:
        logger.info(
            "User not found for application %d procedure %d email %s",
            application.application_id,
            application.procedure_id,
            application.email,
        )
        return

    import_status = DMS_APPLICATION_MAP.get(form.state)
    if import_status:
        subscription_api.attach_beneficiary_import_details(
            user,
            form.dossier_id,
            form.procedure_id,
            BeneficiaryImportSources.demarches_simplifiees,
            "Webhook status update",
            import_status,
        )

    if not user.hasCompletedIdCheck:
        user.hasCompletedIdCheck = True
        repository.save(user)
