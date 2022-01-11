import logging

from pcapi.connectors import api_demarches_simplifiees
import pcapi.core.fraud.api as fraud_api
from pcapi.core.fraud.dms import api as fraud_dms_api
import pcapi.core.fraud.models as fraud_models
from pcapi.core.subscription import messages as subscription_messages
import pcapi.core.users.models as users_models
import pcapi.repository as pcapi_repository


logger = logging.getLogger(__name__)


def start_dms_workflow(user: users_models.User, content: fraud_models.DMSContent) -> fraud_models.BeneficiaryFraudCheck:
    user.submit_user_identity()
    pcapi_repository.repository.save(user)
    fraud_check = fraud_dms_api.start_dms_fraud_check(user, content)
    return fraud_check


def stop_dms_workflow(
    user: users_models.User, thirdparty_id: str, content: fraud_models.DMSContent
) -> fraud_models.BeneficiaryFraudCheck:
    fraud_check = fraud_api.mark_fraud_check_failed(user, thirdparty_id, content, reasons=[])
    return fraud_check


def handle_dms_state(
    user: users_models.User,
    application: fraud_models.DMSContent,
    procedure_id: str,
    application_id: str,
    state: api_demarches_simplifiees.GraphQLApplicationStates,
) -> None:

    if state == api_demarches_simplifiees.GraphQLApplicationStates.accepted:

        logger.info(
            "DMS Application accepted.",
            extra={
                "application_id": application_id,
                "procedure_id": procedure_id,
                "user_email": user.email,
            },
        )
    elif state in (
        api_demarches_simplifiees.GraphQLApplicationStates.draft,
        api_demarches_simplifiees.GraphQLApplicationStates.on_going,
    ):
        subscription_messages.on_dms_application_received(user)
        start_dms_workflow(user, application)

        logger.info(
            "DMS Application created.",
            extra={
                "application_id": application_id,
                "procedure_id": procedure_id,
                "user_email": user.email,
            },
        )

    elif state == api_demarches_simplifiees.GraphQLApplicationStates.refused:
        subscription_messages.on_dms_application_refused(user)
        stop_dms_workflow(user, application_id, application)

        logger.info(
            "DMS Application refused.",
            extra={
                "application_id": application_id,
                "procedure_id": procedure_id,
                "user_email": user.email,
            },
        )
