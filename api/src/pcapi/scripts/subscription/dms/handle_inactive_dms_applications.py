import datetime
import logging

from dateutil.relativedelta import relativedelta
from sqlalchemy.orm import exc as sa_exc

from pcapi import settings
from pcapi.connectors.dms import api as dms_api
from pcapi.connectors.dms import exceptions as dms_exceptions
from pcapi.connectors.dms import models as dms_models
from pcapi.connectors.dms import serializer as dms_serializer
from pcapi.connectors.dms import utils as dms_utils
from pcapi.core.fraud import models as fraud_models
from pcapi.core.users import utils as users_utils
from pcapi.models import db
from pcapi.repository import repository
import pcapi.utils.postal_code as postal_code_utils


logger = logging.getLogger(__name__)

PRE_GENERALISATION_DEPARTMENTS = ["08", "22", "25", "29", "34", "35", "56", "58", "67", "71", "84", "93", "94", "973"]

INACTIVITY_MESSAGE = """Aucune activité n’a eu lieu sur ton dossier depuis plus de {delay} jours.

Conformément à nos CGUs, en cas d’absence de réponse ou de justification insuffisante, nous nous réservons le droit de refuser ta création de compte. Aussi nous avons classé sans suite ton dossier n°{application_number}.

Sous réserve d’être encore éligible, tu peux si tu le souhaites refaire une demande d’inscription. Nous t'invitons à soumettre un nouveau dossier en suivant ce lien : https://www.demarches-simplifiees.fr/dossiers/new?procedure_id={procedure_id}

Tu trouveras toutes les informations dans notre FAQ pour t'accompagner dans cette démarche : https://aide.passculture.app/hc/fr/sections/4411991878545-Inscription-et-modification-d-information-sur-Démarches-Simplifiées
"""


def handle_inactive_dms_applications(procedure_number: int, with_never_eligible_applicant_rule: bool = False) -> None:
    logger.info("[DMS] Handling inactive application for procedure %d", procedure_number)
    marked_applications_count = 0
    draft_applications = dms_api.DMSGraphQLClient().get_applications_with_details(
        procedure_number, dms_models.GraphQLApplicationStates.draft
    )

    for draft_application in draft_applications:
        with dms_utils.lock_ds_application(draft_application.number):
            try:
                if not _has_inactivity_delay_expired(draft_application):
                    continue
                if with_never_eligible_applicant_rule and _is_never_eligible_applicant(draft_application):
                    continue
                _mark_without_continuation_a_draft_application(draft_application)
                _mark_cancel_dms_fraud_check(
                    draft_application.number, draft_application.applicant.email or draft_application.profile.email
                )
                marked_applications_count += 1
            except (dms_exceptions.DmsGraphQLApiException, Exception):  # pylint: disable=broad-except
                logger.exception(
                    "[DMS] Could not mark application %s without continuation",
                    draft_application.number,
                    extra={"procedure_number": procedure_number},
                )
                continue

    logger.info("[DMS] Marked %d inactive applications for procedure %d", marked_applications_count, procedure_number)


def _has_inactivity_delay_expired(dms_application: dms_models.DmsApplicationResponse) -> bool:
    date_with_delay = datetime.datetime.utcnow() - relativedelta(days=settings.DMS_INACTIVITY_TOLERANCE_DELAY)

    if dms_application.latest_modification_datetime >= date_with_delay:
        return False

    # Do not close application if no message has been sent by either an instructor or the automation
    if not dms_application.messages:
        return False

    most_recent_message = max(dms_application.messages, key=lambda message: message.created_at)

    return most_recent_message.created_at <= date_with_delay and not _is_message_from_applicant(
        dms_application, most_recent_message
    )


def _is_message_from_applicant(
    dms_application: dms_models.DmsApplicationResponse, message: dms_models.DMSMessage
) -> bool:
    return message.email == (dms_application.applicant.email or dms_application.profile.email)


def _mark_without_continuation_a_draft_application(dms_application: dms_models.DmsApplicationResponse) -> None:
    """Mark a draft application as without continuation.

    First make it on_going - disable notification to only notify the user of the without_continuation change
    Then mark it without_continuation
    """
    dms_api.DMSGraphQLClient().mark_without_continuation(
        dms_application.id,
        settings.DMS_ENROLLMENT_INSTRUCTOR,
        motivation=INACTIVITY_MESSAGE.format(
            delay=settings.DMS_INACTIVITY_TOLERANCE_DELAY,
            procedure_id=dms_application.procedure.number,
            application_number=dms_application.number,
        ),
        from_draft=True,
    )

    logger.info("[DMS] Marked application %s without continuation", dms_application.number)


def _mark_cancel_dms_fraud_check(application_number: int, email: str) -> None:
    try:
        fraud_check = (
            db.session.query(fraud_models.BeneficiaryFraudCheck)
            .filter(
                fraud_models.BeneficiaryFraudCheck.type == fraud_models.FraudCheckType.DMS,
                fraud_models.BeneficiaryFraudCheck.thirdPartyId == str(application_number),
                fraud_models.BeneficiaryFraudCheck.resultContent.is_not(None),
                fraud_models.BeneficiaryFraudCheck.resultContent.contains({"email": email}),
            )
            .one_or_none()
        )
    except sa_exc.MultipleResultsFound:
        logger.exception("[DMS] Multiple fraud checks found for application %s", application_number)
        return

    if fraud_check:
        fraud_check.status = fraud_models.FraudCheckStatus.CANCELED
        fraud_check.reason = f"Automatiquement classé sans_suite car aucune activité n'a eu lieu depuis plus de {settings.DMS_INACTIVITY_TOLERANCE_DELAY} jours"
        repository.save(fraud_check)


def _is_never_eligible_applicant(dms_application: dms_models.DmsApplicationResponse) -> bool:
    application_content = dms_serializer.parse_beneficiary_information_graphql(dms_application)
    if application_content.field_errors:
        return True
    applicant_birth_date = application_content.get_birth_date()
    applicant_postal_code = application_content.get_postal_code()
    applicant_department = (
        postal_code_utils.PostalCode(applicant_postal_code).get_departement_code() if applicant_postal_code else None
    )
    if applicant_birth_date is None or applicant_department is None:
        return True

    age_at_generalisation = users_utils.get_age_at_date(applicant_birth_date, datetime.datetime(2021, 5, 21))

    return age_at_generalisation >= 19 and applicant_department not in PRE_GENERALISATION_DEPARTMENTS
