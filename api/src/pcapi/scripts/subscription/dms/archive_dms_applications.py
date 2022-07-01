import logging

from pcapi import settings
from pcapi.connectors.dms import api as api_dms
from pcapi.connectors.dms import models as dms_models
from pcapi.core.subscription.dms import repository as dms_repository


logger = logging.getLogger()


def archive_applications(procedure_number: int, dry_run: bool = True) -> None:
    total_applications = 0
    archived_applications = 0

    already_processed_applications_ids = dms_repository.get_already_processed_applications_ids(procedure_number)
    client = api_dms.DMSGraphQLClient()

    for application_details in client.get_applications_with_details(
        procedure_number, dms_models.GraphQLApplicationStates.accepted
    ):
        total_applications += 1

        application_techid = application_details.id
        application_number = application_details.number

        if application_number not in already_processed_applications_ids:
            continue

        if not dry_run:
            try:
                client.archive_application(application_techid, settings.DMS_ENROLLMENT_INSTRUCTOR)
            except Exception:  # pylint: disable=broad-except
                logger.exception("error while archiving application %d", application_number)
        logger.info("Archiving application %d on procedure %d", application_number, procedure_number)
        archived_applications += 1

    logger.info(
        "script ran : total applications : %d to archive applications : %d", total_applications, archived_applications
    )
