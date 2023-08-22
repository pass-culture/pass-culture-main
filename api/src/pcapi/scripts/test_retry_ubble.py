import logging

from sqlalchemy.orm.attributes import flag_modified

from pcapi.analytics.amplitude import events as amplitude_events
from pcapi.core.fraud import factories as fraud_factories
from pcapi.core.fraud import models as fraud_models
from pcapi.core.fraud.ubble import api as ubble_fraud_api
from pcapi.core.fraud.ubble import models as ubble_fraud_models
from pcapi.core.subscription import api as subscription_api
from pcapi.core.subscription.ubble import api as subscription_ubble_api
from pcapi.core.users import models as users_models
from pcapi.models import db
from pcapi.repository import repository


logger = logging.getLogger(__name__)


def make_user_identity_retryable(user_id: int) -> None:
    user = users_models.User.query.get(user_id)
    user.roles = []
    repository.save(user)
    if deposit := user.deposit:
        repository.delete(deposit)
    fraud_check = subscription_api.get_relevant_identity_fraud_check(user, user.eligibility)
    if fraud_check:
        fraud_check.status = fraud_models.FraudCheckStatus.SUSPICIOUS
        fraud_check.reasonCodes = [fraud_models.FraudReasonCode.DOCUMENT_DAMAGED]
    else:
        fraud_check = fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            status=fraud_models.FraudCheckStatus.SUSPICIOUS,
            reasonCodes=[fraud_models.FraudReasonCode.DOCUMENT_DAMAGED],
        )
    fraud_check.resultContent.update(
        comment="Test Ubble Retryable",
        score=ubble_fraud_models.UbbleScore.INVALID.value,
        reason_codes=[fraud_models.FraudReasonCode.DOCUMENT_DAMAGED],
    )
    flag_modified(fraud_check, "resultContent")
    repository.save(fraud_check)
    db.session.refresh(fraud_check)

    try:
        ubble_fraud_api.on_ubble_result(fraud_check)
    except Exception:  # pylint: disable=broad-except
        logger.exception("Error on Ubble fraud check result: %s", extra={"user_id": user.id})
        return

    subscription_ubble_api.handle_validation_errors(user, fraud_check)
    amplitude_events.track_ubble_error_event(user.id, fraud_check.reasonCodes or [])
