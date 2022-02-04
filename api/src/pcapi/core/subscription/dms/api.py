import logging

from pcapi.connectors.dms import api as api_dms
from pcapi.core.fraud.dms import api as fraud_dms_api
import pcapi.core.fraud.models as fraud_models
from pcapi.core.subscription import messages as subscription_messages
import pcapi.core.users.models as users_models
import pcapi.repository as pcapi_repository


logger = logging.getLogger(__name__)


def handle_dms_state(
    user: users_models.User,
    application: fraud_models.DMSContent,
    procedure_id: int,
    application_id: int,
    state: api_dms.GraphQLApplicationStates,
) -> None:

    logs_extra = {"application_id": application_id, "procedure_id": procedure_id, "user_email": user.email}

    current_fraud_check = fraud_dms_api.get_fraud_check(user, application_id)
    if current_fraud_check is None:
        # create a fraud_check whatever the status is because we may have missed a webhook event
        current_fraud_check = fraud_dms_api.create_fraud_check(user, application)
        user.submit_user_identity()

    if state == api_dms.GraphQLApplicationStates.draft:
        subscription_messages.on_dms_application_received(user)
        logger.info("DMS Application started.", extra=logs_extra)

    elif state == api_dms.GraphQLApplicationStates.on_going:
        subscription_messages.on_dms_application_received(user)
        current_fraud_check.status = fraud_models.FraudCheckStatus.PENDING
        logger.info("DMS Application created.", extra=logs_extra)

    elif state == api_dms.GraphQLApplicationStates.accepted:
        logger.info("DMS Application accepted. User will be validated in the cron job.", extra=logs_extra)

    elif state == api_dms.GraphQLApplicationStates.refused:
        current_fraud_check.status = fraud_models.FraudCheckStatus.KO
        subscription_messages.on_dms_application_refused(user)

        logger.info("DMS Application refused.", extra=logs_extra)

    pcapi_repository.repository.save(current_fraud_check)
