import datetime
import logging

from dateutil.relativedelta import relativedelta
from sqlalchemy.orm import exc as sqla_exc

from pcapi import settings
from pcapi.connectors.dms import api as dms_api
from pcapi.connectors.dms import exceptions as dms_exceptions
from pcapi.connectors.dms import models as dms_models
from pcapi.connectors.dms import serializer as dms_serializer
from pcapi.core.fraud import models as fraud_models
from pcapi.core.users import utils as users_utils
from pcapi.domain.postal_code.postal_code import PostalCode
from pcapi.repository import repository


logger = logging.getLogger(__name__)

PRE_GENERALISATION_DEPARTMENTS = ["08", "22", "25", "29", "34", "35", "56", "58", "67", "71", "84", "93", "94", "973"]


def handle_inactive_dms_applications(procedure_number: int, with_never_eligible_applicant_rule: bool = False) -> None:
    logger.info("[DMS] Handling inactive application for procedure %d", procedure_number)
    marked_applications_count = 0
    draft_applications = dms_api.DMSGraphQLClient().get_applications_with_details(
        procedure_number, dms_models.GraphQLApplicationStates.draft
    )

    for draft_application in draft_applications:
        try:
            if not _has_inactivity_delay_expired(draft_application):
                continue
            if with_never_eligible_applicant_rule and _is_never_eligible_applicant(draft_application):
                continue
            _mark_without_continuation_a_draft_application(draft_application)
            _mark_cancel_dms_fraud_check(draft_application.number)
            marked_applications_count += 1
        except (dms_exceptions.DmsGraphQLApiException, Exception):  # pylint: disable=broad-except
            logger.exception(
                "[DMS] Could not mark application %s without continuation",
                draft_application.number,
                extra={"procedure_number": procedure_number},
            )
            continue

    logger.info("[DMS] Marked %d inactive applications for procedure %d", marked_applications_count, procedure_number)


def _has_inactivity_delay_expired(dms_application: dms_models.DmsApplicationResponse) -> bool:
    date_with_delay = datetime.datetime.utcnow() - relativedelta(days=settings.DMS_INACTIVITY_TOLERANCE_DELAY)

    if dms_application.latest_modification_datetime >= date_with_delay:
        return False

    if not dms_application.messages:
        return True

    most_recent_message = max(dms_application.messages, key=lambda message: message.created_at)

    return most_recent_message.created_at <= date_with_delay and not _is_message_from_applicant(
        dms_application, most_recent_message
    )


def _is_message_from_applicant(
    dms_application: dms_models.DmsApplicationResponse, message: dms_models.DMSMessage
) -> bool:
    return message.email == dms_application.profile.email


def _mark_without_continuation_a_draft_application(dms_application: dms_models.DmsApplicationResponse) -> None:
    """Mark a draft application as without continuation.

    First make it on_going - disable notification to only notificate the user of the without_continuation change
    Then mark it without_continuation
    """

    dms_api.DMSGraphQLClient().make_on_going(
        dms_application.id, settings.DMS_ENROLLMENT_INSTRUCTOR, disable_notification=True
    )

    dms_api.DMSGraphQLClient().mark_without_continuation(
        dms_application.id,
        settings.DMS_ENROLLMENT_INSTRUCTOR,
        motivation=f"Aucune activité n'a eu lieu sur votre dossier depuis plus de {settings.DMS_INACTIVITY_TOLERANCE_DELAY} jours. Si vous souhaitez le soumettre à nouveau, vous pouvez contacter le support à l'adresse {settings.SUPPORT_EMAIL_ADDRESS}",
    )

    logger.info("[DMS] Marked application %s without continuation", dms_application.number)


def _mark_cancel_dms_fraud_check(application_number: int) -> None:
    try:
        fraud_check = fraud_models.BeneficiaryFraudCheck.query.filter_by(
            type=fraud_models.FraudCheckType.DMS, thirdPartyId=str(application_number)
        ).one_or_none()
    except sqla_exc.MultipleResultsFound:
        logger.exception("[DMS] Multiple fraud checks found for application %s", application_number)
        return

    if fraud_check:
        fraud_check.status = fraud_models.FraudCheckStatus.CANCELED
        fraud_check.reason = f"Automatiquement classé sans_suite car aucune activité n'a eu lieu depuis plus de {settings.DMS_INACTIVITY_TOLERANCE_DELAY} jours"
        repository.save(fraud_check)


def _is_never_eligible_applicant(dms_application: dms_models.DmsApplicationResponse) -> bool:
    application_content, field_errors = dms_serializer.parse_beneficiary_information_graphql(dms_application)
    if field_errors:
        return True
    applicant_birth_date = application_content.get_birth_date()
    applicant_postal_code = application_content.get_postal_code()
    applicant_department = PostalCode(applicant_postal_code).get_departement_code() if applicant_postal_code else None
    if applicant_birth_date is None or applicant_department is None:
        return True

    age_at_generalisation = users_utils.get_age_at_date(applicant_birth_date, datetime.datetime(2021, 5, 21))

    return age_at_generalisation >= 19 and applicant_department not in PRE_GENERALISATION_DEPARTMENTS
