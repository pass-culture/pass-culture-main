import logging

from sqlalchemy.orm import exc as sqla_exc

from pcapi import settings
from pcapi.connectors.dms import api as dms_api
from pcapi.connectors.dms import exceptions as dms_exceptions
from pcapi.connectors.dms import models as dms_models
from pcapi.core.fraud import models as fraud_models
from pcapi.repository import repository


logger = logging.getLogger(__name__)


def handle_single_inactive_dms_application(application_number: int) -> None:
    logger.info("[DMS] Handling single inactive application %d", application_number)
    marked_applications_count = 0
    draft_application = dms_api.DMSGraphQLClient().get_single_application_details(application_number)

    try:
        _mark_without_continuation_a_draft_application(draft_application)
        _mark_cancel_dms_fraud_check(draft_application.number, draft_application.profile.email)
        marked_applications_count += 1
    except (dms_exceptions.DmsGraphQLApiException, Exception):  # pylint: disable=broad-except
        logger.exception("[DMS] Could not mark application %s without continuation", draft_application.number)


def _mark_without_continuation_a_draft_application(dms_application: dms_models.DmsApplicationResponse) -> None:
    dms_api.DMSGraphQLClient().make_on_going(
        dms_application.id, settings.DMS_ENROLLMENT_INSTRUCTOR, disable_notification=True
    )
    logger.info("[DMS] Marked application %s on going", dms_application.number)
    dms_api.DMSGraphQLClient().mark_without_continuation(
        dms_application.id,
        settings.DMS_ENROLLMENT_INSTRUCTOR,
        motivation=f"Aucune activité n'a eu lieu sur votre dossier depuis plus de {settings.DMS_INACTIVITY_TOLERANCE_DELAY} jours. Si vous souhaitez le soumettre à nouveau, vous pouvez contacter le support à l'adresse {settings.SUPPORT_EMAIL_ADDRESS}",
    )

    logger.info("[DMS] Marked application %s without continuation", dms_application.number)


def _mark_cancel_dms_fraud_check(application_number: int, email: str) -> None:
    try:
        fraud_check = fraud_models.BeneficiaryFraudCheck.query.filter(
            fraud_models.BeneficiaryFraudCheck.type == fraud_models.FraudCheckType.DMS,
            fraud_models.BeneficiaryFraudCheck.thirdPartyId == str(application_number),
            fraud_models.BeneficiaryFraudCheck.resultContent.is_not(None),
            fraud_models.BeneficiaryFraudCheck.resultContent.contains({"email": email}),
        ).one_or_none()
    except sqla_exc.MultipleResultsFound:
        logger.exception("[DMS] Multiple fraud checks found for application %s", application_number)
        return

    if fraud_check:
        fraud_check.status = fraud_models.FraudCheckStatus.CANCELED
        fraud_check.reason = f"Automatiquement classé sans_suite car aucune activité n'a eu lieu depuis plus de {settings.DMS_INACTIVITY_TOLERANCE_DELAY} jours"
        repository.save(fraud_check)
