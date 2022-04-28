import datetime
import logging

from dateutil.relativedelta import relativedelta

from pcapi import settings
from pcapi.connectors.dms import api as dms_api
from pcapi.connectors.dms import exceptions as dms_exceptions
from pcapi.connectors.dms import models as dms_models


logger = logging.getLogger(__name__)


def handle_inactive_dms_applications(procedure_id: int) -> None:
    logger.info("Handling inactive application for procedure %d", procedure_id)

    draft_applications = dms_api.DMSGraphQLClient().get_applications_with_details(
        procedure_id, dms_models.GraphQLApplicationStates.draft
    )

    for draft_application in draft_applications:
        try:
            if _has_inactivity_delay_expired(draft_application):
                _mark_without_continuation_a_draft_application(draft_application)
        except (dms_exceptions.DmsGraphQLApiException, Exception):  # pylint: disable=broad-except
            logger.exception("Could not mark application %s without continuation", draft_application.number)
            continue


def _has_inactivity_delay_expired(dms_application: dms_models.DmsApplicationResponse) -> bool:
    date_with_delay = datetime.datetime.utcnow() - relativedelta(days=settings.DMS_INACTIVITY_TOLERANCE_DELAY)

    if dms_application.latest_modification_date >= date_with_delay:
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
        motivation=f"Aucune activité n'a eu lieu sur votre dossier depuis plus de {settings.DMS_INACTIVITY_TOLERANCE_DELAY} jours",
    )

    logger.info("Marked application %s without continuation", dms_application.number)
